"""
Configuration and user management module
Manages config.json (runtime parameters) and users.json (user accounts).
"""
import os, sys, json, hashlib
import lang

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
USERS_PATH = os.path.join(BASE_DIR, 'users.json')

DEFAULT_CONFIG = {
    "port": 5000,
    "login_required": False,
    "cli_mode": False,
    "public_access": False
}

DEFAULT_USERS = {
    "root": {
        "password": "",
        "salt": "",
        "permissions": {
            "cli": True,
            "regions": ["uk", "au", "us"]
        }
    }
}


# ═══════════════════════════════════════════════════
#  Config file read/write
# ═══════════════════════════════════════════════════

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_users():
    if not os.path.exists(USERS_PATH):
        save_users(DEFAULT_USERS)
        return dict(DEFAULT_USERS)
    with open(USERS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_users(users):
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════
#  Password utilities
# ═══════════════════════════════════════════════════

def hash_password(password, salt=None):
    """Returns (hash_hex, salt_hex)"""
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h, salt


def verify_password(password, stored_hash, salt):
    h, _ = hash_password(password, salt)
    return h == stored_hash


# ═══════════════════════════════════════════════════
#  User CRUD
# ═══════════════════════════════════════════════════

def add_user(username, password, permissions=None):
    users = load_users()
    if username in users:
        return False, lang.get('userdlg_user_exists', 'zh')
    pwd_hash, salt = hash_password(password)
    users[username] = {
        "password": pwd_hash,
        "salt": salt,
        "permissions": permissions or {"cli": False, "regions": []}
    }
    save_users(users)
    return True, lang.get('userdlg_added', 'zh')


def update_user(username, password=None, permissions=None):
    users = load_users()
    if username not in users:
        return False, lang.get('userdlg_not_found', 'zh')
    if password is not None:
        pwd_hash, salt = hash_password(password)
        users[username]["password"] = pwd_hash
        users[username]["salt"] = salt
    if permissions is not None:
        users[username]["permissions"] = permissions
    save_users(users)
    return True, lang.get('userdlg_updated', 'zh')


def delete_user(username):
    if username == "root":
        return False, lang.get('userdlg_root_protect', 'zh')
    users = load_users()
    if username not in users:
        return False, lang.get('userdlg_not_found', 'zh')
    del users[username]
    save_users(users)
    return True, lang.get('success', 'zh')


def get_user_list():
    """Returns all usernames and permission summaries (without password hashes)"""
    users = load_users()
    return [
        {
            "username": name,
            "permissions": info.get("permissions", {})
        }
        for name, info in users.items()
    ]


def authenticate(username, password):
    """Authenticate user; returns permission dict on success, None on failure"""
    users = load_users()
    user = users.get(username)
    if not user:
        return None
    if verify_password(password, user["password"], user.get("salt", "")):
        return user.get("permissions", {"cli": False, "regions": []})
    return None
