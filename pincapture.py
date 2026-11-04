#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 핀캡처 (PinCapture) — 화면 캡처 도구
#
# 출처 / 이력 (주석이라 배포용 EXE 의 바이트코드에는 들어가지 않음)
#   v0.1   2026-08-04  claude.ai 채팅에서 Claude 가 생성
#   v0.2~4             보관함 통합, 단일 인스턴스, 바로가기 생성 등 추가
#   v0.5   2026-09-03  Claude Code (Claude Fable 5.1) — 실행 환경 보호: PySide6 없는 Python 이면
#                      다른 Python 으로 자동 재실행, ~/.pincapture/pincapture.log, 예외 메시지 박스
#   v0.5.1 2026-09-14  Claude Code (Claude Fable 5.1) — 작업 표시줄 고정용 AppUserModelID·재실행 정보,
#                      시작 메뉴 바로가기
#   v0.5.2 2026-09-14  Claude Code (Claude Fable 5.1) — 캡처 후 창을 전경으로 (AttachThreadInput 우회)
#   v0.5.3 2026-10-21  Claude Code (Claude Fable 5.1) — 보관함 다중 선택 (복사/저장/핀/제거 일괄)
#   v0.6.0 2026-10-22  Claude Code (Claude Opus 5.5) — 설치 프로그램(Inno Setup) 배포 대응:
#                      EXE 실행 시 바로가기·작업 표시줄 고정·다시 시작이 깨지던 문제 수정,
#                      --tray(트레이로 시작) / --quit(설치·제거 시 실행 중인 앱 종료) / --version,
#                      설치 프로그램용 실행 감지 뮤텍스, 로그에 앱 버전 기록,
#                      종료를 취소 불가능한 exit(0) 로 (핀 창이 있으면 quit() 가 무시되던 버그),
#                      중복 실행 방지 채널을 사용자·세션별로 분리
#   v0.6.1 2026-10-26  Claude Code (Claude Opus 5.5) — 화면 캡처가 통째로 검게 나올 때(보안 프로그램의
#                      '화면 캡처 방지' 등) 검은 화면을 모니터에 띄우거나 저장하지 않고 원인·해결법 안내
#   v0.7.0 2026-10-26  Grok (Grok 4.7) — 메인·설정 창 문구와 배치를 다듬고, 첫 실행 빠른 안내·정보 창·
#                      트레이 메뉴를 정리. 정보 창과 트레이에 후원하기(Ko-fi). 설정 파일 형식은 그대로
#   v0.8.0 2026-10-26  Grok (Grok 4.7) — 핀 우클릭 글자 복사(Windows OCR), 투명도·클릭 통과,
#                      최근 핀 다시 열기, 거의 검은 캡처는 핀 대신 보안 프로그램 안내
#   v0.9.0 2026-10-26  Grok (Grok 4.7) — 핀 위 표시(화살표·네모·형광펜·모자이크, 실행 취소),
#                      화면 색 스포이트, 두 점 사이 픽셀 자. 메인 창 버튼은 그대로
#   v0.9.1 2026-10-26  Grok (Grok 4.7) — 메인 창 상단을 압축하고, 표시·스포이트·자·글자 복사·
#                      최근 핀을 캡처 줄 오른쪽의 작은 아이콘으로 배치
#   v0.10.0 2026-10-27 Grok (Grok 4.7) — 글자 복사에 문단 맞추기, 표(TSV·Markdown), 수식(LaTeX).
#                      수식은 기본 설치에 넣지 않고, 설치를 눌렀을 때만 받는다
#   v0.10.1 2026-10-28 Grok (Grok 4.7) — 글자 복사 안내를 화면 위 토스트로 보여 줌.
#                      트레이 풍선만 쓰면 알림이 꺼져 있을 때 반응이 없었음
#   v0.10.2 2026-11-04 Grok (Grok 4.7) — 캡처 줄 아이콘(그리기·스포이트·자·글자 복사·최근 핀)이
#                      조건이 없거나 메인 창이 앞에 있을 때 조용히 무시되던 문제. 핀 낙서(자유 곡선)
#   v0.10.3 2026-11-04 Grok (Grok 4.7) — 핀 표시 도구를 핀 아래 둥근 패널의 아이콘으로.
#                      화면 구석의 글자 버튼이 배경에 묻히던 문제
#   Created: 2026-08-04 by Claude via claude.ai / Modified: 2026-11-04 by Grok 4.7 via Cursor
#   빌드: installer/build.py  (PyInstaller onedir + Inno Setup → PinCapture-Setup-<버전>.exe)
"""
핀캡처 (PinCapture) — 화면 캡처 도구

기능
  · 영역 지정 캡처 (드래그, 화면 정지 방식)
  · 창 캡처 (현재 활성 창, Windows에서 PrintWindow 사용)
  · 전체 화면 캡처 (마우스가 있는 모니터)
  · 핀 고정 (캡처한 이미지를 항상 위 창으로 화면에 고정)
  · 핀 우클릭: 글자 복사(문단·표·수식, Windows OCR / 선택 수식 모델), 투명도, 클릭 통과
  · 핀 위 표시: 화살표, 네모, 형광펜, 모자이크, 낙서 (복사·저장에 합성, OCR 은 원본)
  · 스포이트(화면 색 HEX), 자(두 점의 물리 픽셀 거리)
  · 닫은 핀 다시 열기 (전역 단축키·트레이)
  · 전역 단축키, 트레이 상주, 자동 저장 + 클립보드 복사

실행:  PinCapture.exe  (개발: python pincapture.py)
옵션:  --region --window --full --pin   (시작 직후 해당 캡처 1회 실행)
       --tray                            (창을 띄우지 않고 트레이로 시작 — 자동 실행용)
       --quit                            (실행 중인 핀캡처를 종료 — 설치/제거 프로그램용)
       --selftest                        (UI 렌더링 자가 점검, 개발용)

설정 파일: ~/.pincapture/config.json  (설정 창에서도 변경 가능)
"""

import sys
import os
import json
import math
import hashlib
import argparse
import datetime
import tempfile
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
_NO_WINDOW = 0x08000000 if IS_WINDOWS else 0   # subprocess.CREATE_NO_WINDOW

APP_NAME = "핀캡처"
APP_VERSION = "0.10.3"
APP_PUBLISHER = "캐모마일그레이"                 # 정보 창에 보이는 이름
APP_PUBLISHER_EN = "ChamomileGrey"             # 설치 정보·EXE 속성과 같은 영문 이름
KOFI_URL = "https://ko-fi.com/chamomilegrey"   # 후원하기. 이 주소만 연다
APP_USER_MODEL_ID = "pincapture.app"           # 작업 표시줄 그룹/고정 식별자 (설치 프로그램 바로가기와 동일해야 함)
APP_MUTEX_NAME = "PinCaptureRunning"           # 설치 프로그램이 '실행 중' 여부를 확인하는 뮤텍스 (PinCapture.iss 와 동일)
FROZEN = bool(getattr(sys, "frozen", False))   # PyInstaller 로 만든 EXE 로 실행 중인지
_APP_MUTEX = None                              # 위 뮤텍스 핸들 (프로세스가 끝날 때까지 유지)


def launch_argv(*extra: str) -> "list[str]":
    """이 프로그램을 다시 실행하는 명령. 바로가기 대상·작업 표시줄 재실행·'다시 시작' 공용.
    EXE 면 EXE 하나, 스크립트면 pythonw.exe + 이 .py 파일.
    (EXE 에서 __file__ 은 존재하지 않는 임시 경로라 절대 인수로 넘기면 안 된다)"""
    if FROZEN:
        return [sys.executable, *extra]
    pyw = Path(sys.executable).with_name("pythonw.exe")
    return [str(pyw if pyw.exists() else Path(sys.executable)), str(Path(__file__).resolve()), *extra]


def app_dir() -> Path:
    """프로그램이 놓인 폴더 (바로가기 '시작 위치')."""
    return Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 실행 환경 보호
#   · pythonw 로 실행되면 콘솔이 없어 오류가 그냥 사라짐 → ~/.pincapture/pincapture.log 에 기록
#   · 처리되지 않은 예외는 메시지 박스로도 표시
#   · PySide6 가 없는 Python 으로 실행되면(파이썬 업데이트로 기본 python 이 바뀐 경우 등)
#     PySide6 가 설치된 다른 Python 을 찾아 자동으로 그쪽으로 다시 실행
# ---------------------------------------------------------------------------
_CONFIG_DIR = Path.home() / ".pincapture"
LOG_PATH = _CONFIG_DIR / "pincapture.log"


def _msgbox(title: str, text: str, error: bool = True) -> None:
    if IS_WINDOWS:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x10 if error else 0x40)
            return
        except Exception:
            pass
    print(f"{title}: {text}", file=(sys.stderr or sys.stdout))


class _Tee:
    """콘솔과 로그 파일에 동시에 쓰는 스트림."""
    def __init__(self, *streams):
        self._streams = [s for s in streams if s is not None]

    def write(self, s):
        for st in self._streams:
            try:
                st.write(s)
            except Exception:
                pass
        return len(s)

    def flush(self):
        for st in self._streams:
            try:
                st.flush()
            except Exception:
                pass

    def isatty(self):
        return False


def _setup_logging() -> None:
    if os.environ.get("PINCAP_NO_LOG"):            # 빌드 스크립트가 아이콘만 그릴 때 로그를 건드리지 않게
        return
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:   # 다른 인스턴스가 로그를 열고 있으면 회전만 건너뜀
            if LOG_PATH.exists() and LOG_PATH.stat().st_size > 512 * 1024:
                LOG_PATH.replace(LOG_PATH.with_suffix(".log.old"))
        except Exception:
            pass
        f = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
        sys.stdout = _Tee(sys.__stdout__, f)
        sys.stderr = _Tee(sys.__stderr__, f)
        print(f"\n===== {datetime.datetime.now():%Y-%m-%d %H:%M:%S}  "
              f"{APP_NAME} {APP_VERSION} ({'exe' if FROZEN else 'py'})  "
              f"python {sys.version.split()[0]}  {sys.executable}  args={sys.argv[1:]}")
    except Exception:
        pass


def _excepthook(t, v, tb):
    import traceback
    msg = "".join(traceback.format_exception(t, v, tb))
    print(msg, file=sys.stderr)
    _msgbox("핀캡처 오류",
            f"예상치 못한 오류로 종료돼.\n\n{msg[-1200:]}\n\n전체 로그: {LOG_PATH}")


_setup_logging()
sys.excepthook = _excepthook


def _find_python_with_deps() -> "str | None":
    """PySide6(가능하면 pynput 도)가 설치된 다른 Python 실행 파일을 찾는다."""
    import re
    import subprocess
    cands = []
    if IS_WINDOWS:
        try:  # py 런처에 등록된 모든 Python
            r = subprocess.run(["py", "-0p"], capture_output=True, text=True,
                               timeout=10, creationflags=_NO_WINDOW)
            for line in r.stdout.splitlines():
                m = re.match(r"^\s*-V:\S+\s+\*?\s*(.+?\.exe)\s*$", line, re.I)
                if m:
                    cands.append(m.group(1))
        except Exception:
            pass
        home = Path.home()
        pd = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        lad = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        for p in [pd / "Miniconda3/python.exe", pd / "Anaconda3/python.exe",
                  home / "miniconda3/python.exe", home / "anaconda3/python.exe",
                  *sorted((lad / "Programs/Python").glob("Python3*/python.exe"), reverse=True)]:
            cands.append(str(p))
    seen, ordered = set(), []
    for c in cands:
        try:
            key = str(Path(c).resolve()).lower()
        except Exception:
            continue
        if key in seen or not Path(c).exists():
            continue
        seen.add(key)
        if key == str(Path(sys.executable).resolve()).lower():
            continue
        ordered.append(c)
    fallback = None
    for c in ordered:
        try:
            r = subprocess.run([c, "-c", "import PySide6, pynput"], capture_output=True,
                               timeout=30, creationflags=_NO_WINDOW)
            if r.returncode == 0:
                return c
            r = subprocess.run([c, "-c", "import PySide6"], capture_output=True,
                               timeout=30, creationflags=_NO_WINDOW)
            if r.returncode == 0 and fallback is None:
                fallback = c
        except Exception:
            pass
    return fallback


def _handle_missing_deps(err: Exception) -> None:
    if FROZEN:
        # 설치된 EXE 에서 Qt 를 못 불러온 경우: 다른 Python 을 찾거나 pip 안내를 하면 안 됨
        print(f"[deps] EXE 에서 Qt 구성 요소를 불러오지 못함: {err}")
        _msgbox(f"{APP_NAME} 실행 실패",
                "프로그램 구성 요소를 불러오지 못했습니다.\n\n"
                "· 백신 프로그램이 핀캡처 파일을 차단하거나 격리했는지 확인해 주세요.\n"
                "· 설치 파일로 핀캡처를 다시 설치해 주세요.\n"
                "· Windows 10 / 11 (64비트)에서만 실행됩니다.\n\n"
                f"오류: {err}\n로그: {LOG_PATH}")
        sys.exit(1)
    import subprocess
    print(f"[deps] 이 Python({sys.executable}) 에 PySide6 가 없음: {err}")
    alt = None if os.environ.get("PINCAP_REEXEC") else _find_python_with_deps()
    if alt:
        exe = Path(alt)
        pyw = exe.with_name("pythonw.exe")
        if IS_WINDOWS and pyw.exists() and sys.__stdout__ is None:
            exe = pyw   # 콘솔 없이 실행된 경우(pythonw/바로가기)엔 계속 콘솔 없이
        print(f"[deps] PySide6 가 설치된 Python 으로 다시 실행: {exe}")
        env = dict(os.environ, PINCAP_REEXEC="1")
        try:
            subprocess.Popen([str(exe), str(Path(__file__).resolve()), *sys.argv[1:]],
                             env=env, creationflags=_NO_WINDOW, close_fds=True)
            sys.exit(0)
        except Exception as e:
            print(f"[deps] 재실행 실패: {e}")
    pip_py = sys.executable
    _msgbox("핀캡처 — 필요한 패키지가 없음",
            "이 Python 에는 PySide6 가 설치돼 있지 않아서 실행할 수 없어.\n\n"
            f"실행한 Python: {pip_py}\n\n"
            "해결 (명령 프롬프트에서):\n"
            f'    "{pip_py}" -m pip install PySide6 pynput\n\n'
            "또는 PySide6 가 설치된 Python 으로 실행하면 돼. "
            "(설정 창의 '바탕화면 아이콘 만들기'는 현재 실행 중인 Python 을 기억함)\n\n"
            f"로그: {LOG_PATH}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Qt import
# ---------------------------------------------------------------------------
try:
    from PySide6.QtCore import (
        Qt, QObject, QPoint, QPointF, QRect, QSize, QStandardPaths, QTimer, QUrl,
        Signal,
    )
except ImportError as _e:
    _handle_missing_deps(_e)
    raise
from PySide6.QtCore import (
    Qt, QEventLoop, QItemSelectionModel, QMimeData, QObject, QPoint, QPointF, QRect, QRectF, QSize,
    QStandardPaths, QThread, QTimer, QUrl, Signal,
)
from PySide6.QtGui import (
    QBrush, QColor, QCursor, QDesktopServices, QFont, QFontDatabase, QGuiApplication, QIcon,
    QImage, QImageReader, QKeySequence, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QShortcut,
)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication, QCheckBox, QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListView,
    QGridLayout, QListWidget, QListWidgetItem, QMenu, QMessageBox, QPushButton, QSpinBox,
    QSplitter, QSystemTrayIcon, QToolButton, QVBoxLayout, QWidget, QProgressDialog,
)

def _singleton_name() -> str:
    """중복 실행 방지용 로컬 소켓(Windows 에선 명명 파이프) 이름.
    파이프 이름은 PC 전체에서 하나라서, 고정 이름이면 한 PC 의 다른 Windows 계정끼리 충돌한다
    (두 번째 계정은 접근 거부 → 중복 실행, --quit 불가). 사용자·세션별로 분리해 뮤텍스 범위와 맞춘다."""
    base = "pincapture-single-instance"
    if not IS_WINDOWS:
        return base
    try:
        import ctypes
        import hashlib
        # 홈 폴더도 포함: 같은 계정이라도 홈(=설정 폴더)이 다르면 다른 인스턴스로 본다.
        # (시험은 임시 홈을 쓰므로, 시험의 --quit 이 실제로 켜져 있는 핀캡처를 끄는 일이 없게 됨)
        who = (os.environ.get("USERDOMAIN", "") + "\\" + os.environ.get("USERNAME", "")
               + "|" + str(Path.home())).lower()
        sess = ctypes.c_ulong(0)
        ctypes.windll.kernel32.ProcessIdToSessionId(os.getpid(), ctypes.byref(sess))
        return f"{base}-{hashlib.sha1(who.encode('utf-8')).hexdigest()[:10]}-{sess.value}"
    except Exception:
        return base


SINGLETON_NAME = _singleton_name()

# 색상 테마 (밝은 UI + 파란 포인트)
ACCENT = "#2F6BFF"
ACCENT_DARK = "#1F4FD0"
BG = "#FAFBFD"
BORDER = "#D5DCE6"
TEXT = "#2B3442"
TEXT_SUB = "#6B7686"

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
CONFIG_DIR = _CONFIG_DIR
CONFIG_PATH = CONFIG_DIR / "config.json"


def _default_save_dir() -> str:
    pictures = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
    base = Path(pictures) if pictures else Path.home()
    return str(base / "PinCapture")


DEFAULTS = {
    "save_dir": "",                    # 비어 있으면 첫 실행 때 사진/PinCapture 로 설정
    "file_format": "png",              # png | jpg
    "jpg_quality": 92,
    "filename_prefix": "캡처",
    "autosave": True,                  # 캡처 시 자동 저장
    "clipboard": True,                 # 캡처 시 클립보드 복사
    "notify": True,                    # 캡처 후 트레이 알림
    "hide_during_capture": True,       # 캡처하는 동안 툴바 숨김
    "pin_after_capture": False,        # 모든 캡처를 핀으로도 고정
    "pin_autosave": False,             # 핀 캡처도 파일로 저장할지
    "show_viewer_after_capture": True, # 캡처 후 보관함 창 열기
    "hotkeys": {
        "region": "<ctrl>+<alt>+a",
        "window": "<ctrl>+<alt>+w",
        "full":   "<ctrl>+<alt>+f",
        "pin":    "<ctrl>+<alt>+q",
        "reopen_pin": "<ctrl>+<alt>+r",    # 최근 핀 다시 열기
        "clickthrough": "<ctrl>+<alt>+x",  # 클릭 통과 해제 (핀은 클릭을 받지 못함)
        "markup": "<ctrl>+<alt>+m",        # 맨 앞 핀에서 표시 시작
        "eyedropper": "<ctrl>+<alt>+c",    # 화면 색 스포이트 (HEX 복사)
        "ruler": "<ctrl>+<alt>+d",         # 두 점 사이 픽셀 거리
    },
    "recent_pin_limit": 10,            # 닫은 핀을 다시 열 수 있게 보관하는 개수
    "toolbar_pos": None,               # 창 위치 [x, y]
    "window_size": None,               # 창 크기 [w, h]
    "welcome_seen": False,             # 첫 실행 빠른 안내를 닫았는지. 0.6.x 파일에는 없음
}


