"""v0.9.0 pin markup, eyedropper, and ruler. OCR stays on the unmarked original."""
from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QSize, Qt
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
        monkeypatch.setattr(pin, "_ask_markup_color", lambda: QColor())
        pin._bar._custom.click()
        assert pin._color == "#E23B3B"
        assert pin._bar._custom.isChecked() is False

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


def _at(image, x, y):
    ratio = image.devicePixelRatio() or 1
    return QColor(image.pixel(int(x * ratio), int(y * ratio)))


def _panel_is_solid_and_rounded(image, bar):
    button = bar._tools["arrow"]
    origin = button.mapTo(bar, QPoint(0, 0))
    pad = _at(image, origin.x() - 6, origin.y() + button.height() // 2)
    corner = _at(image, 1, 1)
    solid = pad.alpha() > 230 and pad.red() > 245 and pad.green() > 245 and pad.blue() > 245
    rounded = corner.alpha() < 40 or (corner.red() + corner.green() + corner.blue()) < pad.red()
    return solid and rounded


def _button_shows_selection(image, bar, btn):
    origin = btn.mapTo(bar, QPoint(0, 0))
    blues = 0
    for y in range(2, btn.height() - 2):
        for x in range(2, btn.width() - 2):
            c = _at(image, origin.x() + x, origin.y() + y)
            if c.blue() > 170 and c.blue() > c.red() + 15:
                blues += 1
    return blues > 12


def test_markup_bar_docks_under_the_pin_and_stays_visible(pc):
    """The bar sits under the pin (above if the bottom is full), on a solid panel."""
    bounds = QRect(0, 0, 800, 600)
    bar = QSize(180, 56)
    pin_rect = QRect(100, 80, 200, 120)
    mid = pc.markup_bar_position(pin_rect, bar, bounds)
    assert mid.y() == pin_rect.bottom() + 1 + pc.MARKUP_BAR_GAP
    assert mid.x() == pin_rect.center().x() - bar.width() // 2

    wide = QSize(700, 56)
    clamped = pc.markup_bar_position(pin_rect, wide, bounds)
    assert clamped.x() == bounds.left() + pc.MARKUP_BAR_MARGIN
    assert clamped.y() == mid.y()

    low = pc.markup_bar_position(QRect(100, 520, 200, 70), bar, bounds)
    assert low.y() + bar.height() <= 520 - pc.MARKUP_BAR_GAP + 1
    assert low.y() >= bounds.top()

    full = pc.markup_bar_position(QRect(0, 0, 800, 600), wide, bounds)
    placed = QRect(full, wide)
    assert bounds.contains(placed.adjusted(0, 0, -1, -1))
    assert full.y() > bounds.height() / 2
    assert not (full.x() <= 8 and full.y() <= 8)

    edge = pc.markup_bar_position(QRect(740, 40, 50, 40), wide, bounds)
    assert edge.x() >= bounds.left()
    assert edge.x() + wide.width() - 1 <= bounds.right() - pc.MARKUP_BAR_MARGIN
    assert edge.y() >= 40 + 40

    screen = QGuiApplication.primaryScreen()
    area = screen.availableGeometry()
    pin = pc.PinWindow(_img(180, 100, "#4488cc"), dpr=1.0)
    try:
        pin.show()
        home = QPoint(area.left() + 90, area.top() + 36)
        pin.move(home)
        assert pin.frameGeometry().topLeft() == home
        assert pin.begin_markup("arrow") is True
        bar_w = pin._bar
        QApplication.processEvents()

        def docked():
            return bar_w.pos() == pc.markup_bar_position(pin.frameGeometry(), bar_w.size(), area)

        assert bar_w.width() >= 360 and bar_w.height() >= 48
        assert bar_w.is_wrapped is False
        assert docked()
        assert bar_w.frameGeometry().top() >= pin.frameGeometry().bottom()
        assert area.contains(bar_w.frameGeometry().center())

        nudged = QPoint(home.x() + 48, home.y() + 30)
        pin.move(nudged)
        QApplication.processEvents()
        assert pin.frameGeometry().topLeft() == nudged
        assert docked()
        assert bar_w.frameGeometry().top() >= pin.frameGeometry().bottom()

        pin.move(QPoint(area.left() + 24, area.bottom() - pin.height() - 1))
        QApplication.processEvents()
        assert docked()
        assert area.contains(bar_w.frameGeometry().center())
        if pin.frameGeometry().top() - area.top() > bar_w.height() + pc.MARKUP_BAR_GAP:
            assert bar_w.frameGeometry().bottom() <= pin.frameGeometry().top()

        for kind, label in pc.MARK_TOOL_LABELS:
            btn = bar_w._tools[kind]
            assert label == btn.text() == btn.toolTip() == btn.accessibleName()
            assert not btn.icon().isNull()
            assert btn.width() >= pc.MARK_BAR_HIT and btn.height() >= pc.MARK_BAR_HIT
        assert bar_w._tools["arrow"].isChecked()
        assert bar_w._tools["pen"].isChecked() is False
        for preset, label, _icon in pc.MARK_WIDTH_LABELS:
            width_btn = bar_w._widths[preset]
            assert width_btn.toolTip() == label
            assert width_btn.width() >= pc.MARK_BAR_HIT
            assert not width_btn.icon().isNull()
        assert bar_w._widths[4].isChecked()
        assert bar_w._widths[2].isChecked() is False
        bar_w._widths[8].click()
        assert bar_w._widths[8].isChecked() and pin._width_preset == 8
        assert bar_w._colors["#E23B3B"].isChecked()
        assert bar_w._colors["#E23B3B"].width() >= pc.MARK_BAR_SWATCH
        assert "실행 취소" in bar_w._undo.toolTip() and "Ctrl+Z" in bar_w._undo.toolTip()
        assert "다시 실행" in bar_w._redo.toolTip() and "Ctrl+Y" in bar_w._redo.toolTip()
        assert bar_w._done.toolTip().startswith("완료") and "Esc" in bar_w._done.toolTip()
        assert not bar_w._undo.icon().isNull()
        assert not bar_w._done.icon().isNull()

        shot = bar_w.grab().toImage()
        assert _panel_is_solid_and_rounded(shot, bar_w)
        assert _button_shows_selection(shot, bar_w, bar_w._tools["arrow"])
        assert not _button_shows_selection(shot, bar_w, bar_w._tools["pen"])

        pin._commit_mark(pc.Mark("arrow", 8, 8, 40, 30, "#E23B3B", 4))
        bar_w._undo.click()
        assert pin._marks == []
        bar_w._redo.click()
        assert len(pin._marks) == 1
        bar_w._done.click()
        assert pin._editing is False and pin.isVisible() and pin._bar is None
    finally:
        pin.close()


class _FakeScreen:
    """Enough of QScreen for screen_for_rect. Geometry is in logical pixels."""

    def __init__(self, geometry, available=None, dpr=1.0):
        self._geometry = QRect(geometry)
        self._available = QRect(available) if available is not None else QRect(geometry)
        self._dpr = dpr

    def geometry(self):
        return QRect(self._geometry)

    def availableGeometry(self):
        return QRect(self._available)

    def devicePixelRatio(self):
        return self._dpr


def _button_on_screen(bar, btn, origin: QPoint):
    local = btn.mapTo(bar, QPoint(0, 0))
    return QRect(origin.x() + local.x(), origin.y() + local.y(), btn.width(), btn.height())


def _assert_buttons_inside(bar, bounds: QRect, origin: QPoint):
    assert bar.width() > 0 and bar.height() > 0
    host = QRect(origin, bar.size())
    assert bounds.contains(host.adjusted(0, 0, -1, -1))
    seen = set()
    for btn in bar.buttons():
        rect = _button_on_screen(bar, btn, origin)
        assert rect.width() >= 14 and rect.height() >= 14
        assert bounds.contains(rect.adjusted(0, 0, -1, -1)), btn.accessibleName()
        seen.add(btn.accessibleName())
    assert {"화살표", "네모", "형광펜", "모자이크", "낙서", "빨강", "다른 색",
            "얇게", "보통", "굵게", "실행 취소", "다시 실행", "완료"} <= seen


def test_markup_bar_fits_narrow_screens_and_picks_the_visible_monitor(pc, monkeypatch):
    """Real laid-out width, negative coordinates, and mixed device-pixel ratios."""
    left = _FakeScreen(
        QRect(-1920, 0, 1920, 1080), QRect(-1920, 0, 1920, 1040), dpr=1.0)
    right = _FakeScreen(QRect(80, 0, 960, 540), dpr=2.0)
    straddling = QRect(-100, 40, 201, 80)  # center sits in the gap, more pixels on the left
    assert straddling.center().x() > left.geometry().right()
    assert straddling.center().x() < right.geometry().left()
    assert pc.screen_for_rect(straddling, [right, left]) is left

    in_gap = QRect(10, 120, 40, 30)
    assert pc._rect_area(in_gap.intersected(left.geometry())) == 0
    assert pc._rect_area(in_gap.intersected(right.geometry())) == 0
    assert pc.screen_for_rect(in_gap, [right, left]) is left
    near_right = QRect(60, 120, 12, 12)
    assert pc.screen_for_rect(near_right, [left, right]) is right

    on_right = QRect(120, 40, 200, 80)
    chosen = pc.screen_for_rect(on_right, [left, right])
    assert chosen is right and chosen.devicePixelRatio() == 2.0

    pin = pc.PinWindow(_img(80, 50, "#4488cc"), dpr=1.0)
    try:
        pin.show()
        pin.move(40, 30)
        assert pin.begin_markup("arrow") is True
        bar = pin._bar
        assert pin._screen_watch is True
        assert QGuiApplication.primaryScreen() in pin._hooked

        # The laid-out bar, not a stand-in width, must stay inside a right-edge screen.
        bar.fit_width(10000)
        natural = QSize(bar.size())
        assert natural.width() > 400 and bar.is_wrapped is False
        tight = QRect(0, 0, natural.width() + 16, 700)
        edge_pin = QRect(tight.right() - 24, 20, 20, 20)
        bar.fit_width(tight.width() - 2 * pc.MARKUP_BAR_MARGIN)
        assert bar.size() == natural
        edge = pc.markup_bar_position(edge_pin, bar.size(), tight)
        assert edge.x() + bar.width() - 1 <= tight.right() - pc.MARKUP_BAR_MARGIN
        _assert_buttons_inside(bar, tight, edge)

        # Portrait / high-DPI logical width. 2.5x of a 700px panel is 280 logical px.
        narrow = _FakeScreen(QRect(0, 0, 280, 900), dpr=2.5)
        limit = narrow.availableGeometry().width() - 2 * pc.MARKUP_BAR_MARGIN
        bar.fit_width(limit)
        assert bar.is_wrapped is True
        assert bar.width() <= limit
        assert bar.width() < natural.width()
        placed = pc.markup_bar_position(QRect(16, 24, 90, 40), bar.size(), narrow.availableGeometry())
        _assert_buttons_inside(bar, narrow.availableGeometry(), placed)
        assert bar._done.isVisible() and bar._undo.isVisible()

        # A pin on the negative monitor must not fall back to the widget's own screen.
        parked = QRect(-1500, 80, 240, 120)
        assert pc.screen_for_rect(parked, [right, left]) is left
        bar.fit_width(left.availableGeometry().width() - 2 * pc.MARKUP_BAR_MARGIN)
        parked_at = pc.markup_bar_position(parked, bar.size(), left.availableGeometry())
        _assert_buttons_inside(bar, left.availableGeometry(), parked_at)
        assert parked_at.x() < 0

        only = _FakeScreen(QRect(-1600, 0, 1400, 900), QRect(-1600, 48, 1400, 820), dpr=1.0)
        monkeypatch.setattr(pc.QGuiApplication, "screens", lambda: [only])
        pin._on_screens_changed()
        assert pin._bar.frameGeometry().left() < 0
        _assert_buttons_inside(pin._bar, only.availableGeometry(), pin._bar.frameGeometry().topLeft())

        hi = _FakeScreen(QRect(0, 0, 280, 900), dpr=2.0)
        monkeypatch.setattr(pc.QGuiApplication, "screens", lambda: [hi])
        pin._on_screens_changed(2.0)  # logicalDotsPerInchChanged passes the new dpi
        assert pin._bar.is_wrapped is True
        assert pin._bar.width() <= hi.availableGeometry().width() - 2 * pc.MARKUP_BAR_MARGIN
        _assert_buttons_inside(pin._bar, hi.availableGeometry(), pin._bar.frameGeometry().topLeft())

        pin.end_markup()
        assert pin._screen_watch is False and pin._hooked == [] and pin._bar is None
    finally:
        pin.close()


def test_scribble_is_the_first_default_tool_and_markup_stays_on_the_pin(pc, toolbar):
    """낙서, then 네모, then 화살표. Markup reuses the pin's window, place, and size."""
    assert [kind for kind, _label in pc.MARK_TOOL_LABELS] == [
        "pen", "box", "arrow", "highlight", "mosaic"]
    fresh = pc.PinWindow(_img(12, 12, "white"))
    assert fresh._tool == "pen"
    fresh.close()

    src = _img(36, 24, "#336699")
    other = _img(36, 24, "#cc6633")
    toolbar.history = [pc.HistoryEntry(image=other)]
    toolbar.populate()
    pin = toolbar._make_pin(src, None)
    pin._scale = 1.6
    pin._apply_size()
    pin.move(72, 40)
    home = pin.frameGeometry()
    size = pin.size()
    assert toolbar._pin_for_tool() is pin
    opened = toolbar.start_pin_markup()
    spin(30)
    assert opened is pin
    assert toolbar._pins == [pin]
    assert pin._editing is True
    assert pin._tool == "pen"
    assert pin.frameGeometry() == home
    assert pin.size() == size
    assert pin._scale == 1.6
    bar = pin._bar
    assert bar is not None and bar.isVisible()
    tools = [w for w in bar._draw_widgets if w in bar._tools.values()]
    assert tools == [bar._tools[kind] for kind, _label in pc.MARK_TOOL_LABELS]
    assert bar._tools["pen"].isChecked() is True
    assert bar._tools["arrow"].isChecked() is False
    assert bar._tools["box"].isChecked() is False
    menu, acts = pin.build_menu()
    labels = []
    for act in menu.actions():
        sub = act.menu()
        if sub is not None and sub.title() == "표시":
            labels = [a.text() for a in sub.actions() if a.text() and a.text() != "표시 끝내기"]
    assert labels == ["낙서", "네모", "화살표", "형광펜", "모자이크"]
    menu.close()

    # The capture that is already pinned is edited there, not copied into a new window.
    toolbar.history = [pc.HistoryEntry(image=src.copy())]
    toolbar.populate()
    again = toolbar.start_pin_markup()
    spin(20)
    assert again is pin
    assert toolbar._pins == [pin]
    assert pin.frameGeometry() == home

    # A newer pin of a different image stays put. The matching pin is edited in place.
    other_pin = toolbar._make_pin(other, None)
    other_pin.move(200, 120)
    other_home = other_pin.frameGeometry()
    assert toolbar._front_pin() is other_pin
    targeted = toolbar.start_pin_markup()
    spin(20)
    assert targeted is pin
    assert pin._editing is True
    assert other_pin._editing is False
    assert set(toolbar._pins) == {pin, other_pin}
    assert pin.frameGeometry() == home
    assert other_pin.frameGeometry() == other_home


def _bar_visible(bar) -> bool:
    try:
        return bar is not None and bar.isVisible()
    except RuntimeError:
        return False


def test_unmatched_capture_highlights_the_front_pin_on_its_monitor(pc, toolbar):
    """A different history image edits the front pin in place and says so, even on another monitor."""
    primary = QGuiApplication.primaryScreen()
    other = _FakeScreen(QRect(8000, 0, 900, 700))
    red = _img(24, 16, "red")
    blue = _img(24, 16, "blue")
    toolbar.history = [pc.HistoryEntry(image=red)]
    toolbar.populate()
    toolbar.cfg["hotkeys"] = dict(pc.DEFAULTS["hotkeys"])
    toolbar._update_tooltips()
    pin = toolbar._make_pin(blue, QPoint(8200, 80))
    home = pin.frameGeometry()
    assert pc.screen_for_rect(home, [primary, other]) is other
    assert primary.geometry().intersected(home).isEmpty()
    tip = toolbar.btn_markup.toolTip()
    assert "같은 핀" in tip and "맨 앞" in tip and "알려" in tip
    toolbar.btn_markup.click()
    spin(30)
    assert toolbar._pins == [pin]
    assert pin._editing is True
    assert pin._tool == "pen"
    assert pin.frameGeometry() == home
    assert pin._attention is True
    assert toolbar._last_notice == "고른 캡처와 같은 핀이 없어서 맨 앞 핀에 그려요."
    assert toolbar._notice_toast is not None and toolbar._notice_toast.isVisible()
    spin(pc.MARKUP_ATTENTION_MSEC + 80)
    assert pin._attention is False


def test_minimized_pins_are_skipped_and_activation_becomes_front(pc, toolbar):
    red = _img(18, 12, "red")
    blue = _img(18, 12, "blue")
    first = toolbar._make_pin(red, QPoint(30, 30))
    second = toolbar._make_pin(blue, QPoint(90, 30))
    assert toolbar._front_pin() is second
    second.setWindowState(Qt.WindowState.WindowMinimized)
    assert second.isMinimized()
    assert toolbar._front_pin() is first
    assert toolbar._pin_matching(blue) is None
    assert toolbar._pin_matching(red) is first
    second.setWindowState(Qt.WindowState.WindowNoState)
    second.show()
    first.activateWindow()
    spin(20)
    assert first.isActiveWindow()
    assert toolbar._front_pin() is first


def test_hiding_a_pin_closes_markup(pc, toolbar):
    pin = toolbar._make_pin(_img(20, 14, "white"), QPoint(10, 10))
    assert pin.begin_markup("pen") is True
    bar = pin._bar
    pin.hide()
    spin(20)
    assert pin.isVisible() is False
    assert pin._editing is False and pin._bar is None
    assert _bar_visible(bar) is False


def test_minimizing_a_pin_closes_markup(pc, toolbar):
    pin = toolbar._make_pin(_img(20, 14, "white"), QPoint(10, 10))
    assert pin.begin_markup("pen") is True
    bar = pin._bar
    pin.setWindowState(Qt.WindowState.WindowMinimized)
    spin(20)
    assert pin.isMinimized()
    assert pin._editing is False and pin._bar is None
    assert _bar_visible(bar) is False


def test_destroying_a_pin_closes_the_markup_bar(pc, toolbar):
    import shiboken6
    pin = toolbar._make_pin(_img(20, 14, "white"), QPoint(10, 10))
    assert pin.begin_markup("pen") is True
    bar = pin._bar
    toolbar._pins.remove(pin)
    shiboken6.delete(pin)
    spin(20)
    assert _bar_visible(bar) is False


def test_starting_markup_ends_the_other_pins_edit(pc, toolbar):
    first = toolbar._make_pin(_img(16, 12, "red"), QPoint(12, 12))
    second = toolbar._make_pin(_img(16, 12, "blue"), QPoint(80, 12))
    assert first.begin_markup("pen") is True
    first_bar = first._bar
    assert second.begin_markup("box") is True
    assert first._editing is False and first._bar is None
    assert _bar_visible(first_bar) is False
    assert second._editing is True and second._tool == "box"
    assert second._bar is not None and second._bar.isVisible()


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
