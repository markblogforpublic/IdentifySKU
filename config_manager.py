"""
Configuration and user management module
Manages config.json (runtime parameters) and users.json (user accounts).
"""
import os, sys, json, hashlib

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

def hash_password(password, salt_bytes=None):
    """Returns (hash_hex, salt_hex). Uses PBKDF2-HMAC-SHA256 with 600k iterations."""
    if len(password) > 128:
        raise ValueError("Password exceeds maximum length (128 characters)")
    if salt_bytes is None:
        salt_bytes = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 600000)
    return dk.hex(), salt_bytes.hex()


def verify_password(password, stored_hash, salt_hex):
    """Verify password against stored PBKDF2 hash."""
    salt_bytes = bytes.fromhex(salt_hex) if salt_hex else b''
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 600000)
    return dk.hex() == stored_hash


# ═══════════════════════════════════════════════════
#  User CRUD
# ═══════════════════════════════════════════════════

def add_user(username, password, permissions=None):
    users = load_users()
    if username in users:
        return False, "User already exists"
    pwd_hash, salt = hash_password(password)
    users[username] = {
        "password": pwd_hash,
        "salt": salt,
        "permissions": permissions or {"cli": False, "regions": []}
    }
    save_users(users)
    return True, "User added successfully"


def update_user(username, password=None, permissions=None):
    users = load_users()
    if username not in users:
        return False, "User not found"
    if password is not None:
        pwd_hash, salt = hash_password(password)
        users[username]["password"] = pwd_hash
        users[username]["salt"] = salt
    if permissions is not None:
        users[username]["permissions"] = permissions
    save_users(users)
    return True, "User updated successfully"


def delete_user(username):
    if username == "root":
        return False, "Cannot delete root user"
    users = load_users()
    if username not in users:
        return False, "User not found"
    del users[username]
    save_users(users)
    return True, "Success"


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
    stored_hash = user.get("password", "")
    if not stored_hash:
        return None  # No password set, cannot authenticate
    if verify_password(password, stored_hash, user.get("salt", "")):
        return user.get("permissions", {"cli": False, "regions": []})
    return None
