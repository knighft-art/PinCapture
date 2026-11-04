"""v0.9.1 main-window layout. Geometry is logical pixels, so 125% and 150% DPI scale it together."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QImage
from PySide6.QtWidgets import QApplication, QLabel

from conftest import spin


CAPTURE_BUTTONS = ("btn_region", "btn_window", "btn_full", "btn_pin")
ICON_BUTTONS = ("btn_markup", "btn_eyedropper", "btn_ruler", "btn_ocr", "btn_reopen")
SIZES = ((800, 520), (1000, 600), (1600, 1000))


def _img(w, h, color):
    image = QImage(w, h, QImage.Format.Format_RGB32)
    image.fill(QColor(color))
    return image


def _place(tb, w, h):
    tb.resize(w, h)
    tb.show()
    QApplication.processEvents()


def _box(tb, widget):
    origin = widget.mapTo(tb, widget.rect().topLeft())
    return origin.x(), origin.y(), widget.width(), widget.height()


def test_history_area_stays_at_least_three_times_the_top(pc, toolbar):
    """상단(헤더+도구 줄) : 보관함 은 최소 크기부터 큰 창까지 1:3 이상."""
    divider_y = None
    list_w = pc.HistoryEntry.THUMB_W + 48
    previews = []
    for w, h in SIZES:
        _place(toolbar, w, h)
        assert (toolbar.width(), toolbar.height()) == (w, h)
        _x, y, _w, height = _box(toolbar, toolbar._divider)
        assert height == 1
        assert (h - y) / y >= 3.0
        if divider_y is None:
            divider_y = y
        else:
            assert y == divider_y, "the top must not grow when the window grows"
        assert toolbar.listw.width() == list_w
        assert toolbar.listw.minimumWidth() == toolbar.listw.maximumWidth() == list_w
        assert toolbar.preview.width() / toolbar.listw.width() >= 1.618
        previews.append(toolbar.preview.width())
        rx, _ry, rw, _rh = _box(toolbar, toolbar.btn_reopen)
        assert rx + rw <= w - 16
        folder_right = _box(toolbar, toolbar.b_folder)[0] + toolbar.b_folder.width()
        remove_x, _remove_y, remove_w, _remove_h = _box(toolbar, toolbar.b_remove)
        assert folder_right <= remove_x
        assert remove_x + remove_w <= w - 16
        settings_right = _box(toolbar, toolbar.btn_settings)[0] + toolbar.btn_settings.width()
        assert settings_right <= w - 16
    assert previews == sorted(previews)
    assert previews[-1] > previews[0]


def test_spacing_button_size_and_section_titles(pc, toolbar):
    _place(toolbar, 1000, 600)
    margins = toolbar.layout().contentsMargins()
    assert (margins.left(), margins.top(), margins.right(), margins.bottom()) == (16, 8, 16, 8)
    assert toolbar.layout().spacing() == 8
    assert all(v % 8 == 0 for v in (margins.left(), margins.top(), margins.right(), margins.bottom()))

    capture = [getattr(toolbar, name) for name in CAPTURE_BUTTONS]
    assert {b.size().toTuple() for b in capture} == {(80, 48)}
    assert all(b.iconSize() == QSize(20, 20) for b in capture)
    icons = [getattr(toolbar, name) for name in ICON_BUTTONS]
    assert {b.size().toTuple() for b in icons} == {(40, 40)}
    assert all(b.iconSize() == QSize(20, 20) for b in icons)
    assert all(b.height() < capture[0].height() and b.width() < capture[0].width() for b in icons)
    assert {b.height() for b in (toolbar.btn_help, toolbar.btn_about, toolbar.btn_settings)} == {32}
    actions = (toolbar.b_copy, toolbar.b_save, toolbar.b_pin_sel, toolbar.b_folder, toolbar.b_remove)
    assert {b.height() for b in actions} == {32}

    assert toolbar.cap_title.styleSheet() == toolbar.hist_title.styleSheet()
    assert toolbar.cap_title.objectName() == toolbar.hist_title.objectName() == "sectionTitle"
    assert toolbar.cap_title.height() == toolbar.hist_title.height() == 24
    assert toolbar.info.height() == 24

    # 제목은 각 도구 줄 안에 있고, 아이콘은 캡처 버튼과 같은 줄·구분선 위.
    _cx, cy, _cw, ch = _box(toolbar, toolbar.btn_region)
    tx, ty, _tw, th = _box(toolbar, toolbar.cap_title)
    assert cy <= ty + th / 2 <= cy + ch
    assert tx < _box(toolbar, toolbar.btn_region)[0]
    _hx, hy, _hw, hh = _box(toolbar, toolbar.b_copy)
    _sx, sy, _sw, sh = _box(toolbar, toolbar.hist_title)
    assert hy <= sy + sh / 2 <= hy + hh
    divider_y = _box(toolbar, toolbar._divider)[1]
    for name in ICON_BUTTONS:
        ix, iy, iw, ih = _box(toolbar, getattr(toolbar, name))
        assert iy + ih <= divider_y
        assert abs((iy + ih / 2) - (cy + ch / 2)) <= 1
    order = [_box(toolbar, getattr(toolbar, name))[0] for name in CAPTURE_BUTTONS + ICON_BUTTONS]
    assert order == sorted(order)
    pin_right = _box(toolbar, toolbar.btn_pin)[0] + toolbar.btn_pin.width()
    assert _box(toolbar, toolbar.btn_markup)[0] > pin_right

    texts = [label.text() for label in toolbar.findChildren(QLabel)]
    assert not any("왼쪽이 지금 보는" in text for text in texts)
    assert not any("화면을 찍어 보관하고" in text for text in texts)


def test_icons_are_drawn_for_hidpi(pc):
    """아이콘 원본은 2배 픽셀. 배치 자체는 논리 픽셀이라 배율만 달라도 비율이 유지된다."""
    pixmap = pc._make_pixmap(20, pc._draw_markup, pc.TEXT)
    assert pixmap.devicePixelRatio() == 2.0
    assert (pixmap.width(), pixmap.height()) == (40, 40)
    icon = pc.make_icon("ocr", size=20)
    normal = icon.pixmap(20, 20, QIcon.Mode.Normal, QIcon.State.Off).toImage()
    disabled = icon.pixmap(20, 20, QIcon.Mode.Disabled, QIcon.State.Off).toImage()
    assert normal != disabled


def test_pin_tools_need_a_capture_or_a_pin(pc, toolbar):
    # Both stay clickable so a missing target still shows a toast.
    assert toolbar.btn_markup.isEnabled() is True
    assert toolbar.btn_ocr.isEnabled() is True
    toolbar.cfg["hotkeys"] = dict(pc.DEFAULTS["hotkeys"])
    toolbar._update_tooltips()
    assert "없어요" in toolbar.btn_markup.toolTip()
    assert "Ctrl+Alt+M" in toolbar.btn_markup.toolTip()
    assert "낙서" in toolbar.btn_markup.toolTip()
    assert "없어요" in toolbar.btn_ocr.toolTip()
    assert "단축키: 없음" in toolbar.btn_ocr.toolTip()
    toolbar.btn_markup.click()
    assert toolbar._notice_toast is not None and toolbar._notice_toast.isVisible()
    assert "없어요" in toolbar._notice_toast.label.text()
    toolbar.btn_ocr.click()
    assert toolbar._notice_toast is not None
    assert toolbar._notice_toast.isVisible()
    assert "없어요" in toolbar._notice_toast.label.text()
    assert toolbar.btn_eyedropper.isEnabled()
    assert toolbar.btn_ruler.isEnabled()
    assert toolbar.btn_reopen.isEnabled()

    red = _img(48, 32, "red")
    toolbar.history = [pc.HistoryEntry(image=red)]
    toolbar.populate()
    assert toolbar.btn_markup.isEnabled() and toolbar.btn_ocr.isEnabled()

    toolbar.btn_markup.click()
    spin(20)
    assert len(toolbar._pins) == 1
    pin = toolbar._pins[0]
    assert pin._editing and pin._img.cacheKey() == red.cacheKey()
    assert pin._bar is not None and pin._bar.windowTitle() == "표시"
    toolbar.btn_markup.click()
    assert toolbar._pins == [pin]

    toolbar.history = []
    toolbar.populate()
    assert toolbar._pins == [pin]
    assert toolbar.btn_markup.isEnabled() and toolbar.btn_ocr.isEnabled()
    toolbar.btn_markup.click()
    assert toolbar._pins == [pin] and pin._editing


def test_ocr_uses_the_selected_capture_before_the_front_pin(pc, toolbar, monkeypatch):
    red = _img(40, 24, "red")
    blue = _img(40, 24, "blue")
    toolbar.history = [pc.HistoryEntry(image=red)]
    toolbar.populate()
    front = toolbar._make_pin(blue, None)
    assert toolbar._front_pin() is front
    seen = {}

    def recognize(image):
        seen["key"] = image.cacheKey()
        return pc.OcrResult(True, "가나다", "글자를 복사했어요.")

    monkeypatch.setattr(pc, "recognize_image", recognize)
    toolbar.btn_ocr.click()
    assert seen["key"] == red.cacheKey()
    assert QApplication.clipboard().text() == "가나다"
    assert toolbar._pins == [front]

    toolbar.btn_markup.click()
    selected = [p for p in toolbar._pins if p._img.cacheKey() == red.cacheKey()]
    assert len(selected) == 1 and selected[0] is not front
    called = {}
    selected[0].copy_ocr = lambda: called.setdefault("selected", True) or "from-pin"
    front.copy_ocr = lambda: called.setdefault("front", True)
    monkeypatch.setattr(pc, "recognize_image", lambda image: called.setdefault("image", True))
    toolbar.btn_ocr.click()
    assert called == {"selected": True}


def test_icon_tooltips_include_the_name_and_shortcut(pc, toolbar):
    toolbar.history = [pc.HistoryEntry(image=_img(16, 16, "white"))]
    toolbar.populate()
    toolbar.cfg["hotkeys"] = dict(pc.DEFAULTS["hotkeys"])
    toolbar._update_tooltips()
    tips = {name: getattr(toolbar, name).toolTip() for name in ICON_BUTTONS}
    assert "핀에 그리기" in tips["btn_markup"] and "Ctrl+Alt+M" in tips["btn_markup"]
    assert "스포이트" in tips["btn_eyedropper"] and "Ctrl+Alt+C" in tips["btn_eyedropper"]
    assert "자" in tips["btn_ruler"] and "Ctrl+Alt+D" in tips["btn_ruler"]
    assert "Shift" in tips["btn_ruler"]
    assert "Shift" in tips["btn_markup"]
    assert "최근 핀" in tips["btn_reopen"] and "Ctrl+Alt+R" in tips["btn_reopen"]
    assert "글자 복사" in tips["btn_ocr"]
    assert "단축키: 없음" in tips["btn_ocr"]
    assert "Ctrl+" not in tips["btn_ocr"]
    assert toolbar.btn_markup.accessibleName() == "핀에 그리기"
    assert toolbar.btn_ocr.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