def _clamp_recent_limit(value, default: int = 10) -> int:
    """닫은 핀 보관 개수. 잘못된 값은 기본값, 범위는 1~50."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(50, n))


def load_config() -> dict:
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for k, v in data.items():
                if k == "hotkeys" and isinstance(v, dict):
                    cfg["hotkeys"].update(v)
                else:
                    cfg[k] = v
    except Exception as e:
        print(f"[config] 읽기 실패, 기본값 사용: {e}")
    if not cfg["save_dir"]:
        cfg["save_dir"] = _default_save_dir()
    cfg["recent_pin_limit"] = _clamp_recent_limit(cfg.get("recent_pin_limit", DEFAULTS["recent_pin_limit"]))
    return cfg


def save_config(cfg: dict) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[config] 저장 실패: {e}")


def prepare_config() -> dict:
    """설정을 읽고, 첫 실행과 업그레이드를 구분한 뒤 저장한다.

    welcome_seen 은 0.7.0 에서 추가됐다. 키가 없는 기존 파일은 이미 쓰던 사람으로 보고
    빠른 안내를 자동으로 띄우지 않는다. 파일이 없으면 첫 실행이다.
    그 밖의 키는 load_config 가 기본값과 합치고, 모르는 키도 그대로 둔다.
    """
    fresh = not CONFIG_PATH.is_file()
    prior_keys: set = set()
    if not fresh:
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                prior_keys = set(data)
        except Exception:
            prior_keys = set()
    cfg = load_config()
    if "welcome_seen" not in prior_keys:
        cfg["welcome_seen"] = False if fresh else True
    save_config(cfg)
    return cfg


def should_auto_welcome(cfg: dict, start_in_tray: bool, tray_available: bool) -> bool:
    """첫 실행 안내를 지금 자동으로 열지.

    이미 본 경우와, Windows 시작 시 --tray 로 켜진 경우에는 작업을 끊지 않는다.
    트레이가 없는 환경은 --tray 여도 창이 뜨므로 안내를 보여 준다.
    """
    if cfg.get("welcome_seen"):
        return False
    if start_in_tray and tray_available:
        return False
    return True


def hotkey_label(combo: str) -> str:
    """pynput 형식(<ctrl>+<alt>+a)을 화면에 보일 표기(Ctrl+Alt+A)로 바꾼다."""
    if not combo or not str(combo).strip():
        return "없음"
    names = {
        "ctrl": "Ctrl", "control": "Ctrl", "alt": "Alt", "alt_gr": "AltGr",
        "shift": "Shift", "cmd": "Win", "super": "Win", "win": "Win",
        "print_screen": "PrintScreen", "esc": "Esc", "escape": "Esc",
        "space": "Space", "tab": "Tab", "enter": "Enter", "backspace": "Backspace",
    }
    out = []
    for part in str(combo).split("+"):
        raw = part.strip()
        if not raw:
            continue
        key = raw[1:-1] if (raw.startswith("<") and raw.endswith(">") and len(raw) > 2) else raw
        key_l = key.lower()
        if key_l in names:
            out.append(names[key_l])
        elif len(key) == 1:
            out.append(key.upper())
        else:
            out.append(key.replace("_", " ").title().replace(" ", ""))
    return "+".join(out) if out else "없음"


def third_party_notices_path() -> Path:
    """설치본은 프로그램 폴더, 소스 실행은 installer/docs 의 고지 파일."""
    bundled = app_dir() / "THIRD_PARTY_NOTICES.txt"
    if bundled.is_file():
        return bundled
    return app_dir() / "installer" / "docs" / "THIRD_PARTY_NOTICES.txt"


def open_kofi() -> None:
    """기본 브라우저로 후원 페이지만 연다. 앱 안에 창을 띄우지 않는다."""
    QDesktopServices.openUrl(QUrl(KOFI_URL))


def apply_ui_font(app=None) -> None:
    """한글이 있는 환경의 고딕을 고른다. 없으면 Qt 기본 글꼴을 그대로 쓴다."""
    app = app or QApplication.instance()
    if app is None:
        return
    families = set(QFontDatabase.families())
    for name in ("Malgun Gothic", "맑은 고딕", "Noto Sans CJK KR", "Noto Sans CJK JP", "Noto Sans KR"):
        if name in families:
            app.setFont(QFont(name, 10))
            return


def _polish_dialog(dlg: QDialog) -> None:
    dlg.setStyleSheet(f"""
        QDialog {{ background: white; color: {TEXT}; }}
        QGroupBox {{
            font-weight: 600; border: 1px solid {BORDER}; border-radius: 8px;
            margin-top: 14px; padding: 14px 12px 10px 12px; background: {BG};
        }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {TEXT}; }}
        QLabel {{ color: {TEXT}; }}
        QLineEdit, QComboBox, QSpinBox {{
            padding: 4px 8px; border: 1px solid {BORDER}; border-radius: 6px;
            background: white; min-height: 22px;
        }}
        QCheckBox {{ spacing: 8px; padding: 3px 0; }}
        QPushButton {{
            padding: 6px 14px; border: 1px solid {BORDER}; border-radius: 6px;
            background: white; color: {TEXT};
        }}
        QPushButton:hover {{ background: #EDF3FE; }}
        QPushButton:disabled {{ color: {TEXT_SUB}; background: #F3F5F8; }}
        QPushButton#primary {{
            background: {ACCENT}; color: white; border: 1px solid {ACCENT_DARK}; font-weight: 600;
        }}
        QPushButton#primary:hover {{ background: {ACCENT_DARK}; }}
    """)


# ---------------------------------------------------------------------------
# 아이콘 (외부 파일 없이 QPainter 로 직접 그림)
# ---------------------------------------------------------------------------

def _make_pixmap(size: int, draw_fn, color: str = TEXT) -> QPixmap:
    pm = QPixmap(size * 2, size * 2)
    pm.setDevicePixelRatio(2.0)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(color))
    pen.setWidthF(1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    draw_fn(p, size, QColor(color))
    p.end()
    return pm


def _draw_region(p: QPainter, s: int, c: QColor):
    pen = p.pen()
    pen.setStyle(Qt.PenStyle.DashLine)
    p.setPen(pen)
    p.drawRect(4, 5, s - 9, s - 11)
    pen.setStyle(Qt.PenStyle.SolidLine)
    pen.setColor(QColor(ACCENT))
    p.setPen(pen)
    m = s - 5
    p.drawLine(m - 4, m, m + 2, m)
    p.drawLine(m - 1, m - 3, m - 1, m + 3)


def _draw_window(p: QPainter, s: int, c: QColor):
    p.drawRoundedRect(4, 5, s - 8, s - 10, 2, 2)
    p.drawLine(4, 9, s - 4, 9)
    p.setBrush(QBrush(QColor(ACCENT)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(6.5, 7.2), 1.1, 1.1)


def _draw_full(p: QPainter, s: int, c: QColor):
    p.drawRoundedRect(3, 4, s - 6, s - 11, 2, 2)
    p.drawLine(9, s - 4, s - 9, s - 4)
    p.drawLine(s // 2, s - 7, s // 2, s - 4)


def _draw_pin(p: QPainter, s: int, c: QColor):
    p.save()
    p.translate(s / 2.0, s / 2.0)
    p.rotate(40)
    p.setBrush(QBrush(QColor(ACCENT)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(-3, -9, 6, 9, 2, 2)   # 머리
    p.setBrush(QBrush(QColor(c)))
    p.drawRect(-4, 0, 8, 2)                 # 받침
    pen = QPen(QColor(c)); pen.setWidthF(1.6)
    p.setPen(pen)
    p.drawLine(0, 2, 0, 9)                  # 바늘
    p.restore()


def _draw_gear(p: QPainter, s: int, c: QColor):
    p.save()
    p.translate(s / 2.0, s / 2.0)
    for i in range(8):
        p.save()
        p.rotate(i * 45)
        p.drawLine(0, -7, 0, -9)
        p.restore()
    p.drawEllipse(QPointF(0, 0), 5.2, 5.2)
    p.drawEllipse(QPointF(0, 0), 1.8, 1.8)
    p.restore()


def _draw_close(p: QPainter, s: int, c: QColor):
    p.drawLine(6, 6, s - 6, s - 6)
    p.drawLine(s - 6, 6, 6, s - 6)


def _draw_list(p: QPainter, s: int, c: QColor):
    y0, dy = s * 0.30, s * 0.22
    for i in range(3):
        y = round(y0 + i * dy)
        p.drawLine(round(s * 0.20), y, round(s * 0.28), y)
        p.drawLine(round(s * 0.42), y, round(s * 0.80), y)


def _draw_help(p: QPainter, s: int, c: QColor):
    p.drawEllipse(QPointF(s / 2, s / 2), s / 2 - 3.2, s / 2 - 3.2)
    p.setBrush(QBrush(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(s / 2, s * 0.72), 1.15, 1.15)
    pen = QPen(c)
    pen.setWidthF(1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(int(s * 0.32), int(s * 0.22), int(s * 0.36), int(s * 0.32), 30 * 16, 280 * 16)
    p.drawLine(QPointF(s / 2, s * 0.52), QPointF(s / 2, s * 0.60))


def _draw_info(p: QPainter, s: int, c: QColor):
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QPointF(s / 2, s / 2), s / 2 - 3.2, s / 2 - 3.2)
    p.setBrush(QBrush(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(s / 2, s * 0.34), 1.2, 1.2)
    pen = QPen(c)
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(s / 2, s * 0.48), QPointF(s / 2, s * 0.72))


def _draw_copy(p: QPainter, s: int, c: QColor):
    p.drawRoundedRect(8, 8, s - 13, s - 13, 2, 2)
    p.drawRoundedRect(4, 4, s - 13, s - 13, 2, 2)


def _draw_folder(p: QPainter, s: int, c: QColor):
    p.drawLine(4, 9, 9, 9)
    p.drawLine(9, 6, 13, 9)
    p.drawRoundedRect(3, 9, s - 6, s - 13, 2, 2)


def _draw_save(p: QPainter, s: int, c: QColor):
    mid = s / 2
    p.drawLine(QPointF(mid, 4), QPointF(mid, s - 8))
    p.drawLine(QPointF(mid - 4, s - 12), QPointF(mid, s - 8))
    p.drawLine(QPointF(mid + 4, s - 12), QPointF(mid, s - 8))
    p.drawLine(QPointF(4, s - 4), QPointF(s - 4, s - 4))


def _draw_trash(p: QPainter, s: int, c: QColor):
    p.drawLine(5, 7, s - 5, 7)
    p.drawLine(9, 5, s - 9, 5)
    p.drawRect(7, 8, s - 14, s - 13)
    p.drawLine(10, 11, 10, s - 7)
    p.drawLine(s - 10, 11, s - 10, s - 7)


def _draw_markup(p: QPainter, s: int, c: QColor):
    """연필. 핀 위 표시."""
    p.drawLine(QPointF(7, s - 6), QPointF(s - 6, 7))
    p.drawLine(QPointF(5, s - 5), QPointF(8, s - 8))
    p.drawLine(QPointF(5, s - 5), QPointF(8, s - 3))
    p.drawLine(QPointF(s - 8, 5), QPointF(s - 4, 5))
    p.drawLine(QPointF(s - 4, 5), QPointF(s - 4, 9))


def _draw_eyedropper(p: QPainter, s: int, c: QColor):
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(6, s - 6), QPointF(s - 9, 8))
    p.drawEllipse(QPointF(s - 7, 7), 3.4, 3.4)
    p.drawLine(QPointF(5, s - 4), QPointF(8, s - 8))
    p.drawLine(QPointF(5, s - 4), QPointF(9, s - 4))


def _draw_ruler(p: QPainter, s: int, c: QColor):
    p.drawLine(QPointF(5, 6), QPointF(5, s - 5))
    p.drawLine(QPointF(5, s - 5), QPointF(s - 4, s - 5))
    for x in (10, 14, 18):
        p.drawLine(QPointF(x, s - 5), QPointF(x, s - 9))
    p.drawLine(QPointF(5, 10), QPointF(8, 10))
    p.drawLine(QPointF(5, 15), QPointF(9, 15))


def _draw_ocr(p: QPainter, s: int, c: QColor):
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(4, 3, s - 8, s - 7, 2, 2)
    p.drawLine(7, 8, s - 8, 8)
    p.drawLine(7, 12, s - 10, 12)
    p.drawLine(7, 16, s - 12, 16)


def _draw_reopen(p: QPainter, s: int, c: QColor):
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(5, 5, s - 10, s - 10, 45 * 16, 280 * 16)
    p.drawLine(QPointF(s - 7, 6), QPointF(s - 3, 6))
    p.drawLine(QPointF(s - 7, 6), QPointF(s - 7, 10))


def _draw_mark_arrow(p: QPainter, s: int, c: QColor):
    """오른쪽 위 화살표. 핀 표시의 화살표 도구."""
    tail = QPointF(s * 0.26, s * 0.74)
    tip = QPointF(s * 0.76, s * 0.26)
    p.drawLine(tail, tip)
    dx, dy = tip.x() - tail.x(), tip.y() - tail.y()
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    head = s * 0.30
    base = QPointF(tip.x() - ux * head, tip.y() - uy * head)
    left = QPointF(base.x() + px * head * 0.48, base.y() + py * head * 0.48)
    right = QPointF(base.x() - px * head * 0.48, base.y() - py * head * 0.48)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(c))
    p.drawPolygon(QPolygonF([tip, left, right]))


def _draw_mark_box(p: QPainter, s: int, c: QColor):
    p.setBrush(Qt.BrushStyle.NoBrush)
    m = s * 0.22
    p.drawRoundedRect(QRectF(m, m, s - m * 2, s - m * 2), 2, 2)


def _draw_mark_highlight(p: QPainter, s: int, c: QColor):
    """대각 굵은 획. 두께 아이콘(가로선)과 구분되는 형광펜."""
    pen = QPen(c)
    pen.setWidthF(max(3.0, s * 0.26))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(s * 0.24, s * 0.74), QPointF(s * 0.76, s * 0.30))


def _draw_mark_mosaic(p: QPainter, s: int, c: QColor):
    n = 3
    gap = max(1.0, s * 0.07)
    side = (s * 0.70 - gap * (n - 1)) / n
    origin = (s - (side * n + gap * (n - 1))) / 2.0
    pen = QPen(c)
    pen.setWidthF(1.1)
    for row in range(n):
        for col in range(n):
            x = origin + col * (side + gap)
            y = origin + row * (side + gap)
            if (row + col) % 2 == 0:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(c))
            else:
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(x, y, side, side), 1, 1)


def _draw_mark_pen(p: QPainter, s: int, c: QColor):
    path = QPainterPath()
    path.moveTo(s * 0.20, s * 0.68)
    path.cubicTo(s * 0.34, s * 0.28, s * 0.42, s * 0.30, s * 0.50, s * 0.52)
    path.cubicTo(s * 0.58, s * 0.74, s * 0.66, s * 0.70, s * 0.82, s * 0.32)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)


def _draw_hook_arrow(p: QPainter, s: int, c: QColor, mirror: bool):
    """실행 취소·다시 실행. mirror 이면 좌우를 뒤집는다."""
    def x_of(x: float) -> float:
        return (s - x) if mirror else x

    p.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath()
    path.moveTo(x_of(s * 0.74), s * 0.36)
    path.cubicTo(x_of(s * 0.74), s * 0.20, x_of(s * 0.40), s * 0.18, x_of(s * 0.30), s * 0.40)
    path.cubicTo(x_of(s * 0.20), s * 0.60, x_of(s * 0.36), s * 0.78, x_of(s * 0.66), s * 0.70)
    p.drawPath(path)
    tip = QPointF(x_of(s * 0.30), s * 0.40)
    wing = s * 0.15
    p.drawLine(tip, QPointF(x_of(s * 0.30 + wing), s * 0.40 - wing * 0.72))
    p.drawLine(tip, QPointF(x_of(s * 0.30 + wing), s * 0.40 + wing * 0.85))


def _draw_undo(p: QPainter, s: int, c: QColor):
    _draw_hook_arrow(p, s, c, False)


def _draw_redo(p: QPainter, s: int, c: QColor):
    _draw_hook_arrow(p, s, c, True)


def _draw_check(p: QPainter, s: int, c: QColor):
    p.drawLine(QPointF(s * 0.24, s * 0.52), QPointF(s * 0.42, s * 0.72))
    p.drawLine(QPointF(s * 0.42, s * 0.72), QPointF(s * 0.78, s * 0.30))


def _draw_stroke_width(p: QPainter, s: int, c: QColor, width: float):
    pen = QPen(c)
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    y = s * 0.50
    p.drawLine(QPointF(s * 0.20, y), QPointF(s * 0.80, y))


def _draw_width_thin(p: QPainter, s: int, c: QColor):
    _draw_stroke_width(p, s, c, max(1.4, s * 0.07))


def _draw_width_mid(p: QPainter, s: int, c: QColor):
    _draw_stroke_width(p, s, c, max(2.6, s * 0.15))


def _draw_width_thick(p: QPainter, s: int, c: QColor):
    _draw_stroke_width(p, s, c, max(4.2, s * 0.26))


def make_icon(kind: str, color: str = TEXT, size: int = 24) -> QIcon:
    fn = {
        "region": _draw_region, "window": _draw_window, "full": _draw_full,
        "pin": _draw_pin, "gear": _draw_gear, "close": _draw_close,
        "list": _draw_list, "help": _draw_help, "info": _draw_info,
        "copy": _draw_copy, "folder": _draw_folder, "save": _draw_save,
        "trash": _draw_trash, "markup": _draw_markup, "eyedropper": _draw_eyedropper,
        "ruler": _draw_ruler, "ocr": _draw_ocr, "reopen": _draw_reopen,
        "mark_arrow": _draw_mark_arrow, "mark_box": _draw_mark_box,
        "mark_highlight": _draw_mark_highlight, "mark_mosaic": _draw_mark_mosaic,
        "mark_pen": _draw_mark_pen, "undo": _draw_undo, "redo": _draw_redo,
        "check": _draw_check, "width_thin": _draw_width_thin, "width_mid": _draw_width_mid,
        "width_thick": _draw_width_thick,
    }[kind]
    icon = QIcon()
    icon.addPixmap(_make_pixmap(size, fn, color), QIcon.Mode.Normal, QIcon.State.Off)
    icon.addPixmap(_make_pixmap(size, fn, "#9AA3B2"), QIcon.Mode.Disabled, QIcon.State.Off)
    return icon


def make_app_icon(size: int = 64) -> QIcon:
    """트레이/창용 앱 아이콘: 파란 바탕 + 핀. (64px 기준 좌표로 그리고 size 에 맞게 배율 조정 —
    빌드 스크립트가 16~256px 을 각각 그려 EXE 아이콘(.ico)을 만든다)"""
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.scale(size / 64.0, size / 64.0)
    p.setBrush(QBrush(QColor(ACCENT)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(2, 2, 60, 60, 14, 14)
    p.translate(32, 34)
    p.rotate(40)
    p.setBrush(QBrush(QColor("white")))
    p.drawRoundedRect(-8, -24, 16, 22, 5, 5)
    p.drawRect(-11, -2, 22, 5)
    pen = QPen(QColor("white")); pen.setWidth(4); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(0, 5, 0, 22)
    p.end()
    return QIcon(pm)


# ---------------------------------------------------------------------------
# 캡처 백엔드
# ---------------------------------------------------------------------------

def grab_screen_raw(screen) -> QPixmap:
    """해당 모니터 전체를 물리 픽셀 단위로 캡처 (DPR 메타데이터 제거)."""
    pm = screen.grabWindow(0)
    pm.setDevicePixelRatio(1.0)
    return pm


def is_pure_black(img) -> bool:
    """이미지 전체가 완전한 검정(#000000)인지.
    은행·홈택스 등의 보안 프로그램이 '화면 캡처 방지'를 켜면 화면 캡처 결과가 이렇게 통째로 검게 나온다.
    실제 모니터 화면은 작업 표시줄·글자·커서 영역 때문에 픽셀 하나 남김없이 #000000 일 수가 없다.
    (픽셀 비교는 Qt 의 C++ 비교라 2560x1440 도 수 ms)"""
    if img is None:
        return False
    if isinstance(img, QPixmap):
        img = img.toImage()
    if img.isNull() or img.width() <= 0 or img.height() <= 0:
        return False
    im = img.convertToFormat(QImage.Format.Format_RGB32)
    black = QImage(im.size(), QImage.Format.Format_RGB32)
    black.fill(QColor(0, 0, 0))
    return im == black


# 보안 모듈(예: Teruten)은 픽셀이 한두 개만 검정이 아닐 때도 있다. 표본의 이 비율 이상이
# 거의 검정(채널당 0~16)이면 캡처가 막힌 것으로 본다.
MOSTLY_BLACK_RATIO = 0.985
_NEAR_BLACK_MAX = 16


def is_mostly_black(img, ratio: float = MOSTLY_BLACK_RATIO) -> bool:
    """이미지가 거의 전부 검정인지. 완전한 #000000 은 is_pure_black.
    큰 이미지는 격자에서 최대 약 64×64 점을 뽑아 비교한다 (전체 스캔은 하지 않음)."""
    if img is None:
        return False
    if isinstance(img, QPixmap):
        img = img.toImage()
    if img.isNull() or img.width() <= 0 or img.height() <= 0:
        return False
    im = img.convertToFormat(QImage.Format.Format_RGB32)
    w, h = im.width(), im.height()
    step_x = max(1, w // 64)
    step_y = max(1, h // 64)
    total = dark = 0
    for y in range(0, h, step_y):
        for x in range(0, w, step_x):
            c = im.pixel(x, y)
            total += 1
            if ((c & 0xFF) <= _NEAR_BLACK_MAX and ((c >> 8) & 0xFF) <= _NEAR_BLACK_MAX
                    and ((c >> 16) & 0xFF) <= _NEAR_BLACK_MAX):
                dark += 1
    return total > 0 and (dark / total) >= ratio


def screens_capture_blocked(grabs: "list | None" = None) -> bool:
    """모든 모니터의 캡처가 거의 전부 검정이면 True = 보안 프로그램 등이 화면 캡처를 막고 있음.
    grabs 를 주면 이미 찍은 화면들로 판단 (다시 찍지 않음)."""
    if grabs is None:
        grabs = [grab_screen_raw(s) for s in QGuiApplication.screens()]
    return bool(grabs) and all(is_mostly_black(g) for g in grabs)


def screen_under_cursor():
    s = QGuiApplication.screenAt(QCursor.pos())
    return s or QGuiApplication.primaryScreen()


# ---- Windows 전용: 활성 창 캡처 ----
if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32
    _gdi32 = ctypes.windll.gdi32

    class _BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD), ("biWidth", ctypes.c_long),
            ("biHeight", ctypes.c_long), ("biPlanes", wintypes.WORD),
            ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", ctypes.c_long),
            ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wintypes.DWORD),
            ("biClrImportant", wintypes.DWORD),
        ]

    class _BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", _BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]

    def _foreground_hwnd(exclude: set):
        hwnd = _user32.GetForegroundWindow()
        if not hwnd or hwnd in exclude:
            pt = wintypes.POINT()
            _user32.GetCursorPos(ctypes.byref(pt))
            h = _user32.WindowFromPoint(pt)
            GA_ROOT = 2
            hwnd = _user32.GetAncestor(h, GA_ROOT) if h else 0
            if hwnd in exclude:
                hwnd = 0
        return hwnd or None

    def _window_rects(hwnd):
        """(보이는 프레임 rect, GetWindowRect) 물리 픽셀 좌표로 반환."""
        wr = wintypes.RECT()
        _user32.GetWindowRect(hwnd, ctypes.byref(wr))
        er = wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        try:
            ok = ctypes.windll.dwmapi.DwmGetWindowAttribute(
                hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(er), ctypes.sizeof(er))
            if ok != 0:
                er = wr
        except Exception:
            er = wr
        return er, wr

    def _print_window(hwnd) -> "QImage | None":
        """PrintWindow 로 창 내용을 직접 렌더링 (가려져 있어도 캡처됨)."""
        er, wr = _window_rects(hwnd)
        w, h = wr.right - wr.left, wr.bottom - wr.top
        if w <= 0 or h <= 0:
            return None
        hdc_screen = _user32.GetDC(0)
        memdc = _gdi32.CreateCompatibleDC(hdc_screen)
        bmi = _BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = w
        bmi.bmiHeader.biHeight = -h  # top-down
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0  # BI_RGB
        bits = ctypes.c_void_p()
        hbmp = _gdi32.CreateDIBSection(hdc_screen, ctypes.byref(bmi), 0,
                                       ctypes.byref(bits), None, 0)
        img = None
        if hbmp:
            old = _gdi32.SelectObject(memdc, hbmp)
            PW_RENDERFULLCONTENT = 0x00000002
            ok = _user32.PrintWindow(hwnd, memdc, PW_RENDERFULLCONTENT)
            if ok:
                buf = ctypes.string_at(bits, w * h * 4)
                img = QImage(buf, w, h, w * 4, QImage.Format.Format_RGB32).copy()
                # 보이는 프레임만 남기고 그림자·투명 테두리 제거
                dx, dy = er.left - wr.left, er.top - wr.top
                ew, eh = er.right - er.left, er.bottom - er.top
                crop = QRect(dx, dy, ew, eh).intersected(QRect(0, 0, w, h))
                if crop.isValid() and crop != QRect(0, 0, w, h):
                    img = img.copy(crop)
            _gdi32.SelectObject(memdc, old)
            _gdi32.DeleteObject(hbmp)
        _gdi32.DeleteDC(memdc)
        _user32.ReleaseDC(0, hdc_screen)
        return img

    def capture_active_window(exclude_hwnds: set, fallback_hwnd=None) -> "QImage | None":
        hwnd = _foreground_hwnd(exclude_hwnds)
        if not hwnd and fallback_hwnd and fallback_hwnd not in exclude_hwnds:
            hwnd = fallback_hwnd    # 직전에 활성화돼 있던 외부 창
        if not hwnd:
            return None
        img = _print_window(hwnd)
        if img is not None and not img.isNull():
            return img
        # 폴백: 화면에서 창 영역을 잘라냄
        er, _ = _window_rects(hwnd)
        s = screen_under_cursor()
        raw = grab_screen_raw(s)
        dpr = s.devicePixelRatio()
        sg = s.geometry()
        phys = QRect(int(er.left - sg.x() * dpr), int(er.top - sg.y() * dpr),
                     er.right - er.left, er.bottom - er.top)
        phys = phys.intersected(QRect(0, 0, raw.width(), raw.height()))
        if not phys.isValid():
            return raw.toImage()
        return raw.copy(phys).toImage()
else:
    def capture_active_window(exclude_hwnds: set, fallback_hwnd=None) -> "QImage | None":
        # Windows 외 환경(테스트용): 마우스가 있는 모니터 전체로 대체
        return grab_screen_raw(screen_under_cursor()).toImage()


# ---------------------------------------------------------------------------
# 영역 선택 오버레이 (화면 정지 방식, 모니터별 1개)
# ---------------------------------------------------------------------------
class SelectionOverlay(QWidget):
    selected = Signal(QImage, QPoint)   # (잘라낸 이미지, 선택 영역의 전역 논리 좌표)
    canceled = Signal()

    def __init__(self, screen, frozen: QPixmap):
        super().__init__(None)
        self._screen = screen
        self._frozen = frozen           # 물리 픽셀 pixmap (DPR=1)
        self._origin = None             # 드래그 시작점 (위젯 좌표)
        self._current = None
        self._mouse = QPoint(-1, -1)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setGeometry(screen.geometry())

    # --- 좌표 매핑: 위젯(논리) → frozen pixmap(물리) ---
    def _to_phys(self, r: QRect) -> QRect:
        sx = self._frozen.width() / max(1, self.width())
        sy = self._frozen.height() / max(1, self.height())
        return QRect(round(r.x() * sx), round(r.y() * sy),
                     round(r.width() * sx), round(r.height() * sy))

    def _sel_rect(self) -> "QRect | None":
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    # --- 이벤트 ---
    def enterEvent(self, e):
        self.activateWindow()
        self.setFocus(Qt.FocusReason.MouseFocusReason)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.canceled.emit()
        else:
            super().keyPressEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._origin = e.position().toPoint()
            self._current = self._origin
            self.update()
        elif e.button() == Qt.MouseButton.RightButton:
            self.canceled.emit()

    def mouseMoveEvent(self, e):
        self._mouse = e.position().toPoint()
        if self._origin is not None:
            self._current = self._mouse
        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        sel = self._sel_rect()
        self._origin = self._current = None
        if sel is None or sel.width() < 4 or sel.height() < 4:
            self.update()   # 클릭만 한 경우: 취소 아님, 다시 드래그 대기
            return
        phys = self._to_phys(sel).intersected(self._frozen.rect())
        img = self._frozen.copy(phys).toImage()
        gpos = sel.topLeft() + self._screen.geometry().topLeft()
        self.selected.emit(img, gpos)

    # --- 그리기 ---
    def paintEvent(self, e):
        p = QPainter(self)
        p.drawPixmap(self.rect(), self._frozen)           # 정지 화면
        p.fillRect(self.rect(), QColor(0, 0, 0, 110))     # 어둡게
        sel = self._sel_rect()
        if sel is not None and sel.isValid():
            src = self._to_phys(sel)
            p.drawPixmap(sel, self._frozen, src)          # 선택 영역만 밝게
            pen = QPen(QColor(ACCENT)); pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(sel.adjusted(0, 0, -1, -1))
            self._draw_size_label(p, sel)
        elif self._mouse.x() >= 0:
            pen = QPen(QColor(255, 255, 255, 150)); pen.setWidth(1)
            p.setPen(pen)
            p.drawLine(0, self._mouse.y(), self.width(), self._mouse.y())
            p.drawLine(self._mouse.x(), 0, self._mouse.x(), self.height())
            hint = "드래그해서 영역을 고르세요  ·  Esc 또는 우클릭으로 취소"
            self._draw_tag(p, QPoint(self._mouse.x() + 14, self._mouse.y() + 18), hint)
        p.end()

    def _draw_size_label(self, p: QPainter, sel: QRect):
        phys = self._to_phys(sel)
        text = f"{phys.width()} × {phys.height()} px"
        pos = QPoint(sel.x(), sel.y() - 26)
        if pos.y() < 4:
            pos.setY(sel.y() + 6)
        self._draw_tag(p, pos, text)

    def _draw_tag(self, p: QPainter, pos: QPoint, text: str):
        f = QFont(self.font()); f.setPointSize(9)
        p.setFont(f)
        br = p.fontMetrics().boundingRect(text)
        r = QRect(pos, QSize(br.width() + 14, br.height() + 8))
        r.moveLeft(min(r.left(), self.width() - r.width() - 4))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 26, 36, 215))
        p.drawRoundedRect(r, 4, 4)
        p.setPen(QColor("white"))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, text)


def _show_overlay(widget) -> None:
    """정지 화면을 메인 창·핀보다 앞에 두고 키보드 포커스를 준다.

    Windows 에서는 activateWindow 를 force_foreground 보다 먼저 부르면
    전경 전환이 잠시 막혀 Esc 가 먹히지 않는다.
    """
    widget.show()
    widget.raise_()
    if IS_WINDOWS:
        force_foreground(int(widget.winId()))
    widget.activateWindow()
    widget.setFocus()


class RegionCaptureSession(QObject):
    """모든 모니터에 오버레이를 띄우고 첫 선택/취소를 받아 정리."""
    finished = Signal(object, object)   # (QImage | None, QPoint | None)
    blocked = Signal()                  # 화면 캡처가 차단됨 (모든 모니터가 거의 전부 검정)

    def __init__(self):
        super().__init__()
        self._overlays = []
        self._done = False

    def start(self):
        opened = False
        try:
            self._open_overlays()
            opened = True
        finally:
            if not opened:
                self._cleanup()

    def _open_overlays(self):
        screens = QGuiApplication.screens()
        frozens = [grab_screen_raw(s) for s in screens]
        if screens_capture_blocked(frozens):
            # 검은 화면을 모니터 전체에 띄우면 '화면이 꺼진 것처럼' 보이므로 띄우지 않고 알린다
            self._done = True
            QTimer.singleShot(0, self._emit_blocked)
            return
        for screen, frozen in zip(screens, frozens):
            ov = SelectionOverlay(screen, frozen)
            ov.selected.connect(self._on_selected)
            ov.canceled.connect(self._on_canceled)
            self._overlays.append(ov)
            ov.show()
            ov.raise_()
        cur = screen_under_cursor()
        for ov in self._overlays:
            if ov._screen is cur:
                _show_overlay(ov)
                break

    def _emit_blocked(self):
        self.finished.emit(None, None)   # 먼저 캡처 상태 해제·창 복구
        self.blocked.emit()

    def _cleanup(self):
        overlays = list(self._overlays)
        self._overlays.clear()
        for ov in overlays:
            try:
                ov.blockSignals(True)
                ov.close()
            except RuntimeError:
                pass

    def _on_selected(self, img: QImage, gpos: QPoint):
        if self._done:
            return
        self._done = True
        self._cleanup()
        self.finished.emit(img, gpos)

    def _on_canceled(self):
        if self._done:
            return
        self._done = True
        self._cleanup()
        self.finished.emit(None, None)


# ---------------------------------------------------------------------------
# 스포이트 / 자 (모니터별 정지 화면. 논리 좌표를 물리 픽셀로 환산)
# ---------------------------------------------------------------------------
def physical_point(widget_size: QSize, image_size: QSize, pt: QPoint) -> QPoint:
    """위젯(논리) 좌표를 정지 화면의 물리 픽셀로. 화면 밖으로 나가면 가장자리로 붙인다."""
    sx = image_size.width() / max(1, widget_size.width())
    sy = image_size.height() / max(1, widget_size.height())
    x = min(max(0, int(round(pt.x() * sx))), max(0, image_size.width() - 1))
    y = min(max(0, int(round(pt.y() * sy))), max(0, image_size.height() - 1))
    return QPoint(x, y)


def scale_percent(widget_size: QSize, image_size: QSize) -> int:
    """정지 화면 픽셀 / 위젯 논리 크기. 100 이면 100%, 200 이면 배율 2배."""
    sx = image_size.width() / max(1, widget_size.width())
    sy = image_size.height() / max(1, widget_size.height())
    return int(round(((sx + sy) / 2.0) * 100))


def format_color(color: QColor) -> "tuple[str, str]":
    """(#RRGGBB, 'R r  G g  B b'). 클립보드에는 HEX 만 넣는다."""
    hex_s = "#{:02X}{:02X}{:02X}".format(color.red(), color.green(), color.blue())
    rgb = f"R {color.red()}  G {color.green()}  B {color.blue()}"
    return hex_s, rgb


def measure_pixels(a: QPoint, b: QPoint) -> dict:
    """두 물리 픽셀 사이의 거리와 가로·세로. 단위는 픽셀."""
    dx = int(b.x()) - int(a.x())
    dy = int(b.y()) - int(a.y())
    return {
        "dx": abs(dx),
        "dy": abs(dy),
        "distance": int(round(math.hypot(dx, dy))),
    }


def snap_axis_point(origin: QPoint, point: QPoint) -> QPoint:
    """끝점을 시작점 기준 0·45·90° 중 가장 가까운 직선 위로 붙인다.

    길이는 그 방향으로 투영한 거리라서, 커서가 있는 쪽에 남는다.
    """
    dx = int(point.x()) - int(origin.x())
    dy = int(point.y()) - int(origin.y())
    if dx == 0 and dy == 0:
        return QPoint(int(origin.x()), int(origin.y()))
    step = math.pi / 4.0
    snapped = round(math.atan2(dy, dx) / step) * step
    ux, uy = math.cos(snapped), math.sin(snapped)
    proj = dx * ux + dy * uy
    return QPoint(
        int(origin.x()) + int(round(proj * ux)),
        int(origin.y()) + int(round(proj * uy)),
    )


class InspectOverlay(QWidget):
    """한 모니터의 정지 화면 위에서 색을 찍거나 두 점 거리를 잰다."""
    picked = Signal(object)
    canceled = Signal()

    def __init__(self, screen, frozen: QPixmap, mode: str):
        super().__init__(None)
        self._screen = screen
        self._frozen = frozen
        self._image = frozen.toImage()
        self._mode = mode if mode in ("eyedropper", "ruler") else "eyedropper"
        self._mouse = QPoint(-1, -1)
        self._anchor = None            # 자의 첫 점 (물리 픽셀)
        self._shift = False
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setGeometry(screen.geometry())

    def _phys(self, pt: QPoint) -> QPoint:
        return physical_point(self.size(), self._image.size(), pt)

    def _to_widget(self, phys: QPoint) -> QPoint:
        sx = self.width() / max(1, self._image.width())
        sy = self.height() / max(1, self._image.height())
        return QPoint(int(round(phys.x() * sx)), int(round(phys.y() * sy)))

    def _ruler_target(self, widget_pt: QPoint, shift: bool) -> QPoint:
        """자에서 Shift 를 누르면 첫 점 기준 가로·세로·45° 로 맞춘 물리 픽셀."""
        phys = self._phys(widget_pt)
        if shift and self._anchor is not None and self._mode == "ruler":
            return snap_axis_point(self._anchor, phys)
        return phys

    def enterEvent(self, e):
        self.activateWindow()
        self.setFocus(Qt.FocusReason.MouseFocusReason)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.canceled.emit()
            return
        if e.key() == Qt.Key.Key_Shift and self._mode == "ruler":
            self._shift = True
            self.update()
            return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Shift and self._mode == "ruler":
            self._shift = False
            self.update()
            return
        super().keyReleaseEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.canceled.emit()
            return
        if e.button() != Qt.MouseButton.LeftButton:
            return
        pos = e.position().toPoint()
        phys = self._phys(pos)
        if self._mode == "eyedropper":
            color = QColor(self._image.pixel(phys)) if not self._image.isNull() else QColor(0, 0, 0)
            hex_s, rgb = format_color(color)
            self.picked.emit({
                "mode": "eyedropper", "hex": hex_s, "rgb": rgb,
                "r": color.red(), "g": color.green(), "b": color.blue(),
            })
            return
        if self._anchor is None:
            self._anchor = phys
            self._mouse = pos
            self._shift = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self.update()
            return
        shift = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        self._shift = shift
        target = self._ruler_target(pos, shift)
        result = measure_pixels(self._anchor, target)
        result["mode"] = "ruler"
        result["scale"] = scale_percent(self.size(), self._image.size())
        self.picked.emit(result)

    def mouseMoveEvent(self, e):
        self._mouse = e.position().toPoint()
        self._shift = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        if not self._frozen.isNull():
            p.drawPixmap(self.rect(), self._frozen)
        if self._mode == "eyedropper":
            self._paint_eyedropper(p)
        else:
            self._paint_ruler(p)
        p.end()

    def _paint_eyedropper(self, p: QPainter):
        pos = self._mouse if self._mouse.x() >= 0 else QPoint(self.width() // 2, self.height() // 2)
        if self._image.isNull() or self._image.width() < 1:
            return
        phys = self._phys(pos)
        color = QColor(self._image.pixel(phys))
        hex_s, rgb = format_color(color)
        loupe = self._paint_loupe(p, pos, phys)
        label_y = (loupe.bottom() + 8) if loupe is not None else (pos.y() + 20)
        self._draw_tag(p, QPoint(pos.x() + 16, label_y), f"{hex_s}   {rgb}")
        self._draw_tag(p, QPoint(12, 12), "클릭하면 색을 복사해요  ·  Esc 또는 우클릭으로 취소")

    def _paint_loupe(self, p: QPainter, pos: QPoint, phys: QPoint):
        sample = 15
        half = sample // 2
        src = QRect(phys.x() - half, phys.y() - half, sample, sample).intersected(self._image.rect())
        if not src.isValid() or src.width() < 1 or src.height() < 1:
            return None
        side = sample * 8
        origin = QPoint(pos.x() + 18, pos.y() + 18)
        if origin.x() + side > self.width() - 4:
            origin.setX(pos.x() - side - 18)
        if origin.y() + side > self.height() - 4:
            origin.setY(pos.y() - side - 18)
        origin.setX(max(4, origin.x()))
        origin.setY(max(4, origin.y()))
        dest = QRect(origin, QSize(side, side))
        p.drawImage(dest, self._image, src)
        p.setPen(QPen(QColor("white"), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(dest.adjusted(0, 0, -1, -1))
        rx = (phys.x() - src.x() + 0.5) / max(1, src.width())
        ry = (phys.y() - src.y() + 0.5) / max(1, src.height())
        hx = dest.left() + int(rx * dest.width())
        hy = dest.top() + int(ry * dest.height())
        p.drawLine(hx - 8, hy, hx + 8, hy)
        p.drawLine(hx, hy - 8, hx, hy + 8)
        return dest

    def _paint_ruler(self, p: QPainter):
        self._draw_tag(p, QPoint(12, 12),
                       "두 점을 클릭하세요  ·  Shift는 가로·세로·45°  ·  Esc 또는 우클릭으로 취소")
        if self._anchor is None:
            if self._mouse.x() >= 0:
                pen = QPen(QColor(255, 255, 255, 180))
                pen.setWidth(1)
                p.setPen(pen)
                p.drawLine(0, self._mouse.y(), self.width(), self._mouse.y())
                p.drawLine(self._mouse.x(), 0, self._mouse.x(), self.height())
            return
        a = self._to_widget(self._anchor)
        if self._mouse.x() >= 0:
            b_phys = self._ruler_target(self._mouse, self._shift)
            b = self._to_widget(b_phys)
        else:
            b_phys = self._anchor
            b = a
        pen = QPen(QColor(ACCENT))
        pen.setWidth(2)
        p.setPen(pen)
        p.drawLine(a, b)
        p.setBrush(QColor(ACCENT))
        p.drawEllipse(a, 4, 4)
        if self._mouse.x() >= 0 and not self._image.isNull():
            text = _ruler_label(self._anchor, b_phys,
                                scale_percent(self.size(), self._image.size()))
            self._draw_tag(p, QPoint(b.x() + 12, b.y() + 12), text)

    def _draw_tag(self, p: QPainter, pos: QPoint, text: str):
        f = QFont(self.font())
        f.setPointSize(9)
        p.setFont(f)
        br = p.fontMetrics().boundingRect(text)
        r = QRect(pos, QSize(br.width() + 14, br.height() + 8))
        r.moveLeft(min(max(4, r.left()), max(4, self.width() - r.width() - 4)))
        r.moveTop(min(max(4, r.top()), max(4, self.height() - r.height() - 4)))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 26, 36, 215))
        p.drawRoundedRect(r, 4, 4)
        p.setPen(QColor("white"))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, text)


def _ruler_label(a: QPoint, b: QPoint, scale: int) -> str:
    m = measure_pixels(a, b)
    return f"{m['distance']}px   가로 {m['dx']}   세로 {m['dy']}   {scale}%"


class ScreenInspectSession(QObject):
    """모든 모니터에 스포이트 또는 자 오버레이를 띄운다. 캡처가 막히면 검은 화면은 띄우지 않는다."""
    finished = Signal(object)     # dict | None
    blocked = Signal()

    def __init__(self, mode: str):
        super().__init__()
        self._mode = mode if mode in ("eyedropper", "ruler") else "eyedropper"
        self._overlays = []
        self._done = False

    def start(self):
        opened = False
        try:
            self._open_overlays()
            opened = True
        finally:
            if not opened:
                self._cleanup()

    def _open_overlays(self):
        screens = QGuiApplication.screens() or []
        if not screens:
            self._done = True
            QTimer.singleShot(0, lambda: self.finished.emit({"error": "noscreen"}))
            return
        frozens = [grab_screen_raw(s) for s in screens]
        if screens_capture_blocked(frozens):
            self._done = True
            QTimer.singleShot(0, self._emit_blocked)
            return
        for screen, frozen in zip(screens, frozens):
            ov = InspectOverlay(screen, frozen, self._mode)
            ov.picked.connect(self._on_picked)
            ov.canceled.connect(self._on_canceled)
            self._overlays.append(ov)
            ov.show()
            ov.raise_()
        cur = screen_under_cursor()
        shown = False
        for ov in self._overlays:
            if ov._screen is cur:
                _show_overlay(ov)
                shown = True
                break
        if not shown and self._overlays:
            _show_overlay(self._overlays[0])

    def _emit_blocked(self):
        self.finished.emit(None)
        self.blocked.emit()

    def _cleanup(self):
        overlays = list(self._overlays)
        self._overlays.clear()
        for ov in overlays:
            try:
                ov.blockSignals(True)
                ov.close()
            except RuntimeError:
                pass

    def _on_picked(self, result):
        if self._done:
            return
        self._done = True
        self._cleanup()
        self.finished.emit(result)

    def _on_canceled(self):
        if self._done:
            return
        self._done = True
        self._cleanup()
        self.finished.emit(None)


# ---------------------------------------------------------------------------
# 핀 창 (항상 위 이미지 고정) + OCR + 최근 핀
# ---------------------------------------------------------------------------
OPACITY_STEPS = (100, 80, 60, 40)   # 핀 메뉴·Ctrl+휠 이 오가는 투명도 (%)

OCR_UNAVAILABLE_MSG = (
    "Windows OCR을 사용할 수 없어요.\n"
    "Windows 설정 → 시간 및 언어 → 언어 및 지역에서 한국어 또는 영어를 추가하고, "
    "그 언어의 '광학 문자 인식'을 설치한 뒤 다시 시도해 주세요."
)
OCR_NO_LANGUAGE_MSG = (
    "글자를 읽을 언어 팩이 없어요.\n"
    "Windows 설정 → 시간 및 언어 → 언어 및 지역에서 한국어나 영어를 추가하고, "
    "해당 언어의 '광학 문자 인식'을 설치해 주세요."
)
OCR_EMPTY_MSG = "이미지에서 글자를 찾지 못했어요."
OCR_FAILED_MSG = "글자를 읽지 못했어요. 잠시 뒤 다시 시도해 주세요."
OCR_COPIED_MSG = "글자를 복사했어요."
OCR_BUSY_MSG = "읽는 중…"
OCR_TABLE_COPIED_MSG = "표를 복사했어요. 엑셀에 붙여 넣으면 칸으로 들어가요."
OCR_TABLE_MD_MSG = "표를 Markdown으로 복사했어요."
OCR_TABLE_EMPTY_MSG = "표로 읽을 칸을 찾지 못했어요."
MATH_MISSING_MSG = (
    "수식 기능이 아직 없어요.\n"
    "글자 복사의 수식을 고르면 설치할 수 있어요. "
    "설치를 누르기 전에는 파일을 받지 않아요.\n"
    "글자와 표 복사는 그대로 쓸 수 있어요."
)
MATH_RUNTIME_MSG = (
    "수식 파일을 찾았지만 실행할 수 없어요.\n"
    "글자 복사의 수식을 다시 고르면 구성 요소를 받을 수 있어요.\n"
    "글자와 표 복사는 그대로 쓸 수 있어요."
)
# 설치 확인 창의 본문. 버튼은 설치 / 취소.
MATH_INSTALL_TITLE = "수식 기능 설치 (약 214MB 다운로드)"
MATH_INSTALL_CANCELLED_MSG = "수식 기능 설치를 취소했어요."
MATH_INSTALL_FAILED_MSG = (
    "수식 기능을 받지 못했어요. 인터넷 연결을 확인한 뒤 다시 시도해 주세요."
)
MATH_INSTALL_HASH_MSG = "받은 파일이 손상됐어요. 다시 시도해 주세요."
MATH_REMOVE_MSG = "받아 둔 수식 파일을 지울까요?"
# 릴리스에 붙는 선택 구성 요소. 기본 설치 파일에는 없다.
# 해시와 크기는 installer/build_math_pack.py 가 만든 zip 과 같아야 한다.
MATH_PACK_NAME = f"PinCapture-Math-{APP_VERSION}.zip"
MATH_PACK_URL = (
    "https://github.com/ChamomileGrey/PinCapture/releases/download/"
    f"v{APP_VERSION}/{MATH_PACK_NAME}"
)
MATH_PACK_SHA256 = "26f920415c1e2d933cb5b1c2d9f84fa5fb9ca2125f35645f779df4a4bc28db2c"
MATH_PACK_BYTES = 213922566
MATH_ONNX_SHA256 = "30998d10c94ccff1ad8981df0c71048cb1f3eec7b1e515b809767f1f72aebe3b"
MATH_TOKENIZER_SHA256 = "96062655d94c21d39274328dbc82c1a487e66addb8425f5a7fd5b7dfb2421ec3"
MATH_PACK_ONNX = "models/formula/pp_formulanet_plus_s.onnx"
MATH_PACK_TOKENIZER = "models/formula/inference.yml"
MATH_FAILED_MSG = "수식을 읽지 못했어요. 수식만 보이게 다시 찍어 주세요."
MATH_EMPTY_MSG = "이미지에서 수식을 찾지 못했어요."
MATH_COPIED_MSG = "수식을 LaTeX로 복사했어요."
# (모드, 메뉴 이름). 핀 우클릭과 글자 복사 버튼의 우클릭이 같은 목록을 쓴다.
OCR_MODE_ACTIONS = (
    ("text", "글자"),
    ("table", "표 (엑셀)"),
    ("table-md", "표 (Markdown)"),
    ("math", "수식"),
)
_OCR_LANG_ORDER = ("ko-KR", "ko", "en-US", "en")
# PP-FormulaNet_plus-S 입력. L 계열만 768, 나머지는 384.
_MATH_CANVAS_L = 768
_MATH_CANVAS = 384
_MATH_ONNX_NAMES = (
    "pp_formulanet_plus_s.onnx",
    "pp_formulanet_plus_m.onnx",
    "pp_formulanet_plus_l.onnx",
    "model.onnx",
)
_MATH_TOKENIZER_NAMES = ("tokenizer.json", "inference.yml", "inference.yaml")
_math_cache = {"key": None, "session": None, "tokenizer": None}


class OcrResult:
    """recognize_image 의 결과. message 는 사용자에게 보여줄 한국어 문장."""

    def __init__(self, ok: bool, text: str, message: str):
        self.ok = ok
        self.text = text
        self.message = message


def _log_exc(tag: str, exc: BaseException, note: str = "") -> None:
    """예외를 로그에 남긴다. 설치본(EXE)은 콘솔이 없어서 여기가 아니면 오류가 사라진다.

    _setup_logging 이 stdout/stderr 를 ~/.pincapture/pincapture.log 로 복사한다.
    시험은 PINCAP_NO_LOG 라 파일은 건드리지 않고 시험 출력으로만 간다.
    """
    import traceback
    kind = "exe" if FROZEN else "py"
    head = f"[{tag}] {kind}"
    if note:
        head += f" {note}"
    print(f"{head}: {type(exc).__name__}: {exc}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)


def format_hotkey(combo: str) -> str:
    """pynput 표기 `<ctrl>+<alt>+x` 를 `Ctrl+Alt+X` 로."""
    names = {"ctrl": "Ctrl", "alt": "Alt", "shift": "Shift", "cmd": "Win"}
    parts = []
    for raw in (combo or "").split("+"):
        key = raw.strip().strip("<>").lower()
        if not key:
            continue
        parts.append(names.get(key, key.upper()))
    return "+".join(parts)


def iter_hotkey_bindings(hotkeys: dict):
    """(모드, 조합) 을 순서대로. 빈 조합과 이미 쓴 조합(먼저 등록된 모드가 이김)은 건너뜀."""
    seen = set()
    for mode, combo in hotkeys.items():
        combo = (combo or "").strip()
        if not combo:
            continue
        if combo in seen:
            print(f"[hotkey] '{combo}' 가 이미 쓰여 '{mode}' 는 건너뜀")
            continue
        seen.add(combo)
        yield mode, combo


def duplicate_hotkey(hotkeys: dict) -> str:
    """두 모드가 같은 비어 있지 않은 조합을 쓰면 그 조합을, 없으면 빈 문자열."""
    seen = set()
    for _mode, combo in hotkeys.items():
        combo = (combo or "").strip()
        if not combo:
            continue
        if combo in seen:
            return combo
        seen.add(combo)
    return ""


def _import_ocr_modules() -> dict:
    """Windows.Media.Ocr (PyWinRT). 없거나 Windows 가 아니면 ImportError 등으로 실패한다."""
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter
    return {
        "Language": Language,
        "BitmapPixelFormat": BitmapPixelFormat,
        "SoftwareBitmap": SoftwareBitmap,
        "OcrEngine": OcrEngine,
        "DataWriter": DataWriter,
    }


def _pick_ocr_engine(OcrEngine, Language):
    """한국어를 먼저, 그다음 영어. 둘 다 없으면 사용자 프로필 언어."""
    for tag in _OCR_LANG_ORDER:
        try:
            lang = Language(tag)
        except Exception:
            continue
        try:
            supported = bool(OcrEngine.is_language_supported(lang))
        except Exception:
            supported = False
        if not supported:
            continue
        try:
            engine = OcrEngine.try_create_from_language(lang)
        except Exception:
            engine = None
        if engine is not None:
            return engine
    langs = []
    for name in ("get_available_recognizer_languages", "try_get_available_languages"):
        fn = getattr(OcrEngine, name, None)
        if fn is None:
            continue
        try:
            langs = list(fn() or [])
        except Exception:
            langs = []
        if langs:
            break

    def tag_of(lang) -> str:
        return (getattr(lang, "language_tag", "") or "").lower()

    for prefixes in (("ko",), ("en",)):
        for lang in langs:
            t = tag_of(lang)
            if not any(t == p or t.startswith(p + "-") for p in prefixes):
                continue
            try:
                engine = OcrEngine.try_create_from_language(lang)
            except Exception:
                engine = None
            if engine is not None:
                return engine
    try:
        return OcrEngine.try_create_from_user_profile_languages()
    except Exception:
        return None


def _prepare_ocr_image(image: QImage) -> QImage:
    """Windows OCR 이 받는 크기(대략 40~2000px)로 맞춘다."""
    im = image
    w, h = im.width(), im.height()
    long_side = max(w, h)
    if long_side > 2000:
        scale = 2000 / long_side
        im = im.scaled(max(1, round(w * scale)), max(1, round(h * scale)),
                       Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
        w, h = im.width(), im.height()
    if w < 40 or h < 40:
        canvas = QImage(max(w, 40), max(h, 40), QImage.Format.Format_ARGB32)
        canvas.fill(QColor(255, 255, 255))
        painter = QPainter(canvas)
        painter.drawImage(0, 0, im)
        painter.end()
        im = canvas
    return im


def _rgba_bytes(image: QImage) -> "tuple[bytes, int, int]":
    im = image.convertToFormat(QImage.Format.Format_RGBA8888)
    w, h = im.width(), im.height()
    bpl = im.bytesPerLine()
    mv = memoryview(im.constBits())
    row = w * 4
    if bpl == row:
        return bytes(mv[:h * row]), w, h
    out = bytearray(h * row)
    for y in range(h):
        out[y * row:(y + 1) * row] = mv[y * bpl:y * bpl + row]
    return bytes(out), w, h


def _bitmap_from_rgba(data: bytes, w: int, h: int, mods: dict):
    writer = mods["DataWriter"]()
    try:
        writer.write_bytes(data)
    except TypeError:
        writer.write_bytes(list(data))
    buf = writer.detach_buffer()
    fmt = mods["BitmapPixelFormat"].RGBA8
    bitmap_cls = mods["SoftwareBitmap"]
    if hasattr(bitmap_cls, "create_copy_from_buffer"):
        return bitmap_cls.create_copy_from_buffer(buf, fmt, w, h)
    bitmap = bitmap_cls(fmt, w, h)
    bitmap.copy_from_buffer(buf)
    return bitmap


def _await_ocr(operation):
    """WinRT 비동기 인식이 끝날 때까지 기다린다.

    설치본에서 pywinrt 객체가 코루틴으로 안 붙으면, 빈 글자로 삼키지 않고 예외로 올린다.
    """
    if hasattr(operation, "__await__"):
        import asyncio
        try:
            return asyncio.run(operation)
        except RuntimeError as exc:
            _log_exc("ocr", exc, "비동기 인식 재시도")
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(operation)
            finally:
                loop.close()
    if hasattr(operation, "get"):
        return operation.get()
    name = type(operation).__name__
    if "IAsync" in name or name.startswith("_IAsync"):
        raise RuntimeError(f"OCR 비동기 결과를 끝내지 못함: {name}")
    return operation


class OcrBox:
    """OCR 단어·줄 하나의 글자와 픽셀 상자. 시험은 이 상자를 직접 만든다."""

    def __init__(self, text, x, y, w, h):
        self.text = "" if text is None else str(text)
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def cy(self) -> float:
        return self.y + self.h / 2.0


def _median(values) -> float:
    vals = sorted(float(v) for v in values)
    if not vals:
        return 0.0
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def _as_box(word) -> "OcrBox | None":
    if isinstance(word, OcrBox):
        box = word
    else:
        text = getattr(word, "text", "")
        try:
            box = OcrBox(text, word.x, word.y, word.w, word.h)
        except Exception:
            return None
    if not box.text.strip() or box.w <= 0 or box.h <= 0:
        return None
    return box


def _clean_boxes(words) -> list:
    out = []
    for word in words or []:
        box = _as_box(word)
        if box is not None:
            out.append(box)
    return out


def _is_hangul(ch: str) -> bool:
    if not ch:
        return False
    o = ord(ch)
    return (
        0xAC00 <= o <= 0xD7A3
        or 0x1100 <= o <= 0x11FF
        or 0x3130 <= o <= 0x318F
        or 0xA960 <= o <= 0xA97F
        or 0xD7B0 <= o <= 0xD7FF
    )


def _sentence_end(text: str) -> bool:
    t = (text or "").rstrip().rstrip("\"'”’)]}")
    if not t:
        return False
    if t.endswith("...") or t.endswith("…"):
        return True
    return t[-1] in ".?!。！？"


def _cluster_rows(words) -> list:
    """세로 위치가 가까운 단어를 한 줄로 모은다."""
    words = _clean_boxes(words)
    if not words:
        return []
    mh = _median(w.h for w in words) or 1.0
    words = sorted(words, key=lambda w: (w.cy, w.x))
    rows = []
    for word in words:
        if rows and abs(word.cy - _median(b.cy for b in rows[-1])) <= 0.55 * mh:
            rows[-1].append(word)
        else:
            rows.append([word])
    for row in rows:
        row.sort(key=lambda b: b.x)
    return rows


def _char_width(words) -> float:
    samples = []
    for word in words:
        samples.append(word.w / max(len(word.text.strip()), 1))
    return _median(samples) or 8.0


def _join_word_text(words) -> str:
    """한 줄·한 칸 안의 토큰. OCR 이 이미 띄어 쓴 단어라 공백으로 잇는다."""
    return " ".join(w.text.strip() for w in words if w.text.strip())


def _split_gaps(row, gap_thr: float) -> list:
    groups = [[row[0]]]
    for prev, word in zip(row, row[1:]):
        if word.x - prev.x2 > gap_thr:
            groups.append([word])
        else:
            groups[-1].append(word)
    return groups


def _box_from_words(words) -> OcrBox:
    x = min(w.x for w in words)
    y = min(w.y for w in words)
    x2 = max(w.x2 for w in words)
    y2 = max(w.y2 for w in words)
    return OcrBox(_join_word_text(words), x, y, max(1.0, x2 - x), max(1.0, y2 - y))


def lines_from_words(words, column_gap_factor: float = 3.0) -> list:
    """단어 상자를 읽기 순서의 줄로 만든다.

    한 줄 안에서 간격이 크게 벌어지면 다른 단으로 보고, 왼쪽 단부터 위에서 아래로 읽는다.
    모든 줄이 한 덩어리면 들여쓰기는 단으로 나누지 않는다.
    """
    rows = _cluster_rows(words)
    if not rows:
        return []
    flat = [w for row in rows for w in row]
    cw = _char_width(flat)
    mh = _median(w.h for w in flat) or 1.0
    gap_thr = max(column_gap_factor * cw, 1.1 * mh)
    per_row = []
    multi = False
    for row in rows:
        groups = _split_gaps(row, gap_thr)
        if len(groups) > 1:
            multi = True
        per_row.append([_box_from_words(g) for g in groups])
    lines = [seg for row in per_row for seg in row]
    if not multi or len(lines) < 2:
        lines.sort(key=lambda s: (s.y, s.x))
        return lines
    tol = max(2.0 * cw, mh)
    anchors = []
    for seg in sorted(lines, key=lambda s: s.x):
        if not anchors or seg.x - anchors[-1] > tol:
            anchors.append(seg.x)

    def col(seg) -> int:
        return min(range(len(anchors)), key=lambda i: abs(anchors[i] - seg.x))

    lines.sort(key=lambda s: (col(s), s.y, s.x))
    return lines


def _same_column(a: OcrBox, b: OcrBox, cw: float) -> bool:
    overlap = min(a.x2, b.x2) - max(a.x, b.x)
    narrower = min(a.w, b.w)
    if narrower > 0 and overlap >= 0.3 * narrower:
        return True
    return abs(a.x - b.x) <= 2.0 * cw


def _block_width(line: OcrBox, lines, cw: float) -> float:
    same = [ln.w for ln in lines if _same_column(line, ln, cw)]
    return max(same) if same else line.w


def _continues_paragraph(prev: OcrBox, nxt: OcrBox, lines, mh: float, cw: float) -> bool:
    """같은 문단의 다음 줄이면 True. 빈 줄·짧은 문장 끝·다른 단은 문단을 나눈다."""
    if not _same_column(prev, nxt, cw):
        return False
    gap = nxt.y - prev.y2
    if gap > 0.60 * mh:
        return False
    block = _block_width(prev, lines, cw)
    if prev.w < 0.82 * block and _sentence_end(prev.text):
        return False
    return True


def _join_wrapped(left: str, right: str, prev: OcrBox, col_right: float, cw: float) -> str:
    """한 문단 안에서 하드 랩된 두 줄을 잇는다.

    영어 줄끝 하이픈은 빼고, 오른쪽 끝에 붙은 한글 한 음절은 다음 음절과 붙인다.
    그 밖에는 띄어 쓴다. 한국어 워드랩(단어 경계)과 영어에 공통으로 맞춘 규칙이다.
    """
    left = left.rstrip()
    right = right.lstrip()
    if not left:
        return right
    if not right:
        return left
    flush = prev.x2 >= col_right - 1.2 * cw
    if flush and left.endswith("-") and not left.endswith("--"):
        if right[:1].isascii() and right[:1].islower():
            return left[:-1] + right
    if flush and _is_hangul(left[-1]) and _is_hangul(right[0]):
        last = left.split()[-1] if left.split() else left
        if len(last) == 1:
            return left + right
    return left + " " + right


def _join_line_group(group) -> str:
    cw = _char_width(group) or 8.0
    col_right = max(b.x2 for b in group)
    text = group[0].text.strip()
    for prev, nxt in zip(group, group[1:]):
        text = _join_wrapped(text, nxt.text.strip(), prev, col_right, cw)
    return text


def join_paragraphs(lines) -> str:
    """읽기 순서의 줄 상자를 문단 문자열로 만든다. 문단 사이는 빈 줄이다."""
    lines = [ln for ln in (_as_box(ln) for ln in (lines or [])) if ln is not None]
    if not lines:
        return ""
    mh = _median(ln.h for ln in lines) or 1.0
    cw = _char_width(lines) or 8.0
    paragraphs = []
    current = [lines[0]]

    def flush():
        if current:
            paragraphs.append(_join_line_group(current))
            current.clear()

    for prev, nxt in zip(lines, lines[1:]):
        if not _continues_paragraph(prev, nxt, lines, mh, cw):
            flush()
        current.append(nxt)
    flush()
    return "\n\n".join(p for p in paragraphs if p)


def reconstruct_paragraphs(words) -> str:
    """단어 상자에서 하드 랩을 이어 붙이고 문단 나눔은 남긴다."""
    return join_paragraphs(lines_from_words(words))


def table_from_words(words) -> list:
    """단어 상자를 표 칸(행 리스트)으로 맞춘다. 칸이 없으면 빈 리스트."""
    rows = _cluster_rows(words)
    if not rows:
        return []
    flat = [w for row in rows for w in row]
    cw = _char_width(flat) or 8.0
    mh = _median(w.h for w in flat) or 1.0
    gap_thr = max(1.6 * cw, 0.45 * mh)
    row_cells = []
    edges = []
    for row in rows:
        cells = _split_gaps(row, gap_thr)
        row_cells.append(cells)
        for cell in cells:
            edges.append(cell[0].x)
    edges.sort()
    tol = max(1.5 * cw, 4.0)
    clusters = []
    for x in edges:
        if not clusters or x - clusters[-1][-1] > tol:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    anchors = [sum(c) / len(c) for c in clusters] or [0.0]
    grid = []
    for cells in row_cells:
        out = [""] * len(anchors)
        for cell in cells:
            idx = min(range(len(anchors)), key=lambda i: abs(anchors[i] - cell[0].x))
            text = _join_word_text(cell)
            out[idx] = (out[idx] + " " + text).strip() if out[idx] else text
        grid.append(out)
    keep = [i for i in range(len(anchors)) if any(row[i].strip() for row in grid)]
    grid = [[row[i] for i in keep] for row in grid]
    return [row for row in grid if any(cell.strip() for cell in row)]


def _plain_cell(text, escape_bar: bool = False) -> str:
    s = " ".join(str(text).replace("\t", " ").replace("\r", " ").splitlines()).strip()
    if escape_bar:
        s = s.replace("|", "\\|")
    return s


def grid_to_tsv(grid) -> str:
    """엑셀에 붙여 넣으면 칸이 되는 탭 구분 텍스트."""
    return "\n".join("\t".join(_plain_cell(c) for c in row) for row in grid)


def grid_to_markdown(grid) -> str:
    """첫 줄을 헤더로 하는 Markdown 표."""
    if not grid:
        return ""
    width = max(len(row) for row in grid)

    def pad(row) -> str:
        vals = [_plain_cell(c, escape_bar=True) for c in row]
        vals.extend([""] * (width - len(vals)))
        return "| " + " | ".join(vals) + " |"

    lines = [pad(grid[0]), "| " + " | ".join(["---"] * width) + " |"]
    lines.extend(pad(row) for row in grid[1:])
    return "\n".join(lines)


def _words_from_ocr_result(result) -> list:
    """Windows.Media.Ocr 결과에서 단어 상자를 뽑는다. 상자가 없으면 빈 리스트."""
    lines = getattr(result, "lines", None)
    if not lines:
        return []
    words = []
    for line in lines:
        for word in getattr(line, "words", None) or []:
            rect = getattr(word, "bounding_rect", None)
            if rect is None:
                rect = getattr(word, "boundingRect", None)
            text = getattr(word, "text", "") or ""
            if rect is None or not str(text).strip():
                continue
            words.append(OcrBox(
                text,
                getattr(rect, "x", 0),
                getattr(rect, "y", 0),
                getattr(rect, "width", 0),
                getattr(rect, "height", 0),
            ))
    return words


def _math_search_dirs() -> list:
    """수식 모델 파일을 찾을 폴더. 받기 자체는 설치를 누른 뒤 install_math_pack 만 한다."""
    dirs = []
    env = os.environ.get("PINCAPTURE_MATH_DIR", "").strip()
    if env:
        root = Path(env)
        dirs.append(root)
        dirs.append(root / "models")
    dirs.append(CONFIG_DIR / "models" / "formula")
    dirs.append(CONFIG_DIR / "math" / "models")
    dirs.append(app_dir() / "math" / "models")
    seen = set()
    out = []
    for folder in dirs:
        key = str(folder)
        if key in seen:
            continue
        seen.add(key)
        out.append(folder)
    return out


def _math_addon_dirs() -> list:
    """pip --target 로 풀어 둔 수식 런타임. 기본 설치 파일에는 없다."""
    dirs = []
    env = os.environ.get("PINCAPTURE_MATH_DIR", "").strip()
    if env:
        root = Path(env)
        dirs.append(root)
        dirs.append(root.parent)
    dirs.append(CONFIG_DIR / "math")
    dirs.append(app_dir() / "math")
    seen = set()
    out = []
    for folder in dirs:
        key = str(folder)
        if key in seen:
            continue
        seen.add(key)
        out.append(folder)
    return out


def math_model_files():
    """(onnx 경로, 토크나이저 경로). 없으면 (None, None)."""
    for folder in _math_search_dirs():
        if not folder.is_dir():
            continue
        onnx = next((folder / name for name in _MATH_ONNX_NAMES if (folder / name).is_file()), None)
        tok = next((folder / name for name in _MATH_TOKENIZER_NAMES if (folder / name).is_file()), None)
        if onnx is not None and tok is not None:
            return onnx, tok
    return None, None


def _load_module(name: str):
    import importlib
    return importlib.import_module(name)


def _math_module_names(tokenizer_is_yaml: bool) -> list:
    # 이름을 붙여 만든다. 리터럴 import 가 되면 설치 파일이 수식 런타임을 끌고 들어온다.
    names = ["num" + "py", "onnx" + "runtime", "token" + "izers"]
    if tokenizer_is_yaml:
        names.append("ya" + "ml")
    return names


def _prepare_math_imports() -> None:
    for folder in _math_addon_dirs():
        pkg = folder / ("onnx" + "runtime")
        if not pkg.is_dir():
            continue
        path = str(folder)
        if path not in sys.path:
            sys.path.insert(0, path)
        if not (IS_WINDOWS and hasattr(os, "add_dll_directory")):
            continue
        dll_dirs = [pkg / "capi"]
        try:
            for sub in folder.iterdir():
                if sub.is_dir() and sub.name.endswith(".libs"):
                    dll_dirs.append(sub)
        except OSError:
            pass
        for dll_dir in dll_dirs:
            if not dll_dir.is_dir():
                continue
            try:
                os.add_dll_directory(str(dll_dir))
            except Exception:
                pass


def _math_modules_ready(tok_path: Path) -> bool:
    _prepare_math_imports()
    yaml = tok_path.suffix.lower() in {".yml", ".yaml"}
    for name in _math_module_names(yaml):
        try:
            _load_module(name)
        except Exception:
            return False
    return True


def math_status() -> str:
    """'ok' | 'no-model' | 'no-runtime'. 파일을 받거나 네트워크를 열지 않는다."""
    onnx, tok = math_model_files()
    if onnx is None or tok is None:
        return "no-model"
    if not _math_modules_ready(tok):
        return "no-runtime"
    return "ok"


def _find_key(node, key):
    if isinstance(node, dict):
        if key in node:
            return node[key]
        for value in node.values():
            found = _find_key(value, key)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_key(value, key)
            if found is not None:
                return found
    return None


def _load_tokenizer(path: Path):
    tokenizers = _load_module("token" + "izers")
    tokenizer_cls = tokenizers.Tokenizer
    if path.suffix.lower() == ".json":
        return tokenizer_cls.from_file(str(path))
    yaml = _load_module("ya" + "ml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    blob = _find_key(data, "fast_tokenizer_file")
    if blob is None:
        raise ValueError("tokenizer")
    raw = blob if isinstance(blob, str) else json.dumps(blob)
    tok = tokenizer_cls.from_str(raw)
    config = _find_key(data, "tokenizer_config_file")
    added = config.get("added_tokens_decoder") if isinstance(config, dict) else None
    if not isinstance(added, dict):
        return tok
    specials = []
    normals = []
    for idx, token in sorted(added.items(), key=lambda kv: int(kv[0])):
        if not isinstance(token, dict):
            continue
        content = token.get("content") or ""
        if not content or tok.token_to_id(content) is not None:
            continue
        piece = tokenizers.AddedToken(content, special=bool(token.get("special")))
        (specials if piece.special else normals).append(piece)
    if specials:
        tok.add_special_tokens(specials)
    if normals:
        tok.add_tokens(normals)
    return tok


def _formula_canvas_size(path: Path) -> int:
    stem = path.stem.lower().replace("-", "_")
    if stem.endswith("_l"):
        return _MATH_CANVAS_L
    return _MATH_CANVAS


def _qimage_rgb_array(image: QImage, np):
    im = image.convertToFormat(QImage.Format.Format_RGB888)
    w, h = im.width(), im.height()
    bpl = im.bytesPerLine()
    mv = memoryview(im.constBits())
    raw = bytes(mv[:h * bpl])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(h, bpl)
    return arr[:, :w * 3].reshape(h, w, 3).copy()


def _array_to_qimage(arr) -> QImage:
    h, w = arr.shape[:2]
    im = QImage(arr.tobytes(), w, h, w * 3, QImage.Format.Format_RGB888)
    return im.copy()


def _formula_input(image: QImage, np, size: int):
    """PP-FormulaNet 전처리. 여백을 자르고 정사각으로 맞춘 뒤 정규화한다. 네트워크 없음."""
    arr = _qimage_rgb_array(image, np)
    gray = arr.astype(np.float32).mean(axis=2)
    max_val = float(gray.max())
    min_val = float(gray.min())
    if max_val != min_val:
        stretched = (gray - min_val) / (max_val - min_val) * 255.0
        ys, xs = np.where(stretched < 200)
        if len(xs):
            arr = arr[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1]
    im = _array_to_qimage(np.ascontiguousarray(arr))
    im = im.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                   Qt.TransformationMode.SmoothTransformation)
    scaled = _qimage_rgb_array(im, np)
    canvas = np.full((size, size, 3), 255, dtype=np.uint8)
    h, w = scaled.shape[:2]
    y = max(0, (size - h) // 2)
    x = max(0, (size - w) // 2)
    canvas[y:y + h, x:x + w] = scaled[:min(h, size - y), :min(w, size - x)]
    img = canvas.astype(np.float32) / 255.0
    mean = np.array([0.7931, 0.7931, 0.7931], dtype=np.float32)
    std = np.array([0.1738, 0.1738, 0.1738], dtype=np.float32)
    img = (img - mean) / std
    channel = (0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]).astype(np.float32)
    nh = ((channel.shape[0] + 15) // 16) * 16
    nw = ((channel.shape[1] + 15) // 16) * 16
    if nh != channel.shape[0] or nw != channel.shape[1]:
        padded = np.full((nh, nw), 1.0, dtype=np.float32)
        padded[:channel.shape[0], :channel.shape[1]] = channel
        channel = padded
    return channel[np.newaxis, np.newaxis, :, :]


def _math_engine():
    onnx_path, tok_path = math_model_files()
    if onnx_path is None or tok_path is None:
        raise FileNotFoundError("math model")
    key = (str(onnx_path), onnx_path.stat().st_mtime_ns, str(tok_path), tok_path.stat().st_mtime_ns)
    if _math_cache["key"] == key and _math_cache["session"] is not None:
        return _math_cache["session"], _math_cache["tokenizer"]
    _prepare_math_imports()
    ort = _load_module("onnx" + "runtime")
    available = list(ort.get_available_providers())
    providers = ["CPUExecutionProvider"] if "CPUExecutionProvider" in available else available[:1]
    session = ort.InferenceSession(str(onnx_path), providers=providers)
    tokenizer = _load_tokenizer(tok_path)
    _math_cache.update(key=key, session=session, tokenizer=tokenizer, canvas=_formula_canvas_size(onnx_path))
    return session, tokenizer


def _tidy_latex(text: str) -> str:
    text = (text or "").replace("\u0120", " ").replace("Ġ", " ").strip()
    return " ".join(text.split())


def predict_latex(image: QImage) -> str:
    """로컬 ONNX 모델로 수식 이미지를 LaTeX 로 바꾼다. 여기서는 네트워크를 쓰지 않는다."""
    np = _load_module("num" + "py")
    session, tokenizer = _math_engine()
    size = _math_cache.get("canvas") or _MATH_CANVAS
    tensor = _formula_input(image, np, size)
    name = session.get_inputs()[0].name
    out = session.run(None, {name: tensor})
    arr = np.array(out[0])
    if arr.ndim == 3:
        arr = arr.argmax(axis=-1)
    if arr.ndim == 0:
        seq = [int(arr)]
    elif arr.ndim == 1:
        seq = [int(i) for i in arr.tolist()]
    else:
        seq = [int(i) for i in arr.reshape(arr.shape[0], -1)[0].tolist()]
    body = []
    for token_id in seq:
        if token_id in (1, 2):
            break
        if token_id == 0 and not body:
            continue
        body.append(token_id)
    if not body:
        return ""
    return _tidy_latex(tokenizer.decode(body, skip_special_tokens=True))


def _recognize_math(image: QImage) -> OcrResult:
    status = math_status()
    if status == "no-model":
        return OcrResult(False, "", MATH_MISSING_MSG)
    if status != "ok":
        return OcrResult(False, "", MATH_RUNTIME_MSG)
    try:
        latex = predict_latex(image)
    except Exception as e:
        _log_exc("math", e, "인식 실패")
        return OcrResult(False, "", MATH_FAILED_MSG)
    latex = (latex or "").strip()
    if not latex:
        return OcrResult(False, "", MATH_EMPTY_MSG)
    return OcrResult(True, latex, MATH_COPIED_MSG)


class MathInstallError(Exception):
    """수식 설치 실패. message 는 사용자에게 보여줄 한국어 문장."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class MathInstallCancelled(MathInstallError):
    def __init__(self):
        super().__init__(MATH_INSTALL_CANCELLED_MSG)


def _math_download_path() -> Path:
    return CONFIG_DIR / "downloads" / (MATH_PACK_NAME + ".partial")


def _sha256_file(path: Path, cancelled=None, progress=None) -> str:
    import hashlib
    digest = hashlib.sha256()
    done = 0
    total = path.stat().st_size
    with path.open("rb") as handle:
        while True:
            if cancelled and cancelled():
                raise MathInstallCancelled()
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            done += len(block)
            if progress:
                progress(done, total, "check")
    return digest.hexdigest()


def _response_header(resp, name: str):
    headers = getattr(resp, "headers", None)
    if headers is None:
        return None
    getter = getattr(headers, "get", None)
    if getter is None:
        return None
    return getter(name) or getter(name.lower())


def _response_status(resp) -> int:
    status = getattr(resp, "status", None)
    if status:
        return int(status)
    getcode = getattr(resp, "getcode", None)
    if getcode:
        return int(getcode())
    return 0


def _payload_total(resp, status: int, start: int) -> int:
    if status == 206:
        content_range = str(_response_header(resp, "Content-Range") or "")
        if "/" in content_range:
            total = content_range.rsplit("/", 1)[-1]
            if total.isdigit():
                return int(total)
    length = _response_header(resp, "Content-Length")
    if length is not None and str(length).isdigit():
        size = int(length)
        return start + size if status == 206 else size
    return 0


def _open_math_url(url: str, start: int, opener=None):
    """Range 를 유지한 채 연다. 시험은 opener(request, timeout=) 를 넘긴다."""
    import urllib.error
    import urllib.request
    headers = {"User-Agent": f"PinCapture/{APP_VERSION}"}
    if start > 0:
        headers["Range"] = f"bytes={start}-"
    request = urllib.request.Request(url, headers=headers)
    open_url = opener or urllib.request.urlopen
    try:
        return open_url(request, timeout=120)
    except urllib.error.HTTPError:
        raise
    except Exception as exc:
        raise MathInstallError(MATH_INSTALL_FAILED_MSG) from exc


def fetch_math_pack(dest: Path, *, url: str | None = None, expected_sha: str | None = None,
                    opener=None, progress=None, cancelled=None, chunk: int = 256 * 1024) -> None:
    """구성 요소 zip 을 dest 에 받는다. 이어받기와 SHA-256 확인을 한다. 풀지는 않는다."""
    import urllib.error
    url = url or MATH_PACK_URL
    expected = (expected_sha if expected_sha is not None else MATH_PACK_SHA256).lower()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if MATH_PACK_BYTES and dest.is_file():
        size = dest.stat().st_size
        if size == MATH_PACK_BYTES:
            if _sha256_file(dest, cancelled, progress) == expected:
                if progress:
                    progress(size, size, "check")
                return
            dest.unlink()
        elif size > MATH_PACK_BYTES:
            dest.unlink()
    start = dest.stat().st_size if dest.is_file() else 0
    try:
        resp = _open_math_url(url, start, opener)
    except urllib.error.HTTPError as exc:
        if exc.code == 416 and dest.is_file() and _sha256_file(dest, cancelled, progress) == expected:
            return
        if exc.code == 416 and dest.is_file():
            dest.unlink(missing_ok=True)
        raise MathInstallError(MATH_INSTALL_FAILED_MSG) from exc
    status = _response_status(resp)
    if status == 200 and start:
        dest.write_bytes(b"")
        start = 0
    elif status not in (200, 206):
        close = getattr(resp, "close", None)
        if close:
            close()
        raise MathInstallError(MATH_INSTALL_FAILED_MSG)
    total = _payload_total(resp, status, start)
    try:
        with dest.open("ab" if start else "wb") as out:
            done = start
            while True:
                if cancelled and cancelled():
                    raise MathInstallCancelled()
                block = resp.read(chunk)
                if not block:
                    break
                out.write(block)
                out.flush()
                done += len(block)
                if progress:
                    progress(done, total, "download")
    except MathInstallCancelled:
        raise
    except MathInstallError:
        raise
    except Exception as exc:
        raise MathInstallError(MATH_INSTALL_FAILED_MSG) from exc
    finally:
        close = getattr(resp, "close", None)
        if close:
            close()
    digest = _sha256_file(dest, cancelled, progress)
    if digest != expected:
        dest.unlink(missing_ok=True)
        raise MathInstallError(MATH_INSTALL_HASH_MSG)


def _safe_math_member(name: str) -> bool:
    name = (name or "").replace("\\", "/").lstrip("/")
    parts = [part for part in name.split("/") if part not in ("", ".")]
    if not parts or ".." in parts:
        return False
    prefix = parts[0]
    if prefix == "math":
        return len(parts) >= 2
    return prefix == "models" and len(parts) >= 3 and parts[1] == "formula"


def _zip_member_sha256(archive, name: str) -> str:
    import hashlib
    digest = hashlib.sha256()
    with archive.open(name) as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def extract_math_pack(zip_path: Path, *, onnx_sha: str | None = None, tok_sha: str | None = None) -> None:
    """검증된 zip 을 ~/.pincapture 아래에 푼다. 경로 탈출은 받지 않는다."""
    import shutil
    import zipfile
    expected_onnx = (onnx_sha if onnx_sha is not None else MATH_ONNX_SHA256).lower()
    expected_tok = (tok_sha if tok_sha is not None else MATH_TOKENIZER_SHA256).lower()
    with zipfile.ZipFile(zip_path) as archive:
        names = [info.filename.replace("\\", "/") for info in archive.infolist()]
        if MATH_PACK_ONNX not in names or MATH_PACK_TOKENIZER not in names:
            raise MathInstallError(MATH_INSTALL_HASH_MSG)
        if _zip_member_sha256(archive, MATH_PACK_ONNX) != expected_onnx:
            raise MathInstallError(MATH_INSTALL_HASH_MSG)
        if _zip_member_sha256(archive, MATH_PACK_TOKENIZER) != expected_tok:
            raise MathInstallError(MATH_INSTALL_HASH_MSG)
        root = CONFIG_DIR.resolve()
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            if name.endswith("/") or not _safe_math_member(name):
                continue
            target = (CONFIG_DIR / name).resolve()
            if target != root and root not in target.parents:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    _math_cache.update(key=None, session=None, tokenizer=None)


def install_math_pack(progress=None, cancelled=None, opener=None, url: str | None = None) -> None:
    """받아 확인한 뒤 푼다. 끝나면 받은 zip 은 지운다. 설치를 누르기 전에는 호출하지 않는다."""
    dest = _math_download_path()
    fetch_math_pack(dest, url=url, opener=opener, progress=progress, cancelled=cancelled)
    if cancelled and cancelled():
        raise MathInstallCancelled()
    if progress:
        progress(1, 1, "extract")
    extract_math_pack(dest)
    dest.unlink(missing_ok=True)


def math_component_present() -> bool:
    """모델이나 실행 구성 요소 폴더가 있으면 True. 받지는 않는다."""
    onnx, tok = math_model_files()
    if onnx is not None or tok is not None:
        return True
    folder = CONFIG_DIR / "math"
    if not folder.is_dir():
        return False
    try:
        next(folder.iterdir())
    except StopIteration:
        return False
    except OSError:
        return False
    return True


def remove_math_component() -> None:
    """받아 둔 수식 모델, 실행 구성 요소, 이어받기 파일을 지운다."""
    import shutil
    for rel in ("math", Path("models") / "formula", "downloads"):
        target = CONFIG_DIR / rel
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink(missing_ok=True)
    _math_cache.update(key=None, session=None, tokenizer=None)


def build_math_install_box(parent=None) -> QMessageBox:
    """설치 / 취소. exec 는 confirm_math_install 만 한다."""
    box = QMessageBox(parent)
    box.setWindowTitle(APP_NAME)
    box.setIcon(QMessageBox.Icon.Question)
    box.setText(MATH_INSTALL_TITLE)
    install = box.addButton("설치", QMessageBox.ButtonRole.AcceptRole)
    cancel = box.addButton("취소", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(install)
    box._install_btn = install
    box._cancel_btn = cancel
    return box


def confirm_math_install(parent=None) -> bool:
    """설치를 누르면 True. 파일을 받지는 않는다."""
    box = build_math_install_box(parent)
    box.exec()
    return box.clickedButton() is box._install_btn


def confirm_math_remove(parent=None) -> bool:
    box = QMessageBox(parent)
    box.setWindowTitle(APP_NAME)
    box.setIcon(QMessageBox.Icon.Question)
    box.setText(MATH_REMOVE_MSG)
    remove = box.addButton("제거", QMessageBox.ButtonRole.AcceptRole)
    cancel = box.addButton("취소", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(cancel)
    box.exec()
    return box.clickedButton() is remove


class _MathInstallThread(QThread):
    progressed = Signal(int, int, str)
    failed = Signal(str)
    succeeded = Signal()

    def __init__(self):
        super().__init__()
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            install_math_pack(
                progress=lambda done, total, phase: self.progressed.emit(int(done), int(total), str(phase)),
                cancelled=lambda: self._cancel,
            )
        except MathInstallCancelled:
            self.failed.emit(MATH_INSTALL_CANCELLED_MSG)
        except MathInstallError as exc:
            self.failed.emit(exc.message)
        except Exception as exc:
            _log_exc("math", exc, "설치 실패")
            self.failed.emit(MATH_INSTALL_FAILED_MSG)
        else:
            self.succeeded.emit()


def _run_math_install_dialog(parent=None) -> None:
    """진행 창을 띄우고 받는다. 취소·실패는 예외로 알린다."""
    dialog = QProgressDialog("수식 기능을 받고 있어요.", "취소", 0, 0, parent)
    dialog.setWindowTitle(APP_NAME)
    dialog.setMinimumDuration(0)
    dialog.setAutoClose(False)
    dialog.setAutoReset(False)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    worker = _MathInstallThread()
    outcome = {"err": None}
    finished = {"v": False}
    loop = QEventLoop()

    def on_progress(done: int, total: int, phase: str):
        if phase == "check":
            dialog.setLabelText("받은 파일을 확인하고 있어요.")
        elif phase == "extract":
            dialog.setLabelText("수식 기능을 준비하고 있어요.")
        elif total > 0:
            dialog.setMaximum(total)
            dialog.setValue(min(done, total))
            dialog.setLabelText(
                f"수식 기능을 받고 있어요. ({done / 1048576:.0f} / {total / 1048576:.0f}MB)")
        else:
            dialog.setLabelText("수식 기능을 받고 있어요.")

    def stop(err: str):
        if finished["v"]:
            return
        finished["v"] = True
        outcome["err"] = err
        loop.quit()

    dialog.canceled.connect(lambda: None if finished["v"] else worker.cancel())
    worker.progressed.connect(on_progress)
    worker.succeeded.connect(lambda: stop(""))
    worker.failed.connect(stop)
    worker.start()
    dialog.show()
    loop.exec()
    dialog.close()
    worker.wait(5000)
    if outcome["err"]:
        if outcome["err"] == MATH_INSTALL_CANCELLED_MSG:
            raise MathInstallCancelled()
        raise MathInstallError(outcome["err"])


def ensure_math_installed(parent=None) -> tuple:
    """이미 쓸 수 있으면 바로 True. 아니면 설치를 물어 보고, 눌렀을 때만 받는다.

    반환은 (성공 여부, 안내 문장). 실패 안내 창은 여기서 띄운다.
    """
    if math_status() == "ok":
        return True, ""
    if not confirm_math_install(parent):
        return False, MATH_INSTALL_CANCELLED_MSG
    try:
        _run_math_install_dialog(parent)
    except MathInstallCancelled:
        return False, MATH_INSTALL_CANCELLED_MSG
    except MathInstallError as exc:
        QMessageBox.warning(parent, APP_NAME, exc.message)
        return False, exc.message
    return True, ""


def build_ocr_mode_menu(parent=None):
    """글자 / 표 / 수식. 핀 메뉴와 메인 창 우클릭이 함께 쓴다."""
    menu = QMenu(parent)
    acts = {}
    for mode, label in OCR_MODE_ACTIONS:
        acts[mode] = menu.addAction(label)
    return menu, acts


def recognize_image(image: QImage, mode: str = "text") -> OcrResult:
    """글자·표·수식을 읽는다. 글자와 표는 Windows.Media.Ocr, 수식은 로컬 모델.

    모듈·언어 팩·수식 모델이 없으면 안내 문장을 돌려준다. 화면 보호를 우회하지 않는다.
    이 함수는 파일을 받지 않는다. 받기는 사용자가 설치를 누른 뒤 ensure_math_installed 만 한다.
    글자 모드는 하드 랩된 줄을 문단으로 잇는다.
    """
    if image is None or (hasattr(image, "isNull") and image.isNull()):
        return OcrResult(False, "", "이미지가 없어요.")
    mode = (mode or "text").strip().lower()
    if mode == "math":
        return _recognize_math(image)
    try:
        mods = _import_ocr_modules()
    except Exception as e:
        _log_exc("ocr", e, "모듈을 불러오지 못함")
        return OcrResult(False, "", OCR_UNAVAILABLE_MSG)
    try:
        engine = _pick_ocr_engine(mods["OcrEngine"], mods["Language"])
    except Exception as e:
        _log_exc("ocr", e, "엔진 준비 실패")
        return OcrResult(False, "", OCR_NO_LANGUAGE_MSG)
    if engine is None:
        return OcrResult(False, "", OCR_NO_LANGUAGE_MSG)
    try:
        prepared = _prepare_ocr_image(image)
        data, w, h = _rgba_bytes(prepared)
        bitmap = _bitmap_from_rgba(data, w, h, mods)
        result = _await_ocr(engine.recognize_async(bitmap))
    except Exception as e:
        _log_exc("ocr", e, "인식 실패")
        return OcrResult(False, "", OCR_FAILED_MSG)
    raw = (getattr(result, "text", "") or "").strip()
    try:
        words = _words_from_ocr_result(result)
    except Exception as e:
        _log_exc("ocr", e, "단어 상자 해석 실패")
        words = []
    if mode in ("table", "table-md"):
        try:
            grid = table_from_words(words) if words else []
        except Exception as e:
            _log_exc("ocr", e, "표 맞추기 실패")
            grid = []
        if not grid:
            return OcrResult(False, "", OCR_TABLE_EMPTY_MSG)
        if mode == "table-md":
            return OcrResult(True, grid_to_markdown(grid), OCR_TABLE_MD_MSG)
        return OcrResult(True, grid_to_tsv(grid), OCR_TABLE_COPIED_MSG)
    text = raw
    if words:
        try:
            joined = reconstruct_paragraphs(words)
        except Exception as e:
            _log_exc("ocr", e, "문단 맞추기 실패")
            joined = ""
        if joined:
            text = joined
    if not text:
        return OcrResult(False, "", OCR_EMPTY_MSG)
    return OcrResult(True, text, OCR_COPIED_MSG)


def _flush_paint() -> None:
    """읽는 중 토스트가 동기 인식 전에 그려지게 한다. 그 사이 클릭은 다시 받지 않는다."""
    app = QApplication.instance()
    if app is None:
        return
    app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)


def run_ocr(image: QImage, mode: str, announce) -> OcrResult:
    """글자·표·수식을 읽고 announce(문장, 밀리초) 로 진행과 결과를 알린다.

    글자 모드는 recognize_image(image) 한 인자로 부른다. 기존 시험의 가짜 함수와 맞추기 위해서다.
    두 번째 인자가 0 이면 토스트를 자동으로 닫지 않는다 (읽는 중).
    """
    announce(OCR_BUSY_MSG, 0)
    _flush_paint()
    try:
        if (mode or "text") == "text":
            result = recognize_image(image)
        else:
            result = recognize_image(image, mode)
    except Exception as exc:
        _log_exc("ocr", exc, "인식 중 예외")
        result = OcrResult(False, "", OCR_FAILED_MSG)
    if not isinstance(result, OcrResult):
        _log_exc("ocr", TypeError(type(result).__name__), "인식 결과")
        result = OcrResult(False, "", OCR_FAILED_MSG)
    if result.ok and result.text:
        try:
            QApplication.clipboard().setText(result.text)
        except Exception as exc:
            _log_exc("ocr", exc, "클립보드 복사 실패")
            result = OcrResult(False, result.text, OCR_FAILED_MSG)
    announce(result.message, 1800 if result.ok else 4200)
    return result


def _set_win32_click_through(hwnd: int, on: bool) -> None:
    """WS_EX_TRANSPARENT (+ LAYERED when on). 끄면 TRANSPARENT 만 뺀다 (투명도용 LAYERED 는 유지)."""
    if not IS_WINDOWS or not hwnd:
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        # windll 의 전역 프로토타입은 건드리지 않는다 (다른 호출과 겹치지 않게).
        get_name = "GetWindowLongPtrW" if hasattr(user32, "GetWindowLongPtrW") else "GetWindowLongW"
        set_name = "SetWindowLongPtrW" if hasattr(user32, "SetWindowLongPtrW") else "SetWindowLongW"
        get_long = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_int)((get_name, user32))
        set_long = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t)((set_name, user32))
        style = int(get_long(hwnd, GWL_EXSTYLE) or 0)
        if on:
            style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        else:
            style &= ~WS_EX_TRANSPARENT
        set_long(hwnd, GWL_EXSTYLE, style)
    except Exception as e:
        print(f"[pin] 클릭 통과 스타일 변경 실패: {e}")


class PinToast(QWidget):
    """커서·핀·메인 창 옆에 잠깐 떴다 사라지는 안내.

    트레이 풍선과 달리 알림 끄기나 집중 지원과 상관없이 보인다.
    메인 창이 숨겨져 있어도 따로 뜬다. msec 가 0 이하면 다음 안내가 바꿀 때까지 둔다.
    """

    def __init__(self, text: str, anchor: "QWidget | None" = None, msec: int = 1800):
        super().__init__(None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.Tool
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(360)
        self.label.setStyleSheet(
            "background:#1F2430; color:white; padding:8px 12px; border-radius:8px; font-size:12px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.label)
        self.adjustSize()
        self._place(anchor)
        self.show()
        self.raise_()
        if int(msec) > 0:
            QTimer.singleShot(max(400, int(msec)), self.close)

    def _place(self, anchor: "QWidget | None") -> None:
        """보이는 창이 있으면 그 위, 없으면 커서 옆. 어느 쪽이든 화면 안에 둔다."""
        frame = None
        if anchor is not None:
            try:
                if anchor.isVisible():
                    frame = anchor.frameGeometry()
            except RuntimeError:
                frame = None
        if frame is not None:
            x = frame.center().x() - self.width() // 2
            y = frame.top() - self.height() - 8
            center = frame.center()
        else:
            center = QCursor.pos()
            x = center.x() + 12
            y = center.y() + 16
        screen = QGuiApplication.screenAt(center) or QGuiApplication.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            x = min(max(x, bounds.left() + 4), max(bounds.left() + 4, bounds.right() - self.width() - 4))
            y = min(max(y, bounds.top() + 4), max(bounds.top() + 4, bounds.bottom() - self.height() - 4))
        self.move(int(x), int(y))


def recent_pin_dir() -> Path:
    """닫은 핀 PNG 를 두는 임시 폴더. 시험은 PINCAP_RECENT_DIR 로 격리한다."""
    override = os.environ.get("PINCAP_RECENT_DIR")
    return Path(override) if override else Path(tempfile.gettempdir()) / "pincapture-recent-pins"


class RecentPinStore:
    """닫은 핀을 최신 순으로 최대 N개. 메모리의 QImage 와 임시 폴더의 PNG 를 함께 둔다."""

    def __init__(self, limit: int = 10, directory: "Path | None" = None):
        self.directory = Path(directory) if directory is not None else recent_pin_dir()
        self.limit = _clamp_recent_limit(limit)
        self.items: list = []
        self._seq = 0
        self._load()

    def count(self) -> int:
        return len(self.items)

    def set_limit(self, limit: int) -> None:
        self.limit = _clamp_recent_limit(limit)
        self._trim()

    def remember(self, pin: "PinWindow") -> None:
        img = getattr(pin, "_img", None)
        if img is None or img.isNull():
            return
        png = meta = None
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            self._seq += 1
            stamp = f"{datetime.datetime.now():%Y%m%d_%H%M%S_%f}_{self._seq:04d}"
            png = self.directory / f"{stamp}.png"
            meta = self.directory / f"{stamp}.json"
            if not img.save(str(png), "PNG"):
                print(f"[recent] PNG 저장 실패: {png}")
                return
            info = {
                "x": int(pin.x()),
                "y": int(pin.y()),
                "scale": float(pin._scale),
                "opacity": int(pin._opacity),
                "dpr": float(pin._dpr),
            }
            meta.write_text(json.dumps(info), encoding="utf-8")
        except Exception as e:
            print(f"[recent] 보관 실패: {e}")
            for path in (png, meta):
                if path is not None:
                    try:
                        path.unlink(missing_ok=True)
                    except Exception:
                        pass
            return
        self.items.insert(0, {"id": stamp, "png": png, "meta": meta, "image": img.copy(), **info})
        self._trim()

    def pop_latest(self) -> "dict | None":
        while self.items:
            item = self.items.pop(0)
            img = item.get("image")
            if img is None or (hasattr(img, "isNull") and img.isNull()):
                loaded = QImage(str(item.get("png", "")))
                img = loaded if not loaded.isNull() else None
            self._unlink(item)
            if img is not None and not img.isNull():
                item["image"] = img
                return item
        return None

    def _trim(self) -> None:
        while len(self.items) > self.limit:
            self._unlink(self.items.pop())

    def _unlink(self, item: dict) -> None:
        for key in ("png", "meta"):
            path = item.get(key)
            if not path:
                continue
            try:
                Path(path).unlink(missing_ok=True)
            except Exception:
                pass

    def _load(self) -> None:
        try:
            if not self.directory.is_dir():
                return
            metas = sorted(self.directory.glob("*.json"), reverse=True)
        except Exception as e:
            print(f"[recent] 목록 읽기 실패: {e}")
            return
        for meta in metas:
            if len(self.items) >= self.limit:
                self._unlink({"png": meta.with_suffix(".png"), "meta": meta})
                continue
            try:
                info = json.loads(meta.read_text(encoding="utf-8"))
                png = meta.with_suffix(".png")
                img = QImage(str(png))
                if img.isNull():
                    self._unlink({"png": png, "meta": meta})
                    continue
                self.items.append({
                    "id": meta.stem,
                    "png": png,
                    "meta": meta,
                    "image": img,
                    "x": int(info.get("x", 0)),
                    "y": int(info.get("y", 0)),
                    "scale": float(info.get("scale", 1.0)),
                    "opacity": int(info.get("opacity", 100)),
                    "dpr": float(info.get("dpr", 1.0)),
                })
            except Exception as e:
                print(f"[recent] {meta.name} 읽기 실패: {e}")


MARK_KINDS = ("arrow", "box", "highlight", "mosaic", "pen")
MARK_TOOL_LABELS = (
    ("arrow", "화살표"),
    ("box", "네모"),
    ("highlight", "형광펜"),
    ("mosaic", "모자이크"),
    ("pen", "낙서"),
)
MARK_COLORS = (
    ("빨강", "#E23B3B"),
    ("노랑", "#F5C518"),
    ("파랑", "#2F6BFF"),
    ("검정", "#222222"),
)
MARK_WIDTHS = (2, 4, 8)          # 논리 픽셀 프리셋. 이미지에는 dpr 을 곱해 저장
MARK_WIDTH_LABELS = ((2, "얇게", "width_thin"), (4, "보통", "width_mid"), (8, "굵게", "width_thick"))
MARK_TOOL_ICONS = {
    "arrow": "mark_arrow",
    "box": "mark_box",
    "highlight": "mark_highlight",
    "mosaic": "mark_mosaic",
    "pen": "mark_pen",
}
MARK_BAR_HIT = 34                 # 도구·두께·실행 취소 버튼. 예전 글자 버튼보다 조금 큼
MARK_BAR_SWATCH = 28
MARK_BAR_ICON = 20
MARKUP_BAR_GAP = 8                # 핀과 도구 패널 사이
MARKUP_BAR_MARGIN = 4             # 화면 가장자리에서 띄우는 여백
_MARK_BAR_SHADOW = 10             # 패널 밖 그림자. 창 크기에는 포함되고 버튼은 패널 안
_MARK_BAR_PAD_X = 10
_MARK_BAR_PAD_Y = 6
HIGHLIGHT_ALPHA = 110
PIN_TOOLTIP = "드래그로 옮기고, 휠로 크기를 조절해요. Ctrl+휠은 투명도, 우클릭은 메뉴, 더블클릭이나 Esc는 닫기예요."
PIN_EDIT_TOOLTIP = (
    "드래그로 표시를 그려요. 낙서는 마우스를 따라 그려요. "
    "Shift는 가로·세로·45° 직선이에요. "
    "Ctrl+Z 는 실행 취소, Ctrl+Y 는 다시 실행, Esc 는 표시를 끝내요."
)


def mark_width_px(preset: int, dpr: float) -> int:
    """두께 프리셋(논리 px)을 이미지 픽셀로. 150% 는 반올림한 배율을 곱한다."""
    try:
        preset_i = int(preset)
    except (TypeError, ValueError):
        preset_i = 4
    if preset_i not in MARK_WIDTHS:
        preset_i = min(MARK_WIDTHS, key=lambda w: abs(w - preset_i))
    scale = max(1, int(round(float(dpr) if dpr else 1)))
    return max(1, preset_i * scale)


def mosaic_block_px(preset: int, dpr: float) -> int:
    """모자이크 칸 크기(이미지 픽셀). 두꺼운 프리셋일수록 칸이 커진다."""
    try:
        preset_i = int(preset)
    except (TypeError, ValueError):
        preset_i = 4
    scale = max(1, int(round(float(dpr) if dpr else 1)))
    return max(4, (4 + preset_i) * scale)


def image_signature(img: QImage) -> tuple:
    """같은 그림인지 보는 지문. 모든 픽셀과 알파를 포함한다.

    파일을 다시 읽으면 cacheKey 가 달라진다. 일부 칸만 보면 같은 크기의
    다른 캡처가 같은 핀으로 붙어서, 낙서와 글자 복사가 다른 그림에 적용된다.
    """
    if img is None or img.isNull():
        return ()
    conv = img.convertToFormat(QImage.Format.Format_ARGB32)
    w, h = conv.width(), conv.height()
    if w < 1 or h < 1:
        return ()
    raw = bytes(conv.constBits())
    nbytes = int(conv.sizeInBytes())
    if 0 < nbytes < len(raw):
        raw = raw[:nbytes]
    return (w, h, hashlib.sha256(raw).hexdigest())


class Mark:
    """핀 이미지 픽셀 좌표의 표시 하나. 핀을 확대해도 같은 자리에 남는다.

    낙서(pen)는 두 점이 아니라 points 를 따라 그린다.
    """

    def __init__(self, kind: str, x1: int, y1: int, x2: int, y2: int, color: str, width_px: int,
                 points=None):
        self.kind = kind if kind in MARK_KINDS else "arrow"
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.color = str(color)
        self.width_px = max(1, int(width_px))
        if points:
            self.points = [(int(x), int(y)) for x, y in points]
        elif self.kind == "pen":
            self.points = [(self.x1, self.y1), (self.x2, self.y2)]
        else:
            self.points = None

    def rect(self) -> QRect:
        return QRect(QPoint(self.x1, self.y1), QPoint(self.x2, self.y2)).normalized()


def _mark_is_real(mark: Mark) -> bool:
    if mark.kind == "pen":
        return bool(mark.points)
    return abs(mark.x2 - mark.x1) >= 2 or abs(mark.y2 - mark.y1) >= 2


def compose_marks(image: QImage, marks) -> QImage:
    """원본을 바꾸지 않고 표시를 합성한 이미지를 돌려준다. marks 가 비면 형식만 맞춘 복사본."""
    out = image.convertToFormat(QImage.Format.Format_ARGB32).copy()
    for mark in marks or ():
        if mark.kind == "mosaic":
            _apply_mosaic(out, mark)
            continue
        painter = QPainter(out)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        _paint_vector_mark(painter, mark)
        painter.end()
    return out


def _apply_mosaic(image: QImage, mark: Mark) -> None:
    rect = mark.rect().intersected(image.rect())
    if rect.width() < 2 or rect.height() < 2:
        return
    block = max(4, int(mark.width_px))
    chunk = image.copy(rect)
    small_w = max(1, rect.width() // block)
    small_h = max(1, rect.height() // block)
    small = chunk.scaled(small_w, small_h, Qt.AspectRatioMode.IgnoreAspectRatio,
                         Qt.TransformationMode.FastTransformation)
    big = small.scaled(rect.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                       Qt.TransformationMode.FastTransformation)
    painter = QPainter(image)
    painter.drawImage(rect.topLeft(), big)
    painter.end()


def _paint_pen(p: QPainter, mark: Mark) -> None:
    pts = mark.points or [(mark.x1, mark.y1)]
    color = QColor(mark.color)
    if not color.isValid():
        color = QColor(MARK_COLORS[0][1])
    width = max(1, int(mark.width_px))
    if len(pts) <= 1 or all(pt == pts[0] for pt in pts):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        radius = width / 2.0
        p.drawEllipse(QPointF(pts[0][0], pts[0][1]), radius, radius)
        return
    pen = QPen(color)
    pen.setWidth(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath()
    path.moveTo(float(pts[0][0]), float(pts[0][1]))
    for x, y in pts[1:]:
        path.lineTo(float(x), float(y))
    p.drawPath(path)


def _paint_vector_mark(p: QPainter, mark: Mark) -> None:
    if mark.kind == "pen":
        _paint_pen(p, mark)
        return
    color = QColor(mark.color)
    if mark.kind == "highlight":
        rect = mark.rect()
        if rect.width() < 1 or rect.height() < 1:
            return
        color.setAlpha(HIGHLIGHT_ALPHA)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawRect(rect)
        return
    if mark.kind == "box":
        rect = mark.rect()
        if rect.width() < 1 and rect.height() < 1:
            return
        pen = QPen(color)
        pen.setWidth(max(1, mark.width_px))
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(rect)
        return
    if mark.kind == "arrow":
        _paint_arrow(p, mark)


def _paint_arrow(p: QPainter, mark: Mark) -> None:
    a = QPointF(mark.x1, mark.y1)
    b = QPointF(mark.x2, mark.y2)
    dx = b.x() - a.x()
    dy = b.y() - a.y()
    length = math.hypot(dx, dy)
    if length < 1:
        return
    color = QColor(mark.color)
    pen = QPen(color)
    pen.setWidth(max(1, mark.width_px))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(a, b)
    head = max(mark.width_px * 3.0, 8.0)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base = QPointF(b.x() - ux * head, b.y() - uy * head)
    left = QPointF(base.x() + px * head * 0.45, base.y() + py * head * 0.45)
    right = QPointF(base.x() - px * head * 0.45, base.y() - py * head * 0.45)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(color)
    p.drawPolygon(QPolygonF([b, left, right]))


def _edit_key_action(e) -> str:
    """편집 중 키. 'undo' | 'redo' | 'end' | ''."""
    if e.key() == Qt.Key.Key_Escape:
        return "end"
    mods = e.modifiers()
    ctrl = bool(mods & Qt.KeyboardModifier.ControlModifier)
    shift = bool(mods & Qt.KeyboardModifier.ShiftModifier)
    if e.matches(QKeySequence.StandardKey.Undo) or (ctrl and not shift and e.key() == Qt.Key.Key_Z):
        return "undo"
    if (e.matches(QKeySequence.StandardKey.Redo) or (ctrl and e.key() == Qt.Key.Key_Y)
            or (ctrl and shift and e.key() == Qt.Key.Key_Z)):
        return "redo"
    return ""


def _marker_ink(color: str) -> str:
    """밝은 견본 위의 + 는 검게, 어두운 견본 위는 희게."""
    q = QColor(color)
    if not q.isValid():
        return "#222222"
    bright = (q.red() * 299 + q.green() * 587 + q.blue() * 114) // 1000
    return "#222222" if bright >= 160 else "#FFFFFF"


def _swatch_border(color: str, on: bool) -> str:
    """고른 견본은 파란 테두리. 파랑 견본만 더 진한 파랑이라 테두리가 묻히지 않는다."""
    if not on:
        return BORDER
    if QColor(color).name(QColor.NameFormat.HexRgb).lower() == ACCENT.lower():
        return ACCENT_DARK
    return ACCENT


def _rect_area(rect: QRect) -> int:
    if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
        return 0
    return int(rect.width()) * int(rect.height())


def _point_rect_dist2(pt: QPoint, rect: QRect) -> int:
    """점과 사각형 사이의 거리 제곱. 안에 있으면 0."""
    if pt.x() < rect.left():
        dx = rect.left() - pt.x()
    elif pt.x() > rect.right():
        dx = pt.x() - rect.right()
    else:
        dx = 0
    if pt.y() < rect.top():
        dy = rect.top() - pt.y()
    elif pt.y() > rect.bottom():
        dy = pt.y() - rect.bottom()
    else:
        dy = 0
    return dx * dx + dy * dy


def screen_for_rect(rect: QRect, screens=None):
    """핀이 실제로 보이는 화면.

    겹치는 면적이 가장 큰 화면을 고른다. 중심이 모니터 사이 빈 곳에 있어도
    핀 사각형이 걸친 쪽을 따른다. 어디에도 안 겹치면 중심에서 가장 가까운 화면.
    """
    if screens is None:
        screens = QGuiApplication.screens()
    screens = [screen for screen in screens if screen is not None]
    if not screens:
        return QGuiApplication.primaryScreen()
    best = None
    best_area = 0
    for screen in screens:
        area = _rect_area(rect.intersected(screen.geometry()))
        if area > best_area:
            best = screen
            best_area = area
    if best is not None:
        return best
    center = rect.center()
    return min(screens, key=lambda screen: _point_rect_dist2(center, screen.geometry()))


def markup_bar_position(pin: QRect, bar: QSize, bounds: QRect,
                        gap: int = MARKUP_BAR_GAP, margin: int = MARKUP_BAR_MARGIN) -> QPoint:
    """표시 도구 창의 왼쪽 위.

    핀 바로 아래, 가로는 핀 가운데에 맞춘다. 아래가 화면을 넘으면 위에 둔다.
    둘 다 들어가지 않으면 핀 하단에 겹치고, 어느 쪽이든 같은 화면 안에 둔다.
    막대가 화면보다 넓으면 왼쪽 여백에 붙인다. 오른쪽이 잘리지 않게 하려면
    호출하는 쪽에서 MarkupBar.fit_width 로 먼저 줄인다.
    """
    if bounds.width() < 1 or bounds.height() < 1:
        return QPoint(pin.left(), pin.bottom() + 1 + gap)
    left = bounds.left() + margin
    right_limit = bounds.right() - bar.width() - margin + 1
    if bar.width() >= bounds.width() - margin * 2 or right_limit < left:
        x = bounds.left()
    else:
        x = pin.center().x() - bar.width() // 2
        x = min(max(x, left), right_limit)

    top_limit = bounds.top() + margin
    bottom_limit = bounds.bottom() - bar.height() - margin + 1
    if bottom_limit < top_limit:
        bottom_limit = top_limit
    below = pin.bottom() + 1 + gap
    above = pin.top() - gap - bar.height()
    if top_limit <= below <= bottom_limit:
        y = below
    elif top_limit <= above <= bottom_limit:
        y = above
    else:
        y = pin.bottom() + 1 - bar.height() - gap
        y = min(max(y, top_limit), bottom_limit)
    return QPoint(int(x), int(y))


_MARK_BTN_QSS = f"""
    QToolButton {{
        border: 1px solid transparent;
        border-radius: 8px;
        background: transparent;
        padding: 0px;
    }}
    QToolButton:hover {{ background: #EDF3FE; }}
    QToolButton:pressed {{ background: #DDE9FD; }}
    QToolButton:checked {{
        background: #D6E4FC;
        border: 1px solid {ACCENT};
    }}
"""


def _markup_tool_button(icon: QIcon, name: str, tip: str, slot, size: int = MARK_BAR_HIT) -> QToolButton:
    btn = QToolButton()
    btn.setIcon(icon)
    btn.setIconSize(QSize(MARK_BAR_ICON, MARK_BAR_ICON))
    btn.setText(name)
    btn.setAccessibleName(name)
    btn.setToolTip(tip)
    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    btn.setFixedSize(size, size)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setCheckable(True)
    btn.setStyleSheet(_MARK_BTN_QSS)
    btn.clicked.connect(slot)
    return btn


def _markup_separator() -> QFrame:
    line = QFrame()
    line.setFixedSize(1, 22)
    line.setStyleSheet(f"background:{BORDER}; border: none; max-width: 1px;")
    return line


class MarkupBar(QWidget):
    """표시 중인 핀 아래(자리가 없으면 위)에 뜨는 도구. 메인 창에는 넣지 않는다."""

    def __init__(self, pin: "PinWindow"):
        super().__init__(None)
        self._pin = pin
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool
                            | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setWindowTitle("표시")
        self.setObjectName("markupBar")
        # 선택자 없이 배경을 주면 자식 버튼까지 글자만 남는다. 패널은 paintEvent 가 그린다.
        self.setStyleSheet(
            "#markupBar, #markupBarRow { background: transparent; border: none; }")
        self.is_wrapped = False
        self._top = QWidget(self)
        self._bottom = QWidget(self)
        self._top.setObjectName("markupBarRow")
        self._bottom.setObjectName("markupBarRow")
        for host in (self._top, self._bottom):
            host.setAutoFillBackground(False)
        self._row1 = QHBoxLayout(self._top)
        self._row2 = QHBoxLayout(self._bottom)
        self._row1.setContentsMargins(0, 0, 0, 0)
        self._row2.setContentsMargins(0, 0, 0, 0)
        rows = QVBoxLayout(self)
        rows.setSpacing(4)
        rows.addWidget(self._top)
        rows.addWidget(self._bottom)
        self._tools = {}
        self._draw_widgets = []
        for kind, label in MARK_TOOL_LABELS:
            btn = _markup_tool_button(
                make_icon(MARK_TOOL_ICONS[kind], size=MARK_BAR_ICON),
                label, label,
                lambda _checked=False, k=kind: pin.set_markup_tool(k),
            )
            self._tools[kind] = btn
            self._draw_widgets.append(btn)
        self._draw_widgets.append(_markup_separator())
        self._colors = {}
        for name, color in MARK_COLORS:
            btn = QPushButton()
            btn.setFixedSize(MARK_BAR_SWATCH, MARK_BAR_SWATCH)
            btn.setText("")
            btn.setToolTip(name)
            btn.setAccessibleName(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, c=color: pin.set_markup_color(c))
            self._colors[color] = btn
            self._draw_widgets.append(btn)
        self._custom = QPushButton("+")
        self._custom.setFixedSize(MARK_BAR_SWATCH, MARK_BAR_SWATCH)
        self._custom.setToolTip("다른 색")
        self._custom.setAccessibleName("다른 색")
        self._custom.setCheckable(True)
        self._custom.setCursor(Qt.CursorShape.PointingHandCursor)
        self._custom.clicked.connect(lambda _checked=False: pin.pick_markup_color())
        self._draw_widgets.append(self._custom)
        self._mid_sep = _markup_separator()
        self._widths = {}
        self._act_widgets = []
        for preset, label, icon_kind in MARK_WIDTH_LABELS:
            btn = _markup_tool_button(
                make_icon(icon_kind, size=MARK_BAR_ICON),
                label, label,
                lambda _checked=False, w=preset: pin.set_markup_width(w),
            )
            self._widths[preset] = btn
            self._act_widgets.append(btn)
        self._act_widgets.append(_markup_separator())
        self._undo = _markup_tool_button(
            make_icon("undo", size=MARK_BAR_ICON),
            "실행 취소", "실행 취소 (Ctrl+Z)",
            lambda _checked=False: pin.undo_mark(),
        )
        self._redo = _markup_tool_button(
            make_icon("redo", size=MARK_BAR_ICON),
            "다시 실행", "다시 실행 (Ctrl+Y)",
            lambda _checked=False: pin.redo_mark(),
        )
        self._done = _markup_tool_button(
            make_icon("check", ACCENT, size=MARK_BAR_ICON),
            "완료", "완료 (Esc)",
            lambda _checked=False: pin.end_markup(),
        )
        self._undo.setCheckable(False)
        self._redo.setCheckable(False)
        self._done.setCheckable(False)
        self._act_widgets.extend((self._undo, self._redo, self._done))
        self._apply_rows(False)
        self._set_metrics(MARK_BAR_HIT, MARK_BAR_SWATCH, _MARK_BAR_PAD_X, 4)
        self.sync()

    def buttons(self):
        """화면에 남아야 하는 버튼. 구분선은 빼요."""
        return (
            list(self._tools.values())
            + list(self._colors.values())
            + [self._custom]
            + list(self._widths.values())
            + [self._undo, self._redo, self._done]
        )

    def _drain(self, layout) -> None:
        while layout.count():
            layout.takeAt(0)

    def _apply_rows(self, wrapped: bool) -> None:
        """한 줄이 기본. 좁으면 그리기·색 / 두께·실행을 두 줄로 나눈다."""
        self._drain(self._row1)
        self._drain(self._row2)
        for widget in self._draw_widgets:
            self._row1.addWidget(widget)
            widget.show()
        if wrapped:
            self._mid_sep.hide()
            for widget in self._act_widgets:
                self._row2.addWidget(widget)
                widget.show()
            self._bottom.show()
        else:
            self._mid_sep.show()
            self._row1.addWidget(self._mid_sep)
            for widget in self._act_widgets:
                self._row1.addWidget(widget)
                widget.show()
            self._bottom.hide()
        self.is_wrapped = wrapped

    def _set_metrics(self, hit: int, swatch: int, pad_x: int, spacing: int) -> None:
        icon = max(12, int(hit) - 14)
        for btn in (*self._tools.values(), *self._widths.values(), self._undo, self._redo, self._done):
            btn.setFixedSize(hit, hit)
            btn.setIconSize(QSize(icon, icon))
        for btn in (*self._colors.values(), self._custom):
            btn.setFixedSize(swatch, swatch)
        lay = self.layout()
        lay.setContentsMargins(
            _MARK_BAR_SHADOW + pad_x,
            (_MARK_BAR_SHADOW - 2) + _MARK_BAR_PAD_Y,
            _MARK_BAR_SHADOW + pad_x,
            _MARK_BAR_SHADOW + _MARK_BAR_PAD_Y,
        )
        self._row1.setSpacing(spacing)
        self._row2.setSpacing(spacing)

    def _relayout(self) -> QSize:
        self.setMinimumSize(0, 0)
        lay = self.layout()
        lay.invalidate()
        lay.activate()
        self.updateGeometry()
        self.adjustSize()
        return self.size()

    def fit_width(self, max_width: int) -> None:
        """한 줄이 max_width 안에 들어가면 그대로 둔다.

        넘치면 두 줄로 내리고, 그래도 넘치면 버튼과 여백만 줄여 화면 안에 둔다.
        """
        max_width = max(1, int(max_width))
        self._set_metrics(MARK_BAR_HIT, MARK_BAR_SWATCH, _MARK_BAR_PAD_X, 4)
        self._apply_rows(False)
        if self._relayout().width() <= max_width:
            return
        self._apply_rows(True)
        if self._relayout().width() <= max_width:
            return
        hit, swatch, pad, spacing = MARK_BAR_HIT, MARK_BAR_SWATCH, _MARK_BAR_PAD_X, 4
        guard = 0
        while self.width() > max_width and guard < 80:
            guard += 1
            if hit > 16:
                hit -= 1
            elif swatch > 14:
                swatch -= 1
            elif spacing > 2:
                spacing -= 1
            elif pad > 4:
                pad -= 1
            else:
                break
            self._set_metrics(hit, swatch, pad, spacing)
            self._relayout()
        self._relayout()

    def _panel_rect(self) -> QRectF:
        return QRectF(self.rect()).adjusted(
            _MARK_BAR_SHADOW, _MARK_BAR_SHADOW - 2, -_MARK_BAR_SHADOW, -_MARK_BAR_SHADOW)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        panel = self._panel_rect()
        shadow = QColor(43, 52, 66)
        for grow, alpha, drop in ((7, 16, 3), (4, 24, 2), (2, 32, 1)):
            shadow.setAlpha(alpha)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(shadow)
            p.drawRoundedRect(panel.adjusted(-grow, -grow + drop, grow, grow + drop), 12, 12)
        p.setPen(QPen(QColor(BORDER), 1))
        p.setBrush(QColor("white"))
        p.drawRoundedRect(panel.adjusted(0.5, 0.5, -0.5, -0.5), 8, 8)
        p.end()

    def sync(self):
        pin = self._pin
        for kind, btn in self._tools.items():
            on = kind == pin._tool
            btn.setChecked(on)
            btn.setIcon(make_icon(MARK_TOOL_ICONS[kind], ACCENT if on else TEXT, size=MARK_BAR_ICON))
        current = str(pin._color)
        known = {color.lower() for color in self._colors}
        for color, btn in self._colors.items():
            on = color.lower() == current.lower()
            btn.setChecked(on)
            border = _swatch_border(color, on)
            width = 3 if on else 2
            btn.setStyleSheet(
                f"background:{color}; border-radius:8px; padding:0; "
                f"border:{width}px solid {border};")
        custom_on = current.lower() not in known
        swatch = current if custom_on and QColor(current).isValid() else "#FFFFFF"
        self._custom.setChecked(custom_on)
        self._custom.setText("+")
        border = _swatch_border(swatch, custom_on)
        width = 3 if custom_on else 2
        ink = _marker_ink(swatch)
        self._custom.setStyleSheet(
            f"background:{swatch}; color:{ink}; font-size:15px; font-weight:700; "
            f"padding:0; border-radius:8px; border:{width}px solid {border};")
        for preset, btn in self._widths.items():
            on = preset == pin._width_preset
            btn.setChecked(on)
            icon_kind = {w: kind for w, _label, kind in MARK_WIDTH_LABELS}[preset]
            btn.setIcon(make_icon(icon_kind, ACCENT if on else TEXT, size=MARK_BAR_ICON))

    def keyPressEvent(self, e):
        action = _edit_key_action(e)
        if action == "end":
            self._pin.end_markup()
        elif action == "undo":
            self._pin.undo_mark()
        elif action == "redo":
            self._pin.redo_mark()
        else:
            super().keyPressEvent(e)


class PinWindow(QWidget):
    closed = Signal(object)

    def __init__(self, image: QImage, dpr: float = 1.0):
        super().__init__(None)
        self._img = image
        self._pm = QPixmap.fromImage(image)
        self._dpr = max(1.0, dpr)
        self._scale = 1.0
        self._opacity = 100
        self._click_through = False
        self._drag = None
        self._toast = None
        self._ocr_running = False
        self.release_hotkey = ""          # 클릭 통과를 끄는 전역 단축키 (표시용)
        self.on_eyedropper = None         # 화면 스포이트. MainToolbar 가 연결
        self.on_ruler = None
        self.on_activated = None          # 이 핀을 맨 앞 핀으로 기록. MainToolbar 가 연결
        self._img_sig = image_signature(image)
        self._editing = False
        self._tool = "arrow"
        self._color = MARK_COLORS[0][1]
        self._width_preset = 4
        self._marks = []
        self._redo = []
        self._draft = None
        self._draft_origin = None
        self._cache = None
        self._bar = None
        self._screen_watch = False
        self._hooked = []
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowTitle("핀 고정")
        self._apply_size()
        self.setToolTip(PIN_TOOLTIP)

    @property
    def opacity_percent(self) -> int:
        return self._opacity

    @property
    def click_through(self) -> bool:
        return self._click_through

    def _logical_size(self) -> QSize:
        return QSize(max(1, round(self._pm.width() / self._dpr * self._scale)),
                     max(1, round(self._pm.height() / self._dpr * self._scale)))

    def _apply_size(self):
        self.resize(self._logical_size())

    def set_opacity(self, percent: int) -> None:
        percent = int(percent)
        if percent not in OPACITY_STEPS:
            percent = min(OPACITY_STEPS, key=lambda step: abs(step - percent))
        self._opacity = percent
        self.setWindowOpacity(percent / 100.0)

    def adjust_opacity_step(self, direction: int) -> None:
        """direction +1 은 더 불투명(휠 위), -1 은 더 투명."""
        if self._opacity in OPACITY_STEPS:
            idx = OPACITY_STEPS.index(self._opacity)
        else:
            idx = min(range(len(OPACITY_STEPS)), key=lambda i: abs(OPACITY_STEPS[i] - self._opacity))
        idx = max(0, min(len(OPACITY_STEPS) - 1, idx - direction))
        self.set_opacity(OPACITY_STEPS[idx])

    def set_click_through(self, on: bool) -> None:
        """클릭을 뒤 창으로 통과시킨다. 켜면 이 핀의 메뉴·드래그로는 끌 수 없다."""
        on = bool(on)
        if on == self._click_through:
            return
        self._click_through = on
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, on)
        self.setWindowOpacity(self._opacity / 100.0)
        self.show()
        _set_win32_click_through(int(self.winId()), on)
        self.setWindowOpacity(self._opacity / 100.0)
        if on and self._editing:
            self.end_markup()
        if on:
            hint = format_hotkey(self.release_hotkey) or "단축키"
            self.show_toast(
                "클릭 통과를 켰어요. 마우스가 핀 아래 창으로 전달돼요.\n"
                f"끄려면 트레이의 '클릭 통과 해제' 또는 {hint} 를 눌러 주세요.",
                msec=4200)

    def show_toast(self, text: str, msec: int = 1800) -> PinToast:
        if self._toast is not None:
            try:
                self._toast.close()
            except Exception:
                pass
        self._toast = PinToast(text, self, msec)
        return self._toast

    def copy_ocr(self, mode: str = "text") -> OcrResult:
        # 형광펜·모자이크가 글자를 가리면 인식이 나빠져서, OCR 은 표시 없는 원본을 본다.
        # 글자 모드(기본)는 인자 없이 호출한다. 기존 시험의 가짜 copy_ocr 와 맞추기 위해서다.
        # 안내는 이 핀 옆 토스트다. 트레이 풍선에만 맡기지 않는다.
        if self._ocr_running:
            self.show_toast(OCR_BUSY_MSG)
            return OcrResult(False, "", OCR_BUSY_MSG)
        self._ocr_running = True
        try:
            image = self.image_for_ocr()
            if mode == "math" and math_status() != "ok":
                ok, note = ensure_math_installed(self)
                if not ok:
                    self.show_toast(note, 4200)
                    return OcrResult(False, "", note)
            return run_ocr(image, mode, self.show_toast)
        except Exception as exc:
            _log_exc("ocr", exc, "핀 글자 복사")
            try:
                self.show_toast(OCR_FAILED_MSG, 4200)
            except Exception as again:
                _log_exc("ocr", again, "안내 표시 실패")
            return OcrResult(False, "", OCR_FAILED_MSG)
        finally:
            self._ocr_running = False

    def image_for_ocr(self) -> QImage:
        return self._img

    def image_for_export(self) -> QImage:
        """복사·저장에 쓰는 이미지. 확정된 표시가 합성돼 있다."""
        return self._committed_image()

    def _stroke_px(self) -> int:
        if self._tool == "mosaic":
            return mosaic_block_px(self._width_preset, self._dpr)
        return mark_width_px(self._width_preset, self._dpr)

    def _to_image_pt(self, pt: QPoint) -> QPoint:
        return physical_point(self.size(), self._img.size(), pt)

    def _committed_image(self) -> QImage:
        if self._cache is None:
            self._cache = compose_marks(self._img, self._marks)
        return self._cache

    def rendered_image(self) -> QImage:
        base = self._committed_image()
        if self._draft is None:
            return base
        return compose_marks(base, [self._draft])

    def begin_markup(self, tool: str = "arrow") -> bool:
        """표시 모드. 클릭 통과 중에는 핀이 마우스를 받지 못하므로 거절한다."""
        if self._click_through:
            self.show_toast("클릭 통과를 끄고 표시해 주세요.")
            return False
        if tool in MARK_KINDS:
            self._tool = tool
        self._editing = True
        self._drag = None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setToolTip(PIN_EDIT_TOOLTIP)
        self.setFocus()
        self._ensure_bar()
        self.update()
        return True

    def end_markup(self) -> None:
        """표시만 끝낸다. 핀은 닫지 않는다."""
        self._watch_screens(False)
        self._editing = False
        self._draft = None
        self._draft_origin = None
        self._drag = None
        bar = self._bar
        self._bar = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setToolTip(PIN_TOOLTIP)
        if bar is not None:
            bar.hide()
            bar.close()
        self.update()

    def set_markup_tool(self, kind: str) -> None:
        if kind in MARK_KINDS:
            self._tool = kind
        if not self._editing:
            self.begin_markup(self._tool)
        elif self._bar is not None:
            self._bar.sync()

    def set_markup_color(self, color: str) -> None:
        q = QColor(str(color))
        if not q.isValid():
            return
        self._color = q.name(QColor.NameFormat.HexRgb).upper()
        if self._bar is not None:
            self._bar.sync()

    def _markup_color_dialog(self, initial: QColor) -> QColorDialog:
        """다른 색. 핀이 항상 위라 기본 대화상자는 뒤로 숨으니 Qt 대화상자를 맨 앞에 둔다."""
        if not initial.isValid():
            initial = QColor(MARK_COLORS[0][1])
        dlg = QColorDialog(initial, self)
        dlg.setWindowTitle("다른 색")
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dlg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        return dlg

    def pick_markup_color(self) -> str:
        """색 대화상자. 취소하면 빈 문자열. 고르면 #RRGGBB."""
        chosen = self._ask_markup_color()
        if not chosen.isValid():
            if self._bar is not None:
                self._bar.sync()
            return ""
        name = chosen.name(QColor.NameFormat.HexRgb).upper()
        self.set_markup_color(name)
        return name

    def _ask_markup_color(self) -> QColor:
        dlg = self._markup_color_dialog(QColor(self._color))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            dlg.deleteLater()
            return QColor()
        color = QColor(dlg.selectedColor())
        dlg.deleteLater()
        return color

    def set_markup_width(self, preset: int) -> None:
        self._width_preset = int(preset)
        if self._bar is not None:
            self._bar.sync()

    def _commit_mark(self, mark: Mark) -> None:
        if not _mark_is_real(mark):
            return
        self._marks.append(mark)
        self._redo.clear()
        self._cache = None
        self.update()

    def undo_mark(self) -> bool:
        if not self._marks:
            return False
        self._redo.append(self._marks.pop())
        self._cache = None
        self.update()
        return True

    def redo_mark(self) -> bool:
        if not self._redo:
            return False
        self._marks.append(self._redo.pop())
        self._cache = None
        self.update()
        return True

    def _ensure_bar(self) -> None:
        if self._bar is None:
            self._bar = MarkupBar(self)
        self._bar.sync()
        self._bar.show()
        self._watch_screens(True)
        self._place_markup_bar()

    def _on_screens_changed(self, *_args) -> None:
        """모니터가 늘거나 줄고, 위치·작업 표시줄·배율이 바뀌면 도구를 다시 붙인다."""
        if self._editing and self._bar is not None:
            self._place_markup_bar()

    def _hook_screen(self, screen) -> None:
        if screen is None or screen in self._hooked:
            return
        screen.geometryChanged.connect(self._on_screens_changed)
        screen.availableGeometryChanged.connect(self._on_screens_changed)
        if hasattr(screen, "logicalDotsPerInchChanged"):
            screen.logicalDotsPerInchChanged.connect(self._on_screens_changed)
        self._hooked.append(screen)

    def _unhook_screen(self, screen) -> None:
        if screen not in self._hooked:
            return
        signals = [screen.geometryChanged, screen.availableGeometryChanged]
        if hasattr(screen, "logicalDotsPerInchChanged"):
            signals.append(screen.logicalDotsPerInchChanged)
        for signal in signals:
            try:
                signal.disconnect(self._on_screens_changed)
            except (RuntimeError, TypeError):
                pass
        self._hooked.remove(screen)

    def _on_screen_added(self, screen) -> None:
        self._hook_screen(screen)
        self._on_screens_changed()

    def _on_screen_removed(self, screen) -> None:
        self._unhook_screen(screen)
        self._on_screens_changed()

    def _watch_screens(self, on: bool) -> None:
        app = QGuiApplication.instance()
        if app is None:
            return
        if on:
            if self._screen_watch:
                return
            self._screen_watch = True
            app.screenAdded.connect(self._on_screen_added)
            app.screenRemoved.connect(self._on_screen_removed)
            for screen in app.screens():
                self._hook_screen(screen)
            return
        if not self._screen_watch:
            return
        self._screen_watch = False
        try:
            app.screenAdded.disconnect(self._on_screen_added)
            app.screenRemoved.disconnect(self._on_screen_removed)
        except (RuntimeError, TypeError):
            pass
        for screen in list(self._hooked):
            self._unhook_screen(screen)

    def _place_markup_bar(self) -> None:
        bar = self._bar
        if bar is None:
            return
        g = self.frameGeometry()
        screen = screen_for_rect(g)
        if screen is not None:
            bounds = screen.availableGeometry()
            if bounds.width() < 1 or bounds.height() < 1:
                bounds = screen.geometry()
        else:
            bounds = QRect(g.left() - 200, g.top() - 80, max(g.width(), bar.width()) + 400,
                           max(g.height() + bar.height() + 160, 400))
        bar.fit_width(max(1, bounds.width() - 2 * MARKUP_BAR_MARGIN))
        bar.move(markup_bar_position(g, bar.size(), bounds))
        bar.raise_()

    def build_menu(self) -> "tuple[QMenu, dict]":
        m = QMenu(self)
        ocr_menu, ocr_acts = build_ocr_mode_menu(self)
        ocr_menu.setTitle("글자 복사")
        m.addMenu(ocr_menu)
        acts = {
            "ocr_menu": ocr_menu,
            "ocr_modes": ocr_acts,
            "ocr": ocr_acts["text"],
            "copy": m.addAction("클립보드에 복사"),
            "save": m.addAction("다른 이름으로 저장…"),
            "orig": m.addAction("원본 크기 (100%)"),
        }
        mark_menu = m.addMenu("표시")
        acts["tools"] = {}
        for kind, label in MARK_TOOL_LABELS:
            acts["tools"][kind] = mark_menu.addAction(label)
        acts["mark_end"] = mark_menu.addAction("표시 끝내기")
        acts["eyedropper"] = m.addAction("스포이트")
        acts["ruler"] = m.addAction("자")
        opacity_menu = m.addMenu("투명도")
        acts["opacity"] = {}
        for pct in OPACITY_STEPS:
            act = opacity_menu.addAction(f"{pct}%")
            act.setCheckable(True)
            act.setChecked(pct == self._opacity)
            acts["opacity"][pct] = act
        acts["click"] = m.addAction("클릭 통과")
        acts["click"].setCheckable(True)
        acts["click"].setChecked(self._click_through)
        m.addSeparator()
        acts["close"] = m.addAction("닫기")
        return m, acts

    def apply_menu_action(self, chosen, acts: dict) -> None:
        if chosen is None:
            return
        ocr_mode = None
        for mode, act in acts.get("ocr_modes", {}).items():
            if chosen == act:
                ocr_mode = mode
                break
        if ocr_mode is not None:
            if ocr_mode == "text":
                self.copy_ocr()
            else:
                self.copy_ocr(ocr_mode)
        elif chosen == acts["copy"]:
            QApplication.clipboard().setImage(self.image_for_export())
        elif chosen == acts["save"]:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path, _ = QFileDialog.getSaveFileName(
                self, "저장", str(Path.home() / f"핀캡처_{ts}.png"),
                "PNG (*.png);;JPEG (*.jpg)")
            if path:
                self.image_for_export().save(path)
                self.show_toast("저장했어요.")
        elif chosen == acts["orig"]:
            self._scale = 1.0
            self._apply_size()
        elif chosen == acts.get("mark_end"):
            self.end_markup()
        elif chosen == acts.get("eyedropper"):
            if self.on_eyedropper is not None:
                self.on_eyedropper()
        elif chosen == acts.get("ruler"):
            if self.on_ruler is not None:
                self.on_ruler()
        elif chosen in acts["opacity"].values():
            for pct, act in acts["opacity"].items():
                if chosen == act:
                    self.set_opacity(pct)
                    break
        elif chosen == acts["click"]:
            self.set_click_through(acts["click"].isChecked())
        elif chosen == acts["close"]:
            self.close()
        else:
            for kind, act in acts.get("tools", {}).items():
                if chosen == act:
                    self.begin_markup(kind)
                    break

    # --- 이벤트 ---
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.drawImage(self.rect(), self.rendered_image())
        pen = QPen(QColor(ACCENT))
        pen.setWidth(2)
        p.setPen(pen)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        p.end()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.adjust_opacity_step(1 if e.angleDelta().y() > 0 else -1)
            e.accept()
            return
        step = 1.1 if e.angleDelta().y() > 0 else 1 / 1.1
        self._scale = min(5.0, max(0.15, self._scale * step))
        self._apply_size()

    def _remember_front(self) -> None:
        cb = self.on_activated
        if cb is None:
            return
        try:
            cb()
        except Exception as exc:
            _log_exc("pin", exc, "맨 앞 핀 기록")

    def _extend_pen(self, end: QPoint, shift: bool = False) -> None:
        origin = self._draft_origin or end
        color = self._color
        width = self._stroke_px()
        if self._draft is not None and self._draft.kind == "pen":
            color = self._draft.color
            width = self._draft.width_px
        if shift:
            end = snap_axis_point(origin, end)
            start = (int(origin.x()), int(origin.y()))
            pt = (int(end.x()), int(end.y()))
            points = [start] if pt == start else [start, pt]
            self._draft = Mark("pen", start[0], start[1], pt[0], pt[1], color, width, points=points)
            return
        pt = (int(end.x()), int(end.y()))
        if self._draft is None or self._draft.kind != "pen" or not self._draft.points:
            self._draft = Mark(
                "pen", origin.x(), origin.y(), end.x(), end.y(),
                color, width, points=[(origin.x(), origin.y())])
        if self._draft.points[-1] != pt:
            self._draft.points.append(pt)
        self._draft.x2 = int(end.x())
        self._draft.y2 = int(end.y())

    def mousePressEvent(self, e):
        self._remember_front()
        if self._editing and e.button() == Qt.MouseButton.LeftButton:
            self._drag = None
            origin = self._to_image_pt(e.position().toPoint())
            self._draft_origin = origin
            if self._tool == "pen":
                self._draft = Mark(
                    "pen", origin.x(), origin.y(), origin.x(), origin.y(),
                    self._color, self._stroke_px(), points=[(origin.x(), origin.y())])
                self.update()
            else:
                self._draft = None
            self.setFocus()
            return
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._editing:
            if self._draft_origin is not None and (e.buttons() & Qt.MouseButton.LeftButton):
                end = self._to_image_pt(e.position().toPoint())
                if self._tool == "pen":
                    shift = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                    self._extend_pen(end, shift)
                else:
                    self._draft = Mark(
                        self._tool, self._draft_origin.x(), self._draft_origin.y(),
                        end.x(), end.y(), self._color, self._stroke_px())
                self.update()
            return
        if self._drag is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        if self._editing:
            if e.button() == Qt.MouseButton.LeftButton and self._draft_origin is not None:
                # 빠르게 그으면 move 가 없이 press 와 release 만 온다. 놓는 점을 빠뜨리면
                # 획이 잘리거나 점 하나로 남는다.
                if self._tool == "pen":
                    shift = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                    self._extend_pen(self._to_image_pt(e.position().toPoint()), shift)
                if self._draft is not None:
                    self._commit_mark(self._draft)
                self._draft = None
                self._draft_origin = None
                self.update()
            return
        self._drag = None

    def mouseDoubleClickEvent(self, e):
        if self._editing:
            e.accept()
            return
        self.close()

    def keyPressEvent(self, e):
        if self._editing:
            action = _edit_key_action(e)
            if action == "end":
                self.end_markup()
            elif action == "undo":
                self.undo_mark()
            elif action == "redo":
                self.redo_mark()
            return
        if e.key() == Qt.Key.Key_Escape:
            self.close()

    def moveEvent(self, e):
        super().moveEvent(e)
        self._place_markup_bar()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._place_markup_bar()

    def closeEvent(self, e):
        self.end_markup()
        self.closed.emit(self)
        super().closeEvent(e)

    def contextMenuEvent(self, e):
        menu, acts = self.build_menu()
        chosen = menu.exec(e.globalPos())
        self.apply_menu_action(chosen, acts)


# ---------------------------------------------------------------------------
# 보관함 (캡처 기록): 메인에 최신/선택 캡처, 우측에 이전 캡처 썸네일 리스트
# ---------------------------------------------------------------------------
class HistoryEntry:
    """캡처 1건: 메모리 이미지 또는 저장된 파일 경로."""
    THUMB_W = 168

    def __init__(self, image: "QImage | None" = None, path: "str | None" = None,
                 ts: "datetime.datetime | None" = None):
        self._image = image
        self.path = path
        self.ts = ts or datetime.datetime.now()
        self._thumb = None
        self._size = (image.width(), image.height()) if image is not None else None

    def full_image(self) -> "QImage | None":
        if self._image is not None:
            return self._image
        if self.path and Path(self.path).exists():
            img = QImage(self.path)
            if not img.isNull():
                self._size = (img.width(), img.height())
                return img
        return None

    def thumbnail(self) -> "QPixmap | None":
        if self._thumb is not None:
            return self._thumb
        pm = None
        if self._image is not None:
            img = self._image
            if img.width() > self.THUMB_W:
                img = img.scaledToWidth(self.THUMB_W,
                                        Qt.TransformationMode.SmoothTransformation)
            pm = QPixmap.fromImage(img)
        elif self.path and Path(self.path).exists():
            reader = QImageReader(self.path)
            sz = reader.size()
            if sz.isValid():
                self._size = (sz.width(), sz.height())
                if sz.width() > self.THUMB_W:
                    reader.setScaledSize(QSize(
                        self.THUMB_W,
                        max(1, round(sz.height() * self.THUMB_W / sz.width()))))
            img = reader.read()
            if not img.isNull():
                pm = QPixmap.fromImage(img)
        self._thumb = pm
        return pm

    def label(self) -> str:
        fmt = "%H:%M:%S" if self.ts.date() == datetime.date.today() else "%m/%d %H:%M"
        t = self.ts.strftime(fmt)
        return f"{t}\n{self._size[0]}×{self._size[1]}" if self._size else t


class PreviewPane(QWidget):
    """보관함 메인 미리보기 (비율 유지, 100% 이상 확대 안 함)."""

    def __init__(self):
        super().__init__()
        self._pm = None
        self.setMinimumSize(320, 240)

    def set_image(self, img: "QImage | None"):
        self._pm = QPixmap.fromImage(img) if (img is not None and not img.isNull()) else None
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#2B303A"))
        if self._pm is None:
            p.setPen(QColor("#8A93A3"))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "아직 캡처가 없어요\n위쪽 버튼이나 단축키로 화면을 찍어 보세요")
            p.end()
            return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        area = self.rect().adjusted(14, 14, -14, -14)
        size = self._pm.size().scaled(area.size(), Qt.AspectRatioMode.KeepAspectRatio)
        if size.width() >= self._pm.width():
            size = self._pm.size()      # 원본보다 크게 늘리지 않음
        target = QRect(QPoint(0, 0), size)
        target.moveCenter(area.center())
        p.drawPixmap(target, self._pm)
        p.setPen(QPen(QColor("#4A5160")))
        p.drawRect(target.adjusted(-1, -1, 0, 0))
        p.end()


# ---------------------------------------------------------------------------
# 전역 단축키 (pynput — 실패해도 앱은 동작)
# ---------------------------------------------------------------------------
class HotkeyManager(QObject):
    triggered = Signal(str)   # region | window | full | pin | reopen_pin | clickthrough | markup | eyedropper | ruler

    def __init__(self):
        super().__init__()
        self._listener = None
        self.available = False
        self.error = ""

    def restart(self, hotkeys: dict):
        self.stop()
        try:
            from pynput import keyboard
        except Exception as e:
            self.available = False
            self.error = f"pynput 사용 불가: {e}"
            print(f"[hotkey] {self.error}")
            return
        mapping = {}
        for mode, combo in iter_hotkey_bindings(hotkeys):
            try:
                keyboard.HotKey.parse(combo)
            except Exception as e:
                print(f"[hotkey] '{combo}' 형식 오류, 건너뜀: {e}")
                continue
            mapping[combo] = (lambda m=mode: self.triggered.emit(m))
        if not mapping:
            self.available = False
            return
        try:
            self._listener = keyboard.GlobalHotKeys(mapping)
            self._listener.daemon = True
            self._listener.start()
            self.available = True
            self.error = ""
        except Exception as e:
            self.available = False
            self.error = str(e)
            print(f"[hotkey] 등록 실패: {e}")

    def stop(self):
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None


# ---------------------------------------------------------------------------
# 작업 표시줄 식별 (Windows)
#   창과 바로가기에 같은 AppUserModelID 를 심고, 창에는 재실행 명령/이름/아이콘까지 기록한다.
#   이게 없으면 '작업 표시줄에 고정' 했을 때 Windows 가 pythonw.exe 자체를 고정해 Python 아이콘이 뜬다.
# ---------------------------------------------------------------------------
def app_icon_path() -> "Path | None":
    """바로가기/작업 표시줄에 쓸 아이콘 파일. EXE 는 자기 자신(아이콘 내장),
    스크립트 실행이면 ~/.pincapture/pincapture.ico (없으면 생성)."""
    if FROZEN:
        return Path(sys.executable)
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ico = CONFIG_DIR / "pincapture.ico"
        if not ico.exists() and not make_app_icon().pixmap(256, 256).save(str(ico), "ICO"):
            return None
        return ico
    except Exception:
        return None


def relaunch_command() -> str:
    """작업 표시줄 고정 아이콘이 실행할 명령 (EXE 면 PinCapture.exe, 스크립트면 pythonw.exe "pincapture.py")."""
    import subprocess
    return subprocess.list2cmdline(launch_argv())


if IS_WINDOWS:
    import ctypes as _ct
    from ctypes import wintypes as _wt

    class _GUID(_ct.Structure):
        _fields_ = [("Data1", _ct.c_ulong), ("Data2", _ct.c_ushort), ("Data3", _ct.c_ushort),
                    ("Data4", _ct.c_ubyte * 8)]

        def __init__(self, s=None):
            super().__init__()
            if s:
                _ct.windll.ole32.CLSIDFromString(_ct.c_wchar_p(s), _ct.byref(self))

    class _PROPERTYKEY(_ct.Structure):
        _fields_ = [("fmtid", _GUID), ("pid", _wt.DWORD)]

    class _PROPVARIANT(_ct.Structure):
        _fields_ = [("vt", _ct.c_ushort), ("r1", _ct.c_ushort), ("r2", _ct.c_ushort),
                    ("r3", _ct.c_ushort), ("data", _ct.c_byte * 16)]

    _IID_IPropertyStore = _GUID("{886d8eeb-8cf2-4446-8d02-cdba1dbdcf99}")
    _FMTID_AppUserModel = "{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}"
    _PKEY = {"RelaunchCommand": 2, "RelaunchIconResource": 3,      # System.AppUserModel.*
             "RelaunchDisplayNameResource": 4, "ID": 5}
    _CSIDL = {"Desktop": 0x10, "Startup": 0x07, "Programs": 0x02}

    def _special_folder(name: str) -> Path:
        buf = _ct.create_unicode_buffer(260)
        _ct.windll.shell32.SHGetFolderPathW(None, _CSIDL[name], None, 0, buf)
        return Path(buf.value)

    def _com_method(obj, index, *argtypes):
        vtable = _ct.cast(obj, _ct.POINTER(_ct.c_void_p))[0]
        fn = _ct.cast(vtable, _ct.POINTER(_ct.c_void_p))[index]
        return _ct.WINFUNCTYPE(_ct.c_long, _ct.c_void_p, *argtypes)(fn)

    def _propstore_set(ps, props: dict) -> None:
        """IPropertyStore 에 문자열 속성을 쓰고 Commit. vtable: 0-2 IUnknown, 5 GetValue, 6 SetValue, 7 Commit."""
        SetValue = _com_method(ps, 6, _ct.POINTER(_PROPERTYKEY), _ct.POINTER(_PROPVARIANT))
        Commit = _com_method(ps, 7)
        Release = _com_method(ps, 2)
        try:
            for name, val in props.items():
                key = _PROPERTYKEY(_GUID(_FMTID_AppUserModel), _PKEY[name])
                pv = _PROPVARIANT()
                pv.vt = 31                                        # VT_LPWSTR
                p = _ct.c_void_p()
                if _ct.windll.shlwapi.SHStrDupW(_ct.c_wchar_p(val), _ct.byref(p)) != 0:
                    raise OSError("SHStrDupW 실패")
                _ct.cast(pv.data, _ct.POINTER(_ct.c_void_p))[0] = p.value
                hr = SetValue(ps, _ct.byref(key), _ct.byref(pv))
                _ct.windll.ole32.PropVariantClear(_ct.byref(pv))
                if hr < 0:
                    raise OSError(f"SetValue({name}) hr={hr & 0xffffffff:#x}")
            hr = Commit(ps)
            if hr < 0:
                raise OSError(f"Commit hr={hr & 0xffffffff:#x}")
        finally:
            Release(ps)

    def set_shortcut_app_id(lnk: "str | Path") -> bool:
        """바로가기(.lnk) 파일에 System.AppUserModel.ID 를 기록."""
        try:
            ps = _ct.c_void_p()
            hr = _ct.windll.shell32.SHGetPropertyStoreFromParsingName(
                _ct.c_wchar_p(str(lnk)), None, 2, _ct.byref(_IID_IPropertyStore), _ct.byref(ps))  # GPS_READWRITE
            if hr < 0:
                raise OSError(f"SHGetPropertyStoreFromParsingName hr={hr & 0xffffffff:#x}")
            _propstore_set(ps, {"ID": APP_USER_MODEL_ID})
            return True
        except Exception as e:
            print(f"[taskbar] 바로가기 AppID 기록 실패 ({lnk}): {e}")
            return False

    def set_window_taskbar_identity(hwnd: int) -> bool:
        """메인 창에 AppID + 재실행 명령/이름/아이콘을 기록 → 실행 중 창에서 고정해도 핀캡처로 고정됨."""
        try:
            props = {"ID": APP_USER_MODEL_ID,
                     "RelaunchCommand": relaunch_command(),
                     "RelaunchDisplayNameResource": APP_NAME}
            ico = app_icon_path()
            if ico:
                props["RelaunchIconResource"] = f"{ico},0"
            ps = _ct.c_void_p()
            hr = _ct.windll.shell32.SHGetPropertyStoreForWindow(
                _wt.HWND(hwnd), _ct.byref(_IID_IPropertyStore), _ct.byref(ps))
            if hr < 0:
                raise OSError(f"SHGetPropertyStoreForWindow hr={hr & 0xffffffff:#x}")
            _propstore_set(ps, props)
            return True
        except Exception as e:
            print(f"[taskbar] 창 식별 정보 설정 실패: {e}")
            return False

    def force_foreground(hwnd: int) -> bool:
        """창을 확실히 전경으로. Windows 는 마지막 입력을 받지 않은 프로세스의 SetForegroundWindow 를
        막고 작업 표시줄만 깜빡이게 한다. 단계적으로 우회:
          1) 그냥 SetForegroundWindow
          2) 전경 창의 입력 스레드에 잠시 붙어서(AttachThreadInput) 전환
          3) Alt 키를 누른 상태로 전환하고 놓기 (놓는 입력은 이미 전경이 된 우리 창으로 감)
          4) 그래도 안 되면 TOPMOST 켰다 끄기로 화면 맨 앞에라도 두고 작업 표시줄 깜빡임"""
        if QGuiApplication.platformName() != "windows":
            return False          # offscreen 등: winId 가 실제 HWND 가 아니므로 Win32 에 넘기지 않음
        u = _ct.windll.user32
        k = _ct.windll.kernel32
        h = _wt.HWND(hwnd)
        VK_MENU, KEYEVENTF_KEYUP = 0x12, 0x0002

        def is_fg() -> bool:
            return u.GetForegroundWindow() == hwnd

        try:
            if u.IsIconic(h):
                u.ShowWindow(h, 9)                                  # SW_RESTORE
            if is_fg():
                return True
            u.BringWindowToTop(h)
            u.SetForegroundWindow(h)                                # 1)
            if is_fg():
                return True

            fg = u.GetForegroundWindow()
            cur_tid = k.GetCurrentThreadId()
            fg_tid = u.GetWindowThreadProcessId(fg, None) if fg else 0
            attached = bool(fg_tid and fg_tid != cur_tid and u.AttachThreadInput(fg_tid, cur_tid, True))
            attach_err = 0 if attached else k.GetLastError()
            try:
                if attached:
                    u.BringWindowToTop(h)
                    u.SetForegroundWindow(h)                        # 2)
            finally:
                if attached:
                    u.AttachThreadInput(fg_tid, cur_tid, False)
            if is_fg():
                return True

            u.keybd_event(VK_MENU, 0, 0, 0)                         # 3)
            try:
                u.BringWindowToTop(h)
                u.SetForegroundWindow(h)
            finally:
                u.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
            if is_fg():
                return True

            flags = 0x0001 | 0x0002 | 0x0010                        # 4) SWP_NOSIZE|NOMOVE|NOACTIVATE
            u.SetWindowPos(h, _wt.HWND(-1), 0, 0, 0, 0, flags)      # HWND_TOPMOST
            u.SetWindowPos(h, _wt.HWND(-2), 0, 0, 0, 0, flags)      # HWND_NOTOPMOST
            print(f"[window] 전경 전환 안 됨: fg={fg} fg_tid={fg_tid} attached={attached} "
                  f"attach_err={attach_err} now={u.GetForegroundWindow()}")
            return False
        except Exception as e:
            print(f"[window] 전경 전환 실패: {e}")
            return False
else:
    def set_shortcut_app_id(lnk) -> bool:
        return False

    def set_window_taskbar_identity(hwnd: int) -> bool:
        return False

    def force_foreground(hwnd: int) -> bool:
        return False


# ---------------------------------------------------------------------------
# 바로가기 만들기 (Windows): 바탕화면 / 시작 프로그램 / 시작 메뉴
# ---------------------------------------------------------------------------
_SHORTCUT_PLACES = {"Desktop": "바탕화면", "Startup": "시작 프로그램", "Programs": "시작 메뉴"}


def create_shortcut(where: str) -> "tuple[bool, str]":
    """where: 'Desktop' | 'Startup' | 'Programs'. (성공 여부, 메시지) 반환.
    Desktop/Startup 을 만들 때는 시작 메뉴(Programs) 바로가기도 함께 갱신한다 —
    Windows 는 실행 중인 창을 작업 표시줄에 고정할 때 AppID 가 같은 시작 메뉴 바로가기를 찾아 쓴다."""
    if not IS_WINDOWS:
        return False, "Windows에서만 만들 수 있어요."
    try:
        import base64
        import subprocess

        def q(s) -> str:                     # PowerShell 작은따옴표 문자열 이스케이프
            return str(s).replace("'", "''")

        ico = app_icon_path()
        ico_line = f"$s.IconLocation='{q(ico)},0';" if ico else ""
        places = [where] if where == "Programs" else [where, "Programs"]
        made = []
        for place in places:
            # 시작 프로그램(자동 실행)은 창 없이 트레이로 시작
            argv = launch_argv("--tray") if place == "Startup" else launch_argv()
            ps = (
                f"$d=[Environment]::GetFolderPath('{place}');"
                "$s=(New-Object -ComObject WScript.Shell)"
                ".CreateShortcut(\"$d\\핀캡처.lnk\");"
                f"$s.TargetPath='{q(argv[0])}';"
                f"$s.Arguments='{q(subprocess.list2cmdline(argv[1:]))}';"
                f"$s.WorkingDirectory='{q(app_dir())}';"
                f"{ico_line}"
                "$s.Save()"
            )
            enc = base64.b64encode(ps.encode("utf-16-le")).decode()
            r = subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", enc],
                               capture_output=True, timeout=30, creationflags=_NO_WINDOW)
            if r.returncode != 0:
                err = (r.stderr or b"").decode(errors="replace")[:300]
                return False, f"바로가기 생성 실패 ({_SHORTCUT_PLACES[place]}): {err}"
            set_shortcut_app_id(_special_folder(place) / "핀캡처.lnk")   # 작업 표시줄 고정용 AppID
            made.append(_SHORTCUT_PLACES[place])
        note = "" if FROZEN else " pythonw로 실행해서 터미널 창 없이 켜져요."
        return True, f"{' · '.join(made)}에 '핀캡처' 바로가기를 만들었어요.{note}"
    except Exception as e:
        return False, f"바로가기 생성 실패: {e}"


# ---------------------------------------------------------------------------
# 빠른 안내 / 정보
# ---------------------------------------------------------------------------
_WELCOME_MODES = (
    ("region", "영역 지정", "화면이 멈추면 드래그로 골라요. Esc나 우클릭으로 취소해요."),
    ("window", "창 캡처", "지금 쓰는 창을 찍어요. 일부가 가려져 있어도 창 내용이 나와요."),
    ("full", "전체 화면", "마우스가 있는 모니터 전체를 찍어요."),
    ("pin", "핀 고정", "고른 영역이 항상 위에 떠 있는 창이 돼요."),
    ("markup", "핀 표시", "고른 캡처나 맨 앞 핀에 화살표·네모·형광펜·모자이크·낙서를 그려요. Esc로 표시만 끝내요."),
    ("eyedropper", "스포이트", "화면 색을 찍어 HEX로 복사해요. RGB도 함께 보여 줘요."),
    ("ruler", "자", "두 점 사이의 픽셀 거리와 가로·세로를 재요. Shift는 가로·세로·45°예요."),
)


def _muted(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setWordWrap(True)
    lab.setStyleSheet(f"color:{TEXT_SUB}; font-weight: 400;")
    return lab


class WelcomeDialog(QDialog):
    """단축키와 핀 사용법. 첫 실행에 한 번, 그 뒤엔 메뉴에서만 연다."""

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} 빠른 안내")
        self.setWindowIcon(make_app_icon())
        self.setMinimumWidth(520)
        _polish_dialog(self)
        v = QVBoxLayout(self)
        v.setContentsMargins(22, 18, 22, 16)
        v.setSpacing(10)

        title = QLabel("핀캡처에 오신 것을 환영해요")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        v.addWidget(title)
        v.addWidget(_muted(
            "화면을 찍어 저장하고, 필요한 부분은 다른 창 위에 핀으로 남겨 둘 수 있어요. "
            "이 안내는 처음 한 번만 자동으로 열리고, 트레이 메뉴의 빠른 안내에서 언제든 다시 볼 수 있어요."
        ))

        g = QGroupBox("단축키")
        gv = QVBoxLayout(g)
        gv.setSpacing(8)
        hk = cfg.get("hotkeys") or {}
        for mode, label, desc in _WELCOME_MODES:
            line = QLabel(f"{label}    {hotkey_label(hk.get(mode, DEFAULTS['hotkeys'].get(mode, '')))}")
            line.setStyleSheet("font-weight: 700;")
            gv.addWidget(line)
            gv.addWidget(_muted(desc))
        v.addWidget(g)

        g2 = QGroupBox("핀은 이렇게 써요")
        gv2 = QVBoxLayout(g2)
        gv2.addWidget(_muted(
            "· 드래그로 옮기고, 마우스 휠로 크기를 조절해요. Ctrl+휠은 투명도예요.\n"
            "· 우클릭하면 글자 복사(글자·표·수식), 복사, 다른 이름으로 저장, 표시(낙서 포함), 스포이트, 자, 투명도, 클릭 통과 메뉴가 나와요.\n"
            "· 표시 중에는 핀 바로 아래 도구에서 고르고 드래그로 그려요. 낙서는 마우스를 따라 그려요. Shift는 가로·세로·45° 직선이에요. 색은 견본이나 다른 색에서 고르고, Ctrl+Z로 실행 취소해요. Esc는 핀을 닫지 않고 표시만 끝내요.\n"
            "· 클릭 통과를 켜면 핀을 누를 수 없어요. 트레이의 클릭 통과 해제나 단축키로 꺼 주세요.\n"
            "· 더블클릭이나 Esc로 닫아요. 닫은 핀은 단축키로 다시 열 수 있어요.\n"
            "· 핀 고정으로 찍은 이미지는 기본적으로 파일로 저장하지 않고 클립보드에만 복사해요. "
            "파일로 남기려면 설정에서 ‘핀 캡처도 파일로 저장해요’를 켜 주세요."
        ))
        v.addWidget(g2)
        v.addWidget(_muted(
            "창의 ×를 눌러도 트레이에서 단축키는 계속 동작해요. "
            "끝내려면 트레이 아이콘을 우클릭하고 종료를 눌러 주세요."
        ))

        btn = QPushButton("시작하기")
        btn.setObjectName("primary")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn)
        v.addLayout(row)


class AboutDialog(QDialog):
    """버전, 브랜드, 라이선스 요약, 서드파티 고지, 후원."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} 정보")
        self.setWindowIcon(make_app_icon())
        self.setMinimumWidth(460)
        _polish_dialog(self)
        v = QVBoxLayout(self)
        v.setContentsMargins(22, 18, 22, 16)
        v.setSpacing(10)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(make_app_icon(48).pixmap(48, 48))
        head.addWidget(icon, alignment=Qt.AlignmentFlag.AlignTop)
        titles = QVBoxLayout()
        name = QLabel(f"{APP_NAME}  {APP_VERSION}")
        name.setStyleSheet("font-size: 18px; font-weight: 700;")
        brand = QLabel(f"{APP_PUBLISHER}  ·  {APP_PUBLISHER_EN}")
        brand.setStyleSheet("font-size: 13px; font-weight: 600;")
        titles.addWidget(name)
        titles.addWidget(brand)
        titles.addWidget(_muted("화면을 캡처해 저장·복사하고, 필요한 부분은 화면 위에 핀으로 고정하는 Windows 트레이 앱이에요."))
        head.addLayout(titles, 1)
        v.addLayout(head)

        lic = QGroupBox("라이선스")
        lv = QVBoxLayout(lic)
        lv.addWidget(_muted(
            "All rights reserved.\n"
            "누구나 개인적·상업적 목적으로 무료로 사용할 수 있어요.\n"
            "코드의 재배포·수정·판매는 저작권자의 허락 없이 할 수 없어요."
        ))
        notices = QPushButton("서드파티 고지 열기")
        notices.setCursor(Qt.CursorShape.PointingHandCursor)
        notices.setToolTip("Qt, pynput 등 설치본에 포함된 오픈소스 고지를 열어요.")
        notices.clicked.connect(self._open_notices)
        lv.addWidget(notices, alignment=Qt.AlignmentFlag.AlignLeft)
        v.addWidget(lic)

        donate = QGroupBox("후원")
        dv = QVBoxLayout(donate)
        dv.addWidget(_muted(
            "핀캡처가 도움이 되었다면, 부담 없이 후원할 수 있어요. "
            "후원하지 않아도 모든 기능은 그대로 무료예요."
        ))
        gift = QPushButton("후원하기")
        gift.setCursor(Qt.CursorShape.PointingHandCursor)
        gift.setToolTip("브라우저에서 Ko-fi 페이지를 열어요.")
        gift.clicked.connect(open_kofi)
        dv.addWidget(gift, alignment=Qt.AlignmentFlag.AlignLeft)
        v.addWidget(donate)

        close = QPushButton("닫기")
        close.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(close)
        v.addLayout(row)

    def _open_notices(self):
        path = third_party_notices_path()
        if not path.is_file():
            QMessageBox.information(
                self, "서드파티 고지",
                "고지 파일을 찾지 못했어요.\n설치 폴더의 THIRD_PARTY_NOTICES.txt를 확인해 주세요.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


# ---------------------------------------------------------------------------
# 설정 창
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, hotkey_ok: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} 설정")
        self.setWindowIcon(make_app_icon())
        self.setMinimumWidth(760)
        _polish_dialog(self)
        self._cfg = cfg
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 14, 16, 12)
        v.setSpacing(8)

        intro = _muted("저장 위치, 캡처한 뒤의 동작, 전역 단축키를 바꿔요. 확인을 눌러야 저장돼요.")
        v.addWidget(intro)

        cols = QHBoxLayout()
        cols.setSpacing(12)
        left = QVBoxLayout()
        right = QVBoxLayout()

        g1 = QGroupBox("저장")
        f1 = QFormLayout(g1)
        f1.setHorizontalSpacing(10)
        f1.setVerticalSpacing(8)
        f1.addRow(_muted("캡처 파일이 쌓이는 곳이에요. 사진 폴더가 클라우드에 있으면 캡처도 함께 동기화돼요."))
        h = QHBoxLayout()
        self.ed_dir = QLineEdit(cfg["save_dir"])
        self.ed_dir.setToolTip("캡처 이미지를 저장할 폴더예요.")
        btn_browse = QPushButton("찾아보기")
        btn_browse.setToolTip("저장할 폴더를 골라 주세요.")
        btn_browse.clicked.connect(self._browse)
        h.addWidget(self.ed_dir)
        h.addWidget(btn_browse)
        f1.addRow("저장 폴더", h)
        self.ed_prefix = QLineEdit(cfg["filename_prefix"])
        self.ed_prefix.setToolTip("파일 이름 앞부분이에요. 뒤에는 날짜와 시각이 붙어요.")
        f1.addRow("파일 이름", self.ed_prefix)
        self.cb_format = QComboBox()
        self.cb_format.addItems(["png", "jpg"])
        self.cb_format.setCurrentText(cfg["file_format"])
        self.cb_format.setToolTip("png는 그대로 저장하고, jpg는 용량이 더 작아요.")
        f1.addRow("파일 형식", self.cb_format)
        self.sp_quality = QSpinBox()
        self.sp_quality.setRange(50, 100)
        self.sp_quality.setValue(int(cfg["jpg_quality"]))
        self.sp_quality.setToolTip("jpg로 저장할 때의 화질이에요. png에는 적용되지 않아요.")
        f1.addRow("JPG 품질", self.sp_quality)
        left.addWidget(g1)

        g_sc = QGroupBox("바로가기")
        sc = QVBoxLayout(g_sc)
        sc.addWidget(_muted("Windows 바탕화면, 시작 메뉴, 로그인할 때 자동 실행을 등록해요."))
        btn_desktop = QPushButton("바탕화면 아이콘 만들기")
        btn_startup = QPushButton("부팅 시 자동 실행 등록")
        btn_desktop.setToolTip("바탕화면과 시작 메뉴에 핀캡처 바로가기를 만들어요.")
        btn_startup.setToolTip("Windows에 로그인할 때 창 없이 트레이로 시작하게 등록해요.")
        btn_desktop.clicked.connect(lambda: self._make_shortcut("Desktop"))
        btn_startup.clicked.connect(lambda: self._make_shortcut("Startup"))
        if not IS_WINDOWS:
            btn_desktop.setEnabled(False)
            btn_startup.setEnabled(False)
            btn_desktop.setToolTip("Windows에서만 만들 수 있어요.")
            btn_startup.setToolTip("Windows에서만 만들 수 있어요.")
        sc.addWidget(btn_desktop)
        sc.addWidget(btn_startup)
        left.addWidget(g_sc)

        g_math = QGroupBox("수식")
        math_lay = QVBoxLayout(g_math)
        self.lbl_math = _muted("")
        self.btn_math_remove = QPushButton("수식 기능 제거")
        self.btn_math_remove.setToolTip("받아 둔 수식 모델과 실행 구성 요소를 지워요. 글자와 표는 그대로예요.")
        self.btn_math_remove.clicked.connect(self._remove_math)
        math_lay.addWidget(self.lbl_math)
        math_lay.addWidget(self.btn_math_remove)
        self._refresh_math_row()
        left.addWidget(g_math)
        left.addStretch(1)

        g2 = QGroupBox("캡처할 때")
        v2 = QVBoxLayout(g2)
        self.ck_autosave = QCheckBox("캡처하면 파일로 저장해요")
        self.ck_clip = QCheckBox("캡처하면 클립보드에 복사해요")
        self.ck_notify = QCheckBox("캡처 후 트레이 알림을 보여 줘요")
        self.ck_hide = QCheckBox("캡처하는 동안 이 창을 숨겨요")
        self.ck_pin_all = QCheckBox("모든 캡처를 핀으로도 고정해요")
        self.ck_pin_save = QCheckBox("핀 캡처도 파일로 저장해요")
        self.ck_viewer = QCheckBox("캡처 후 이 창을 열어 방금 찍은 이미지를 보여 줘요")
        tips = {
            self.ck_autosave: "영역·창·전체 화면 캡처를 저장 폴더에 바로 저장해요.",
            self.ck_clip: "캡처한 이미지를 클립보드에 넣어, 다른 곳에 바로 붙여 넣을 수 있어요.",
            self.ck_notify: "캡처가 끝나면 트레이에 짧은 알림을 띄워요.",
            self.ck_hide: "캡처하는 동안 핀캡처 창이 화면이나 찍힌 이미지에 나오지 않아요.",
            self.ck_pin_all: "영역·창·전체 화면으로 찍은 이미지도 핀으로 띄워요.",
            self.ck_pin_save: "핀 고정으로 찍은 이미지도 파일로 남겨요. 끄면 클립보드에만 복사해요.",
            self.ck_viewer: "캡처가 끝나면 이 창을 열어 방금 찍은 이미지를 크게 보여 줘요.",
        }
        for ck, key in [(self.ck_autosave, "autosave"), (self.ck_clip, "clipboard"),
                        (self.ck_notify, "notify"), (self.ck_hide, "hide_during_capture"),
                        (self.ck_pin_all, "pin_after_capture"), (self.ck_pin_save, "pin_autosave"),
                        (self.ck_viewer, "show_viewer_after_capture")]:
            ck.setChecked(bool(cfg[key]))
            ck.setToolTip(tips[ck])
            v2.addWidget(ck)
        recent_row = QHBoxLayout()
        recent_row.addWidget(QLabel("닫은 핀 보관 개수"))
        self.sp_recent = QSpinBox()
        self.sp_recent.setRange(1, 50)
        self.sp_recent.setValue(_clamp_recent_limit(cfg.get("recent_pin_limit", 10)))
        self.sp_recent.setToolTip("닫은 핀을 다시 열 수 있게 임시로 보관하는 개수예요.")
        recent_row.addWidget(self.sp_recent)
        recent_row.addStretch(1)
        v2.addLayout(recent_row)
        right.addWidget(g2)

        cols.addLayout(left, 1)
        cols.addLayout(right, 1)
        v.addLayout(cols)

        g3 = QGroupBox("전역 단축키" + ("" if hotkey_ok else "  (현재 사용 불가)"))
        grid = QGridLayout(g3)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        self.ed_hk = {}
        labels = (("region", "영역 지정"), ("window", "창 캡처"),
                  ("full", "전체 화면"), ("pin", "핀 고정"),
                  ("reopen_pin", "최근 핀 다시 열기"), ("clickthrough", "클릭 통과 해제"),
                  ("markup", "핀 표시"), ("eyedropper", "스포이트"),
                  ("ruler", "자"))
        for i, (mode, label) in enumerate(labels):
            ed = QLineEdit(cfg["hotkeys"].get(mode, ""))
            ed.setPlaceholderText("비우면 사용 안 함")
            ed.setToolTip("예: <ctrl>+<alt>+a")
            self.ed_hk[mode] = ed
            grid.addWidget(QLabel(label), i // 2, (i % 2) * 2)
            grid.addWidget(ed, i // 2, (i % 2) * 2 + 1)
        tip_row = (len(labels) + 1) // 2
        tip = _muted("형식은 <ctrl>+<alt>+a, <print_screen> 이에요. 비우면 그 단축키를 쓰지 않아요. "
                     "다른 프로그램과 겹치면 여기 조합을 바꿔 주세요.")
        grid.addWidget(tip, tip_row, 0, 1, 4)
        btn_reset = QPushButton("단축키를 기본값으로")
        btn_reset.setToolTip(
            "영역 Ctrl+Alt+A, 창 Ctrl+Alt+W, 전체 Ctrl+Alt+F, 핀 Ctrl+Alt+Q, "
            "최근 핀 Ctrl+Alt+R, 클릭 통과 해제 Ctrl+Alt+X, "
            "표시 Ctrl+Alt+M, 스포이트 Ctrl+Alt+C, 자 Ctrl+Alt+D 로 되돌려요.")
        btn_reset.clicked.connect(self._reset_hotkeys)
        grid.addWidget(btn_reset, tip_row + 1, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        v.addWidget(g3)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                              | QDialogButtonBox.StandardButton.Cancel)
        ok_btn = bb.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = bb.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn is not None:
            ok_btn.setText("확인")
            ok_btn.setObjectName("primary")
        if cancel_btn is not None:
            cancel_btn.setText("취소")
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def _refresh_math_row(self):
        if math_component_present():
            self.lbl_math.setText("수식 기능이 설치되어 있어요.")
            self.btn_math_remove.setEnabled(True)
        else:
            self.lbl_math.setText("아직 설치하지 않았어요. 글자 복사에서 수식을 고르면 설치할 수 있어요.")
            self.btn_math_remove.setEnabled(False)

    def _remove_math(self):
        if not math_component_present():
            self._refresh_math_row()
            return
        if not confirm_math_remove(self):
            return
        remove_math_component()
        self._refresh_math_row()

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "저장할 폴더를 골라 주세요", self.ed_dir.text())
        if d:
            self.ed_dir.setText(d)

    def _reset_hotkeys(self):
        for mode, ed in self.ed_hk.items():
            ed.setText(DEFAULTS["hotkeys"][mode])

    def _make_shortcut(self, where: str):
        ok, msg = create_shortcut(where)
        if ok:
            QMessageBox.information(self, "바로가기", msg)
        else:
            QMessageBox.warning(self, "바로가기", msg)

    def _accept(self):
        # 단축키 형식 검증 (pynput 있을 때만)
        try:
            from pynput import keyboard
            for mode, ed in self.ed_hk.items():
                s = ed.text().strip()
                if s:
                    try:
                        keyboard.HotKey.parse(s)
                    except Exception:
                        QMessageBox.warning(self, "단축키 형식 오류",
                                            f"'{s}' 는 올바른 형식이 아니에요.\n예: <ctrl>+<alt>+a")
                        return
        except Exception:
            pass
        pending = {mode: ed.text().strip() for mode, ed in self.ed_hk.items()}
        clash = duplicate_hotkey(pending)
        if clash:
            QMessageBox.warning(self, "단축키 겹침",
                                f"'{clash}' 가 두 기능에 겹쳐요. 서로 다르게 정해 주세요.")
            return
        c = self._cfg
        c["save_dir"] = self.ed_dir.text().strip() or _default_save_dir()
        c["filename_prefix"] = self.ed_prefix.text().strip() or "캡처"
        c["file_format"] = self.cb_format.currentText()
        c["jpg_quality"] = self.sp_quality.value()
        c["autosave"] = self.ck_autosave.isChecked()
        c["clipboard"] = self.ck_clip.isChecked()
        c["notify"] = self.ck_notify.isChecked()
        c["hide_during_capture"] = self.ck_hide.isChecked()
        c["pin_after_capture"] = self.ck_pin_all.isChecked()
        c["pin_autosave"] = self.ck_pin_save.isChecked()
        c["show_viewer_after_capture"] = self.ck_viewer.isChecked()
        c["recent_pin_limit"] = self.sp_recent.value()
        for mode, ed in self.ed_hk.items():
            c["hotkeys"][mode] = ed.text().strip()
        self.accept()


# ---------------------------------------------------------------------------
# 메인 툴바
# ---------------------------------------------------------------------------
_TOOL_QSS = f"""
    QToolButton {{
        border: none; border-radius: 8px; color: {TEXT};
        font-size: 12px; background: transparent; padding: 0px;
    }}
    QToolButton:hover {{ background: #EDF3FE; }}
    QToolButton:pressed {{ background: #DDE9FD; }}
    QToolButton:disabled {{ color: #9AA3B2; background: transparent; }}
"""

SECTION_TITLE_QSS = "font-size: 13px; font-weight: 700; margin: 0px; padding: 0px;"


class ToolButton(QToolButton):
    """캡처 줄의 글자 있는 버튼. 너비·높이는 8px 격자."""

    def __init__(self, icon: QIcon, text: str, tip: str = ""):
        super().__init__()
        self.setIcon(icon)
        self.setText(text)
        self.setToolTip(tip or text)
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(80, 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(_TOOL_QSS)


class IconToolButton(QToolButton):
    """캡처 줄 오른쪽의 아이콘만 있는 버튼. 툴팁에 이름과 단축키를 적는다."""

    def __init__(self, icon: QIcon, name: str):
        super().__init__()
        self.setIcon(icon)
        self.setText(name)
        self.setAccessibleName(name)
        self.setToolTip(name)
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(_TOOL_QSS)


class MainToolbar(QWidget):
    """핀캡처 메인 창: 위쪽 = 캡처 기능함, 아래 = 보관함(미리보기 + 기록 리스트)."""

    def __init__(self, cfg: dict, server: "QLocalServer | None" = None):
        super().__init__(None)
        apply_ui_font()
        self.cfg = cfg
        self._server = server              # 단일 인스턴스 수신용
        if server is not None:
            server.newConnection.connect(self._on_singleton_msg)
        try:   # .py 갱신 감지(개발용). EXE 는 설치 프로그램이 교체·재실행하므로 사용 안 함
            self._script_mtime = None if FROZEN else Path(__file__).stat().st_mtime
        except Exception:
            self._script_mtime = None
        self._capturing = False
        self._was_visible = True
        self._pins = []
        self._recent = RecentPinStore(limit=cfg.get("recent_pin_limit", 10))
        self._notice_toast = None
        self._ocr_running = False
        self._session = None
        self._tray = None
        self._toast_shown = False
        self.history = []              # HistoryEntry 목록 (0 = 최신)
        self._cur_img = None           # 미리보기에 떠 있는 이미지 (현재 항목)
        self._scan_existing_files()    # 저장 폴더의 기존 캡처를 기록에 채움

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(make_app_icon())
        self.setMinimumSize(800, 520)
        size = cfg.get("window_size")
        if isinstance(size, (list, tuple)) and len(size) == 2:
            self.resize(int(size[0]), int(size[1]))
        else:
            self.resize(1080, 700)

        self._build_ui()
        if QSystemTrayIcon.isSystemTrayAvailable():
            self._build_tray()

        # 전역 단축키
        self.hotkeys = HotkeyManager()
        self.hotkeys.triggered.connect(self._on_hotkey)
        self.hotkeys.restart(cfg["hotkeys"])
        self._update_tooltips()

        # 활성 창 추적 (창 캡처용: 이 창이 포커스를 가져도 직전 앱 창을 기억)
        if IS_WINDOWS:
            self._last_ext_hwnd = None
            self._fg_timer = QTimer(self)
            self._fg_timer.timeout.connect(self._track_foreground)
            self._fg_timer.start(400)

        # 위치 복원 (화면 밖으로 나가지 않게 보정)
        pos = cfg.get("toolbar_pos")
        if isinstance(pos, (list, tuple)) and len(pos) == 2:
            self.move(int(pos[0]), int(pos[1]))
            self._clamp_to_screen()

        self.populate()

    def _clamp_to_screen(self):
        scr = (QGuiApplication.screenAt(self.frameGeometry().center())
               or QGuiApplication.primaryScreen())
        g = scr.availableGeometry()
        x = min(max(self.x(), g.left()), max(g.left(), g.right() - self.width() + 1))
        y = min(max(self.y(), g.top()), max(g.top(), g.bottom() - self.height() + 1))
        self.move(x, y)

    # ---------- UI ----------
    def _build_ui(self):
        self.setObjectName("mainRoot")
        self.setStyleSheet(f"""
            #mainRoot {{ background: white; color: {TEXT}; }}
            QPushButton {{
                padding: 4px 12px; border: 1px solid {BORDER}; color: {TEXT};
                border-radius: 6px; background: {BG}; font-size: 12px;
            }}
            QPushButton:hover {{ background: #EDF3FE; }}
            QPushButton:pressed {{ background: #DDE9FD; }}
            QPushButton#actionBtn {{
                padding: 0px 8px;
            }}
            QToolButton#headerBtn {{
                border: 1px solid {BORDER}; border-radius: 6px; background: {BG};
                color: {TEXT}; padding: 4px 10px; font-size: 12px;
            }}
            QToolButton#headerBtn:hover {{ background: #EDF3FE; }}
            QListWidget {{
                background: #F2F4F8; border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; color: {TEXT_SUB};
            }}
            QListWidget::item {{ border-radius: 6px; padding: 3px; }}
            QListWidget::item:selected {{ background: #D6E4FC; color: {TEXT}; }}
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 8, 16, 8)
        root.setSpacing(8)

        head = QHBoxLayout()
        head.setSpacing(8)
        mark = QLabel()
        mark.setPixmap(make_app_icon(24).pixmap(24, 24))
        mark.setFixedSize(24, 24)
        head.addWidget(mark, alignment=Qt.AlignmentFlag.AlignVCenter)
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 16px; font-weight: 700; margin: 0; padding: 0;")
        title.setFixedHeight(32)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        head.addWidget(title, alignment=Qt.AlignmentFlag.AlignVCenter)
        head.addStretch(1)
        self.btn_help = self._header_btn("help", "안내", "단축키와 핀 사용법을 다시 봐요.", self.show_welcome)
        self.btn_about = self._header_btn("info", "정보", "버전, 만든 이, 라이선스, 후원을 봐요.", self.show_about)
        self.btn_settings = self._header_btn("gear", "설정", "저장 폴더, 동작, 단축키를 바꿔요.", self.open_settings)
        for b in (self.btn_help, self.btn_about, self.btn_settings):
            head.addWidget(b, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(head)

        cap = QHBoxLayout()
        cap.setSpacing(8)
        self.cap_title = QLabel("캡처")
        self.cap_title.setObjectName("sectionTitle")
        self.cap_title.setStyleSheet(SECTION_TITLE_QSS)
        self.cap_title.setFixedHeight(24)
        self.cap_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        cap.addWidget(self.cap_title, alignment=Qt.AlignmentFlag.AlignVCenter)
        cap.addSpacing(8)
        self.btn_region = ToolButton(make_icon("region", size=20), "영역 지정")
        self.btn_window = ToolButton(make_icon("window", size=20), "창 캡처")
        self.btn_full = ToolButton(make_icon("full", size=20), "전체 화면")
        self.btn_pin = ToolButton(make_icon("pin", size=20), "핀 고정")
        self.btn_region.clicked.connect(lambda: self.capture("region"))
        self.btn_window.clicked.connect(lambda: self.capture("window"))
        self.btn_full.clicked.connect(lambda: self.capture("full"))
        self.btn_pin.clicked.connect(lambda: self.capture("pin"))
        for b in (self.btn_region, self.btn_window, self.btn_full):
            cap.addWidget(b, alignment=Qt.AlignmentFlag.AlignVCenter)
        cap.addWidget(self._vsep(), alignment=Qt.AlignmentFlag.AlignVCenter)
        cap.addWidget(self.btn_pin, alignment=Qt.AlignmentFlag.AlignVCenter)
        cap.addStretch(1)
        cap.addWidget(self._vsep(), alignment=Qt.AlignmentFlag.AlignVCenter)
        self.btn_markup = IconToolButton(make_icon("markup", size=20), "핀에 그리기")
        self.btn_eyedropper = IconToolButton(make_icon("eyedropper", size=20), "스포이트")
        self.btn_ruler = IconToolButton(make_icon("ruler", size=20), "자")
        self.btn_ocr = IconToolButton(make_icon("ocr", size=20), "글자 복사")
        self.btn_reopen = IconToolButton(make_icon("reopen", size=20), "최근 핀")
        # clicked 는 체크 여부(bool)를 넘긴다. 인자를 받는 슬롯에 그대로 연결하면
        # 글자 모드가 False 가 되거나, 인자를 받지 않는 람다는 예외로 조용히 무시된다.
        self.btn_markup.clicked.connect(lambda _checked=False: self._markup_current())
        self.btn_eyedropper.clicked.connect(lambda _checked=False: self.start_inspect("eyedropper"))
        self.btn_ruler.clicked.connect(lambda _checked=False: self.start_inspect("ruler"))
        self.btn_ocr.clicked.connect(lambda _checked=False: self._ocr_current())
        self.btn_ocr.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_ocr.customContextMenuRequested.connect(self._popup_ocr_menu)
        self.btn_reopen.clicked.connect(lambda _checked=False: self.reopen_recent_pin())
        for b in (self.btn_markup, self.btn_eyedropper, self.btn_ruler, self.btn_ocr, self.btn_reopen):
            cap.addWidget(b, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(cap)

        self._divider = QFrame()
        self._divider.setObjectName("sectionDivider")
        self._divider.setFrameShape(QFrame.Shape.HLine)
        self._divider.setFixedHeight(1)
        self._divider.setStyleSheet(f"color:{BORDER}; background:{BORDER}; border: none; max-height: 1px;")
        root.addWidget(self._divider)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.hist_title = QLabel("보관함")
        self.hist_title.setObjectName("sectionTitle")
        self.hist_title.setStyleSheet(SECTION_TITLE_QSS)
        self.hist_title.setFixedHeight(24)
        self.hist_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        bar.addWidget(self.hist_title, alignment=Qt.AlignmentFlag.AlignVCenter)
        bar.addSpacing(8)
        self.b_copy = self._action_btn("copy", "클립보드에 복사",
                                       "선택한 캡처를 클립보드에 복사해요. 여러 개면 파일 묶음으로 복사해요.")
        self.b_save = self._action_btn("save", "다른 이름으로 저장",
                                       "선택한 캡처를 다른 곳에 저장해요. 여러 개면 폴더를 하나 골라 한꺼번에 저장해요.")
        self.b_pin_sel = self._action_btn("pin", "화면에 고정",
                                          "선택한 캡처를 항상 위에 보이는 핀으로 띄워요.")
        self.b_folder = self._action_btn("folder", "저장 폴더 열기",
                                         "캡처가 저장되는 폴더를 열어요.")
        self.b_remove = self._action_btn("trash", "목록에서 제거",
                                         "목록에서만 빼요. 저장해 둔 파일은 지우지 않아요.")
        self.b_copy.clicked.connect(self._copy_selected)
        self.b_save.clicked.connect(self._save_selected_as)
        self.b_pin_sel.clicked.connect(self._pin_selected)
        self.b_folder.clicked.connect(self._open_folder)
        self.b_remove.clicked.connect(self._remove_selected)
        for b in (self.b_copy, self.b_save, self.b_pin_sel, self.b_folder):
            bar.addWidget(b, alignment=Qt.AlignmentFlag.AlignVCenter)
        bar.addStretch(1)
        bar.addWidget(self.b_remove, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(bar)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        split.setHandleWidth(8)
        self.preview = PreviewPane()
        self.preview.setMinimumSize(320, 160)
        self.listw = QListWidget()
        self.listw.setViewMode(QListView.ViewMode.IconMode)
        self.listw.setResizeMode(QListView.ResizeMode.Adjust)
        self.listw.setMovement(QListView.Movement.Static)
        self.listw.setIconSize(QSize(HistoryEntry.THUMB_W, 112))
        self.listw.setGridSize(QSize(HistoryEntry.THUMB_W + 32, 176))
        self.listw.setWordWrap(True)
        list_w = HistoryEntry.THUMB_W + 48   # 한 줄. 창을 늘려도 미리보기가 넓어진다
        self.listw.setMinimumWidth(list_w)
        self.listw.setMaximumWidth(list_w)
        self.listw.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listw.setToolTip("클릭하면 크게 봐요. Ctrl이나 Shift를 누른 채 클릭하거나 드래그하면 여러 개를 골라요. "
                              "Ctrl+A는 전체, Ctrl+C는 복사, Delete는 목록에서 제거예요. "
                              "목록에서 빼도 파일은 지워지지 않아요.")
        self.listw.currentRowChanged.connect(self._on_row_changed)
        self.listw.itemSelectionChanged.connect(self._refresh_info)
        for seq, slot in ((QKeySequence.StandardKey.Copy, self._copy_selected),
                          (QKeySequence(Qt.Key.Key_Delete), self._remove_selected),
                          (QKeySequence.StandardKey.SelectAll, self.listw.selectAll)):
            sc = QShortcut(seq, self)
            sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            sc.activated.connect(slot)
        split.addWidget(self.preview)
        split.addWidget(self.listw)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 0)
        split.setSizes([760, list_w])
        root.addWidget(split, 1)

        self.info = QLabel("")
        self.info.setFixedHeight(24)
        self.info.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.info.setStyleSheet(f"color:{TEXT_SUB}; font-size: 12px; margin: 0; padding: 0;")
        root.addWidget(self.info)

    def _header_btn(self, kind: str, text: str, tip: str, slot) -> QToolButton:
        b = QToolButton()
        b.setObjectName("headerBtn")
        b.setIcon(make_icon(kind, TEXT, 16))
        b.setIconSize(QSize(16, 16))
        b.setText(text)
        b.setToolTip(tip)
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b.setFixedHeight(32)
        b.setIconSize(QSize(16, 16))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(slot)
        return b

    def _vsep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedSize(1, 32)
        sep.setStyleSheet(f"color:{BORDER}; background:{BORDER}; border: none;")
        return sep

    def _action_btn(self, kind: str, text: str, tip: str) -> QPushButton:
        b = QPushButton(make_icon(kind, TEXT, 16), text)
        b.setObjectName("actionBtn")
        b.setIconSize(QSize(16, 16))
        b.setFixedHeight(32)
        b.setToolTip(tip)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def _hotkey_line(self, mode: "str | None") -> str:
        if not mode:
            return "단축키: 없음"
        combo = (self.cfg.get("hotkeys") or {}).get(mode, "")
        if combo:
            return f"단축키: {hotkey_label(combo)}"
        return "단축키: 없음 (설정에서 지정할 수 있어요)"

    def _update_tooltips(self):
        hk_tips = (
            ("region", self.btn_region, "영역 지정", "드래그로 영역을 골라 캡처해요. Esc나 우클릭으로 취소해요."),
            ("window", self.btn_window, "창 캡처", "지금 쓰는 창을 캡처해요. 일부가 가려져 있어도 창 내용이 나와요."),
            ("full", self.btn_full, "전체 화면", "마우스가 있는 모니터 전체를 캡처해요."),
            ("pin", self.btn_pin, "핀 고정", "영역을 고르면 그 부분이 항상 위에 떠 있는 핀이 돼요."),
            ("markup", self.btn_markup, "핀에 그리기",
             "보관함에서 고른 캡처나 맨 앞 핀에 화살표·네모·형광펜·모자이크·낙서를 그려요. 낙서 중 Shift는 직선이에요."),
            ("eyedropper", self.btn_eyedropper, "스포이트", "화면 색을 찍어 HEX로 복사해요. RGB도 보여 줘요."),
            ("ruler", self.btn_ruler, "자", "두 점 사이의 픽셀 거리와 가로·세로를 재요. Shift는 가로·세로·45°예요."),
            (None, self.btn_ocr, "글자 복사",
             "보관함에서 고른 캡처나 맨 앞 핀의 글자를 문단으로 맞춰 복사해요. 우클릭하면 글자, 표, 수식을 골라요."),
            ("reopen_pin", self.btn_reopen, "최근 핀", "가장 최근에 닫은 핀을 다시 열어요."),
        )
        empty = {
            self.btn_markup: "그릴 캡처나 핀이 없어요. 보관함에서 고르거나 핀을 띄워 주세요.",
            self.btn_ocr: "글자를 읽을 캡처나 핀이 없어요. 보관함에서 고르거나 핀을 띄워 주세요.",
        }
        missing = not self._has_tool_target()
        no_recent = self._recent.count() == 0
        for mode, btn, name, text in hk_tips:
            lines = [name, text, self._hotkey_line(mode)]
            if missing and btn in empty:
                lines.append(empty[btn])
            elif btn is self.btn_reopen and no_recent:
                lines.append("다시 열 핀이 없어요. 핀을 닫으면 다시 열 수 있어요.")
            btn.setToolTip("\n".join(lines))

    def _has_tool_target(self) -> bool:
        img = getattr(self, "_cur_img", None)
        if img is not None and not img.isNull():
            return True
        return self._front_pin() is not None

    def _sync_pin_tools(self) -> None:
        """다섯 아이콘은 항상 누를 수 있다. 조건이 없으면 눌러서 이유를 본다.
        끄면 클릭이 슬롯까지 가지 않아 안내가 나오지 않는다."""
        for btn in (self.btn_markup, self.btn_eyedropper, self.btn_ruler,
                    self.btn_ocr, self.btn_reopen):
            btn.setEnabled(True)
        self._update_tooltips()

    def _pin_matching(self, img: QImage):
        """같은 객체(cacheKey)를 먼저 찾고, 없으면 픽셀 지문이 같은 핀.
        보관함 파일을 다시 읽으면 cacheKey 만 달라지고 화면의 핀은 그대로다."""
        if img is None or img.isNull():
            return None
        key = img.cacheKey()
        sig = image_signature(img)
        fuzzy = None
        for pin in reversed(self._pins):
            try:
                if not pin.isVisible():
                    continue
                if pin._img.cacheKey() == key:
                    return pin
                if fuzzy is None and sig and sig == getattr(pin, "_img_sig", None):
                    fuzzy = pin
            except RuntimeError:
                continue
        return fuzzy

    def _pin_for_tool(self):
        """선택된 보관함 캡처를 우선하고, 없으면 맨 앞 핀. 캡처는 핀으로 띄운 뒤 쓴다."""
        img = getattr(self, "_cur_img", None)
        if img is not None and not img.isNull():
            found = self._pin_matching(img)
            if found is not None:
                return found
            return self._make_pin(img, None)
        return self._front_pin()

    def _markup_current(self):
        return self.start_pin_markup()

    def _popup_ocr_menu(self, pos):
        """글자 복사 아이콘의 우클릭. 왼쪽 클릭은 예전처럼 글자 모드만 실행한다."""
        if not self.btn_ocr.isEnabled():
            return
        menu, acts = build_ocr_mode_menu(self.btn_ocr)
        chosen = menu.exec(self.btn_ocr.mapToGlobal(pos))
        for mode, act in acts.items():
            if chosen == act:
                self._ocr_current(mode)
                break
        menu.deleteLater()

    def _stop_math_until_installed(self):
        """수식이 없으면 설치를 묻는다. 핀의 copy_ocr 가 다시 묻지 않게, 직접 인식할 때만 쓴다."""
        if math_status() == "ok":
            return None
        ok, note = ensure_math_installed(self)
        if ok:
            return None
        self._show_notice(note, msec=4200)
        return OcrResult(False, "", note)

    def _announce_ocr(self, text: str, msec: int = 1800) -> None:
        """읽는 중은 토스트만. 결과는 토스트가 본이고, 트레이 풍선은 설정이 켜져 있을 때만 덧붙인다."""
        if text == OCR_BUSY_MSG:
            self._show_toast(text, msec)
        else:
            self._show_notice(text, msec=msec)

    def _ocr_current(self, mode: str = "text"):
        if self._ocr_running:
            self._announce_ocr(OCR_BUSY_MSG)
            return OcrResult(False, "", OCR_BUSY_MSG)
        self._ocr_running = True
        try:
            return self._ocr_current_body(mode)
        except Exception as exc:
            _log_exc("ocr", exc, "글자 복사")
            try:
                self._show_notice(OCR_FAILED_MSG, msec=4200)
            except Exception as again:
                _log_exc("ocr", again, "안내 표시 실패")
            return OcrResult(False, "", OCR_FAILED_MSG)
        finally:
            self._ocr_running = False

    def _ocr_current_body(self, mode: str = "text"):
        img = getattr(self, "_cur_img", None)
        if img is not None and not img.isNull():
            pin = self._pin_matching(img)
            if pin is not None:
                self._present_pin_soon(pin)
                if mode == "text":
                    return pin.copy_ocr()
                return pin.copy_ocr(mode)
            if mode == "math":
                stopped = self._stop_math_until_installed()
                if stopped is not None:
                    return stopped
            return run_ocr(img, mode, self._announce_ocr)
        pin = self._front_pin()
        if pin is None:
            note = "글자를 읽을 캡처나 핀이 없어요. 보관함에서 고르거나 핀을 띄워 주세요."
            self._show_notice(note)
            return OcrResult(False, "", note)
        self._present_pin_soon(pin)
        if mode == "text":
            return pin.copy_ocr()
        return pin.copy_ocr(mode)

    def _tray_menu(self) -> QMenu:
        """트레이 우클릭 메뉴. 캡처, 안내, 후원을 나눠 두었어요."""
        m = QMenu()
        self._act_toggle = m.addAction(
            "창 숨기기" if self.isVisible() else "창 열기", self._toggle_window)
        m.addSeparator()
        m.addAction("영역 지정", lambda: self.capture("region"))
        m.addAction("창 캡처", lambda: self.capture("window"))
        m.addAction("전체 화면", lambda: self.capture("full"))
        m.addAction("핀 고정", lambda: self.capture("pin"))
        m.addSeparator()
        self._act_reopen = m.addAction("최근 핀 다시 열기", self.reopen_recent_pin)
        self._act_release_ct = m.addAction("클릭 통과 해제", self.clear_click_through)
        m.addSeparator()
        m.addAction("빠른 안내", self.show_welcome)
        m.addAction("설정", self.open_settings)
        m.addAction("정보", self.show_about)
        m.addAction("후원하기", open_kofi)
        m.addSeparator()
        m.addAction("다시 시작" if FROZEN else "다시 시작 (업데이트 적용)", self.restart_app)
        m.addAction("종료", self.quit_app)
        m.aboutToShow.connect(self._sync_tray_labels)
        return m

    def _sync_tray_labels(self):
        if getattr(self, "_act_toggle", None) is not None:
            self._act_toggle.setText("창 숨기기" if self.isVisible() else "창 열기")

    def _build_tray(self):
        self._tray = QSystemTrayIcon(make_app_icon(), self)
        self._tray.setToolTip(f"{APP_NAME} {APP_VERSION}  ·  {APP_PUBLISHER_EN}")
        self._tray.setContextMenu(self._tray_menu())
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def show_welcome(self):
        """빠른 안내. 닫으면 welcome_seen 을 저장해서 다음 실행부터는 자동으로 열지 않아요."""
        if getattr(self, "_welcome_open", False):
            return
        self._welcome_open = True
        try:
            WelcomeDialog(self.cfg, self).exec()
        finally:
            self._welcome_open = False
            self.cfg["welcome_seen"] = True
            save_config(self.cfg)

    def show_about(self):
        AboutDialog(self).exec()

    # ---------- 창 동작 ----------
    def closeEvent(self, e):
        if self._tray is not None:
            e.ignore()
            self.hide()
            self._save_geometry()
            if not self._toast_shown:
                self._toast_shown = True
                self._tray.showMessage(
                    APP_NAME,
                    "트레이에서 계속 실행 중이에요. 단축키도 그대로 동작하고, 끝내려면 트레이 아이콘을 우클릭한 뒤 종료를 눌러 주세요.",
                    QSystemTrayIcon.MessageIcon.Information, 3000)
        else:
            self.quit_app()
            e.accept()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape and self._tray is not None:
            self.hide()
        else:
            super().keyPressEvent(e)

    def _bring_to_front(self, _retry: int = 3):
        """창을 보이고 전경으로. (캡처 직후·트레이 클릭·바로가기 재실행 공통)
        Windows 에선 Qt 의 activateWindow 가 먼저 실패하면 잠깐 전경 잠금이 걸리므로 우회 전환을 먼저 한다."""
        self.show()
        if self.isMinimized():
            self.showNormal()
        self.raise_()
        if IS_WINDOWS:
            if not force_foreground(int(self.winId())) and _retry > 0:
                QTimer.singleShot(150, lambda: self._bring_to_front(_retry - 1))
                return
        self.activateWindow()

    def _toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self._bring_to_front()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_window()

    def _save_geometry(self):
        self.cfg["toolbar_pos"] = [self.x(), self.y()]
        self.cfg["window_size"] = [self.width(), self.height()]
        save_config(self.cfg)

    def _release_singleton(self):
        if self._server is not None:
            try:
                self._server.close()
            except Exception:
                pass
            QLocalServer.removeServer(SINGLETON_NAME)
            self._server = None

    def _on_singleton_msg(self):
        """다른 실행이 보낸 신호 처리.
        show = 창 앞으로 (바로가기 재실행), tray = 아무것도 안 함 (자동 실행 중복),
        quit = 종료 (설치/제거 프로그램이 파일을 교체하기 전에 보냄), 빈 연결 = 무시."""
        conn = self._server.nextPendingConnection() if self._server else None
        msg = b""
        if conn is not None:
            if not conn.bytesAvailable():
                conn.waitForReadyRead(300)
            msg = bytes(conn.readAll())
            conn.disconnectFromServer()
        cmd = msg.decode(errors="ignore").strip().lower()
        if cmd == "quit":
            print("[singleton] 종료 요청을 받음 (설치/제거 프로그램)")
            QTimer.singleShot(0, self.quit_app)
            return
        if cmd != "show":
            return
        try:
            cur = None if FROZEN else Path(__file__).stat().st_mtime
        except Exception:
            cur = None
        if cur and self._script_mtime and cur > self._script_mtime + 0.5:
            print("[singleton] pincapture.py 가 갱신됨 → 새 버전으로 다시 시작")
            self.restart_app()
        else:
            self._bring_to_front()

    def restart_app(self):
        """같은 프로그램으로 새 프로세스를 띄우고 이 프로세스는 종료."""
        import subprocess
        self._save_geometry()
        self.hotkeys.stop()
        self._release_singleton()
        if self._tray is not None:
            self._tray.hide()
        env = dict(os.environ)
        env.pop("PINCAP_REEXEC", None)
        if FROZEN:
            # 없으면 자식이 곧 정리될 부모의 PyInstaller 런타임 환경을 물려받음 → 독립 실행으로 리셋
            env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        try:
            if IS_WINDOWS:
                subprocess.Popen(launch_argv(), cwd=str(app_dir()), env=env,
                                 creationflags=_NO_WINDOW, close_fds=True)
            else:
                subprocess.Popen(launch_argv(), cwd=str(app_dir()), env=env, start_new_session=True)
        except Exception as e:
            print(f"[restart] 재시작 실패: {e}")
        self._exit_now()

    def quit_app(self):
        self._save_geometry()
        self.hotkeys.stop()
        self._release_singleton()
        if self._tray is not None:
            self._tray.hide()
        self._exit_now()

    def _exit_now(self):
        """이벤트 루프를 확실히 끝낸다.
        QApplication.quit() 는 Qt 6 에서 '취소 가능한 요청'이라, 이 창의 closeEvent 가 닫기를 거부(트레이로 숨김)하고
        핀 창이 화면에 남아 있으면 종료가 무시된다 → 트레이·단축키 없는 유령 프로세스가 남아 업데이트/제거를 막음.
        exit(0) 은 취소되지 않는다. 핀 창은 먼저 닫아 정리."""
        for p in list(self._pins):
            try:
                p.close()
            except Exception:
                pass
        QApplication.instance().exit(0)

    # ---------- 캡처 파이프라인 ----------
    def _on_hotkey(self, mode: str):
        if mode == "reopen_pin":
            self.reopen_recent_pin()
            return
        if mode == "clickthrough":
            self.clear_click_through()
            return
        if mode == "markup":
            self.start_pin_markup()
            return
        if mode in ("eyedropper", "ruler"):
            self.start_inspect(mode)
            return
        self.capture(mode)

    def _front_pin(self):
        """가장 최근에 만들거나 누른, 보이는 핀. 목록 앞이 아니라 맨 뒤가 앞이다."""
        for pin in reversed(self._pins):
            try:
                if pin.isVisible():
                    return pin
            except RuntimeError:
                continue
        return None

    def _note_front_pin(self, pin) -> None:
        try:
            if pin in self._pins:
                self._pins.remove(pin)
                self._pins.append(pin)
        except RuntimeError:
            return

    def _present_pin(self, pin) -> None:
        """핀을 메인 창보다 앞에 둔다.

        메인 창이 활성인 채로 setFocus 만 하면 핀과 표시 도구가 뒤에 남는다.
        Windows 에서는 activateWindow 보다 force_foreground 를 먼저 한다.
        """
        try:
            if not pin.isVisible():
                pin.show()
            self._note_front_pin(pin)
            pin.raise_()
            if IS_WINDOWS:
                force_foreground(int(pin.winId()))
            pin.activateWindow()
            pin.setFocus(Qt.FocusReason.OtherFocusReason)
            bar = getattr(pin, "_bar", None)
            if bar is not None and getattr(pin, "_editing", False):
                bar.show()
                bar.raise_()
                pin._place_markup_bar()
        except RuntimeError:
            return

    def _present_pin_soon(self, pin) -> None:
        """클릭 처리가 끝난 뒤에 다시 앞으로. 버튼 클릭은 메인 창으로 포커스를 되돌린다."""
        def go():
            try:
                if pin not in self._pins:
                    return
            except RuntimeError:
                return
            self._present_pin(pin)
        QTimer.singleShot(0, go)

    def start_pin_markup(self):
        """고른 캡처나 맨 앞 핀에서 표시를 시작한다. 버튼과 단축키가 같은 길을 탄다."""
        pin = self._pin_for_tool()
        if pin is None:
            self._show_notice("그릴 캡처나 핀이 없어요. 보관함에서 고르거나 핀을 띄워 주세요.")
            return None
        self._present_pin(pin)
        if not pin.begin_markup(pin._tool):
            self._show_notice("클릭 통과를 끄고 표시해 주세요.")
            return None
        self._present_pin(pin)
        self._present_pin_soon(pin)
        return pin

    def start_inspect(self, mode: str):
        """스포이트 또는 자. 영역 캡처와 같이 화면을 먼저 멈추고, 막혀 있으면 검은 화면을 띄우지 않는다."""
        if mode not in ("eyedropper", "ruler"):
            self._show_notice("이 도구를 시작하지 못했어요.")
            return
        if self._capturing:
            self._show_notice("이미 화면을 고르고 있어요.")
            return
        self._capturing = True
        self._was_visible = self.isVisible()
        delay = 30
        if self.cfg.get("hide_during_capture") and self._was_visible:
            self.hide()
            delay = 220
        QTimer.singleShot(delay, lambda m=mode: self._run_inspect(m))

    def _run_inspect(self, mode: str):
        session = None
        try:
            session = ScreenInspectSession(mode)
            self._session = session
            session.finished.connect(self._finish_inspect)
            session.blocked.connect(self._capture_blocked)
            session.start()
        except Exception as exc:
            _log_exc("inspect", exc, "스포이트·자")
            if session is not None:
                try:
                    session._cleanup()
                except Exception:
                    pass
            self._session = None
            self._capturing = False
            if self._was_visible:
                try:
                    self.show()
                except Exception:
                    pass
            self._show_notice("화면을 멈추지 못했어요.")

    def _finish_inspect(self, result):
        self._session = None
        self._capturing = False
        if self._was_visible:
            self.show()
        if isinstance(result, dict) and result.get("error"):
            self._show_notice("화면을 찾지 못했어요.")
            return
        if not result:
            return
        try:
            if result.get("mode") == "eyedropper":
                QApplication.clipboard().setText(result.get("hex", ""))
                self._show_notice(f"{result.get('hex', '')}   {result.get('rgb', '')} 를 복사했어요.")
            elif result.get("mode") == "ruler":
                self._show_notice(
                    f"{result['distance']}px예요. 가로 {result['dx']}px, 세로 {result['dy']}px, "
                    f"화면 배율 {result['scale']}%예요.")
            else:
                self._show_notice("결과를 보여 주지 못했어요.")
        except Exception as exc:
            _log_exc("inspect", exc, "결과 안내")
            self._show_notice("결과를 보여 주지 못했어요.")

    def _show_toast(self, text: str, msec: int = 2200) -> PinToast:
        """화면 위 안내. 메인 창이 숨겨져 있으면 커서 옆에 둔다."""
        self._last_notice = text
        prev = self._notice_toast
        self._notice_toast = None
        if prev is not None:
            try:
                prev.close()
            except Exception:
                pass
        anchor = self if self.isVisible() else None
        self._notice_toast = PinToast(text, anchor, msec)
        return self._notice_toast

    def _show_notice(self, text: str, title: str = APP_NAME, msec: int = 2200) -> None:
        """토스트가 본 안내. 트레이 풍선만 쓰면 알림 끄기·집중 지원에서 반응이 없어 보인다.

        풍선은 '캡처 후 트레이 알림'이 켜져 있을 때만 덧붙이고, 그것만으로 끝내지 않는다.
        """
        self._show_toast(text, msec)
        tray = self._tray
        if tray is None or not self.cfg.get("notify"):
            return
        try:
            tray.showMessage(title, text, QSystemTrayIcon.MessageIcon.Information, msec)
        except Exception as exc:
            _log_exc("notice", exc, "트레이 알림 실패")

    def reopen_recent_pin(self):
        """가장 최근에 닫은 핀을 다시 띄운다. 없으면 짧은 안내만 한다."""
        try:
            item = self._recent.pop_latest()
        except Exception as exc:
            _log_exc("recent", exc, "최근 핀")
            self._show_notice("핀을 다시 열지 못했어요.")
            return None
        if item is None:
            self._show_notice("다시 열 핀이 없어요. 핀을 닫으면 다시 열 수 있어요.")
            return None
        try:
            pin = self._make_pin(
                item["image"], QPoint(int(item["x"]), int(item["y"])),
                scale=float(item["scale"]), opacity=int(item["opacity"]), dpr=float(item["dpr"]))
        except Exception as exc:
            _log_exc("recent", exc, "최근 핀")
            self._show_notice("핀을 다시 열지 못했어요.")
            return None
        self._present_pin_soon(pin)
        return pin

    def clear_click_through(self) -> int:
        """클릭 통과 중인 핀을 모두 끈다. 핀 자체는 클릭을 받지 못하므로 트레이·단축키가 이 일을 한다."""
        n = 0
        for pin in list(self._pins):
            if pin.click_through:
                pin.set_click_through(False)
                n += 1
        if n:
            self._show_notice("클릭 통과를 껐어요.")
        else:
            self._show_notice("클릭 통과 중인 핀이 없어요.")
        return n

    def capture(self, mode: str):
        """mode: region | window | full | pin"""
        if self._capturing:
            return
        self._capturing = True
        self._was_visible = self.isVisible()
        delay = 30
        if self.cfg["hide_during_capture"] and self._was_visible:
            self.hide()   # 이 창이 캡처에 찍히지 않게
            delay = 220
        if mode == "region":
            QTimer.singleShot(delay, lambda: self._run_region(pin=False))
        elif mode == "pin":
            QTimer.singleShot(delay, lambda: self._run_region(pin=True))
        elif mode == "window":
            QTimer.singleShot(max(delay, 150), self._run_window)
        elif mode == "full":
            QTimer.singleShot(delay, self._run_full)
        else:
            self._capturing = False

    def _run_region(self, pin: bool):
        self._session = RegionCaptureSession()
        self._session.finished.connect(
            lambda img, gpos, pin=pin: self._finish(img, gpos, pin=pin))
        self._session.blocked.connect(self._capture_blocked)
        self._session.start()

    def _own_hwnds(self) -> set:
        s = set()
        for w in QApplication.topLevelWidgets():
            try:
                s.add(int(w.winId()))
            except Exception:
                pass
        return s

    def _track_foreground(self):
        """(Windows) 주기적으로 외부 활성 창을 기억 — 창 캡처 버튼용."""
        try:
            h = _user32.GetForegroundWindow()
            if h and h not in self._own_hwnds():
                self._last_ext_hwnd = h
        except Exception:
            pass

    def _run_window(self):
        exclude = self._own_hwnds() if IS_WINDOWS else set()
        fallback = self._last_ext_hwnd if IS_WINDOWS else None
        img = capture_active_window(exclude, fallback)
        if is_mostly_black(img) and screens_capture_blocked():
            self._finish(None, None, pin=False)
            self._capture_blocked()
            return
        self._finish(img, None, pin=False)

    def _run_full(self):
        s = screen_under_cursor()
        pm = grab_screen_raw(s)
        # 이 모니터가 완전한 검정일 때만 나머지 모니터도 확인 (한 모니터만 검정이면 실제로 검은 화면일 수 있음)
        if is_mostly_black(pm) and screens_capture_blocked():
            self._finish(None, None, pin=False)
            self._capture_blocked()
            return
        self._finish(pm.toImage(), s.geometry().topLeft(), pin=False)

    def _capture_blocked(self):
        """화면 캡처가 통째로 검게 나올 때: 검은 화면을 띄우거나 저장하지 않고 이유를 알린다.
        (보안 프로그램의 캡처 방지를 우회하지는 않는다 — 사용자가 직접 해제하도록 안내만)"""
        print("[capture] 모든 모니터가 거의 전부 검정으로 캡처됨 — 보안 프로그램의 화면 캡처 방지로 추정")
        # 실제 사례(2026-10-26): 정부24 전자문서 뷰어(ezPDFReader 2.0G)와 함께 설치된 화면 캡처 방지 모듈
        # (Teruten WebCube: TUCtlSystem 서비스 + T_Prevent64.dll)이 실행 중인 거의 모든 프로그램에 주입되어
        # 캡처가 검게 됨. 새로 띄운 프로그램도 수 초 안에 주입되므로 핀캡처 재시작은 도움이 안 된다.
        # → 1순위 해결책은 '문서 뷰어 닫기', 안 되면 재부팅·해당 뷰어 제거. (우회는 하지 않는다)
        title = "화면 캡처가 막혀 있어요"
        text = ("보안 프로그램 때문에 캡처가 막혔을 수 있어요.\n\n"
                "화면이 거의 전부 검은색으로만 캡처되고 있어요.\n\n"
                "정부24·홈택스·은행 같은 사이트의 전자문서 뷰어나 보안 프로그램이 '화면 캡처 방지' 기능을 "
                "켜 두면 이렇게 됩니다. 이 기능은 실행 중인 다른 프로그램에도 들어가기 때문에 "
                "다른 캡처 프로그램도 검게 찍힐 수 있어요.\n\n"
                "해결 방법\n"
                "  1. 열려 있는 전자문서 보기 창(예: 정부24 '전자문서 전용 Viewer')을 닫고 다시 캡처해 보세요.\n"
                "  2. 그래도 검게 나오면 그 사이트의 브라우저 창도 닫아 보세요.\n"
                "  3. 계속되면 컴퓨터를 다시 시작하거나, Windows 설정 → 앱에서 그때 설치된\n"
                "     문서 뷰어(예: ezPDFReader)나 화면 보안 프로그램(예: WebCube)을 제거해 주세요.")
        if self._tray is not None:
            self._tray.showMessage(title, "보안 프로그램 때문에 캡처가 막혔을 수 있어요. 안내 창을 확인해 주세요.",
                                   QSystemTrayIcon.MessageIcon.Warning, 4000)
        box = getattr(self, "_blocked_box", None)
        if box is None:
            box = QMessageBox(QMessageBox.Icon.Warning, title, text, QMessageBox.StandardButton.Ok)
            box.setWindowModality(Qt.WindowModality.NonModal)   # 캡처 단축키를 막지 않게
            box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self._blocked_box = box
        box.show()
        box.raise_()
        box.activateWindow()
        if IS_WINDOWS:
            force_foreground(int(box.winId()))

    def _finish(self, img, gpos, pin: bool):
        self._session = None
        self._capturing = False
        if img is None or (hasattr(img, "isNull") and img.isNull()):
            if self._was_visible:
                self.show()             # 취소: 창 원상 복구
            return

        do_pin = pin or self.cfg["pin_after_capture"]
        do_save = self.cfg["pin_autosave"] if pin else self.cfg["autosave"]
        path = None
        if do_save:
            path = self._save_image(img)
        if self.cfg["clipboard"]:
            QApplication.clipboard().setImage(img)
        if do_pin:
            self._make_pin(img, gpos)

        # 보관함 기록: 방금 캡처가 맨 위(메인), 이전 캡처들이 우측 리스트
        entry = HistoryEntry(image=img, path=path)
        self.history.insert(0, entry)
        self.add_entry(entry)
        self._trim_history()

        # 창 복귀: 일반 캡처면 결과를 바로 보여주고, 핀 캡처면 이전 상태만 복구
        if not pin and self.cfg.get("show_viewer_after_capture", True):
            self._bring_to_front()
        elif self._was_visible:
            self.show()

        self._notify(path)

        if os.environ.get("PINCAP_TEST_AUTOEXIT"):
            print(f"SAVED:{path}")
            QTimer.singleShot(300, self.quit_app)

    def _save_image(self, img: QImage) -> "str | None":
        d = Path(self.cfg["save_dir"])
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[save] 폴더 생성 실패: {e}")
            return None
        ext = self.cfg["file_format"].lower()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{self.cfg['filename_prefix']}_{ts}"
        path = d / f"{base}.{ext}"
        n = 1
        while path.exists():
            path = d / f"{base}_{n}.{ext}"
            n += 1
        out = img
        if ext in ("jpg", "jpeg"):
            out = img.convertToFormat(QImage.Format.Format_RGB32)
            ok = out.save(str(path), "JPG", int(self.cfg["jpg_quality"]))
        else:
            ok = out.save(str(path), "PNG")
        if not ok:
            print(f"[save] 저장 실패: {path}")
            return None
        return str(path)

    def _make_pin(self, img: QImage, gpos, *, scale: float = 1.0, opacity: int = 100,
                  dpr: "float | None" = None):
        scr = screen_under_cursor()
        if dpr is None:
            dpr = scr.devicePixelRatio() if scr is not None else 1.0
        pin = PinWindow(img, dpr=dpr)
        pin.release_hotkey = self.cfg.get("hotkeys", {}).get("clickthrough", "")
        pin.on_eyedropper = lambda: self.start_inspect("eyedropper")
        pin.on_ruler = lambda: self.start_inspect("ruler")
        pin.on_activated = lambda p=pin: self._note_front_pin(p)
        if scale != 1.0:
            pin._scale = float(scale)
            pin._apply_size()
        if int(opacity) != 100:
            pin.set_opacity(int(opacity))
        pin.closed.connect(self._on_pin_closed)
        self._pins.append(pin)
        if isinstance(gpos, QPoint):
            pin.move(gpos)
        else:
            g = scr.availableGeometry()
            pin.move(g.center() - QPoint(pin.width() // 2, pin.height() // 2))
        pin.show()
        pin.raise_()
        self._sync_pin_tools()
        return pin

    def _on_pin_closed(self, pin):
        if pin in self._pins:
            self._pins.remove(pin)
        try:
            self._recent.remember(pin)
        except Exception as e:
            print(f"[recent] 보관 실패: {e}")
        self._sync_pin_tools()

    def _notify(self, path):
        if not self.cfg["notify"] or self._tray is None:
            return
        if path:
            self._tray.showMessage("캡처 완료", f"저장했어요: {path}",
                                   QSystemTrayIcon.MessageIcon.Information, 2200)
        elif self.cfg["clipboard"]:
            self._tray.showMessage("캡처 완료", "클립보드에 복사했어요.",
                                   QSystemTrayIcon.MessageIcon.Information, 1800)

    # ---------- 보관함 ----------
    def _scan_existing_files(self):
        """저장 폴더의 기존 캡처(최신 60개)를 기록 목록에 채움."""
        try:
            d = Path(self.cfg["save_dir"])
            if not d.is_dir():
                return
            files = [f for pat in ("*.png", "*.jpg", "*.jpeg") for f in d.glob(pat)]
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files[:60]:
                self.history.append(HistoryEntry(
                    path=str(f),
                    ts=datetime.datetime.fromtimestamp(f.stat().st_mtime)))
        except Exception as e:
            print(f"[history] 기존 파일 스캔 실패: {e}")

    def _trim_history(self, limit: int = 150):
        while len(self.history) > limit:
            self.history.pop()
            if self.listw.count() > limit:
                self.listw.takeItem(self.listw.count() - 1)

    def populate(self):
        self.listw.blockSignals(True)
        self.listw.clear()
        for e in self.history:
            self.listw.addItem(self._make_item(e))
        self.listw.blockSignals(False)
        self._select_only(0 if self.listw.count() else -1)

    def add_entry(self, entry: HistoryEntry):
        self.listw.insertItem(0, self._make_item(entry))
        self._select_only(0)

    def _select_only(self, row: int):
        """해당 행만 선택하고 현재 항목으로. (다중 선택 모드에선 setCurrentRow 가 기존 선택을 안 지움)"""
        self.listw.blockSignals(True)
        if 0 <= row < self.listw.count():
            self.listw.setCurrentRow(row, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        else:
            self.listw.clearSelection()
            row = -1
        self.listw.blockSignals(False)
        self._on_row_changed(row)

    def _make_item(self, e: HistoryEntry) -> QListWidgetItem:
        thumb = e.thumbnail()
        icon = QIcon(thumb) if thumb is not None else make_app_icon()
        item = QListWidgetItem(icon, e.label())
        item.setToolTip(e.path or "저장하지 않은 캡처 (메모리)")
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        return item

    def _current_entry(self) -> "HistoryEntry | None":
        row = self.listw.currentRow()
        if 0 <= row < len(self.history):
            return self.history[row]
        return None

    def _selected_rows(self) -> "list[int]":
        """선택된 행 번호(오름차순). 선택이 없으면 현재 행 하나."""
        rows = sorted({ix.row() for ix in self.listw.selectedIndexes()
                       if 0 <= ix.row() < len(self.history)})
        if not rows:
            cur = self.listw.currentRow()
            if 0 <= cur < len(self.history):
                rows = [cur]
        return rows

    def _selected_entries(self) -> "list[HistoryEntry]":
        return [self.history[r] for r in self._selected_rows()]

    def _on_row_changed(self, row: int):
        e = self._current_entry()
        self._cur_img = e.full_image() if e else None
        self.preview.set_image(self._cur_img)
        self._refresh_info()

    def _refresh_info(self):
        rows = self._selected_rows()
        e = self._current_entry()
        n = len(rows)
        self.b_remove.setText(f"목록에서 제거 ({n})" if n > 1 else "목록에서 제거")
        if e is None or not rows:
            self.info.setText("아직 캡처가 없어요. 위쪽 버튼이나 단축키로 화면을 찍어 보세요.")
            self._sync_pin_tools()
            return
        if n > 1:
            self.info.setText(f"{n}개 선택   ·   복사하면 파일 묶음으로 복사하고, 저장하면 폴더에 한꺼번에 저장해요."
                              "   ·   핀은 모두 고정하고, Delete는 목록에서만 제거해요. 파일은 지우지 않아요.")
            self._sync_pin_tools()
            return
        img = getattr(self, "_cur_img", None)
        where = e.path if e.path else "저장하지 않은 캡처 (메모리에만 있어요)"
        if img is None:
            self.info.setText(f"(이미지를 읽을 수 없음)   ·   {where}")
        else:
            self.info.setText(f"{img.width()}×{img.height()} px   ·   {where}")
        self._sync_pin_tools()

    def _copy_selected(self):
        entries = self._selected_entries()
        if not entries:
            return
        if len(entries) == 1:
            img = entries[0].full_image()
            if img is not None:
                QApplication.clipboard().setImage(img)
            return
        # 여러 개: 파일 묶음으로 복사 (탐색기·메신저·메일에 붙여넣기 가능).
        # 저장 안 된 캡처는 ~/.pincapture/clipboard/ 에 임시 저장해 포함. 이미지만 받는 앱을 위해 첫 장도 같이 실음.
        tmp_dir = CONFIG_DIR / "clipboard"
        try:
            tmp_dir.mkdir(parents=True, exist_ok=True)
            for old in tmp_dir.glob("*.png"):
                old.unlink(missing_ok=True)
        except Exception:
            pass
        urls, first_img = [], None
        for i, e in enumerate(entries):
            p = Path(e.path) if e.path else None
            if p is None or not p.exists():
                img = e.full_image()
                if img is None:
                    continue
                p = tmp_dir / f"캡처_{e.ts:%Y%m%d_%H%M%S}_{i}.png"
                if not img.save(str(p), "PNG"):
                    continue
            if first_img is None:
                first_img = e.full_image()
            urls.append(QUrl.fromLocalFile(str(p)))
        if not urls:
            return
        md = QMimeData()
        md.setUrls(urls)
        if first_img is not None:
            md.setImageData(first_img)
        QApplication.clipboard().setMimeData(md)
        if self._tray is not None and self.cfg["notify"]:
            self._tray.showMessage("복사 완료", f"{len(urls)}개를 클립보드에 복사했어요.",
                                   QSystemTrayIcon.MessageIcon.Information, 1800)

    def _save_selected_as(self):
        entries = self._selected_entries()
        if not entries:
            return
        if len(entries) == 1:
            e = entries[0]
            img = e.full_image()
            if img is None:
                return
            ts = e.ts.strftime("%Y%m%d_%H%M%S")
            path, _ = QFileDialog.getSaveFileName(
                self, "다른 이름으로 저장", str(Path.home() / f"캡처_{ts}.png"),
                "PNG (*.png);;JPEG (*.jpg)")
            if path:
                img.save(path)
            return
        # 여러 개: 폴더를 고르면 각각 저장 (파일이 있는 건 그대로 복사, 메모리 캡처는 PNG 로)
        import shutil
        d = QFileDialog.getExistingDirectory(self, "저장할 폴더를 골라 주세요", str(Path.home()))
        if not d:
            return
        saved, failed = 0, 0
        for e in entries:
            src = Path(e.path) if e.path and Path(e.path).exists() else None
            base = src.stem if src else f"캡처_{e.ts:%Y%m%d_%H%M%S}"
            ext = src.suffix if src else ".png"
            out = Path(d) / f"{base}{ext}"
            n = 1
            while out.exists():
                out = Path(d) / f"{base}_{n}{ext}"
                n += 1
            try:
                if src:
                    shutil.copy2(src, out)
                    saved += 1
                else:
                    img = e.full_image()
                    if img is not None and img.save(str(out), "PNG"):
                        saved += 1
                    else:
                        failed += 1
            except Exception as ex:
                print(f"[save] 일괄 저장 실패 {out}: {ex}")
                failed += 1
        msg = f"{saved}개를 저장했어요.\n{d}" + (f"\n(실패 {failed}개)" if failed else "")
        QMessageBox.information(self, "저장", msg)

    def _pin_selected(self):
        entries = self._selected_entries()
        shown = 0
        for e in entries:
            img = e.full_image()
            if img is None:
                continue
            self._make_pin(img, None)
            if shown and self._pins:                      # 여러 장이면 계단식으로 어긋나게
                p = self._pins[-1]
                p.move(p.pos() + QPoint(32 * shown, 32 * shown))
            shown += 1

    def _open_folder(self):
        d = Path(self.cfg["save_dir"])
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))

    def _remove_selected(self):
        """선택된 항목을 모두 목록에서 제거 (파일은 지우지 않음)."""
        rows = self._selected_rows()
        if not rows:
            return
        self.listw.blockSignals(True)
        for row in reversed(rows):              # 뒤에서부터 지워야 앞 인덱스가 안 밀림
            del self.history[row]
            self.listw.takeItem(row)
        self.listw.blockSignals(False)
        self._select_only(min(rows[0], self.listw.count() - 1))

    # ---------- 설정 ----------
    def open_settings(self):
        dlg = SettingsDialog(self.cfg, self.hotkeys.available)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            save_config(self.cfg)
            self._recent.set_limit(self.cfg.get("recent_pin_limit", 10))
            hint = self.cfg.get("hotkeys", {}).get("clickthrough", "")
            for pin in self._pins:
                pin.release_hotkey = hint
            self.hotkeys.restart(self.cfg["hotkeys"])
            self._update_tooltips()


# ---------------------------------------------------------------------------
# 자가 점검 (--selftest): 헤드리스 환경에서 위젯을 만들어 PNG 로 저장
# ---------------------------------------------------------------------------
def run_selftest() -> int:
    out = Path("selftest_out")
    out.mkdir(exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv)
    apply_ui_font(app)
    cfg = load_config()
    results = []

    def grab(widget, name, size=None):
        if size:
            widget.resize(*size)
        widget.show()
        app.processEvents()
        pm = widget.grab()
        p = out / f"{name}.png"
        pm.save(str(p))
        results.append((name, pm.width(), pm.height()))
        widget.hide()

    # 1) 메인 창 (위: 기능함, 아래: 보관함) — 더미 캡처 3개
    def _dummy(w, h, base):
        im = QImage(w, h, QImage.Format.Format_RGB32)
        q = QPainter(im)
        for y in range(h):
            q.setPen(QColor((base + y // 4) % 256, (base * 2 + y // 6) % 256,
                            (255 - base + y // 5) % 256))
            q.drawLine(0, y, w, y)
        q.setPen(QColor("white"))
        ff = QFont(); ff.setPointSize(14); q.setFont(ff)
        q.drawText(im.rect(), Qt.AlignmentFlag.AlignCenter, f"{w}×{h}")
        q.end()
        return im

    tb = MainToolbar(cfg)
    tb.history = [HistoryEntry(image=_dummy(900, 560, 60)),
                  HistoryEntry(image=_dummy(640, 400, 130)),
                  HistoryEntry(image=_dummy(500, 700, 200))]
    tb.populate()
    grab(tb, "main", size=(1080, 720))

    # 2) 설정 창
    dlg = SettingsDialog(cfg, hotkey_ok=tb.hotkeys.available)
    dlg.adjustSize()
    grab(dlg, "settings")

    welcome = WelcomeDialog(cfg)
    welcome.adjustSize()
    grab(welcome, "welcome")
    about = AboutDialog()
    about.adjustSize()
    grab(about, "about")

    # 3) 핀 창 (그라데이션 더미 이미지)
    img = QImage(420, 260, QImage.Format.Format_RGB32)
    pt = QPainter(img)
    for y in range(260):
        pt.setPen(QColor(40 + y // 3, 90 + y // 4, 200 - y // 3))
        pt.drawLine(0, y, 420, y)
    pt.setPen(QColor("white"))
    f = QFont(); f.setPointSize(16); pt.setFont(f)
    pt.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, "PIN TEST 420×260")
    pt.end()
    pin = PinWindow(img)
    grab(pin, "pin")

    # 4) 영역 선택 오버레이 (더미 정지 화면 + 가짜 선택 영역)
    frozen = QPixmap(1280, 800)
    pf = QPainter(frozen)
    for y in range(800):
        pf.setPen(QColor(30 + y // 8, 60 + y // 10, 110 + y // 9))
        pf.drawLine(0, y, 1280, y)
    pf.setPen(QColor(255, 255, 255, 200))
    f2 = QFont(); f2.setPointSize(22); pf.setFont(f2)
    pf.drawText(frozen.rect(), Qt.AlignmentFlag.AlignCenter, "FROZEN SCREEN (dummy)")
    pf.end()
    scr = app.primaryScreen()
    ov = SelectionOverlay(scr, frozen)
    ov.resize(1280, 800)
    ov._origin = QPoint(340, 220)
    ov._current = QPoint(820, 540)
    grab(ov, "overlay", size=(1280, 800))
    sel = ov._sel_rect()
    phys = ov._to_phys(sel)
    results.append(("overlay_mapping", phys.width(), phys.height()))
    ov.blockSignals(True); ov.close()

    # 5) 좌표 매핑 단위 확인 (200% DPI 시뮬레이션)
    frozen2x = QPixmap(2560, 1600)
    frozen2x.fill(QColor("gray"))
    ov2 = SelectionOverlay(scr, frozen2x)
    ov2.resize(1280, 800)
    r = ov2._to_phys(QRect(100, 50, 300, 200))
    expect = QRect(200, 100, 600, 400)
    ok = (r == expect)
    results.append(("dpi_mapping_ok" if ok else "dpi_mapping_FAIL", r.width(), r.height()))
    ov2.blockSignals(True); ov2.close()

    hk = tb.hotkeys
    alive = hk._listener.is_alive() if hk._listener is not None else None
    tb.hotkeys.stop()
    for name, w, h in results:
        print(f"[selftest] {name}: {w}x{h}")
    print(f"[selftest] hotkeys available={hk.available} listener_alive={alive} error={hk.error!r}")
    print(f"[selftest] version={APP_VERSION} frozen={FROZEN}")
    print(f"[selftest] launch_argv={launch_argv()}  tray_argv={launch_argv('--tray')}")
    print(f"[selftest] relaunch_command={relaunch_command()}")
    print(f"[selftest] app_dir={app_dir()}  icon={app_icon_path()}")
    print("[selftest] done ->", out.resolve())
    return 0


def _send_quit_to_running() -> int:
    """--quit: 실행 중인 핀캡처에 종료를 요청하고 실제로 끝날 때까지 최대 10초 기다린다.
    설치/제거 프로그램이 파일을 바꾸기 전에 호출한다. 실행 중이 아니면 바로 0."""
    import time
    sock = QLocalSocket()
    sock.connectToServer(SINGLETON_NAME)
    if not sock.waitForConnected(1000):
        print("[quit] 실행 중인 핀캡처 없음")
        return 0
    sock.write(b"quit")
    sock.flush()
    sock.waitForBytesWritten(1000)
    sock.disconnectFromServer()
    if not IS_WINDOWS:
        return 0
    import ctypes
    k32 = ctypes.windll.kernel32
    SYNCHRONIZE = 0x00100000
    for _ in range(100):                     # 뮤텍스가 사라지면 = 프로세스 종료
        time.sleep(0.1)
        h = k32.OpenMutexW(SYNCHRONIZE, False, APP_MUTEX_NAME)
        if not h:
            print("[quit] 종료 확인")
            return 0
        k32.CloseHandle(h)
    print("[quit] 10초 안에 종료되지 않음")
    return 1


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} {APP_VERSION}")
    parser.add_argument("--selftest", action="store_true", help="UI 자가 점검 (개발용)")
    parser.add_argument("--region", action="store_true", help="시작 직후 영역 캡처")
    parser.add_argument("--window", action="store_true", help="시작 직후 창 캡처")
    parser.add_argument("--full", action="store_true", help="시작 직후 전체 캡처")
    parser.add_argument("--pin", action="store_true", help="시작 직후 핀 캡처")
    parser.add_argument("--tray", action="store_true", help="창 없이 트레이로 시작 (자동 실행용)")
    parser.add_argument("--quit", action="store_true", help="실행 중인 핀캡처 종료 (설치/제거 프로그램용)")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {APP_VERSION}")
    # 모르는 인수가 있어도 죽지 않게 (예전 버전이 만든 바로가기 등)
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"[args] 알 수 없는 인수 무시: {unknown}")

    if args.selftest and not IS_WINDOWS and not os.environ.get("DISPLAY"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    if IS_WINDOWS:
        try:  # 작업표시줄 아이콘 그룹핑
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("PinCapture")
    app.setApplicationDisplayName(APP_NAME)
    app.setWindowIcon(make_app_icon())
    app.setQuitOnLastWindowClosed(False)

    if args.selftest:
        return run_selftest()
    if args.quit:
        return _send_quit_to_running()

    cfg = prepare_config()  # 첫 실행이면 안내를 띄울 준비를 하고, 없으면 기본 설정 파일을 만든다

    # 단일 인스턴스: 이미 실행 중이면 신호만 보내고 이 프로세스는 종료.
    # 기존 인스턴스는 창을 앞으로 띄운다 (개발용 .py 실행이면 파일이 갱신됐을 때 재시작).
    sock = QLocalSocket()
    sock.connectToServer(SINGLETON_NAME)
    if sock.waitForConnected(300):
        if IS_WINDOWS and not args.tray:
            # 바로가기로 실행된 이 프로세스가 받은 '전경 전환 권한'을 이미 실행 중인 창에 넘겨줌
            # (없으면 기존 창이 앞으로 오지 못하고 작업 표시줄만 깜빡일 수 있음)
            try:
                import ctypes
                ctypes.windll.user32.AllowSetForegroundWindow(-1)   # ASFW_ANY
            except Exception:
                pass
        sock.write(b"tray" if args.tray else b"show")
        sock.flush()
        sock.waitForBytesWritten(300)
        sock.disconnectFromServer()
        print("이미 실행 중이에요. 기존 창을 앞으로 가져왔어요.")
        return 0
    QLocalServer.removeServer(SINGLETON_NAME)   # 비정상 종료 잔여물 정리
    server = QLocalServer()
    server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)   # 같은 사용자만 연결 가능
    if not server.listen(SINGLETON_NAME):
        print(f"[singleton] listen 실패: {server.errorString()}")

    if IS_WINDOWS:
        # 설치/제거 프로그램이 '실행 중'을 감지하는 뮤텍스. 프로세스가 끝나면 OS 가 자동 해제.
        try:
            import ctypes
            global _APP_MUTEX
            _APP_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)
        except Exception as e:
            print(f"[mutex] 생성 실패: {e}")

    toolbar = MainToolbar(cfg, server)
    if IS_WINDOWS:
        # 창을 보이기 전에 작업 표시줄 식별 정보를 심어야 '고정' 시 핀캡처 아이콘/명령이 쓰인다
        set_window_taskbar_identity(int(toolbar.winId()))
    if not args.tray or toolbar._tray is None:   # 트레이가 없는 환경이면 --tray 여도 창을 띄움
        toolbar.show()
    if should_auto_welcome(cfg, args.tray, toolbar._tray is not None):
        # 첫 실행에만. --tray(자동 실행)에서는 띄우지 않아 로그인을 끊지 않는다.
        QTimer.singleShot(400, toolbar.show_welcome)

    for flag, mode in [(args.region, "region"), (args.window, "window"),
                       (args.full, "full"), (args.pin, "pin")]:
        if flag:
            QTimer.singleShot(600, lambda m=mode: toolbar.capture(m))
            break

    if os.environ.get("PINCAP_TEST_RESTART"):
        QTimer.singleShot(1500, toolbar.restart_app)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
