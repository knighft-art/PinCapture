# AGENTS.md — 핀캡처 운영 매뉴얼

이 저장소에서 일하는 AI 코딩 에이전트(Grok, Claude, Codex 등)가 **가장 먼저** 읽는 문서예요.
문서와 코드가 다르면 코드가 맞아요. 코드를 따르고, 이 문서를 고쳐 주세요.

## 1. 프로젝트 한 줄 요약

핀캡처(PinCapture)는 PySide6로 만든 Windows 10/11 x64용 화면 캡처 트레이 앱이에요. 영역·창·전체 화면 캡처, 화면 위 핀 고정, 보관함, 전역 단축키를 제공해요.
소스는 `pincapture.py` 한 파일이고, 배포는 PyInstaller onedir + Inno Setup 설치 파일로 해요. 버전은 `pincapture.py`의 `APP_VERSION`(현재 `0.10.3`) 한 곳에서만 관리해요.

## 2. 저장소 지도

| 경로 | 내용 | 주의 |
|---|---|---|
| `pincapture.py` | 앱 전체(약 2,400줄, 단일 파일). 맨 위 주석에 버전 이력이 있어요 | 루트에서 옮기거나 쪼개지 않기 |
| `requirements.txt` | 실행 의존성: `PySide6==6.11.2`, `pynput==1.8.2`, `six==1.17.0`, Windows OCR용 PyWinRT 3.2.1(`winrt-*`)과 `typing_extensions==4.15.0` | 버전 고정. winrt는 `sys_platform == "win32"` |
| `requirements-dev.txt` | 위 항목 + `pyinstaller==6.22.3`, `pyinstaller-hooks-contrib==2026.9`, `pillow==12.3.0`, `pytest>=8` | |
| `tests/conftest.py`, `tests/_isolation.py` | Qt offscreen, `PINCAP_NO_LOG=1`, 격리된 `USERPROFILE`/`HOME`과 임시 `save_dir`, 픽스처 `pc`·`toolbar`, `spin(ms)`. 끝날 때 클립보드를 비운 뒤 `os._exit` | `import pincapture`보다 먼저 환경을 설정함. 사진 폴더는 `USERPROFILE`을 따르지 않아요 |
| `tests/test_*.py`, `tests/quit_probe.py` | 캡처 차단 감지, 보관함, 별도 프로세스(종료·CLI·selftest) 시험 | |
| `installer/build.py` | 설치 파일 빌드: 아이콘 → 버전 정보 → PyInstaller → 번들 검사 → selftest → ISCC → SHA-256·배포 안내문 | |
| `installer/PinCapture.spec` | PyInstaller onedir 설정. 안 쓰는 Qt 플러그인 제외(`DROP`) | |
| `installer/PinCapture.iss` | Inno Setup 스크립트 | UTF-8 BOM + CRLF |
| `installer/docs/사용법.txt` | 최종 사용자 안내. 앱과 함께 설치돼요 | UTF-8 BOM + CRLF |
| `installer/docs/THIRD_PARTY_NOTICES.txt`, `installer/docs/licenses/` | 오픈소스 고지, 라이선스 전문. `Qt-third-party.txt`는 Qt 6.11.2 `qt_attribution.json`에서 생성한 원문 | UTF-8 BOM + CRLF |
| `installer/build/`, `installer/output/` | 빌드 산출물 | gitignore |
| `.github/workflows/build.yml` | CI: 시험 → 빌드 → 아티팩트, 태그면 초안 릴리스 | 0.7.0에서 복구. 시험은 통과인데 단계만 실패하면 `tests/conftest.py`의 종료 처리를 먼저 봐요 |
| `.gitignore`, `.gitattributes` | `.gitattributes`가 `.iss`와 `installer/docs/*.txt`의 CRLF를 지켜요 | |
| `README.md`, `CHANGELOG.md`, `GROK.md` | 소개, 변경 기록, Grok용 요약 | |
| `docs/` | 개발 문서(10장 참고). `docs/images/screenshot-*.png`는 README용 | |
| `archive/` | 옛 버전 보관 | **로컬 전용, 커밋 금지**(gitignore) |
| `selftest_out/` | `--selftest` 출력 | gitignore |

