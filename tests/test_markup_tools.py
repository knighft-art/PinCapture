"""v0.9.0 pin markup, eyedropper, and ruler. OCR stays on the unmarked original."""
from PySide6.QtCore import QEvent, QPoint, QPointF, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QKeyEvent, QMouseEvent, QPixmap
from PySide6.QtWidgets import QApplication

from conftest import spin


def _img(w, h, color):
    im = QImage(w, h, QImage.Format.Format_RGB32)
    im.fill(QColor(color))
    return im


def _rgb(image, x, y):
    c = QColor(image.pixel(x, y))
    return (c.red(), c.green(), c.blue())


def _changed(before, after):
    w, h = before.width(), before.height()
    for y in range(h):
        for x in range(w):
            if _rgb(before, x, y) != _rgb(after, x, y):
                return True
    return False


def _press(widget, pos, button=Qt.MouseButton.LeftButton, mods=Qt.KeyboardModifier.NoModifier):
    local = QPointF(pos)
    global_pos = QPointF(widget.mapToGlobal(QPoint(pos)))
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, local, global_pos,
        button, button, mods)
    QApplication.sendEvent(widget, event)


def _move(widget, pos, mods=Qt.KeyboardModifier.NoModifier):
    local = QPointF(pos)
    global_pos = QPointF(widget.mapToGlobal(QPoint(pos)))
    event = QMouseEvent(
        QEvent.Type.MouseMove, local, global_pos,
        Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, mods)
    QApplication.sendEvent(widget, event)


def _release(widget, pos, mods=Qt.KeyboardModifier.NoModifier):
    local = QPointF(pos)
    global_pos = QPointF(widget.mapToGlobal(QPoint(pos)))
    event = QMouseEvent(
        QEvent.Type.MouseButtonRelease, local, global_pos,
        Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, mods)
    QApplication.sendEvent(widget, event)


def _key(widget, key, mods=Qt.KeyboardModifier.NoModifier):
    event = QKeyEvent(QEvent.Type.KeyPress, key, mods)
    QApplication.sendEvent(widget, event)


def test_compose_arrow_box_highlight_and_mosaic(pc):
    white = _img(48, 48, "white")
    arrow = pc.compose_marks(white, [pc.Mark("arrow", 4, 24, 44, 24, "#E23B3B", 4)])
    assert _changed(white, arrow)
    assert _rgb(white, 24, 24) == (255, 255, 255)

    box = pc.compose_marks(white, [pc.Mark("box", 8, 8, 40, 40, "#E23B3B", 6)])
    assert _rgb(box, 24, 24) == (255, 255, 255)
    assert _rgb(box, 8, 24) != (255, 255, 255)

    hi = pc.compose_marks(white, [pc.Mark("highlight", 4, 4, 40, 40, "#F5C518", 4)])
    r, g, b = _rgb(hi, 20, 20)
    assert (r, g, b) != (255, 255, 255)
    assert b < 230 and r > 200 and g > 180
    assert _rgb(hi, 0, 0) == (255, 255, 255)

    checker = QImage(32, 32, QImage.Format.Format_RGB32)
    for y in range(32):
        for x in range(32):
            checker.setPixel(x, y, QColor("red" if (x + y) % 2 == 0 else "blue").rgb())
    mosaic = pc.compose_marks(checker, [pc.Mark("mosaic", 0, 0, 31, 31, "#000000", 8)])
    assert _rgb(mosaic, 0, 0) == _rgb(mosaic, 1, 0)
    assert _changed(checker, mosaic)


