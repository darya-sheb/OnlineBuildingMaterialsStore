# test_coverage.py
import pytest
import subprocess
import sys


def test_coverage() -> None:
    """Тест проверяет, что покрытие кода не ниже 65%"""
    # Запускаем pytest с плагином coverage
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=.",  # измеряем покрытие для текущей директории
        "--cov-report=term-missing",  # показываем непокрытые строки
        "--cov-fail-under=65",  # минимальный процент покрытия
        "-q"
    ], capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    assert result.returncode == 0, "Покрытие кода ниже 65%"