## 3. 개발 환경 준비

- Windows 10/11 x64, Python 3.13을 써요. PySide6 6.11.2는 3.10~3.14를 지원하지만, 빌드·시험·CI는 3.13 기준이에요.
- PC에 Python이 여러 개 있을 수 있어요. `python` 대신 항상 `py -3.13`을 쓰세요. 목록은 `py -0p`로 볼 수 있어요.
- 의존성 설치: `py -3.13 -m pip install -r requirements-dev.txt`
- 설치 파일까지 만들려면 Inno Setup 6이 필요해요. `build.py`는 `ISCC.exe`를 `%LOCALAPPDATA%\Programs\Inno Setup 6`, `%ProgramFiles(x86)%\Inno Setup 6`, `%ProgramFiles%\Inno Setup 6`, `PATH` 순서로 찾아요.

## 4. 실행·시험·빌드 명령

모든 명령은 저장소 루트(`D:\Tools\PinCapture`)에서 실행해요.

| 목적 | 명령 | 결과 |
|---|---|---|
| 시험(작업을 끝낼 때마다) | `py -3.13 -m pytest -q` | `64 passed`, 약 12초(2026-10-26, Windows CI 기준. Linux에서는 단일 인스턴스 이름 시험 1개가 실패할 수 있어요) |
| 설치 파일 빌드 | `py -3.13 installer\build.py` | `installer\output\PinCapture-Setup-<버전>.exe`, `.sha256.txt`, `_배포안내.txt` |
| 앱 폴더까지만 빌드 | `py -3.13 installer\build.py --no-setup` | `installer\build\dist\PinCapture\`(Inno Setup 없이도 됨) |
| 버전 확인 | `py -3.13 pincapture.py --version` | `핀캡처 0.10.3` |
| 소스로 실행(소유자 확인 후) | `py -3.13 pincapture.py`, 콘솔 없이 실행하려면 `pyw -3.13 pincapture.py` | 창과 트레이 아이콘 |

명령줄 옵션은 아래와 같아요. 모르는 인수는 무시해요(`parse_known_args`).

| 옵션 | 동작 |
|---|---|
| `--region` `--window` `--full` `--pin` | 시작 0.6초 뒤 해당 캡처를 한 번 실행 |
| `--tray` | 창 없이 트레이로 시작. 자동 실행과 무인 업데이트 후 재실행에 쓰여요 |
| `--quit` | 실행 중인 인스턴스에 종료를 요청하고 최대 10초 기다려요. 설치·제거 프로그램이 써요 |
| `--version` | 버전 출력 |
| `--selftest` | 창 4개를 그려 `./selftest_out/*.png`로 저장하고 진단 정보를 출력해요 |

화면 렌더링 점검은 `pytest`의 `test_selftest_renders_every_window`가 격리된 홈에서 대신 해 줘요. 직접 실행할 때는 `QT_QPA_PLATFORM=offscreen`과 `PINCAP_NO_LOG=1`을 설정하세요.

> **주의**: 에이전트는 화면에 창이 뜨는 실행을 하지 마세요. 소유자의 핀캡처가 이미 실행 중이면 새 실행은 `show` 신호만 보내요. 그런데 `pincapture.py`가 그 사이 수정됐다면 **소유자의 앱이 수정된 코드로 재시작**돼요. 소유자의 바로가기가 바로 이 파일을 실행하니, 루트의 `pincapture.py`를 깨진 상태로 두지 마세요.

## 5. 작업 규칙

1. **작게 바꿔요.** 한 작업에는 한 가지 목적만 담아요. 관련 없는 리팩터링, 이름 변경, 포맷 정리는 하지 않아요.
2. **`pincapture.py`는 루트의 단일 파일로 유지해요.** 소유자의 바탕화면·시작 프로그램 바로가기가 `D:\Tools\PinCapture\pincapture.py`를 실행하고, `installer/PinCapture.spec`과 `tests/`도 이 경로에서 import해요.
3. **끝내기 전에 `py -3.13 -m pytest -q`를 통과시켜요.** 설치 파일이나 EXE 동작을 바꿨다면 `py -3.13 installer\build.py --no-setup`도 돌려요.
4. **버그를 고치면 그 버그를 재현하는 테스트를 함께 추가해요.** Qt 위젯은 `pc`·`toolbar` 픽스처와 `spin(ms)`로 시험해요. 화면 캡처는 `monkeypatch.setattr(pc, "grab_screen_raw", ...)`로 대체해요. 종료나 CLI처럼 이벤트 루프가 끝나는 동작은 별도 프로세스로 시험해요(`tests/quit_probe.py` 참고).
5. **`APP_VERSION`, 헤더 이력 주석, CHANGELOG 버전 항목은 배포할 때만 함께 바꿔요**(`docs/RELEASE.md`). 작업 중 변경 내용은 `CHANGELOG.md`의 `[Unreleased]`에 적어 둘 수 있어요.
6. **새 UI 문구는 해요체로 써요.** 예: `복사했어요`, `저장할 폴더를 골라 주세요`. 옛 문구에는 반말(`복사했어`, `종료돼`)이 남아 있어요. 고치는 창이나 메시지 안의 문구는 함께 해요체로 맞추고, 전체 통일은 로드맵 항목으로 따로 해요. `tests/test_history.py`(`"아직 캡처가 없어"`, `"목록에서 제거 (2)"` 등)와 `tests/test_capture_blocked.py`가 일부 문구를 검사하니, 문구를 바꾸면 테스트도 함께 고치세요. 버튼·메뉴 이름이 바뀌면 `installer/docs/사용법.txt`와 `docs/images/`도 맞춰요.
7. **출처 주석을 남겨요.** `pincapture.py` 맨 위 이력에 아래 형식으로 한 줄을 추가하고 `Modified:` 줄을 갱신해요. 이건 배포할 때 해요.
   ```
   #   v0.6.2 2026-11-02  Grok (모델 이름) — 바뀐 점 요약
   #   Created: 2026-08-04 by Claude via claude.ai / Modified: 2026-11-02 by <모델> via <도구>
   ```
   새 파일에는 `installer/build.py`처럼 `Created:` 줄과 `Changelog:`가 있는 머리 주석을 달아요.
8. **파일의 언어를 따라요.** `pincapture.py`의 주석과 독스트링은 한국어, `installer/build.py`·spec·`tests/`는 영어예요.
9. **소유자 승인 없이 의존성을 추가하지 않아요**(6장 9번).
10. **git은 소유자가 요청할 때만 써요.** `main`에 강제 푸시하지 않고, 태그는 `docs/RELEASE.md` 절차로만 만들어요.

## 6. 절대 깨면 안 되는 것

| # | 규칙 | 위치 | 깨지면 |
|---|---|---|---|
| 1 | `APP_USER_MODEL_ID = "pincapture.app"`과 `APP_MUTEX_NAME = "PinCaptureRunning"`이 `.iss`의 `AppUserModelID`·`AppMutex`와 같아야 해요 | `pincapture.py`, `installer/PinCapture.iss` | 작업 표시줄 고정·그룹이 깨지고, 설치·제거 프로그램이 실행 중인 앱을 감지하지 못해요 |
| 2 | Inno `AppId` GUID는 절대 바꾸지 않아요 | `installer/PinCapture.iss` `[Setup]` | 업그레이드가 아니라 별개 프로그램으로 설치돼요 |
| 3 | 재실행·바로가기 명령은 반드시 `launch_argv()`와 `app_dir()`로 만들어요 | `create_shortcut`, `restart_app`, `relaunch_command` | EXE의 `__file__`은 존재하지 않는 임시 경로라 바로가기·고정·다시 시작이 깨져요 |
| 4 | 종료는 `MainToolbar._exit_now()`의 `QApplication.instance().exit(0)`으로 해요. `quit()`는 쓰지 않아요 | `quit_app`, `restart_app` | Qt 6에서 `quit()`는 취소될 수 있어요. 핀 창이 떠 있으면 유령 프로세스가 남아 업데이트·제거를 막아요(회귀 테스트 `test_quit_really_exits_with_pins_on_screen`) |
| 5 | 단일 인스턴스 파이프는 사용자·홈 폴더·세션별 이름(`SINGLETON_NAME = _singleton_name()`)을 쓰고, 서버는 `UserAccessOption`을 켜요. 메시지는 `show`, `tray`, `quit`이에요 | `_singleton_name`, `main()`, `_on_singleton_msg` | 다른 Windows 계정끼리 충돌해 `--quit`이 실패해요. 홈 폴더가 빠지면 격리된 홈으로 도는 시험이 소유자의 실제 앱에 `quit`을 보내요(실제로 한 번 일어났어요. 회귀 테스트 `test_tests_never_talk_to_the_real_running_app`) |
| 6 | 다른 프로그램의 화면 캡처 방지를 우회하는 코드는 넣지 않아요. DXGI Desktop Duplication, Windows.Graphics.Capture 전환, DLL 언훅, 보호 프로세스 종료 모두 금지예요. 감지(`is_pure_black`, `screens_capture_blocked`)와 안내(`_capture_blocked`)만 해요 | 캡처 백엔드 | 소유자 정책 위반이고, 보안·법적 문제가 생길 수 있어요 |
| 7 | PyInstaller는 onedir로 유지해요 | `installer/PinCapture.spec` | onefile은 시작에 6~14초 걸려요(onedir은 약 3초) |
| 8 | pynput은 `.py` 그대로 넣어요(`module_collection_mode={"pynput": "py"}`). Qt 플러그인 제외 목록(`DROP`)을 바꾸면 `build.py`의 `MUST_HAVE`/`MUST_NOT`과 `THIRD_PARTY_NOTICES.txt`도 함께 바꿔요 | spec, `build.py` | LGPL 교체 가능성 조건이 깨지고, 번들 검사가 빌드를 중단시켜요 |
| 9 | 새 서드파티 의존성은 소유자 승인 후 `requirements*.txt`에 버전을 고정하고, `installer/docs/THIRD_PARTY_NOTICES.txt`와 `installer/docs/licenses/`에 고지와 라이선스 전문을 추가해요 | | 라이선스 위반 |
| 10 | `.iss`, `installer/docs/*.txt`, `installer/docs/licenses/*`는 UTF-8 BOM + CRLF를 유지해요 | `.gitattributes` | Inno Setup은 BOM이 없으면 한국어를 깨뜨려요 |
| 11 | 버전은 `X.Y.Z` 형식이고, 태그는 `vX.Y.Z`예요 | `build.py` 정규식, CI 태그 검사 | 빌드나 CI가 실패해요 |
| 12 | 바로가기 이름 `핀캡처.lnk`와 `--tray`·`--quit` 동작을 유지해요 | `create_shortcut`, `.iss`의 `[Icons]`·`[Run]`·`[UninstallDelete]`·`[Code]` | 자동 실행, 무인 업데이트, 제거 시 정리가 깨져요 |

에이전트의 파일 쓰기 도구는 보통 BOM 없이 LF로 저장해요. 10번 파일을 고쳤다면 반드시 확인하고 복구하세요.

```powershell
# 확인: True True 가 나와야 함 (BOM 있음, 모든 줄바꿈이 CRLF)
py -3.13 -c "import sys;b=open(sys.argv[1],'rb').read();print(b[:3]==b'\xef\xbb\xbf', b.count(b'\n')==b.count(b'\r\n'))" installer\docs\사용법.txt
# 복구: BOM + CRLF 로 다시 저장
py -3.13 -c "import sys,pathlib;p=pathlib.Path(sys.argv[1]);p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf-8-sig',newline='\r\n')" installer\docs\사용법.txt
```

## 7. 정해진 것, 그리고 아직 정하지 않은 것

아래는 확정이에요. 에이전트가 다른 값으로 바꾸지 않아요.

| 항목 | 확정 값 | 위치 |
|---|---|---|
| 앱 코드의 라이선스 | All rights reserved. MIT가 아니에요. 무료로 쓸 수 있지만 재배포·수정·판매는 허락 없이 할 수 없어요 | `LICENSE`, `README.md`, 정보 창 |
| 게시자 이름 | `ChamomileGrey` (한글 표기는 정보 창의 캐모마일그레이) | `installer/PinCapture.iss`의 `#define AppPublisher`와 `installer/build.py`의 `PUBLISHER`. 둘을 함께 바꿔요 |
| GitHub 저장소 | `ChamomileGrey/PinCapture` | https://github.com/ChamomileGrey/PinCapture |
| 후원 | https://ko-fi.com/chamomilegrey | `pincapture.py`의 `KOFI_URL`. 정보 창과 트레이의 후원하기만 이 주소를 열어요 |

아직 정하지 않은 것은 **소유자에게 물어보고, 에이전트가 정하지 않아요.**

| 항목 | 현재 상태 | 영향받는 곳 |
|---|---|---|
| 코드 서명 | 없음 | SmartScreen 경고가 떠요(안내는 `_배포안내.txt`, `사용법.txt` 4장). Windows 11 스마트 앱 컨트롤이 켜진 PC에서는 설치가 막혀요 |
| pynput을 Win32 `RegisterHotKey`로 바꿀지 | 미정(`docs/reviews/2026-10-22-release-review.md` 2번) | 단축키 코드, LGPL 고지, spec의 `module_collection_mode`, `build.py`의 `MUST_HAVE`, 관리자 권한 창 위에서의 단축키 동작 |

## 8. 알려진 환경 잡음

| 현상 | 원인 | 대처 |
|---|---|---|
| pytest 도중 `Windows fatal exception: access violation`이 한 번 출력되지만 시험은 모두 통과 | 소유자 PC의 Teruten WebCube(`T_Prevent64.dll`, 정부24 ezPDFReader 2.0G와 함께 설치됨)가 실행 중인 프로세스에 주입돼요. faulthandler가 그 예외를 출력해요 | 무시해도 돼요. 실패한 테스트가 있을 때만 조사하세요 |
| pytest가 `N passed`를 찍은 뒤 프로세스가 죽어요. Linux는 SIGSEGV(139), Windows는 `0xC0000005` 또는 CI 종료 코드 1 | 두 가지예요. (1) offscreen 클립보드에 남은 `QMimeData`를 해석기가 끝난 뒤에 지워요. (2) Qt 정적 소멸자가 shiboken을 호출해요. 로그에 예외 문장이 없을 수 있어요 | `pytest_sessionfinish`가 클립보드를 비우고, `pytest_unconfigure`가 그 다음 pytest 종료 코드로 `os._exit` 해요. 둘 다 지우지 마세요. Teruten이 시험 도중에 한 줄 찍는 것과는 다른 현상이에요 |
| 그 뷰어가 열려 있는 동안 모든 GDI 화면 캡처가 완전한 검정 | 같은 원인 | 앱은 0.6.1부터 감지하고 안내해요. 수동 확인 전에 뷰어를 닫거나 재부팅하세요. 우회 코드는 금지예요(6장 6번) |
| 단축키 자동 시험이 안 됨 | pynput은 주입된 키 입력(`SendInput` 등)을 무시해요 | 단축키는 사람이 실제 키보드로 확인해요(`docs/RELEASE.md` 수동 시험) |
| offscreen 스크린샷에 글자가 없음 | `QT_QPA_PLATFORM=offscreen`에는 글꼴이 없어요 | 구조 확인용으로는 충분해요. README 스크린샷은 실제 Windows 플랫폼에서 만들어요(9장) |

## 9. 개인정보 규칙

- `archive/`는 절대 커밋하지 않아요. 옛 버전에 소유자 이메일이 들어 있어요. 그 내용을 추적되는 파일로 옮기지도 않아요.
- 코드, 주석, 문서, 테스트, 커밋 메시지, 이슈 어디에도 소유자 이메일, Windows 사용자 이름, OneDrive 경로, 실제 이름이 들어간 `C:\Users\...` 경로를 쓰지 않아요. 예시는 `C:\Users\<사용자>`나 `%USERPROFILE%`로 써요.
- `pincapture.log`에는 Python 실행 파일 경로(사용자 이름 포함)와 인수가 기록돼요. 로그를 문서나 이슈에 붙일 때는 경로를 가리세요.
- 시험은 항상 격리된 홈에서 실행해요. 새 테스트도 실제 `~/.pincapture`나 실제 저장 폴더를 건드리지 않도록 `pc`·`toolbar` 픽스처나 `tmp_path`를 쓰고, 별도 프로세스에는 `tests/_isolation.py`의 `isolated_env(home)`을 넘겨요(`test_process._env`가 이걸 써요). 홈만 바꾸면 안 돼요. 기본 저장 폴더는 Windows 알려진 폴더 API(사진)라서 `USERPROFILE`을 따르지 않아요. Windows에서는 단일 인스턴스 파이프 이름에 홈 폴더가 들어가서, 시험이 소유자의 실행 중인 앱에 신호를 보내지 않아요.
- 커밋 전에 개인정보를 점검해요(`git add` 다음에 실행):
  ```powershell
  git grep --cached -nIE '@(gmail|naver|daum|hanmail)\.|\\OneDrive|C:\\Users\\[A-Za-z]'
  ```
  PowerShell에서 실행해요(Git Bash는 `\\`를 바꿔 버려요). 나와도 되는 결과는 이 명령이 적힌 `AGENTS.md` 줄과 `installer/docs/licenses/Qt-third-party.txt`의 제3자 주소(원문 그대로 둬요)뿐이에요. 한글 이름이 들어간 경로는 이 패턴에 걸리지 않으니 `C:\Users\` 검색 결과도 직접 훑어보세요. `archive/`가 목록에 보이면 즉시 `git rm -r --cached archive`로 빼요.
- **README 스크린샷을 다시 만드는 방법**: 창이 잠깐 화면에 뜨니 소유자에게 먼저 알려요. 격리된 홈과 중립적인 저장 폴더를 쓰고, `QT_QPA_PLATFORM` 없이 실제 플랫폼에서 실행해요.
  ```powershell
  $h = Join-Path $env:TEMP "pincap-shot-home"
  New-Item -ItemType Directory -Force "$h\.pincapture" | Out-Null
  # BOM 없이 써야 함 (Set-Content/Out-File -Encoding utf8 은 BOM 을 붙여 설정 읽기가 실패 → 실제 사진 폴더 경로가 찍힘)
  [IO.File]::WriteAllText("$h\.pincapture\config.json", '{"save_dir": "C:\\Users\\사용자\\Pictures\\PinCapture"}')
  $env:USERPROFILE = $h; $env:HOME = $h; $env:PINCAP_NO_LOG = "1"
  Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
  Push-Location $h; py -3.13 D:\Tools\PinCapture\pincapture.py --selftest; Pop-Location
  # $h\selftest_out\{main,settings,pin,overlay}.png → docs\images\screenshot-{main,settings,pin,overlay}.png
  ```
  복사하기 전에 `settings.png`의 저장 폴더가 `C:\Users\사용자\Pictures\PinCapture`인지, 다른 개인정보가 없는지 눈으로 확인해요. 이 PowerShell 창은 환경 변수가 바뀌었으니 끝나면 닫아요.

## 10. 문서 위치

| 문서 | 내용 |
|---|---|
| `README.md` | 저장소 소개, 설치, 스크린샷 |
| `GROK.md` | Grok 운영자용 요약(이 문서가 원본) |
| `CHANGELOG.md` | 버전별 변경 기록 |
| `docs/ARCHITECTURE.md` | 코드 구조와 주요 흐름 |
| `docs/ROADMAP.md` | 할 일과 우선순위(P0부터) |
| `docs/RELEASE.md` | 배포 체크리스트, 수동 시험, CI 첫 실행 디버깅 |
| `docs/DEVELOPMENT.md` | 소스 실행, Python 선택 함정, 설정·로그 위치, 바로가기, 문제 해결, DPI |
| `docs/reviews/` | 검토·사건 기록. 작성 시점 기준이라 현재 코드와 다를 수 있어요. `2026-10-22-release-review.md`는 v0.5.3 배포 전 검토예요(차단 항목 대부분은 0.6.x에서 반영). `2026-10-26-black-capture.md`는 검은 캡처 사건 기록이에요 |
| `installer/docs/사용법.txt` | 최종 사용자 안내(설치 폴더와 시작 메뉴 `핀캡처 사용법`) |