def test_undo_restores_pixels_and_redo_puts_them_back(pc):
    pin = pc.PinWindow(_img(40, 40, "white"), dpr=1.0)
    try:
        pin.show()
        pin.begin_markup("box")
        pin._commit_mark(pc.Mark("box", 4, 4, 36, 36, "#E23B3B", 6))
        assert _rgb(pin.rendered_image(), 4, 20) != (255, 255, 255)
        assert pin.undo_mark() is True
        assert _rgb(pin.rendered_image(), 4, 20) == (255, 255, 255)
        assert pin.redo_mark() is True
        assert _rgb(pin.rendered_image(), 4, 20) != (255, 255, 255)
        assert pin.undo_mark() is True
        _key(pin, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        assert _rgb(pin.rendered_image(), 4, 20) != (255, 255, 255)
    finally:
        pin.close()


def test_copy_composites_marks_but_ocr_uses_original(pc, monkeypatch):
    pin = pc.PinWindow(_img(36, 36, "white"), dpr=1.0)
    seen = {}

    def fake(image):
        seen["image"] = image.copy()
        return pc.OcrResult(True, "가나다", pc.OCR_COPIED_MSG)

    monkeypatch.setattr(pc, "recognize_image", fake)
    try:
        pin.show()
        pin._commit_mark(pc.Mark("highlight", 0, 0, 35, 35, "#F5C518", 4))
        pin.copy_ocr()
        assert _rgb(seen["image"], 10, 10) == _rgb(pin._img, 10, 10)
        assert _rgb(pin.image_for_export(), 10, 10) != _rgb(pin._img, 10, 10)
        menu, acts = pin.build_menu()
        pin.apply_menu_action(acts["copy"], acts)
        copied = QApplication.clipboard().image()
        assert not copied.isNull()
        assert _rgb(copied, 10, 10) != (255, 255, 255)
        menu.close()
    finally:
        pin.close()


def test_editing_draws_without_moving_and_escape_ends_edit(pc):
    pin = pc.PinWindow(_img(80, 60, "#4488cc"), dpr=2.0)
    try:
        pin.show()
        origin = pin.pos()
        assert pin.begin_markup("arrow") is True
        assert pin._bar is not None and pin._bar.isVisible()
        assert pin._bar.windowTitle() == "표시"
        pin._bar._tools["mosaic"].click()
        pin._bar._colors["#2F6BFF"].click()
        pin._bar._widths[2].click()
        assert pin._tool == "mosaic" and pin._color == "#2F6BFF" and pin._width_preset == 2
        pin._bar._tools["arrow"].click()
        assert pin._tool == "arrow"
        _press(pin, QPoint(4, 4))
        _move(pin, QPoint(30, 20))
        assert pin.pos() == origin
        assert pin._drag is None
        assert pin._draft is not None
        _release(pin, QPoint(30, 20))
        assert len(pin._marks) == 1
        assert pin._marks[0].kind == "arrow"
        _key(pin, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        assert pin._marks == []
        assert pin._editing is True
        _key(pin, Qt.Key.Key_Escape)
        assert pin._editing is False
        assert pin.isVisible()
        assert pin._bar is None
        _key(pin, Qt.Key.Key_Escape)
        assert not pin.isVisible()
    finally:
        pin.close()


def test_click_through_refuses_markup_and_menu_starts_tools(pc, toolbar):
    pin = toolbar._make_pin(_img(24, 24, "white"), None)
    pin.set_click_through(True)
    assert pin.begin_markup("mosaic") is False
    assert pin._editing is False
    assert pin._bar is None
    pin.set_click_through(False)
    menu, acts = pin.build_menu()
    assert acts["tools"]["arrow"].text() == "화살표"
    assert acts["tools"]["mosaic"].text() == "모자이크"
    assert acts["eyedropper"].text() == "스포이트"
    assert acts["ruler"].text() == "자"
    called = []
    pin.on_eyedropper = lambda: called.append("eye")
    pin.on_ruler = lambda: called.append("ruler")
    pin.apply_menu_action(acts["tools"]["highlight"], acts)
    assert pin._editing and pin._tool == "highlight"
    pin.set_click_through(True)
    assert pin._editing is False and pin._bar is None
    pin.set_click_through(False)
    pin.apply_menu_action(acts["eyedropper"], acts)
    pin.apply_menu_action(acts["ruler"], acts)
    pin.apply_menu_action(acts["mark_end"], acts)
    assert called == ["eye", "ruler"]
    assert pin._editing is False
    assert pin.isVisible()
    menu.close()


def test_pen_scribble_color_width_undo_and_export(pc, toolbar, monkeypatch):
    white = _img(48, 48, "white")
    stroke = pc.Mark("pen", 4, 24, 40, 24, "#E23B3B", 4, points=[(4, 24), (20, 24), (40, 24)])
    drawn = pc.compose_marks(white, [stroke])
    assert _rgb(drawn, 20, 24) != (255, 255, 255)
    assert _rgb(drawn, 0, 0) == (255, 255, 255)
    dot = pc.compose_marks(white, [pc.Mark("pen", 8, 8, 8, 8, "#2F6BFF", 6, points=[(8, 8)])])
    assert _rgb(dot, 8, 8) != (255, 255, 255)

    pin = pc.PinWindow(white, dpr=1.0)
    try:
        pin.resize(48, 48)
        pin.show()
        assert pin.begin_markup("pen") is True
        assert pin._bar._tools["pen"].text() == "낙서"
        pin._bar._tools["pen"].click()
        pin._bar._widths[8].click()
        assert pin._tool == "pen" and pin._width_preset == 8
        monkeypatch.setattr(pin, "_ask_markup_color", lambda: QColor("#10FF20"))
        assert pin.pick_markup_color() == "#10FF20"
        assert pin._color == "#10FF20"
        assert pin._bar._custom.isChecked()
        assert pin._bar._custom.text() == "+"
        assert pin._bar._custom.accessibleName() == "다른 색"
        dlg = pin._markup_color_dialog(QColor("#10FF20"))
        assert dlg.testOption(pc.QColorDialog.ColorDialogOption.DontUseNativeDialog)
        assert dlg.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        dlg.close()
        pin.set_markup_color("not-a-color")
        assert pin._color == "#10FF20"
        pin._bar._colors["#E23B3B"].click()
        assert pin._color == "#E23B3B"
        assert pin._bar._custom.isChecked() is False
        assert pin._bar._custom.text() == "+"
        assert "222222" in pin._bar._custom.styleSheet()

        origin = pin.pos()
        _press(pin, QPoint(6, 20))
        _move(pin, QPoint(16, 22))
        _move(pin, QPoint(30, 28))
        _release(pin, QPoint(30, 28))
        assert pin.pos() == origin
        assert len(pin._marks) == 1
        assert pin._marks[0].kind == "pen"
        assert len(pin._marks[0].points) >= 3
        assert pin._marks[0].width_px == pc.mark_width_px(8, 1.0)
        assert pin._marks[0].color == "#E23B3B"
        assert _rgb(pin.image_for_export(), 16, 22) != (255, 255, 255)
        assert _rgb(pin.image_for_ocr(), 16, 22) == (255, 255, 255)
        assert pin.undo_mark() is True
        assert pin._marks == []
        assert _rgb(pin.rendered_image(), 16, 22) == (255, 255, 255)
        assert pin.redo_mark() is True
        _key(pin, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        assert pin._marks == []

        _press(pin, QPoint(10, 10))
        _release(pin, QPoint(10, 10))
        assert len(pin._marks) == 1
        assert pin._marks[0].points
        menu, acts = pin.build_menu()
        assert acts["tools"]["pen"].text() == "낙서"
        pin.apply_menu_action(acts["tools"]["pen"], acts)
        assert pin._editing and pin._tool == "pen"
        menu.close()
    finally:
        pin.close()

    # A reloaded copy shares pixels but not cacheKey, so markup must reuse the pin.
    src = _img(24, 16, "#336699")
    src.setPixel(2, 2, QColor("white").rgb())
    live = toolbar._make_pin(src, None)
    copy = src.copy()
    assert copy.cacheKey() != src.cacheKey()
    toolbar._cur_img = copy
    assert toolbar._pin_for_tool() is live


def test_pen_release_without_move_keeps_the_end_point(pc):
    pin = pc.PinWindow(_img(48, 48, "white"), dpr=1.0)
    try:
        pin.resize(48, 48)
        pin.show()
        pin.begin_markup("pen")
        _press(pin, QPoint(4, 6))
        _release(pin, QPoint(40, 22))
        assert len(pin._marks) == 1
        assert pin._marks[0].points[0] == (4, 6)
        assert pin._marks[0].points[-1] == (40, 22)
        assert len(pin._marks[0].points) >= 2
    finally:
        pin.close()


def test_shift_scribble_is_a_straight_snapped_line(pc):
    assert pc.snap_axis_point(QPoint(0, 0), QPoint(10, 1)) == QPoint(10, 0)
    assert pc.snap_axis_point(QPoint(0, 0), QPoint(2, 20)) == QPoint(0, 20)
    diagonal = pc.snap_axis_point(QPoint(10, 10), QPoint(30, 26))
    assert abs(diagonal.x() - 10) == abs(diagonal.y() - 10)
    assert diagonal != QPoint(10, 10)

    pin = pc.PinWindow(_img(64, 48, "white"), dpr=1.0)
    shift = Qt.KeyboardModifier.ShiftModifier
    try:
        pin.resize(64, 48)
        pin.show()
        pin.begin_markup("pen")
        _press(pin, QPoint(8, 20))
        _move(pin, QPoint(12, 22))
        _move(pin, QPoint(40, 24), shift)
        _release(pin, QPoint(48, 23), shift)
        assert len(pin._marks) == 1
        pts = pin._marks[0].points
        assert pts[0] == (8, 20)
        assert pts[-1][1] == 20
        assert pts[-1][0] != 8
        assert len(pts) == 2
    finally:
        pin.close()


def test_image_signature_sees_one_pixel_and_alpha(pc, toolbar):
    base = QImage(24, 16, QImage.Format.Format_ARGB32)
    base.fill(QColor(50, 60, 70, 255))
    # (1, 1) is off the old 8×8 lattice (x step 3, y step 2).
    nudged = base.copy()
    nudged.setPixelColor(1, 1, QColor(51, 60, 70, 255))
    assert pc.image_signature(base) != pc.image_signature(nudged)
    faded = base.copy()
    faded.setPixelColor(0, 0, QColor(50, 60, 70, 200))
    assert pc.image_signature(base) != pc.image_signature(faded)
    assert pc.image_signature(base) == pc.image_signature(base.copy())

    pin = toolbar._make_pin(base, None)
    assert toolbar._pin_matching(nudged) is None
    assert toolbar._pin_matching(faded) is None
    assert toolbar._pin_matching(base.copy()) is pin


def test_markup_hotkey_needs_a_pin(pc, toolbar):
    toolbar._on_hotkey("markup")
    assert "없어요" in toolbar._last_notice
    pin = toolbar._make_pin(_img(20, 20, "white"), None)
    assert toolbar.start_pin_markup() is pin
    assert pin._editing is True


def test_physical_mapping_and_eyedropper_hex(pc, toolbar):
    assert pc.scale_percent(QSize(100, 50), QSize(200, 100)) == 200
    assert pc.physical_point(QSize(100, 50), QSize(200, 100), QPoint(20, 10)) == QPoint(40, 20)
    measured = pc.measure_pixels(QPoint(0, 0), QPoint(100, 50))
    assert measured == {"dx": 100, "dy": 50, "distance": 112}

    screen = QGuiApplication.primaryScreen()
    image = QImage(200, 100, QImage.Format.Format_RGB32)
    image.fill(QColor("#3366CC"))
    image.setPixel(40, 20, QColor("#FF8800").rgb())
    overlay = pc.InspectOverlay(screen, QPixmap.fromImage(image), "eyedropper")
    picked = []
    try:
        overlay.resize(100, 50)
        overlay.show()
        overlay.picked.connect(picked.append)
        _press(overlay, QPoint(20, 10))
        assert picked and picked[0]["hex"] == "#FF8800"
        assert picked[0]["rgb"] == "R 255  G 136  B 0"
        assert picked[0]["r"] == 255 and picked[0]["g"] == 136 and picked[0]["b"] == 0
    finally:
        overlay.close()

    QApplication.clipboard().clear()
    toolbar._was_visible = False
    toolbar._capturing = True
    toolbar._finish_inspect(picked[0])
    assert QApplication.clipboard().text() == "#FF8800"
    assert "#FF8800" in toolbar._last_notice and "255" in toolbar._last_notice
    assert toolbar._capturing is False


def test_ruler_uses_physical_pixels_at_2x(pc, toolbar):
    screen = QGuiApplication.primaryScreen()
    frozen = QPixmap(200, 100)
    frozen.fill(QColor("#224466"))
    overlay = pc.InspectOverlay(screen, frozen, "ruler")
    picked = []
    try:
        overlay.resize(100, 50)
        overlay.show()
        overlay.picked.connect(picked.append)
        _press(overlay, QPoint(0, 0))
        assert picked == []
        assert overlay._anchor == QPoint(0, 0)
        _move(overlay, QPoint(50, 25))
        _press(overlay, QPoint(50, 25))
        assert picked[0]["mode"] == "ruler"
        assert picked[0]["distance"] == 112
        assert picked[0]["dx"] == 100 and picked[0]["dy"] == 50
        assert picked[0]["scale"] == 200
        first = dict(picked[0])
        overlay._anchor = None
        picked.clear()
        _press(overlay, QPoint(0, 0))
        _press(overlay, QPoint(40, 8), mods=Qt.KeyboardModifier.ShiftModifier)
        assert picked[0]["dx"] == 80 and picked[0]["dy"] == 0
        assert picked[0]["distance"] == 80
    finally:
        overlay.close()

    toolbar._was_visible = False
    toolbar._capturing = True
    toolbar._finish_inspect(first)
    assert "112px" in toolbar._last_notice
    assert "가로 100px" in toolbar._last_notice and "세로 50px" in toolbar._last_notice
    assert "200%" in toolbar._last_notice


def test_inspect_skips_overlay_when_capture_blocked(pc, toolbar, monkeypatch):
    black = QPixmap(8, 8)
    black.fill(QColor(0, 0, 0))
    monkeypatch.setattr(pc, "grab_screen_raw", lambda _screen: black)
    session = pc.ScreenInspectSession("eyedropper")
    got = {}
    session.blocked.connect(lambda: got.setdefault("blocked", True))
    session.finished.connect(lambda result: got.setdefault("result", result))
    session.start()
    spin(30)
    assert got.get("blocked") is True
    assert got.get("result") is None
    assert session._overlays == []

    seen = {}
    monkeypatch.setattr(toolbar, "_capture_blocked", lambda: seen.setdefault("blocked", True))
    toolbar._on_hotkey("ruler")
    spin(250)
    assert seen.get("blocked") is True
    assert toolbar._capturing is False


def test_new_hotkeys_default_without_clashing_old_config(pc, tmp_path, monkeypatch):
    assert pc.DEFAULTS["hotkeys"]["markup"] == "<ctrl>+<alt>+m"
    assert pc.DEFAULTS["hotkeys"]["eyedropper"] == "<ctrl>+<alt>+c"
    assert pc.DEFAULTS["hotkeys"]["ruler"] == "<ctrl>+<alt>+d"
    combos = [v for v in pc.DEFAULTS["hotkeys"].values() if v]
    assert len(combos) == len(set(combos))
    assert "<ctrl>+<alt>+e" not in combos

    path = tmp_path / "config.json"
    path.write_text('{"autosave": false, "hotkeys": {"region": "<ctrl>+<alt>+b"}}', encoding="utf-8")
    monkeypatch.setattr(pc, "CONFIG_PATH", path)
    cfg = pc.load_config()
    assert cfg["hotkeys"]["region"] == "<ctrl>+<alt>+b"
    assert cfg["hotkeys"]["markup"] == "<ctrl>+<alt>+m"
    assert cfg["hotkeys"]["eyedropper"] == "<ctrl>+<alt>+c"
    assert cfg["hotkeys"]["ruler"] == "<ctrl>+<alt>+d"
    assert cfg["hotkeys"]["reopen_pin"] == "<ctrl>+<alt>+r"

    dlg = pc.SettingsDialog(cfg, hotkey_ok=False)
    assert dlg.ed_hk["markup"].text() == "<ctrl>+<alt>+m"
    assert dlg.ed_hk["eyedropper"].text() == "<ctrl>+<alt>+c"
    assert dlg.ed_hk["ruler"].text() == "<ctrl>+<alt>+d"
    dlg.ed_hk["ruler"].setText("<ctrl>+<alt>+9")
    dlg._reset_hotkeys()
    assert dlg.ed_hk["ruler"].text() == "<ctrl>+<alt>+d"
    dlg.close()
