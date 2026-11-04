"""Main-window icon buttons: click and hotkey must toast, and must not lose the front pin."""
import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QGuiApplication, QPixmap
from PySide6.QtWidgets import QWidget

from conftest import spin
from test_markup_tools import _img, _press


def test_icon_clicks_reach_their_actions(pc, toolbar, monkeypatch):
    started = []
    monkeypatch.setattr(toolbar, "start_inspect", lambda mode: started.append(mode))
    toolbar.btn_eyedropper.click()
    toolbar.btn_ruler.click()
    assert started == ["eyedropper", "ruler"]
    toolbar.btn_reopen.click()
    assert "없어요" in toolbar._last_notice
    assert toolbar._notice_toast.isVisible()
    toolbar.cfg["hotkeys"] = dict(pc.DEFAULTS["hotkeys"])
    toolbar._update_tooltips()
    tip = toolbar.btn_reopen.toolTip()
    assert "최근 핀" in tip and "Ctrl+Alt+R" in tip and "없어요" in tip


def test_inspect_toasts_when_busy_or_it_fails(pc, toolbar, monkeypatch):
    toolbar._capturing = True
    toolbar.btn_eyedropper.click()
    assert "고르고" in toolbar._last_notice
    toolbar._on_hotkey("ruler")
    assert toolbar._session is None
    assert toolbar._capturing is True

    toolbar._capturing = False

    class Boom:
        def __init__(self, mode):
            raise RuntimeError("grab failed")

    monkeypatch.setattr(pc, "ScreenInspectSession", Boom)
    toolbar.btn_eyedropper.click()
    spin(80)
    assert toolbar._capturing is False
    assert "못했어요" in toolbar._last_notice
    assert toolbar._notice_toast.isVisible()


def test_inspect_without_a_screen_toasts(pc, toolbar, monkeypatch):
    monkeypatch.setattr(pc.QGuiApplication, "screens", lambda: [])
    session = pc.ScreenInspectSession("eyedropper")
    got = {}
    session.finished.connect(lambda result: got.setdefault("result", result))
    session.start()
    spin(30)
    assert got["result"]["error"] == "noscreen"

    toolbar._on_hotkey("ruler")
    spin(80)
    assert toolbar._capturing is False
    assert "찾지 못했어요" in toolbar._last_notice


def test_inspect_overlay_is_raised_before_it_is_activated(pc, monkeypatch):
    def grab(_screen):
        pixmap = QPixmap(12, 8)
        pixmap.fill(QColor("white"))
        return pixmap

    monkeypatch.setattr(pc, "grab_screen_raw", grab)
    order = []

    def track_raise(self):
        order.append("raise")
        QWidget.raise_(self)

    def track_activate(self):
        order.append("activate")

    monkeypatch.setattr(pc.InspectOverlay, "raise_", track_raise)
    monkeypatch.setattr(pc.InspectOverlay, "activateWindow", track_activate)
    session = pc.ScreenInspectSession("ruler")
    session.start()
    try:
        assert session._overlays
        assert order.index("raise") < order.index("activate")
    finally:
        session._cleanup()


def test_markup_hotkey_edits_the_existing_pin_in_place(pc, toolbar):
    """A different history image must not open a second window over a pin."""
    red = _img(20, 16, "red")
    blue = _img(20, 16, "blue")
    toolbar.history = [pc.HistoryEntry(image=red)]
    toolbar.populate()
    front = toolbar._make_pin(blue, None)
    front.move(48, 36)
    home = front.frameGeometry()
    size = front.size()
    toolbar.show()
    toolbar.activateWindow()
    toolbar._on_hotkey("markup")
    spin(30)
    assert toolbar._pins == [front]
    assert front._editing is True
    assert front._tool == "pen"
    assert front.frameGeometry() == home
    assert front.size() == size
    assert front._bar is not None and front._bar.isVisible()


def test_last_clicked_pin_stays_front_when_the_main_window_is_active(pc, toolbar):
    older = toolbar._make_pin(_img(16, 12, "red"), None)
    newer = toolbar._make_pin(_img(16, 12, "blue"), None)
    assert toolbar._front_pin() is newer
    toolbar.show()
    toolbar.activateWindow()
    _press(older, QPoint(2, 2))
    assert toolbar._front_pin() is older
    toolbar.btn_markup.click()
    spin(30)
    assert older._editing is True
    assert newer._editing is False
    assert older._bar is not None and older._bar.isVisible()


def test_markup_click_through_toasts_on_the_main_window(pc, toolbar):
    pin = toolbar._make_pin(_img(16, 12, "white"), None)
    pin.set_click_through(True)
    toolbar.show()
    toolbar.btn_markup.click()
    assert pin._editing is False
    assert "클릭 통과" in toolbar._last_notice
    assert toolbar._notice_toast.isVisible()


def test_ocr_button_toasts_when_already_reading(pc, toolbar):
    toolbar._ocr_running = True
    toolbar.btn_ocr.click()
    assert toolbar._last_notice == pc.OCR_BUSY_MSG
    assert toolbar._notice_toast.isVisible()
    pin = toolbar._make_pin(_img(12, 8, "white"), None)
    pin._ocr_running = True
    result = pin.copy_ocr()
    assert result.ok is False
    assert result.message == pc.OCR_BUSY_MSG
    assert pin._toast is not None
    assert pin._toast.label.text() == pc.OCR_BUSY_MSG


def test_reopen_button_brings_the_pin_forward(pc, toolbar):
    pin = toolbar._make_pin(_img(12, 10, "navy"), QPoint(6, 8))
    pin.close()
    spin(20)
    assert toolbar._pins == []
    seen = []
    original = toolbar._present_pin

    def track(target):
        seen.append(target)
        original(target)

    toolbar._present_pin = track
    toolbar.show()
    toolbar.activateWindow()
    toolbar.btn_reopen.click()
    spin(30)
    assert len(toolbar._pins) == 1
    assert toolbar._pins[0].isVisible()
    assert seen and seen[0] is toolbar._pins[0]


def _overlay_still_open(widget) -> bool:
    try:
        return widget.isVisible()
    except RuntimeError:
        return False


def test_second_inspect_overlay_is_closed_when_creation_fails(pc, toolbar, monkeypatch):
    screen = QGuiApplication.primaryScreen()
    monkeypatch.setattr(pc.QGuiApplication, "screens", lambda: [screen, screen])

    def grab(_screen):
        pixmap = QPixmap(8, 8)
        pixmap.fill(QColor("white"))
        return pixmap

    monkeypatch.setattr(pc, "grab_screen_raw", grab)
    opened = []

    class Boom(pc.InspectOverlay):
        def __init__(self, screen, frozen, mode):
            if opened:
                raise RuntimeError("second overlay")
            super().__init__(screen, frozen, mode)
            opened.append(self)

    monkeypatch.setattr(pc, "InspectOverlay", Boom)
    session = pc.ScreenInspectSession("ruler")
    with pytest.raises(RuntimeError, match="second overlay"):
        session.start()
    assert session._overlays == []
    assert opened and _overlay_still_open(opened[0]) is False

    opened.clear()
    toolbar._was_visible = False
    toolbar._run_inspect("eyedropper")
    assert toolbar._capturing is False
    assert toolbar._session is None
    assert "못했어요" in toolbar._last_notice
    assert opened and _overlay_still_open(opened[0]) is False
