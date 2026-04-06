import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".devswings"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_config(data: dict):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def get_token():
    return load_config().get("access_token")

def save_token(token: str):
    config = load_config()
    config["access_token"] = token
    save_config(config)
