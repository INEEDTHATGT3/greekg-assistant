import os
import json
import sys

_APP_NAME = "GreekG"
_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".greekg")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "settings.json")

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_CONFIG_PATH = os.path.join(_BASE_DIR, "config", "default_config.json")
APPS_CONFIG_PATH = os.path.join(_BASE_DIR, "apps_config.json")

_settings = {}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_settings() -> dict:
    global _settings
    with open(_DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        defaults = json.load(f)

    if os.path.exists(_CONFIG_FILE):
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                user = json.load(f)
            _settings = _deep_merge(defaults, user)
        except (json.JSONDecodeError, OSError):
            _settings = defaults
    else:
        _settings = defaults

    os.makedirs(_CONFIG_DIR, exist_ok=True)
    save_settings()
    return _settings


def save_settings():
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(_settings, f, indent=2)


def get(key_path: str, default=None):
    keys = key_path.split(".")
    val = _settings
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


def set(key_path: str, value):
    global _settings
    keys = key_path.split(".")
    d = _settings
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value
    save_settings()


def get_all() -> dict:
    return _settings.copy()


def get_apps_config_path() -> str:
    custom = get("apps_config_path", "")
    if custom and os.path.exists(custom):
        return custom
    return APPS_CONFIG_PATH


def load_apps_config() -> dict:
    path = get_apps_config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k.lower(): v for k, v in raw.items() if not k.startswith("_")}
    except (json.JSONDecodeError, OSError):
        return {}


def is_auto_start_enabled() -> bool:
    return get("general.auto_start_windows", False)


def set_auto_start(enabled: bool):
    set("general.auto_start_windows", enabled)
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            exe = sys.executable
            if getattr(sys, "frozen", False):
                exe = sys.executable
            else:
                exe = f'"{sys.executable}" "{os.path.join(_BASE_DIR, "main.py")}"'
            winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, exe)
        else:
            try:
                winreg.DeleteValue(key, _APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass
