import json
import os
import tempfile
from typing import Dict, Any, List

STORE_DIR = os.environ.get('STORAGE_DIR', os.path.join(os.path.dirname(__file__), 'data'))
STORE_PATH = os.path.join(STORE_DIR, 'store.json')

DEFAULT_STORE = {
    "users": [],  # list of {id, name, email, password}
    "expenses": []  # list of {id, description, amount, date_iso, paid_by, split_type, shares:[{user_id, amount}]}
}


def ensure_store_exists() -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_PATH):
        save_store(DEFAULT_STORE)


def load_store() -> Dict[str, Any]:
    ensure_store_exists()
    with open(STORE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _atomic_write(path: str, data: str) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_store_', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
            tmp.write(data)
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def save_store(store: Dict[str, Any]) -> None:
    ensure_store_exists()
    data = json.dumps(store, ensure_ascii=False, indent=2)
    _atomic_write(STORE_PATH, data)


def next_id(items: List[Dict[str, Any]]) -> int:
    return (max((item.get('id', 0) for item in items), default=0) + 1)


# CRUD helpers

def list_users() -> List[Dict[str, Any]]:
    return load_store().get('users', [])


def add_user(name: str, email: str, password: str) -> Dict[str, Any]:
    store = load_store()
    users = store.get('users', [])
    if any(u['email'].lower() == email.lower() for u in users):
        raise ValueError('Email already exists')
    user = {
        'id': next_id(users),
        'name': name,
        'email': email,
        'password': password,
    }
    users.append(user)
    store['users'] = users
    save_store(store)
    return user


def get_user(user_id: int) -> Dict[str, Any]:
    users = list_users()
    for u in users:
        if u['id'] == user_id:
            return u
    raise ValueError('User not found')


def list_expenses() -> List[Dict[str, Any]]:
    return load_store().get('expenses', [])


def add_expense_record(description: str, amount: float, paid_by: int, split_type: str, shares: List[Dict[str, Any]], date_iso: str) -> Dict[str, Any]:
    store = load_store()
    expenses = store.get('expenses', [])
    expense = {
        'id': next_id(expenses),
        'description': description,
        'amount': amount,
        'date_iso': date_iso,
        'paid_by': paid_by,
        'split_type': split_type,
        'shares': shares,
    }
    expenses.append(expense)
    store['expenses'] = expenses
    save_store(store)
    return expense


def compute_balances() -> Dict[int, float]:
    users = list_users()
    expenses = list_expenses()
    balances = {u['id']: 0.0 for u in users}

    # Amount paid per user
    paid_by_map = {}
    for e in expenses:
        paid_by_map[e['paid_by']] = paid_by_map.get(e['paid_by'], 0.0) + float(e['amount'])

    # Amount owed per user (sum of shares)
    owed_map = {}
    for e in expenses:
        for s in e.get('shares', []):
            owed_map[s['user_id']] = owed_map.get(s['user_id'], 0.0) + float(s['amount'])

    for uid in balances:
        paid = paid_by_map.get(uid, 0.0)
        owed = owed_map.get(uid, 0.0)
        balances[uid] = paid - owed

    return balances
