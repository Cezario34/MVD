# tests/test_captcha_service.py
import os
import pytest
import tempfile

import modules.captcha_service as cs_mod
from modules.captcha_service import CaptchaService

# Заглушка — успешное решение
class DummySolverSuccess:
    def __init__(self, api_key):
        assert api_key == "test-key"
    def normal(self, image_path):
        return {"code": "42", "captchaId": "cid"}
    def report(self, cid, correct):
        pass

# Заглушка — всегда неудача
class DummySolverFailure:
    def __init__(self, api_key): pass
    def normal(self, image_path):
        return {"code": "", "captchaId": "cid"}
    def report(self, cid, correct): pass

@pytest.fixture(autouse=True)
def clear_proxies():
    """Перед каждым тестом и после него чистим прокси-переменные."""
    for k in ("HTTP_PROXY", "HTTPS_PROXY"):
        os.environ.pop(k, None)
    yield
    for k in ("HTTP_PROXY", "HTTPS_PROXY"):
        os.environ.pop(k, None)

@pytest.fixture
def img_file(tmp_path):
    """Создаёт временный файл-«картинку» и отдаёт его путь."""
    f = tmp_path / "cap.png"
    f.write_bytes(b"")  # можно пустой
    return str(f)

def test_solve_success(monkeypatch, img_file):
    # Мокаем TwoCaptcha на заглушку, возвращающую code="42"
    monkeypatch.setattr(cs_mod, "TwoCaptcha", DummySolverSuccess)

    svc = CaptchaService(api_key="test-key", max_attempts=3)
    result = svc.solve(img_file)

    assert result == "42"
    # и прокси убраны
    assert "HTTP_PROXY" not in os.environ
    assert "HTTPS_PROXY" not in os.environ

def test_solve_failure(monkeypatch, img_file):
    # Мокаем TwoCaptcha на заглушку, всегда возвращающую пустой код
    monkeypatch.setattr(cs_mod, "TwoCaptcha", DummySolverFailure)

    svc = CaptchaService(api_key="any", max_attempts=2)
    result = svc.solve(img_file)

    assert result is None
    # прокси тоже убраны
    assert "HTTP_PROXY" not in os.environ
    assert "HTTPS_PROXY" not in os.environ

def test_proxy_set_and_cleared(monkeypatch, img_file):
    called = {}
    class DummySolver:
        def __init__(self, api_key): pass
        def normal(self, path):
            # Проверяем, что прокси уже установлены
            called['http']  = os.environ.get("HTTP_PROXY")
            called['https'] = os.environ.get("HTTPS_PROXY")
            return {"code": "ok", "captchaId": "cid"}
        def report(self, cid, correct): pass

    monkeypatch.setattr(cs_mod, "TwoCaptcha", DummySolver)

    svc = CaptchaService(api_key="k", max_attempts=1)
    result = svc.solve(img_file)

    assert result == "ok"
    assert called['http']  == 'http://FgtSa8:YupXza@168.80.202.107:8000'
    assert called['https'] == 'http://FgtSa8:YupXza@168.80.202.107:8000'
    # после solve() прокси должны быть сброшены
    assert "HTTP_PROXY" not in os.environ
    assert "HTTPS_PROXY" not in os.environ

