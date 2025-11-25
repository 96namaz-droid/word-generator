"""
Удобный запуск веб-версии приложения одним кликом.
Скрипт сам переключается на venv, ставит зависимости и открывает браузер.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn

import config

PROJECT_ROOT = Path(__file__).parent.resolve()
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / ("python.exe" if os.name == "nt" else "python")
LAUNCH_URL = "http://localhost:8000"


def _running_in_venv() -> bool:
    return Path(sys.executable).resolve() == VENV_PYTHON.resolve()


def ensure_venv():
    """Перезапускает скрипт через python из venv, если его запустили напрямую."""
    if _running_in_venv() or os.environ.get("WORDGEN_WEB_INSIDE_VENV") == "1":
        return

    if not VENV_PYTHON.exists():
        print("Не найден виртуальный интерпретатор по адресу:", VENV_PYTHON)
        print("Создай venv командой: python -m venv venv")
        sys.exit(1)

    print("Переключаюсь на интерпретатор из venv...")
    env = os.environ.copy()
    env["WORDGEN_WEB_INSIDE_VENV"] = "1"
    subprocess.check_call([str(VENV_PYTHON), __file__], env=env)
    sys.exit(0)


def ensure_dependencies():
    """Ставит быстрые зависимости при необходимости."""
    try:
        import fastapi  # noqa: F401
    except ModuleNotFoundError:
        print("FastAPI не найден. Устанавливаю зависимости...")
        req = PROJECT_ROOT / "requirements.txt"
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])

    try:
        import web_app  # noqa: F401
    except ModuleNotFoundError:
        # Если локальные пакеты не находятся, что-то совсем не так — пусть свалится позже.
        pass


def open_browser_when_ready(url: str):
    """Пытается открыть браузер, когда сервер начинает отвечать."""

    def _worker():
        for _ in range(30):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen(url):  # noqa: S310
                    pass
                break
            except Exception:
                continue
        webbrowser.open(url)

    threading.Thread(target=_worker, daemon=True).start()


def main():
    config.ensure_directories()
    print("=" * 60)
    print("Запуск веб-версии генератора протоколов")
    print("=" * 60)
    print("\nВеб-интерфейс откроется автоматически или доступен по адресу:")
    print(f"  {LAUNCH_URL}")
    print("\nДля доступа из локальной сети используйте IP текущего ПК:")
    print("  http://<IP_компьютера>:8000")
    print("\nДля остановки нажми Ctrl+C в этом окне")
    print("=" * 60)
    print()

    open_browser_when_ready(LAUNCH_URL)

    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    ensure_venv()
    ensure_dependencies()
    main()

