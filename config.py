import json
import os

CONFIG_FILE = os.path.expanduser("~/.config/gotify-client-arch.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"url": "", "token": ""}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {"url": "", "token": ""}

def save_config(url, token):
    config = {"url": url, "token": token}
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
