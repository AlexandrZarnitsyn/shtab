from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Header, Query, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import base64
import requests
import json
from datetime import datetime, timedelta, timezone
import sqlite3
import os
import hashlib
import secrets
import hmac
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DATA_DIR = os.environ.get('SHTAB_DATA_DIR') or ('/data' if os.path.isdir('/data') else os.path.dirname(BASE_DIR))
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
DB_PATH = os.environ.get('SHTAB_DB_PATH', os.path.join(DEFAULT_DATA_DIR, 'shtab.db'))
SESSION_TTL_DAYS = 30
SUPERADMIN_EMAIL = 's.zarnitsyn@yandex.ru'
SUPERADMIN_PASSWORD = '1235476890qwE@'
SUPERADMIN_NAME = 'Александр Зарницын'
APP_SECRET = os.environ.get('SHTAB_APP_SECRET', 'shtab-local-dev-secret')
WB_TOKEN_LIFETIME_DAYS = 180
WB_TOKEN_WARNING_DAYS = 30
DEFAULT_SYNC_INTERVAL_MINUTES = 15
FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', 'https://shtab-three.vercel.app').rstrip('/')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', 're_QfqZXsrg_KJ4cTiwumpvnGi5AyFibH3XG')
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
PASSWORD_RESET_TTL_MINUTES = int(os.environ.get('PASSWORD_RESET_TTL_MINUTES', '30'))


app = FastAPI(title="Shtab Backend")

TARIFFS = {
    "none": {"label": "Не назначен", "dashboard": False, "procurement": False, "finance": False, "team": False, "sku_details": False, "import_history": False, "audit_log": False, "forecasting": False, "max_users": 1, "max_sku": 500},
    "starter": {"label": "Старт", "dashboard": True, "procurement": False, "finance": False, "team": False, "sku_details": False, "import_history": False, "audit_log": False, "forecasting": False, "max_users": 2, "max_sku": 500},
    "growth": {"label": "Рост", "dashboard": True, "procurement": True, "finance": True, "team": True, "sku_details": True, "import_history": True, "audit_log": True, "forecasting": True, "max_users": 5, "max_sku": 5000},
    "enterprise": {"label": "Корпоративный", "dashboard": True, "procurement": True, "finance": True, "team": True, "sku_details": True, "import_history": True, "audit_log": True, "forecasting": True, "max_users": 9999, "max_sku": 999999},
}

ORG_ADMIN_ROLES = {"Руководитель"}
TEAM_ROLES = {"Руководитель", "Финансы", "Закупки", "Оператор"}
ROLE_PERMISSIONS = {
    "Руководитель": {
        "manage_org": True,
        "manage_billing": True,
        "manage_team": True,
        "manage_products": True,
        "view_finance": True,
        "view_team": True,
        "view_audit": True,
        "view_sku_details": True,
    },
    "Финансы": {
        "manage_org": False,
        "manage_billing": False,
        "manage_team": False,
        "manage_products": False,
        "view_finance": True,
        "view_team": False,
        "view_audit": False,
        "view_sku_details": True,
    },
    "Закупки": {
        "manage_org": False,
        "manage_billing": False,
        "manage_team": False,
        "manage_products": True,
        "view_finance": False,
        "view_team": False,
        "view_audit": False,
        "view_sku_details": True,
    },
    "Оператор": {
        "manage_org": False,
        "manage_billing": False,
        "manage_team": False,
        "manage_products": False,
        "view_finance": False,
        "view_team": False,
        "view_audit": False,
        "view_sku_details": False,
    },
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().replace(microsecond=0).isoformat()


def db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table_name, column_def):
    col_name = column_def.split()[0]
    cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if col_name not in cols:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")


def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS organizations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, tariff TEXT NOT NULL, marketplace TEXT, owner_user_id INTEGER NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS memberships (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, user_id INTEGER NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS invites (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, email TEXT NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, sku TEXT NOT NULL, account TEXT NOT NULL, name TEXT NOT NULL, channel TEXT NOT NULL, warehouse TEXT NOT NULL, price REAL NOT NULL, unit_cost REAL NOT NULL, stock REAL NOT NULL, reserved REAL NOT NULL, inbound REAL NOT NULL, lead_time_days REAL NOT NULL, avg_daily_sales REAL NOT NULL, trend REAL NOT NULL, commission_rate REAL NOT NULL, logistics_per_unit REAL NOT NULL, ad_spend REAL NOT NULL, return_rate REAL NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS product_imports (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, imported_by_user_id INTEGER NOT NULL, row_count INTEGER NOT NULL, mode TEXT NOT NULL DEFAULT 'replace', created_at TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, actor_user_id INTEGER, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT DEFAULT '', details_json TEXT DEFAULT '{}', created_at TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS manual_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, actor_user_id INTEGER, tariff_code TEXT NOT NULL, amount REAL NOT NULL DEFAULT 0, period_days INTEGER NOT NULL DEFAULT 30, payer_name TEXT DEFAULT '', payment_channel TEXT DEFAULT '', note TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'confirmed', created_at TEXT NOT NULL, paid_until TEXT DEFAULT '')")
    cur.execute("CREATE TABLE IF NOT EXISTS marketplace_connections (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, marketplace TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'disconnected', client_id TEXT DEFAULT '', api_key_encrypted TEXT DEFAULT '', token_created_at TEXT DEFAULT '', token_expires_at TEXT DEFAULT '', auto_sync_enabled INTEGER NOT NULL DEFAULT 1, sync_interval_minutes INTEGER NOT NULL DEFAULT 15, last_sync_at TEXT DEFAULT '', last_success_at TEXT DEFAULT '', last_error TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS marketplace_sync_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, marketplace TEXT NOT NULL, status TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT DEFAULT '', added_count INTEGER NOT NULL DEFAULT 0, updated_count INTEGER NOT NULL DEFAULT 0, removed_count INTEGER NOT NULL DEFAULT 0, message TEXT DEFAULT '' )")
    cur.execute("CREATE TABLE IF NOT EXISTS admin_client_meta (organization_id INTEGER PRIMARY KEY, source TEXT DEFAULT '', stage TEXT DEFAULT 'new', note TEXT DEFAULT '', tags TEXT DEFAULT '', internal_status TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS tariff_presets (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, label TEXT NOT NULL, price_month REAL NOT NULL DEFAULT 0, max_users INTEGER NOT NULL DEFAULT 2, max_sku INTEGER NOT NULL DEFAULT 500, features_json TEXT NOT NULL DEFAULT '{}' , is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS password_reset_tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, token TEXT NOT NULL UNIQUE, expires_at TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, used_at TEXT DEFAULT '')")

    add_column_if_missing(conn, "organizations", "tariff_code TEXT DEFAULT 'starter'")
    add_column_if_missing(conn, "organizations", "billing_status TEXT DEFAULT 'pending_payment'")
    add_column_if_missing(conn, "organizations", "paid_until TEXT DEFAULT ''")
    add_column_if_missing(conn, "organizations", "max_users INTEGER DEFAULT 2")
    add_column_if_missing(conn, "organizations", "max_sku INTEGER DEFAULT 500")
    add_column_if_missing(conn, "sessions", "created_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "sessions", "expires_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "invites", "token TEXT DEFAULT ''")
    add_column_if_missing(conn, "invites", "created_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "invites", "accepted_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "product_imports", "added_count INTEGER DEFAULT 0")
    add_column_if_missing(conn, "product_imports", "updated_count INTEGER DEFAULT 0")
    add_column_if_missing(conn, "product_imports", "removed_count INTEGER DEFAULT 0")
    add_column_if_missing(conn, "product_imports", "change_summary_json TEXT DEFAULT '{}' ")
    add_column_if_missing(conn, "products", "source_marketplace TEXT DEFAULT ''")
    add_column_if_missing(conn, "products", "external_product_id TEXT DEFAULT ''")
    add_column_if_missing(conn, "products", "last_sync_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "users", "created_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "organizations", "access_state TEXT DEFAULT 'pending'")
    add_column_if_missing(conn, "organizations", "custom_tariff_label TEXT DEFAULT ''")
    add_column_if_missing(conn, "organizations", "custom_features_json TEXT DEFAULT ''")
    add_column_if_missing(conn, "organizations", "custom_price_month REAL DEFAULT 0")
    add_column_if_missing(conn, "organizations", "frozen_at TEXT DEFAULT ''")
    add_column_if_missing(conn, "organizations", "blocked_reason TEXT DEFAULT ''")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memberships_org_user ON memberships(organization_id, user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_org ON products(organization_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_product_imports_org_created ON product_imports(organization_id, created_at DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_org_created ON audit_logs(organization_id, created_at DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_manual_payments_org_created ON manual_payments(organization_id, created_at DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_connections_org ON marketplace_connections(organization_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_sync_logs_org ON marketplace_sync_logs(organization_id, started_at DESC)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_memberships_org_user ON memberships(organization_id, user_id)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_invites_org_email_status ON invites(organization_id, email, status)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_marketplace_connections_org_marketplace ON marketplace_connections(organization_id, marketplace)")

    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_tariff_presets_code ON tariff_presets(code)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_password_reset_tokens_token ON password_reset_tokens(token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id)")

    conn.execute(
        "UPDATE sessions SET created_at = COALESCE(NULLIF(created_at, ''), ?), expires_at = COALESCE(NULLIF(expires_at, ''), ?) WHERE COALESCE(created_at, '') = '' OR COALESCE(expires_at, '') = ''",
        (iso_now(), (now_utc() + timedelta(days=SESSION_TTL_DAYS)).replace(microsecond=0).isoformat()),
    )
    conn.execute("DELETE FROM invites WHERE lower(email) = ?", ("finance@company.ru",))
    now_iso = iso_now()
    builtin_preset_rows = [
        ('starter', 'Старт', 4900, TARIFFS['starter']['max_users'], TARIFFS['starter']['max_sku'], json.dumps(TARIFFS['starter'], ensure_ascii=False), 1, now_iso, now_iso),
        ('growth', 'Рост', 14900, TARIFFS['growth']['max_users'], TARIFFS['growth']['max_sku'], json.dumps(TARIFFS['growth'], ensure_ascii=False), 1, now_iso, now_iso),
        ('enterprise', 'Корпоративный', 49900, TARIFFS['enterprise']['max_users'], TARIFFS['enterprise']['max_sku'], json.dumps(TARIFFS['enterprise'], ensure_ascii=False), 1, now_iso, now_iso),
    ]
    for row in builtin_preset_rows:
        conn.execute("INSERT OR IGNORE INTO tariff_presets(code, label, price_month, max_users, max_sku, features_json, is_active, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?)", row)
    conn.execute("UPDATE users SET created_at = COALESCE(NULLIF(created_at, ''), ?) WHERE COALESCE(created_at, '') = ''", (now_iso,))
    existing_admin = conn.execute("SELECT id FROM users WHERE email = ?", (SUPERADMIN_EMAIL,)).fetchone()
    if existing_admin:
        conn.execute("UPDATE users SET full_name = ?, password_hash = ? WHERE email = ?", (SUPERADMIN_NAME, hash_password(SUPERADMIN_PASSWORD), SUPERADMIN_EMAIL))
    else:
        conn.execute("INSERT INTO users(full_name, email, password_hash, created_at) VALUES(?, ?, ?, ?)", (SUPERADMIN_NAME, SUPERADMIN_EMAIL, hash_password(SUPERADMIN_PASSWORD), iso_now()))
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return hmac.compare_digest(check, digest)


def purge_expired_sessions(conn):
    conn.execute("DELETE FROM sessions WHERE COALESCE(expires_at, '') != '' AND expires_at < ?", (iso_now(),))


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    created_at = iso_now()
    expires_at = (now_utc() + timedelta(days=SESSION_TTL_DAYS)).replace(microsecond=0).isoformat()
    conn = db()
    purge_expired_sessions(conn)
    conn.execute("INSERT INTO sessions(token, user_id, created_at, expires_at) VALUES(?, ?, ?, ?)", (token, user_id, created_at, expires_at))
    conn.commit()
    conn.close()
    return token


def get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.replace("Bearer ", "", 1)


def get_user_id_from_token(authorization: Optional[str]) -> int:
    token = get_bearer_token(authorization)
    conn = db()
    purge_expired_sessions(conn)
    row = conn.execute("SELECT user_id, expires_at FROM sessions WHERE token = ?", (token,)).fetchone()
    conn.commit()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(row["user_id"])


def get_user(authorization: Optional[str]):
    user_id = get_user_id_from_token(authorization)
    conn = db()
    row = conn.execute("SELECT id, full_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return row


def is_super_admin_email(email: Optional[str]) -> bool:
    return (email or '').strip().lower() == SUPERADMIN_EMAIL


def ensure_super_admin(authorization: Optional[str]):
    user = get_user(authorization)
    if not is_super_admin_email(user['email']):
        raise HTTPException(status_code=403, detail='Админ-панель доступна только главному администратору')
    return user


def ensure_membership(user_id: int, organization_id: int):
    conn = db()
    row = conn.execute("SELECT id FROM memberships WHERE user_id = ? AND organization_id = ?", (user_id, organization_id)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=403, detail="No access to organization")


def get_membership(user_id: int, organization_id: int):
    conn = db()
    row = conn.execute("SELECT * FROM memberships WHERE user_id = ? AND organization_id = ?", (user_id, organization_id)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=403, detail="No access to organization")
    return row


def ensure_org_admin(user_id: int, organization_id: int):
    membership = get_membership(user_id, organization_id)
    if membership["role"] not in ORG_ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Роль руководителя обязательна для этого действия")
    return membership




def get_role_permissions(role: str):
    return ROLE_PERMISSIONS.get(role or "", ROLE_PERMISSIONS["Оператор"])


def membership_to_dict(row):
    item = dict(row)
    item["permissions"] = get_role_permissions(item.get("role") or "")
    return item


def ensure_org_permission(user_id: int, organization_id: int, permission_name: str):
    membership = get_membership(user_id, organization_id)
    permissions = get_role_permissions(membership["role"])
    if not permissions.get(permission_name, False):
        raise HTTPException(status_code=403, detail="Недостаточно прав для этого действия")
    return membership


def sanitize_product_for_role(item: dict, role: str):
    permissions = get_role_permissions(role)
    if permissions.get("view_finance", False):
        return item
    for field in [
        "price", "unit_cost", "commission_rate", "logistics_per_unit", "ad_spend", "return_rate",
        "break_even_price", "recommended_price", "forecast_revenue_30d", "forecast_profit_30d",
        "profit_margin_pct", "roas", "acos_pct", "contribution_per_unit",
    ]:
        item[field] = None
    return item

def sync_org_billing_state(conn, org_row):
    if not org_row:
        return org_row
    item = dict(org_row)
    paid_until = (item.get("paid_until") or "").strip()
    if item.get("billing_status") == "active" and paid_until:
        try:
            expiry_date = datetime.fromisoformat(paid_until).date()
            today = now_utc().date()
            if expiry_date < today:
                conn.execute("UPDATE organizations SET billing_status = ?, paid_until = ? WHERE id = ?", ("blocked", paid_until, int(item["id"])))
                item["billing_status"] = "blocked"
                log_action(conn, int(item["id"]), None, "Тариф автоматически завершён", "billing", str(item["id"]), {"paid_until": paid_until})
            item["billing_days_left"] = (expiry_date - today).days
        except Exception:
            item["billing_days_left"] = None
    else:
        item["billing_days_left"] = None
    return item


def get_org(org_id: int):
    conn = db()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    row = sync_org_billing_state(conn, row)
    conn.commit()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Organization not found")
    return row


def get_tariff_features(code: str):
    normalized = (code or "starter").strip()
    if normalized in TARIFFS:
        return TARIFFS[normalized]
    conn = db()
    row = conn.execute("SELECT * FROM tariff_presets WHERE code = ? AND is_active = 1", (normalized,)).fetchone()
    conn.close()
    if row:
        try:
            features = json.loads(row["features_json"] or "{}")
        except Exception:
            features = {}
        features.setdefault("label", row["label"])
        features.setdefault("max_users", int(row["max_users"] or 2))
        features.setdefault("max_sku", int(row["max_sku"] or 500))
        return features
    return TARIFFS["starter"]

def tariff_exists(code: str) -> bool:
    normalized = (code or "").strip()
    if normalized in TARIFFS:
        return True
    conn = db()
    row = conn.execute("SELECT id FROM tariff_presets WHERE code = ? AND is_active = 1", (normalized,)).fetchone()
    conn.close()
    return bool(row)


def enrich_org(row, current_role: Optional[str] = None):
    item = dict(row)
    item["features"] = get_tariff_features(item.get("tariff_code") or "starter")
    item["tariff_label"] = (item.get("custom_tariff_label") or "").strip() or item["features"].get("label") or item.get("tariff_code") or "—"
    paid_until = (item.get("paid_until") or "").strip()
    days_left = item.get("billing_days_left")
    if days_left is None and paid_until:
        try:
            days_left = (datetime.fromisoformat(paid_until).date() - now_utc().date()).days
        except Exception:
            days_left = None
    item["billing_days_left"] = days_left
    if item.get("billing_status") == "active" and isinstance(days_left, int):
        if days_left < 0:
            item["billing_notice"] = "Тариф закончился"
        elif days_left == 0:
            item["billing_notice"] = "Тариф закончится сегодня"
        elif days_left <= 3:
            item["billing_notice"] = f"До конца тарифа {days_left} дн."
        elif days_left <= 7:
            item["billing_notice"] = f"Тариф скоро закончится: {days_left} дн."
        else:
            item["billing_notice"] = ""
    elif item.get("billing_status") == "blocked" and paid_until:
        item["billing_notice"] = f"Доступ закончился {paid_until}"
    else:
        item["billing_notice"] = ""
    if current_role:
        item["current_role"] = current_role
        item["permissions"] = get_role_permissions(current_role)
    return item


def check_billing_and_feature(org_row, feature_name: Optional[str] = None):
    if org_row["billing_status"] != "active":
        raise HTTPException(status_code=402, detail="Payment required")
    if feature_name:
        features = get_tariff_features(org_row["tariff_code"])
        if not features.get(feature_name, False):
            raise HTTPException(status_code=403, detail=f"Feature '{feature_name}' not available on current tariff")


def log_action(conn, organization_id: int, actor_user_id: Optional[int], action: str, entity_type: str, entity_id: str = "", details: Optional[dict] = None):
    conn.execute(
        "INSERT INTO audit_logs(organization_id, actor_user_id, action, entity_type, entity_id, details_json, created_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (organization_id, actor_user_id, action, entity_type, entity_id, json.dumps(details or {}, ensure_ascii=False), iso_now()),
    )


def compare_products(existing_rows, incoming_items):
    existing = {str(row["sku"]).strip().lower(): dict(row) for row in existing_rows}
    incoming = {item.sku.strip().lower(): item for item in incoming_items}
    added = 0
    updated = 0
    removed = 0
    changed_fields = {}
    field_map = {
        "account": "account",
        "name": "name",
        "channel": "channel",
        "warehouse": "warehouse",
        "price": "price",
        "unit_cost": "unit_cost",
        "stock": "stock",
        "reserved": "reserved",
        "inbound": "inbound",
        "lead_time_days": "lead_time_days",
        "avg_daily_sales": "avg_daily_sales",
        "trend": "trend",
        "commission_rate": "commission_rate",
        "logistics_per_unit": "logistics_per_unit",
        "ad_spend": "ad_spend",
        "return_rate": "return_rate",
    }
    for sku, item in incoming.items():
        row = existing.get(sku)
        if not row:
            added += 1
            continue
        item_changed = []
        for item_field, row_field in field_map.items():
            old = row[row_field]
            new = getattr(item, item_field)
            if isinstance(old, float) or isinstance(new, float):
                if abs(float(old) - float(new)) > 1e-9:
                    item_changed.append(item_field)
            elif str(old) != str(new):
                item_changed.append(item_field)
        if item_changed:
            updated += 1
            changed_fields[item.sku] = item_changed
    for sku in existing:
        if sku not in incoming:
            removed += 1
    top_changes = {}
    for fields in changed_fields.values():
        for field in fields:
            top_changes[field] = top_changes.get(field, 0) + 1
    return {
        "added_count": added,
        "updated_count": updated,
        "removed_count": removed,
        "changed_fields": top_changes,
        "changed_sku_count": len(changed_fields),
    }


def enrich_audit_row(row):
    item = dict(row)
    try:
        item["details"] = json.loads(item.get("details_json") or "{}")
    except Exception:
        item["details"] = {}
    return item


def product_metrics(row):
    usable_stock = max(0, row["stock"] - row["reserved"])
    adjusted_daily_sales = max(0.1, row["avg_daily_sales"] * (1 + row["trend"]))
    days_of_cover = usable_stock / adjusted_daily_sales
    reorder_qty = max(0, round(adjusted_daily_sales * (row["lead_time_days"] + 7) + adjusted_daily_sales * max(4, round(row["lead_time_days"] * 0.35)) - usable_stock - row["inbound"]))
    stockout_risk = "high" if days_of_cover < row["lead_time_days"] else "medium" if days_of_cover < row["lead_time_days"] + 5 else "low"
    commission_per_unit = row["price"] * row["commission_rate"]
    fees_per_unit = commission_per_unit + row["logistics_per_unit"]
    ad_spend_per_unit = row["ad_spend"] / max(1, adjusted_daily_sales * 30)
    return_loss_per_unit = row["price"] * row["return_rate"] * 0.45
    contribution_per_unit = row["price"] - row["unit_cost"] - fees_per_unit - ad_spend_per_unit - return_loss_per_unit
    profit_margin_pct = (contribution_per_unit / row["price"] * 100) if row["price"] else 0.0
    forecast_revenue_30d = row["price"] * adjusted_daily_sales * 30
    forecast_profit_30d = contribution_per_unit * adjusted_daily_sales * 30
    roas = forecast_revenue_30d / row["ad_spend"] if row["ad_spend"] > 0 else None
    acos_pct = (row["ad_spend"] / forecast_revenue_30d * 100) if forecast_revenue_30d > 0 and row["ad_spend"] > 0 else None
    break_even_price = row["unit_cost"] + fees_per_unit + ad_spend_per_unit + return_loss_per_unit
    recommended_price = max(break_even_price * 1.18, row["price"])
    expected_stockout_date = (now_utc() + timedelta(days=days_of_cover)).date().isoformat()
    return {
        "days_of_cover": days_of_cover,
        "reorder_qty": reorder_qty,
        "stockout_risk": stockout_risk,
        "contribution_per_unit": contribution_per_unit,
        "adjusted_daily_sales": adjusted_daily_sales,
        "commission_per_unit": commission_per_unit,
        "ad_spend_per_unit": ad_spend_per_unit,
        "return_loss_per_unit": return_loss_per_unit,
        "profit_margin_pct": profit_margin_pct,
        "forecast_revenue_7d": row["price"] * adjusted_daily_sales * 7,
        "forecast_revenue_30d": forecast_revenue_30d,
        "forecast_profit_30d": forecast_profit_30d,
        "roas": roas,
        "acos_pct": acos_pct,
        "break_even_price": break_even_price,
        "recommended_price": recommended_price,
        "expected_stockout_date": expected_stockout_date,
    }


def secret_mask(value: str) -> str:
    value = (value or '').strip()
    if not value:
        return ''
    if len(value) <= 8:
        return '•' * len(value)
    return value[:4] + '•' * max(4, len(value) - 8) + value[-4:]


def _secret_stream(length: int) -> bytes:
    seed = hashlib.sha256(APP_SECRET.encode('utf-8')).digest()
    out = b''
    while len(out) < length:
        seed = hashlib.sha256(seed + APP_SECRET.encode('utf-8')).digest()
        out += seed
    return out[:length]


def encrypt_secret(value: str) -> str:
    raw = (value or '').encode('utf-8')
    if not raw:
        return ''
    stream = _secret_stream(len(raw))
    encrypted = bytes([a ^ b for a, b in zip(raw, stream)])
    return base64.urlsafe_b64encode(encrypted).decode('ascii')


def decrypt_secret(value: str) -> str:
    if not value:
        return ''
    raw = base64.urlsafe_b64decode(value.encode('ascii'))
    stream = _secret_stream(len(raw))
    decrypted = bytes([a ^ b for a, b in zip(raw, stream)])
    return decrypted.decode('utf-8')


def get_connection_notice(item: dict) -> str:
    if (item.get('marketplace') or '').lower() == 'wb' and item.get('token_expires_at'):
        try:
            days_left = (datetime.fromisoformat(item['token_expires_at']).date() - now_utc().date()).days
            if days_left < 0:
                return 'Срок действия WB-токена уже истёк. Обновите токен в кабинете WB.'
            if days_left <= WB_TOKEN_WARNING_DAYS:
                return f'До окончания WB-токена осталось {days_left} дн. Обновите его заранее, общий срок жизни токена — 180 дней.'
        except Exception:
            return ''
    return ''


def normalize_connection_row(row):
    item = dict(row)
    item['masked_api_key'] = secret_mask(decrypt_secret(item.get('api_key_encrypted') or '')) if item.get('api_key_encrypted') else ''
    item['auto_sync_enabled'] = bool(item.get('auto_sync_enabled'))
    item['sync_notice'] = get_connection_notice(item)
    return item


def connection_headers(marketplace: str, conn_row: sqlite3.Row):
    api_key = decrypt_secret(conn_row['api_key_encrypted'])
    if marketplace == 'ozon':
        return {
            'Client-Id': (conn_row['client_id'] or '').strip(),
            'Api-Key': api_key,
            'Content-Type': 'application/json',
        }
    return {
        'Authorization': api_key,
        'Content-Type': 'application/json',
    }


def fetch_ozon_products(conn_row: sqlite3.Row):
    headers = connection_headers('ozon', conn_row)
    list_resp = requests.post(
        'https://api-seller.ozon.ru/v3/product/list',
        headers=headers,
        json={'filter': {'visibility': 'ALL'}, 'last_id': '', 'limit': 1000},
        timeout=25,
    )
    list_resp.raise_for_status()
    list_data = list_resp.json() or {}
    items = ((list_data.get('result') or {}).get('items') or [])
    product_ids = [int(item.get('product_id')) for item in items if item.get('product_id')]
    offer_map = {int(item.get('product_id')): item.get('offer_id') or '' for item in items if item.get('product_id')}
    details = []
    if product_ids:
        info_resp = requests.post(
            'https://api-seller.ozon.ru/v2/product/info/list',
            headers=headers,
            json={'product_id': product_ids},
            timeout=25,
        )
        info_resp.raise_for_status()
        info_data = info_resp.json() or {}
        details = (info_data.get('result') or {}).get('items') or info_data.get('items') or []
    out = []
    if details:
        for item in details:
            pid = item.get('id') or item.get('product_id')
            sku = str(item.get('offer_id') or offer_map.get(int(pid or 0)) or pid or '').strip()
            if not sku:
                continue
            name = item.get('name') or item.get('offer_id') or sku
            price_raw = item.get('price') or item.get('price_index') or '0'
            try:
                price = float(str(price_raw).replace(',', '.'))
            except Exception:
                price = 0.0
            out.append({
                'sku': sku,
                'external_product_id': str(pid or ''),
                'account': 'Ozon',
                'name': name,
                'channel': 'Ozon',
                'warehouse': 'Ozon',
                'price': price,
            })
    else:
        for item in items:
            pid = item.get('product_id')
            sku = str(item.get('offer_id') or pid or '').strip()
            if not sku:
                continue
            out.append({
                'sku': sku,
                'external_product_id': str(pid or ''),
                'account': 'Ozon',
                'name': item.get('offer_id') or sku,
                'channel': 'Ozon',
                'warehouse': 'Ozon',
                'price': 0.0,
            })
    return out


def fetch_wb_products(conn_row: sqlite3.Row):
    headers = connection_headers('wb', conn_row)
    payload = {'settings': {'cursor': {'limit': 100}, 'filter': {'withPhoto': -1}}}
    resp = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    data = resp.json() or {}
    cards = data.get('cards') or data.get('result') or []
    out = []
    for card in cards:
        nm_id = card.get('nmID') or card.get('nmId') or card.get('imtID') or card.get('imtId')
        vendor = str(card.get('vendorCode') or nm_id or '').strip()
        if not vendor:
            continue
        title = card.get('title') or card.get('subjectName') or vendor
        out.append({
            'sku': vendor,
            'external_product_id': str(nm_id or ''),
            'account': 'WB',
            'name': title,
            'channel': 'WB',
            'warehouse': 'WB',
            'price': 0.0,
        })
    return out


def upsert_marketplace_products(conn, organization_id: int, marketplace: str, products: list[dict]):
    added = 0
    updated = 0
    sync_time = iso_now()
    for item in products:
        existing = conn.execute(
            'SELECT * FROM products WHERE organization_id = ? AND lower(sku) = ?',
            (organization_id, (item['sku'] or '').strip().lower())
        ).fetchone()
        price = float(item.get('price') or (existing['price'] if existing else 0) or 0)
        unit_cost = float(existing['unit_cost'] if existing else 0)
        stock = float(existing['stock'] if existing else 0)
        reserved = float(existing['reserved'] if existing else 0)
        inbound = float(existing['inbound'] if existing else 0)
        lead_time_days = float(existing['lead_time_days'] if existing else 14)
        avg_daily_sales = float(existing['avg_daily_sales'] if existing else 1)
        trend = float(existing['trend'] if existing else 0)
        commission_rate = float(existing['commission_rate'] if existing else 0.15)
        logistics_per_unit = float(existing['logistics_per_unit'] if existing else 0)
        ad_spend = float(existing['ad_spend'] if existing else 0)
        return_rate = float(existing['return_rate'] if existing else 0.02)
        if existing:
            conn.execute(
                'UPDATE products SET account=?, name=?, channel=?, warehouse=?, price=?, source_marketplace=?, external_product_id=?, last_sync_at=? WHERE id=?',
                (item['account'], item['name'], item['channel'], item['warehouse'], price, marketplace, item.get('external_product_id') or '', sync_time, int(existing['id']))
            )
            updated += 1
        else:
            conn.execute(
                'INSERT INTO products(organization_id, sku, account, name, channel, warehouse, price, unit_cost, stock, reserved, inbound, lead_time_days, avg_daily_sales, trend, commission_rate, logistics_per_unit, ad_spend, return_rate, source_marketplace, external_product_id, last_sync_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (organization_id, item['sku'], item['account'], item['name'], item['channel'], item['warehouse'], price, unit_cost, stock, reserved, inbound, lead_time_days, avg_daily_sales, trend, commission_rate, logistics_per_unit, ad_spend, return_rate, marketplace, item.get('external_product_id') or '', sync_time)
            )
            added += 1
    return added, updated, 0


def run_marketplace_sync(organization_id: int, marketplace: str, actor_user_id: Optional[int] = None, reason: str = 'manual'):
    marketplace = (marketplace or '').strip().lower()
    if marketplace not in {'wb', 'ozon'}:
        raise HTTPException(status_code=400, detail='Поддерживаются только WB и Ozon')
    conn = db()
    row = conn.execute('SELECT * FROM marketplace_connections WHERE organization_id = ? AND marketplace = ?', (organization_id, marketplace)).fetchone()
    if not row or row['status'] != 'connected':
        conn.close()
        raise HTTPException(status_code=400, detail='Сначала подключите кабинет маркетплейса')
    started_at = iso_now()
    log_id = conn.execute('INSERT INTO marketplace_sync_logs(organization_id, marketplace, status, started_at, message) VALUES(?,?,?,?,?)', (organization_id, marketplace, 'running', started_at, f'{reason} sync started')).lastrowid
    try:
        products = fetch_wb_products(row) if marketplace == 'wb' else fetch_ozon_products(row)
        added, updated, removed = upsert_marketplace_products(conn, organization_id, marketplace, products)
        finished_at = iso_now()
        conn.execute('UPDATE marketplace_connections SET last_sync_at=?, last_success_at=?, last_error=?, updated_at=? WHERE id=?', (finished_at, finished_at, '', finished_at, int(row['id'])))
        conn.execute('UPDATE marketplace_sync_logs SET status=?, finished_at=?, added_count=?, updated_count=?, removed_count=?, message=? WHERE id=?', ('success', finished_at, added, updated, removed, f'Синхронизировано товаров: {len(products)}', log_id))
        log_action(conn, organization_id, actor_user_id, f'Синхронизация {marketplace.upper()} выполнена', 'marketplace_sync', str(log_id), {'marketplace': marketplace, 'added_count': added, 'updated_count': updated, 'reason': reason})
        conn.commit()
        result = {'marketplace': marketplace, 'status': 'success', 'added_count': added, 'updated_count': updated, 'removed_count': removed, 'fetched_count': len(products), 'finished_at': finished_at}
        conn.close()
        return result
    except requests.HTTPError as exc:
        body = exc.response.text[:600] if exc.response is not None else str(exc)
        finished_at = iso_now()
        conn.execute('UPDATE marketplace_connections SET last_sync_at=?, last_error=?, updated_at=? WHERE id=?', (finished_at, body, finished_at, int(row['id'])))
        conn.execute('UPDATE marketplace_sync_logs SET status=?, finished_at=?, message=? WHERE id=?', ('error', finished_at, body, log_id))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail=f'Ошибка ответа {marketplace.upper()} API: {body}')
    except Exception as exc:
        finished_at = iso_now()
        conn.execute('UPDATE marketplace_connections SET last_sync_at=?, last_error=?, updated_at=? WHERE id=?', (finished_at, str(exc), finished_at, int(row['id'])))
        conn.execute('UPDATE marketplace_sync_logs SET status=?, finished_at=?, message=? WHERE id=?', ('error', finished_at, str(exc), log_id))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=500, detail=f'Синхронизация {marketplace.upper()} не удалась: {exc}')


def maybe_run_auto_sync(organization_id: int):
    conn = db()
    rows = conn.execute('SELECT * FROM marketplace_connections WHERE organization_id = ? AND status = ? AND auto_sync_enabled = 1', (organization_id, 'connected')).fetchall()
    conn.close()
    for row in rows:
        last_success_at = (row['last_success_at'] or '').strip()
        interval = max(1, int(row['sync_interval_minutes'] or DEFAULT_SYNC_INTERVAL_MINUTES))
        due = True
        if last_success_at:
            try:
                due = datetime.fromisoformat(last_success_at) <= (now_utc() - timedelta(minutes=interval))
            except Exception:
                due = True
        if due:
            try:
                run_marketplace_sync(organization_id, row['marketplace'], actor_user_id=None, reason='auto')
            except Exception:
                pass



class MarketplaceConnectIn(BaseModel):
    client_id: str = ''
    api_key: str
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = DEFAULT_SYNC_INTERVAL_MINUTES


class RegisterIn(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str


class OrganizationIn(BaseModel):
    name: str
    tariff: str = "none"
    marketplace: str = "Ozon"
    tariff_code: Optional[str] = None


class OrgUpdateIn(BaseModel):
    name: str
    tariff: str = "starter"
    marketplace: str = "Ozon"
    tariff_code: Optional[str] = None


class BillingSelectIn(BaseModel):
    tariff_code: str


class PaymentConfirmIn(BaseModel):
    paid: bool = True


class ManualPaymentIn(BaseModel):
    tariff_code: str
    amount: float = 0
    period_days: int = 30
    payer_name: str = ""
    payment_channel: str = ""
    note: str = ""


class InviteIn(BaseModel):
    email: EmailStr
    role: str


class InviteAcceptIn(BaseModel):
    token: str


class InviteRegisterIn(BaseModel):
    token: str
    full_name: str
    email: EmailStr
    password: str


class ProductIn(BaseModel):
    sku: str
    account: str
    name: str
    channel: str
    warehouse: str
    price: float
    unit_cost: float
    stock: float
    reserved: float
    inbound: float
    lead_time_days: float
    avg_daily_sales: float
    trend: float
    commission_rate: float
    logistics_per_unit: float
    ad_spend: float
    return_rate: float


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"service": "shtab-backend", "status": "ok"}


@app.get("/api/v1/tariffs")
def list_tariffs():
    out = []
    for code, features in TARIFFS.items():
        if code == 'none':
            continue
        out.append({
            "code": code,
            "label": features["label"],
            "features": features,
            "price_month": 4900 if code == "starter" else 14900 if code == "growth" else 49900,
            "kind": "builtin",
        })
    conn = db()
    rows = conn.execute("SELECT * FROM tariff_presets WHERE is_active = 1 ORDER BY id ASC").fetchall()
    conn.close()
    builtin_codes = {item["code"] for item in out}
    for row in rows:
        if row["code"] in builtin_codes:
            continue
        try:
            features = json.loads(row["features_json"] or "{}")
        except Exception:
            features = {}
        features.setdefault("label", row["label"])
        features.setdefault("max_users", int(row["max_users"] or 2))
        features.setdefault("max_sku", int(row["max_sku"] or 500))
        out.append({
            "code": row["code"],
            "label": row["label"],
            "features": features,
            "price_month": float(row["price_month"] or 0),
            "kind": "custom",
        })
    return out



def _parse_iso_datetime(value: str) -> datetime:
    cleaned = (value or '').strip()
    if not cleaned:
        return now_utc()
    if cleaned.endswith('Z'):
        cleaned = cleaned[:-1] + '+00:00'
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return now_utc()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def purge_expired_reset_tokens(conn: sqlite3.Connection) -> None:
    now_iso = iso_now()
    conn.execute("DELETE FROM password_reset_tokens WHERE used = 1 OR expires_at <= ?", (now_iso,))


def build_password_reset_link(token: str) -> str:
    return f"{FRONTEND_ORIGIN}/reset-password.html?token={token}"


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is not configured")
    payload = {
        "from": RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Сброс пароля в ШТАБ",
        "html": f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#0f172a">
          <h2 style="margin:0 0 12px">Сброс пароля</h2>
          <p>Нажмите на кнопку ниже, чтобы задать новый пароль для аккаунта ШТАБ.</p>
          <p style="margin:20px 0">
            <a href="{reset_link}" style="display:inline-block;padding:12px 18px;background:#60a5fa;color:#ffffff;text-decoration:none;border-radius:10px">Сбросить пароль</a>
          </p>
          <p>Если кнопка не открывается, используйте ссылку:</p>
          <p><a href="{reset_link}">{reset_link}</a></p>
          <p style="color:#64748b">Ссылка действует {PASSWORD_RESET_TTL_MINUTES} минут и становится недействительной после смены пароля.</p>
        </div>
        """.strip(),
    }
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Resend error {response.status_code}: {response.text}")


@app.post("/api/v1/auth/forgot-password")
def forgot_password(payload: ForgotPasswordIn):
    normalized_email = payload.email.lower().strip()
    conn = db()
    purge_expired_reset_tokens(conn)
    user = conn.execute("SELECT id, email FROM users WHERE lower(email) = ?", (normalized_email,)).fetchone()
    if not user:
        conn.commit()
        conn.close()
        return {"ok": True, "message": "Если аккаунт существует, письмо уже отправлено."}

    token = secrets.token_urlsafe(32)
    now_iso = iso_now()
    expires_at = (now_utc() + timedelta(minutes=PASSWORD_RESET_TTL_MINUTES)).replace(microsecond=0).isoformat()
    conn.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (int(user["id"]),))
    conn.execute(
        "INSERT INTO password_reset_tokens(user_id, token, expires_at, used, created_at, used_at) VALUES(?, ?, ?, 0, ?, '')",
        (int(user["id"]), token, expires_at, now_iso),
    )
    conn.commit()
    conn.close()

    reset_link = build_password_reset_link(token)
    send_password_reset_email(user["email"], reset_link)
    return {"ok": True, "message": "Письмо со ссылкой для сброса пароля отправлено."}


@app.get("/api/v1/auth/reset-password/validate")
def validate_reset_password(token: str = Query(...)):
    conn = db()
    purge_expired_reset_tokens(conn)
    row = conn.execute("SELECT * FROM password_reset_tokens WHERE token = ?", (token.strip(),)).fetchone()
    conn.commit()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Ссылка недействительна или устарела")
    if int(row["used"] or 0):
        raise HTTPException(status_code=400, detail="Ссылка уже использована")
    if _parse_iso_datetime(row["expires_at"]) <= now_utc():
        raise HTTPException(status_code=400, detail="Срок действия ссылки истёк")
    return {"ok": True}


@app.post("/api/v1/auth/reset-password")
def reset_password(payload: ResetPasswordIn):
    token = payload.token.strip()
    new_password = payload.new_password or ''
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 8 символов")

    conn = db()
    purge_expired_reset_tokens(conn)
    row = conn.execute("SELECT * FROM password_reset_tokens WHERE token = ?", (token,)).fetchone()
    if not row:
        conn.commit()
        conn.close()
        raise HTTPException(status_code=404, detail="Ссылка недействительна или устарела")
    if int(row["used"] or 0):
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Ссылка уже использована")
    if _parse_iso_datetime(row["expires_at"]) <= now_utc():
        conn.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Срок действия ссылки истёк")

    user_id = int(row["user_id"])
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))
    conn.execute("UPDATE password_reset_tokens SET used = 1, used_at = ? WHERE token = ?", (iso_now(), token))
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"ok": True, "message": "Пароль обновлён"}


@app.post("/api/v1/auth/register")
def register(payload: RegisterIn):
    conn = db()
    exists = conn.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    if exists:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")
    cur = conn.execute(
        "INSERT INTO users(full_name, email, password_hash, created_at) VALUES(?, ?, ?, ?)",
        (payload.full_name.strip(), payload.email.lower(), hash_password(payload.password), iso_now())
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    token = create_session(user_id)
    return {"user": {"id": user_id, "full_name": payload.full_name.strip(), "email": payload.email.lower(), "is_super_admin": is_super_admin_email(payload.email.lower())}, "access_token": token}


@app.post("/api/v1/auth/register-by-invite")
def register_by_invite(payload: InviteRegisterIn):
    conn = db()
    invite = conn.execute(
        "SELECT * FROM invites WHERE token = ? AND status = ?",
        (payload.token, "Приглашение отправлено")
    ).fetchone()
    if not invite:
        conn.close()
        raise HTTPException(status_code=404, detail="Invite not found or already used")

    normalized_email = payload.email.lower().strip()
    if invite["email"].lower() != normalized_email:
        conn.close()
        raise HTTPException(status_code=403, detail="Invite email does not match the registration email")

    exists = conn.execute("SELECT id FROM users WHERE email = ?", (normalized_email,)).fetchone()
    if exists:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists. Войдите в аккаунт и примите приглашение.")

    org = conn.execute("SELECT * FROM organizations WHERE id = ?", (invite["organization_id"],)).fetchone()
    member_count = conn.execute("SELECT COUNT(*) AS c FROM memberships WHERE organization_id = ?", (invite["organization_id"],)).fetchone()["c"]
    if member_count >= int(org["max_users"] or 0):
        conn.close()
        raise HTTPException(status_code=403, detail="User limit reached for current tariff")

    cur = conn.execute(
        "INSERT INTO users(full_name, email, password_hash, created_at) VALUES(?, ?, ?, ?)",
        (payload.full_name.strip(), normalized_email, hash_password(payload.password), iso_now())
    )
    user_id = cur.lastrowid
    conn.execute(
        "INSERT INTO memberships(organization_id, user_id, role, status) VALUES(?, ?, ?, ?)",
        (invite["organization_id"], int(user_id), invite["role"], "Активен")
    )
    conn.execute(
        "UPDATE invites SET status = ?, accepted_at = ? WHERE id = ?",
        ("Принято", iso_now(), invite["id"])
    )
    log_action(conn, int(invite["organization_id"]), int(user_id), "Аккаунт создан по приглашению", "invite", invite["token"], {"email": normalized_email, "role": invite["role"]})
    conn.commit()
    conn.close()
    token = create_session(user_id)
    return {"user": {"id": user_id, "full_name": payload.full_name.strip(), "email": normalized_email, "is_super_admin": is_super_admin_email(normalized_email)}, "access_token": token, "organization_id": int(invite["organization_id"]), "role": invite["role"]}


@app.post("/api/v1/auth/login")
def login(payload: LoginIn):
    conn = db()
    purge_expired_sessions(conn)
    row = conn.execute("SELECT * FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    conn.commit()
    conn.close()
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session(int(row["id"]))
    return {"user": {"id": int(row["id"]), "full_name": row["full_name"], "email": row["email"], "is_super_admin": is_super_admin_email(row['email'])}, "access_token": token}


@app.post("/api/v1/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    conn = db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/v1/me")
def me(authorization: Optional[str] = Header(default=None)):
    user = get_user(authorization)
    item = dict(user)
    item['is_super_admin'] = is_super_admin_email(item.get('email'))
    return item


@app.post("/api/v1/organizations")
def create_org(payload: OrganizationIn, authorization: Optional[str] = Header(default=None)):
    user = get_user(authorization)
    tariff_code = payload.tariff_code or 'none'
    features = get_tariff_features(tariff_code)
    conn = db()
    cur = conn.execute(
        "INSERT INTO organizations(name, tariff, marketplace, owner_user_id, tariff_code, billing_status, paid_until, max_users, max_sku) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (payload.name.strip(), tariff_code, payload.marketplace, int(user["id"]), tariff_code, "pending_payment", "", features["max_users"], features["max_sku"])
    )
    org_id = cur.lastrowid
    conn.execute("INSERT INTO memberships(organization_id, user_id, role, status) VALUES(?, ?, ?, ?)", (org_id, int(user["id"]), "Руководитель", "Активен"))
    log_action(conn, org_id, int(user["id"]), "Организация создана", "organization", str(org_id), {"name": payload.name.strip(), "tariff_code": tariff_code, "marketplace": payload.marketplace})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    conn.close()
    return enrich_org(row, "Руководитель")


@app.get("/api/v1/organizations")
def list_orgs(authorization: Optional[str] = Header(default=None)):
    user = get_user(authorization)
    conn = db()
    rows = conn.execute(
        "SELECT o.*, m.role AS current_role FROM organizations o JOIN memberships m ON m.organization_id = o.id WHERE m.user_id = ? ORDER BY o.id DESC",
        (int(user["id"]),)
    ).fetchall()
    rows = [sync_org_billing_state(conn, r) for r in rows]
    conn.commit()
    conn.close()
    return [enrich_org(r, r["current_role"]) for r in rows]


@app.put("/api/v1/organizations/{org_id}")
def update_org(org_id: int, payload: OrgUpdateIn, authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = ensure_org_permission(user_id, org_id, "manage_org")
    current = get_org(org_id)
    conn = db()
    conn.execute(
        "UPDATE organizations SET name = ?, marketplace = ?, tariff = ?, tariff_code = ?, max_users = ?, max_sku = ? WHERE id = ?",
        (
            payload.name.strip(),
            payload.marketplace,
            current["tariff"],
            current["tariff_code"],
            current["max_users"],
            current["max_sku"],
            org_id,
        )
    )
    log_action(conn, org_id, user_id, "Настройки организации обновлены", "organization", str(org_id), {"name": payload.name.strip(), "marketplace": payload.marketplace})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    conn.close()
    return enrich_org(row, membership["role"])


@app.post("/api/v1/billing/select")
def billing_select(payload: BillingSelectIn, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = ensure_org_permission(user_id, organization_id, "manage_billing")
    if not tariff_exists(payload.tariff_code):
        raise HTTPException(status_code=400, detail="Unknown tariff")
    features = get_tariff_features(payload.tariff_code)
    conn = db()
    conn.execute(
        "UPDATE organizations SET tariff_code = ?, tariff = ?, billing_status = ?, max_users = ?, max_sku = ? WHERE id = ?",
        (payload.tariff_code, payload.tariff_code, "pending_payment", features["max_users"], features["max_sku"], organization_id)
    )
    log_action(conn, organization_id, user_id, "Тариф выбран", "billing", str(organization_id), {"tariff_code": payload.tariff_code})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,)).fetchone()
    conn.close()
    return enrich_org(row, membership["role"])


@app.post("/api/v1/billing/confirm")
def billing_confirm(payload: PaymentConfirmIn, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = ensure_org_permission(user_id, organization_id, "manage_billing")
    status = "active" if payload.paid else "blocked"
    paid_until = (now_utc() + timedelta(days=30)).date().isoformat() if payload.paid else ""
    conn = db()
    conn.execute("UPDATE organizations SET billing_status = ?, paid_until = ? WHERE id = ?", (status, paid_until, organization_id))
    log_action(conn, organization_id, user_id, "Статус оплаты обновлён", "billing", str(organization_id), {"billing_status": status, "paid_until": paid_until})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,)).fetchone()
    conn.close()
    return enrich_org(row, membership["role"])




@app.post("/api/v1/billing/manual-payment")
def billing_manual_payment(payload: ManualPaymentIn, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = ensure_org_permission(user_id, organization_id, "manage_billing")
    if not tariff_exists(payload.tariff_code):
        raise HTTPException(status_code=400, detail="Unknown tariff")
    period_days = max(1, min(int(payload.period_days or 30), 366))
    amount = float(payload.amount or 0)
    features = get_tariff_features(payload.tariff_code)
    paid_until = (now_utc() + timedelta(days=period_days)).date().isoformat()
    created_at = iso_now()
    conn = db()
    conn.execute(
        "UPDATE organizations SET tariff_code = ?, tariff = ?, billing_status = ?, paid_until = ?, max_users = ?, max_sku = ? WHERE id = ?",
        (payload.tariff_code, payload.tariff_code, "active", paid_until, features["max_users"], features["max_sku"], organization_id)
    )
    cur = conn.execute(
        "INSERT INTO manual_payments(organization_id, actor_user_id, tariff_code, amount, period_days, payer_name, payment_channel, note, status, created_at, paid_until) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (organization_id, user_id, payload.tariff_code, amount, period_days, (payload.payer_name or "").strip(), (payload.payment_channel or "").strip(), (payload.note or "").strip(), "confirmed", created_at, paid_until)
    )
    log_action(conn, organization_id, user_id, "Ручная оплата подтверждена", "billing", str(cur.lastrowid), {"tariff_code": payload.tariff_code, "amount": amount, "period_days": period_days, "payer_name": (payload.payer_name or "").strip(), "payment_channel": (payload.payment_channel or "").strip(), "paid_until": paid_until, "note": (payload.note or "").strip()})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,)).fetchone()
    conn.close()
    return enrich_org(row, membership["role"])


@app.get("/api/v1/billing/manual-payments")
def list_manual_payments(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None), limit: int = Query(default=20, ge=1, le=100)):
    user_id = get_user_id_from_token(authorization)
    get_membership(user_id, organization_id)
    ensure_org_permission(user_id, organization_id, "manage_billing")
    conn = db()
    rows = conn.execute(
        "SELECT mp.*, u.full_name AS actor_name, u.email AS actor_email FROM manual_payments mp LEFT JOIN users u ON u.id = mp.actor_user_id WHERE mp.organization_id = ? ORDER BY mp.created_at DESC LIMIT ?",
        (organization_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/v1/admin/organizations-legacy")
def admin_list_organizations_legacy(authorization: Optional[str] = Header(default=None), limit: int = Query(default=200, ge=1, le=500)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute(
        "SELECT o.*, u.full_name AS owner_name, u.email AS owner_email FROM organizations o LEFT JOIN users u ON u.id = o.owner_user_id ORDER BY o.id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    rows = [sync_org_billing_state(conn, r) for r in rows]
    conn.commit()
    conn.close()
    return [{**enrich_org(r), 'owner_name': r['owner_name'], 'owner_email': r['owner_email'], 'is_super_admin': True} for r in rows]


@app.post("/api/v1/admin/organizations/{org_id}/manual-payment-legacy")
def admin_manual_payment_legacy(org_id: int, payload: ManualPaymentIn, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    if not tariff_exists(payload.tariff_code) or payload.tariff_code == 'none':
        raise HTTPException(status_code=400, detail='Unknown tariff')
    period_days = max(1, min(int(payload.period_days or 30), 366))
    amount = float(payload.amount or 0)
    features = get_tariff_features(payload.tariff_code)
    paid_until = (now_utc() + timedelta(days=period_days)).date().isoformat()
    created_at = iso_now()
    conn = db()
    org = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    if not org:
        conn.close()
        raise HTTPException(status_code=404, detail='Organization not found')
    conn.execute(
        "UPDATE organizations SET tariff_code = ?, tariff = ?, billing_status = ?, paid_until = ?, max_users = ?, max_sku = ? WHERE id = ?",
        (payload.tariff_code, payload.tariff_code, 'active', paid_until, features['max_users'], features['max_sku'], org_id)
    )
    cur = conn.execute(
        "INSERT INTO manual_payments(organization_id, actor_user_id, tariff_code, amount, period_days, payer_name, payment_channel, note, status, created_at, paid_until) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (org_id, int(admin_user['id']), payload.tariff_code, amount, period_days, (payload.payer_name or '').strip(), (payload.payment_channel or '').strip(), (payload.note or '').strip(), 'confirmed', created_at, paid_until)
    )
    log_action(conn, org_id, int(admin_user['id']), 'Тариф выдан главным администратором', 'billing', str(cur.lastrowid), {'tariff_code': payload.tariff_code, 'amount': amount, 'period_days': period_days, 'payer_name': (payload.payer_name or '').strip(), 'payment_channel': (payload.payment_channel or '').strip(), 'paid_until': paid_until, 'note': (payload.note or '').strip()})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    conn.close()
    return enrich_org(row)


@app.get("/api/v1/admin/manual-payments")
def admin_list_manual_payments(authorization: Optional[str] = Header(default=None), limit: int = Query(default=100, ge=1, le=500)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute(
        "SELECT mp.*, o.name AS organization_name, u.full_name AS actor_name, u.email AS actor_email FROM manual_payments mp LEFT JOIN organizations o ON o.id = mp.organization_id LEFT JOIN users u ON u.id = mp.actor_user_id ORDER BY mp.created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/v1/admin/organizations/{org_id}/block-legacy")
def admin_block_org_legacy(org_id: int, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail='Organization not found')
    conn.execute("UPDATE organizations SET billing_status = ?, paid_until = ? WHERE id = ?", ('blocked', '', org_id))
    log_action(conn, org_id, int(admin_user['id']), 'Доступ заблокирован главным администратором', 'billing', str(org_id), {})
    conn.commit()
    row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    conn.close()
    return enrich_org(row)


@app.get('/api/v1/integrations')
def list_integrations(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    get_membership(user_id, organization_id)
    conn = db()
    rows = conn.execute('SELECT * FROM marketplace_connections WHERE organization_id = ? ORDER BY marketplace ASC', (organization_id,)).fetchall()
    logs = conn.execute('SELECT * FROM marketplace_sync_logs WHERE organization_id = ? ORDER BY id DESC LIMIT 12', (organization_id,)).fetchall()
    conn.close()
    items = {row['marketplace']: normalize_connection_row(row) for row in rows}
    result = []
    for marketplace in ['wb', 'ozon']:
        if marketplace in items:
            result.append(items[marketplace])
        else:
            result.append({
                'organization_id': organization_id,
                'marketplace': marketplace,
                'status': 'disconnected',
                'client_id': '',
                'masked_api_key': '',
                'token_created_at': '',
                'token_expires_at': '',
                'auto_sync_enabled': True,
                'sync_interval_minutes': DEFAULT_SYNC_INTERVAL_MINUTES,
                'last_sync_at': '',
                'last_success_at': '',
                'last_error': '',
                'sync_notice': '',
            })
    return {'connections': result, 'logs': [dict(r) for r in logs], 'csv_fallback_enabled': True}


@app.post('/api/v1/integrations/{marketplace}/connect')
def connect_integration(marketplace: str, payload: MarketplaceConnectIn, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    ensure_org_permission(user_id, organization_id, 'manage_org')
    marketplace = (marketplace or '').strip().lower()
    if marketplace not in {'wb', 'ozon'}:
        raise HTTPException(status_code=400, detail='Поддерживаются только WB и Ozon')
    api_key = (payload.api_key or '').strip()
    client_id = (payload.client_id or '').strip()
    if not api_key:
        raise HTTPException(status_code=400, detail='Введите API-ключ или токен')
    if marketplace == 'ozon' and not client_id:
        raise HTTPException(status_code=400, detail='Для Ozon обязателен Client ID')
    now = iso_now()
    token_expires_at = ''
    token_created_at = now
    if marketplace == 'wb':
        token_expires_at = (now_utc() + timedelta(days=WB_TOKEN_LIFETIME_DAYS)).date().isoformat()
    conn = db()
    existing = conn.execute('SELECT id FROM marketplace_connections WHERE organization_id = ? AND marketplace = ?', (organization_id, marketplace)).fetchone()
    values = (organization_id, marketplace, 'connected', client_id, encrypt_secret(api_key), token_created_at, token_expires_at, 1 if payload.auto_sync_enabled else 0, max(1, min(int(payload.sync_interval_minutes or DEFAULT_SYNC_INTERVAL_MINUTES), 720)), '', '', '', now, now)
    if existing:
        conn.execute('UPDATE marketplace_connections SET status=?, client_id=?, api_key_encrypted=?, token_created_at=?, token_expires_at=?, auto_sync_enabled=?, sync_interval_minutes=?, updated_at=? WHERE id=?', ('connected', client_id, encrypt_secret(api_key), token_created_at, token_expires_at, 1 if payload.auto_sync_enabled else 0, max(1, min(int(payload.sync_interval_minutes or DEFAULT_SYNC_INTERVAL_MINUTES), 720)), now, int(existing['id'])))
    else:
        conn.execute('INSERT INTO marketplace_connections(organization_id, marketplace, status, client_id, api_key_encrypted, token_created_at, token_expires_at, auto_sync_enabled, sync_interval_minutes, last_sync_at, last_success_at, last_error, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
    log_action(conn, organization_id, user_id, f'Подключение {marketplace.upper()} обновлено', 'marketplace_connection', marketplace, {'marketplace': marketplace, 'auto_sync_enabled': payload.auto_sync_enabled, 'sync_interval_minutes': payload.sync_interval_minutes})
    conn.commit()
    row = conn.execute('SELECT * FROM marketplace_connections WHERE organization_id = ? AND marketplace = ?', (organization_id, marketplace)).fetchone()
    conn.close()
    return normalize_connection_row(row)


@app.post('/api/v1/integrations/{marketplace}/disconnect')
def disconnect_integration(marketplace: str, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    ensure_org_permission(user_id, organization_id, 'manage_org')
    marketplace = (marketplace or '').strip().lower()
    conn = db()
    conn.execute('DELETE FROM marketplace_connections WHERE organization_id = ? AND marketplace = ?', (organization_id, marketplace))
    log_action(conn, organization_id, user_id, f'Подключение {marketplace.upper()} удалено', 'marketplace_connection', marketplace, {'marketplace': marketplace})
    conn.commit()
    conn.close()
    return {'ok': True}


@app.post('/api/v1/integrations/{marketplace}/sync')
def manual_sync_integration(marketplace: str, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    ensure_org_permission(user_id, organization_id, 'manage_products')
    return run_marketplace_sync(organization_id, marketplace, actor_user_id=user_id, reason='manual')


@app.get('/api/v1/integrations/sync-logs')
def integration_sync_logs(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None), limit: int = Query(default=20, ge=1, le=100)):
    user_id = get_user_id_from_token(authorization)
    get_membership(user_id, organization_id)
    conn = db()
    rows = conn.execute('SELECT * FROM marketplace_sync_logs WHERE organization_id = ? ORDER BY id DESC LIMIT ?', (organization_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]



@app.get("/api/v1/members")
def list_members(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = get_membership(user_id, organization_id)
    permissions = get_role_permissions(membership["role"])
    if not permissions.get("view_team", False):
        raise HTTPException(status_code=403, detail="Просмотр команды недоступен для вашей роли")
    org = get_org(organization_id)
    check_billing_and_feature(org, "team")
    conn = db()
    rows = conn.execute(
        "SELECT u.full_name, u.email, m.role, m.status FROM memberships m JOIN users u ON u.id = m.user_id WHERE m.organization_id = ? ORDER BY m.id ASC",
        (organization_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/v1/invites")
def list_invites(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = get_membership(user_id, organization_id)
    permissions = get_role_permissions(membership["role"])
    if not permissions.get("view_team", False):
        raise HTTPException(status_code=403, detail="Просмотр приглашений недоступен для вашей роли")
    org = get_org(organization_id)
    check_billing_and_feature(org, "team")
    conn = db()
    rows = conn.execute(
        "SELECT email, role, status, token, created_at, accepted_at FROM invites WHERE organization_id = ? AND lower(email) != ? ORDER BY id DESC",
        (organization_id, "finance@company.ru")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/v1/invites")
def create_invite(payload: InviteIn, request: Request, organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    ensure_org_permission(user_id, organization_id, "manage_team")
    org = get_org(organization_id)
    check_billing_and_feature(org, "team")
    if payload.role not in TEAM_ROLES:
        raise HTTPException(status_code=400, detail="Unknown role")

    conn = db()
    member_count = conn.execute("SELECT COUNT(*) AS c FROM memberships WHERE organization_id = ?", (organization_id,)).fetchone()["c"]
    pending_count = conn.execute(
        "SELECT COUNT(*) AS c FROM invites WHERE organization_id = ? AND status = ?",
        (organization_id, "Приглашение отправлено")
    ).fetchone()["c"]
    if member_count + pending_count >= int(org["max_users"] or 0):
        conn.close()
        raise HTTPException(status_code=403, detail="User limit reached for current tariff")

    existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    if existing_user:
        existing_membership = conn.execute(
            "SELECT id FROM memberships WHERE organization_id = ? AND user_id = ?",
            (organization_id, int(existing_user["id"]))
        ).fetchone()
        if existing_membership:
            conn.close()
            raise HTTPException(status_code=400, detail="User is already in the organization")

    active_invite = conn.execute(
        "SELECT id FROM invites WHERE organization_id = ? AND email = ? AND status = ?",
        (organization_id, payload.email.lower(), "Приглашение отправлено")
    ).fetchone()
    if active_invite:
        conn.close()
        raise HTTPException(status_code=400, detail="Active invite already exists for this email")

    token = secrets.token_urlsafe(24)
    conn.execute(
        "INSERT INTO invites(organization_id, email, role, status, token, created_at, accepted_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (organization_id, payload.email.lower(), payload.role, "Приглашение отправлено", token, iso_now(), "")
    )
    frontend_origin = (os.environ.get("FRONTEND_ORIGIN") or "").rstrip("/")
    request_origin = (request.headers.get("origin") or "").rstrip("/")
    referer = request.headers.get("referer") or ""
    if not request_origin and referer:
        parsed_referer = urlparse(referer)
        if parsed_referer.scheme and parsed_referer.netloc:
            request_origin = f"{parsed_referer.scheme}://{parsed_referer.netloc}"
    public_origin = frontend_origin or request_origin or f"{request.base_url.scheme}://{request.base_url.netloc}"
    public_link = f"{public_origin}/invite.html?token={token}" 
    log_action(conn, organization_id, user_id, "Приглашение отправлено", "invite", token, {"email": payload.email.lower(), "role": payload.role, "public_link": public_link})
    conn.commit()
    conn.close()
    return {"ok": True, "token": token, "invite_link": public_link}


@app.get("/api/v1/invites/public")
def get_public_invite(token: str = Query(...)):
    conn = db()
    invite = conn.execute(
        "SELECT i.email, i.role, i.status, i.token, i.created_at, i.accepted_at, o.id AS organization_id, o.name AS organization_name FROM invites i JOIN organizations o ON o.id = i.organization_id WHERE i.token = ?",
        (token,)
    ).fetchone()
    conn.close()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    return dict(invite)


@app.post("/api/v1/invites/accept")
def accept_invite(payload: InviteAcceptIn, authorization: Optional[str] = Header(default=None)):
    user = get_user(authorization)
    conn = db()
    invite = conn.execute(
        "SELECT * FROM invites WHERE token = ? AND status = ?",
        (payload.token, "Приглашение отправлено")
    ).fetchone()
    if not invite:
        conn.close()
        raise HTTPException(status_code=404, detail="Invite not found or already used")
    if invite["email"].lower() != user["email"].lower():
        conn.close()
        raise HTTPException(status_code=403, detail="Invite email does not match current user")

    org = conn.execute("SELECT * FROM organizations WHERE id = ?", (invite["organization_id"],)).fetchone()
    member_count = conn.execute("SELECT COUNT(*) AS c FROM memberships WHERE organization_id = ?", (invite["organization_id"],)).fetchone()["c"]
    if member_count >= int(org["max_users"] or 0):
        conn.close()
        raise HTTPException(status_code=403, detail="User limit reached for current tariff")

    conn.execute(
        "INSERT OR IGNORE INTO memberships(organization_id, user_id, role, status) VALUES(?, ?, ?, ?)",
        (invite["organization_id"], int(user["id"]), invite["role"], "Активен")
    )
    conn.execute(
        "UPDATE invites SET status = ?, accepted_at = ? WHERE id = ?",
        ("Принято", iso_now(), invite["id"])
    )
    log_action(conn, int(invite["organization_id"]), int(user["id"]), "Приглашение принято", "invite", invite["token"], {"email": user["email"], "role": invite["role"]})
    conn.commit()
    conn.close()
    return {"ok": True, "organization_id": int(invite["organization_id"]), "role": invite["role"]}


@app.get("/api/v1/import-history")
def list_import_history(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None), limit: int = Query(default=20, ge=1, le=100)):
    user_id = get_user_id_from_token(authorization)
    ensure_membership(user_id, organization_id)
    org = get_org(organization_id)
    check_billing_and_feature(org, "import_history")
    conn = db()
    rows = conn.execute(
        "SELECT pi.id, pi.row_count, pi.mode, pi.created_at, pi.added_count, pi.updated_count, pi.removed_count, pi.change_summary_json, u.full_name AS imported_by_name, u.email AS imported_by_email FROM product_imports pi JOIN users u ON u.id = pi.imported_by_user_id WHERE pi.organization_id = ? ORDER BY pi.created_at DESC LIMIT ?",
        (organization_id, limit)
    ).fetchall()
    conn.close()
    out = []
    for row in rows:
        item = dict(row)
        try:
            item["change_summary"] = json.loads(item.get("change_summary_json") or "{}")
        except Exception:
            item["change_summary"] = {}
        out.append(item)
    return out


@app.get("/api/v1/audit-log")
def list_audit_log(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None), limit: int = Query(default=30, ge=1, le=100)):
    user_id = get_user_id_from_token(authorization)
    membership = get_membership(user_id, organization_id)
    permissions = get_role_permissions(membership["role"])
    if not permissions.get("view_audit", False):
        raise HTTPException(status_code=403, detail="Журнал действий недоступен для вашей роли")
    org = get_org(organization_id)
    check_billing_and_feature(org, "audit_log")
    conn = db()
    rows = conn.execute(
        "SELECT al.*, u.full_name AS actor_name, u.email AS actor_email FROM audit_logs al LEFT JOIN users u ON u.id = al.actor_user_id WHERE al.organization_id = ? ORDER BY al.created_at DESC LIMIT ?",
        (organization_id, limit)
    ).fetchall()
    conn.close()
    return [enrich_audit_row(r) for r in rows]


@app.post("/api/v1/products")
def create_products(payload: list[ProductIn], organization_id: int = Query(...), mode: str = Query(default="replace"), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    ensure_org_permission(user_id, organization_id, "manage_products")
    org = get_org(organization_id)

    if mode != "replace":
        raise HTTPException(status_code=400, detail="Only replace mode is supported in this version")
    if len(payload) > int(org["max_sku"] or 0):
        raise HTTPException(status_code=403, detail="SKU limit reached for current tariff")

    seen_sku = set()
    for item in payload:
        sku_norm = item.sku.strip().lower()
        if sku_norm in seen_sku:
            raise HTTPException(status_code=400, detail=f"Duplicate SKU in import: {item.sku}")
        seen_sku.add(sku_norm)
        if not item.channel.strip() or not item.warehouse.strip():
            raise HTTPException(status_code=400, detail=f"Channel and warehouse are required for SKU {item.sku}")
        numeric_fields = {
            "price": item.price,
            "unit_cost": item.unit_cost,
            "stock": item.stock,
            "reserved": item.reserved,
            "inbound": item.inbound,
            "lead_time_days": item.lead_time_days,
            "avg_daily_sales": item.avg_daily_sales,
            "logistics_per_unit": item.logistics_per_unit,
            "ad_spend": item.ad_spend,
            "return_rate": item.return_rate,
            "commission_rate": item.commission_rate,
        }
        for field_name, value in numeric_fields.items():
            if field_name in {"return_rate", "commission_rate"}:
                if value < 0 or value > 1:
                    raise HTTPException(status_code=400, detail=f"Field {field_name} must be between 0 and 1 for SKU {item.sku}")
            elif value < 0:
                raise HTTPException(status_code=400, detail=f"Field {field_name} cannot be negative for SKU {item.sku}")

    conn = db()
    existing_rows = conn.execute("SELECT * FROM products WHERE organization_id = ?", (organization_id,)).fetchall()
    import_stats = compare_products(existing_rows, payload)
    conn.execute("DELETE FROM products WHERE organization_id = ?", (organization_id,))
    for item in payload:
        conn.execute(
            "INSERT INTO products(organization_id, sku, account, name, channel, warehouse, price, unit_cost, stock, reserved, inbound, lead_time_days, avg_daily_sales, trend, commission_rate, logistics_per_unit, ad_spend, return_rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (organization_id, item.sku, item.account, item.name, item.channel, item.warehouse, item.price, item.unit_cost, item.stock, item.reserved, item.inbound, item.lead_time_days, item.avg_daily_sales, item.trend, item.commission_rate, item.logistics_per_unit, item.ad_spend, item.return_rate)
        )
    conn.execute(
        "INSERT INTO product_imports(organization_id, imported_by_user_id, row_count, mode, created_at, added_count, updated_count, removed_count, change_summary_json) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (organization_id, user_id, len(payload), mode, iso_now(), import_stats["added_count"], import_stats["updated_count"], import_stats["removed_count"], json.dumps(import_stats["changed_fields"], ensure_ascii=False))
    )
    log_action(conn, organization_id, user_id, "CSV импорт выполнен", "products", str(organization_id), {"row_count": len(payload), **import_stats})
    conn.commit()
    conn.close()
    return {"ok": True, "count": len(payload), "mode": mode, **import_stats}


@app.get("/api/v1/products")
def list_products(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = get_membership(user_id, organization_id)
    org = get_org(organization_id)
    check_billing_and_feature(org, "dashboard")
    maybe_run_auto_sync(organization_id)
    conn = db()
    rows = conn.execute("SELECT * FROM products WHERE organization_id = ? ORDER BY id ASC", (organization_id,)).fetchall()
    conn.close()
    out = []
    for row in rows:
        item = dict(row)
        item.update(product_metrics(row))
        out.append(sanitize_product_for_role(item, membership["role"]))
    return out


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(organization_id: int = Query(...), authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_token(authorization)
    membership = get_membership(user_id, organization_id)
    permissions = get_role_permissions(membership["role"])
    org = get_org(organization_id)
    check_billing_and_feature(org, "dashboard")
    maybe_run_auto_sync(organization_id)
    conn = db()
    rows = conn.execute("SELECT * FROM products WHERE organization_id = ?", (organization_id,)).fetchall()
    conn.close()
    revenue = 0.0
    contribution = 0.0
    at_risk = 0.0
    frozen = 0.0
    ad_spend_total = 0.0
    high_risk_count = 0
    low_margin_count = 0
    due_soon_count = 0
    for row in rows:
        m = product_metrics(row)
        revenue += m["forecast_revenue_30d"]
        contribution += m["forecast_profit_30d"]
        ad_spend_total += row["ad_spend"]
        if m["stockout_risk"] == "high":
            high_risk_count += 1
            at_risk += row["price"] * m["adjusted_daily_sales"] * max(1, row["lead_time_days"] - m["days_of_cover"])
        if m["days_of_cover"] <= 7:
            due_soon_count += 1
        if m["days_of_cover"] > 45:
            frozen += (m["days_of_cover"] - 45) * m["adjusted_daily_sales"] * row["unit_cost"]
        if m["profit_margin_pct"] < 15:
            low_margin_count += 1
    if permissions.get("view_finance", False):
        return {
            "revenue_30d": revenue,
            "contribution_30d": contribution,
            "revenue_at_risk": at_risk,
            "frozen_cash": frozen,
            "profit_margin_pct": (contribution / revenue * 100) if revenue else 0.0,
            "roas": (revenue / ad_spend_total) if ad_spend_total else None,
            "ad_spend_30d": ad_spend_total,
            "high_risk_count": high_risk_count,
            "low_margin_count": low_margin_count,
            "due_soon_count": due_soon_count,
            "sku_count": len(rows),
            "role": membership["role"],
        }
    return {
        "revenue_30d": None,
        "contribution_30d": None,
        "revenue_at_risk": None,
        "frozen_cash": None,
        "profit_margin_pct": None,
        "roas": None,
        "ad_spend_30d": None,
        "high_risk_count": high_risk_count,
        "low_margin_count": None,
        "due_soon_count": due_soon_count,
        "sku_count": len(rows),
        "role": membership["role"],
    }

class AdminMetaUpdateIn(BaseModel):
    source: str = ""
    stage: str = "new"
    note: str = ""
    tags: str = ""
    internal_status: str = ""


class AdminAccessUpdateIn(BaseModel):
    access_state: str = "active"
    period_days: int = 30
    tariff_code: str = "starter"
    custom_tariff_label: str = ""
    price_month: float = 0
    max_users: Optional[int] = None
    max_sku: Optional[int] = None
    features_override: Optional[dict] = None
    blocked_reason: str = ""


class AdminBulkActionIn(BaseModel):
    org_ids: list[int]
    action: str
    period_days: int = 30
    tariff_code: str = "starter"


class TariffPresetIn(BaseModel):
    code: str
    label: str
    price_month: float = 0
    max_users: int = 2
    max_sku: int = 500
    features: dict = {}
    is_active: bool = True


CLIENT_STAGES = {'new', 'contacted', 'demo', 'negotiation', 'paid', 'churned'}
ACCESS_STATES = {'pending', 'trial', 'active', 'expired', 'blocked', 'vip', 'frozen'}


def ensure_client_meta(conn, organization_id: int):
    row = conn.execute('SELECT * FROM admin_client_meta WHERE organization_id = ?', (organization_id,)).fetchone()
    if not row:
        now = iso_now()
        conn.execute('INSERT INTO admin_client_meta(organization_id, source, stage, note, tags, internal_status, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?)', (organization_id, '', 'new', '', '', '', now, now))
        row = conn.execute('SELECT * FROM admin_client_meta WHERE organization_id = ?', (organization_id,)).fetchone()
    return row


def user_last_login(conn, user_id: Optional[int]):
    if not user_id:
        return ''
    row = conn.execute('SELECT MAX(created_at) AS last_login FROM sessions WHERE user_id = ?', (user_id,)).fetchone()
    return (row['last_login'] or '') if row else ''


def org_effective_state(org: dict):
    state = (org.get('access_state') or '').strip() or ''
    billing_status = (org.get('billing_status') or '').strip()
    paid_until = (org.get('paid_until') or '').strip()
    if state in {'blocked', 'vip', 'trial', 'frozen'}:
        if state == 'trial' and paid_until:
            try:
                if datetime.fromisoformat(paid_until).date() < now_utc().date():
                    return 'expired'
            except Exception:
                pass
        return state
    if billing_status == 'active':
        if paid_until:
            try:
                if datetime.fromisoformat(paid_until).date() < now_utc().date():
                    return 'expired'
            except Exception:
                return 'active'
        return 'active'
    if billing_status == 'blocked':
        return 'blocked'
    return 'pending'


def state_label(state: str):
    return {
        'pending': 'Ожидает доступа',
        'trial': 'Пробный период',
        'active': 'Активен',
        'expired': 'Истёк',
        'blocked': 'Заблокирован',
        'vip': 'VIP',
        'frozen': 'Заморожен',
    }.get(state, state or '—')


def connection_summary(conn, organization_id: int):
    rows = conn.execute('SELECT * FROM marketplace_connections WHERE organization_id = ? ORDER BY marketplace ASC', (organization_id,)).fetchall()
    out = []
    for row in rows:
        item = normalize_connection_row(row)
        out.append({
            'marketplace': item['marketplace'],
            'status': item['status'],
            'last_success_at': item['last_success_at'],
            'last_error': item['last_error'],
            'sync_notice': item['sync_notice'],
            'token_expires_at': item['token_expires_at'],
        })
    return out


def org_issues(conn, org_row):
    item = dict(org_row)
    issues = []
    state = org_effective_state(item)
    if state in {'pending', 'expired'}:
        issues.append({'type': 'billing', 'level': 'warning', 'title': 'Нет активного доступа', 'message': 'Организация не может открыть рабочие разделы без активации тарифа.'})
    if state == 'blocked':
        issues.append({'type': 'billing', 'level': 'critical', 'title': 'Организация заблокирована', 'message': item.get('blocked_reason') or 'Доступ был принудительно отключён администратором.'})
    if state == 'frozen':
        issues.append({'type': 'billing', 'level': 'warning', 'title': 'Доступ заморожен', 'message': 'Организация временно неактивна до решения администратора.'})
    products_count = conn.execute('SELECT COUNT(*) AS c FROM products WHERE organization_id = ?', (item['id'],)).fetchone()['c']
    if products_count == 0:
        issues.append({'type': 'data', 'level': 'warning', 'title': 'Нет товаров', 'message': 'В организации нет загруженных товаров. Можно подключить WB/Ozon или использовать CSV.'})
    for c in connection_summary(conn, item['id']):
        if c['sync_notice']:
            issues.append({'type': 'token', 'level': 'warning', 'title': f"{(c['marketplace'] or '').upper()} токен", 'message': c['sync_notice']})
        if c['last_error']:
            issues.append({'type': 'sync', 'level': 'critical', 'title': f"Ошибка синхронизации {(c['marketplace'] or '').upper()}", 'message': c['last_error'][:220]})
        if c['status'] == 'connected' and c['last_success_at']:
            try:
                last_ok = datetime.fromisoformat(c['last_success_at'])
                if last_ok <= now_utc() - timedelta(hours=24):
                    issues.append({'type': 'sync', 'level': 'warning', 'title': f"Давно не было синхронизации {(c['marketplace'] or '').upper()}", 'message': f"Последний успешный обмен был {c['last_success_at']}"})
            except Exception:
                pass
    owner_last_login = user_last_login(conn, item.get('owner_user_id'))
    if owner_last_login:
        try:
            if datetime.fromisoformat(owner_last_login) <= now_utc() - timedelta(days=14):
                issues.append({'type': 'engagement', 'level': 'info', 'title': 'Клиент давно не заходил', 'message': f'Последний вход владельца: {owner_last_login}'})
        except Exception:
            pass
    return issues


def admin_org_payload(conn, row):
    org = enrich_org(sync_org_billing_state(conn, row))
    meta = ensure_client_meta(conn, int(org['id']))
    member_count = conn.execute('SELECT COUNT(*) AS c FROM memberships WHERE organization_id = ?', (org['id'],)).fetchone()['c']
    product_count = conn.execute('SELECT COUNT(*) AS c FROM products WHERE organization_id = ?', (org['id'],)).fetchone()['c']
    import_count = conn.execute('SELECT COUNT(*) AS c FROM product_imports WHERE organization_id = ?', (org['id'],)).fetchone()['c']
    last_import = conn.execute('SELECT MAX(created_at) AS v FROM product_imports WHERE organization_id = ?', (org['id'],)).fetchone()['v']
    last_payment = conn.execute('SELECT MAX(created_at) AS v FROM manual_payments WHERE organization_id = ?', (org['id'],)).fetchone()['v']
    owner_last_login = user_last_login(conn, org.get('owner_user_id'))
    issues = org_issues(conn, org)
    org.update({
        'owner_last_login': owner_last_login,
        'member_count': int(member_count or 0),
        'product_count': int(product_count or 0),
        'import_count': int(import_count or 0),
        'last_import_at': last_import or '',
        'last_payment_at': last_payment or '',
        'client_meta': dict(meta),
        'stage': meta['stage'],
        'source': meta['source'],
        'note': meta['note'],
        'tags': meta['tags'],
        'internal_status': meta['internal_status'],
        'effective_state': org_effective_state(org),
        'effective_state_label': state_label(org_effective_state(org)),
        'issues': issues,
        'issues_count': len(issues),
        'connections': connection_summary(conn, org['id']),
    })
    return org


def apply_access_update(conn, org_id: int, admin_user_id: int, payload: AdminAccessUpdateIn):
    row = conn.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Organization not found')
    state = (payload.access_state or 'active').strip()
    if state not in ACCESS_STATES:
        raise HTTPException(status_code=400, detail='Unknown access state')
    tariff_code = (payload.tariff_code or 'starter').strip()
    if state in {'active', 'trial', 'vip'} and not tariff_exists(tariff_code):
        raise HTTPException(status_code=400, detail='Unknown tariff')
    features = get_tariff_features(tariff_code)
    max_users = int(payload.max_users or features.get('max_users') or row['max_users'] or 2)
    max_sku = int(payload.max_sku or features.get('max_sku') or row['max_sku'] or 500)
    custom_features_json = json.dumps(payload.features_override or {}, ensure_ascii=False) if payload.features_override else (row['custom_features_json'] or '')
    custom_label = (payload.custom_tariff_label or '').strip()
    price_month = float(payload.price_month or 0)
    period_days = max(1, min(int(payload.period_days or 30), 3650))
    paid_until = ''
    billing_status = row['billing_status']
    frozen_at = row['frozen_at'] or ''
    blocked_reason = (payload.blocked_reason or '').strip()
    if state in {'active', 'trial', 'vip'}:
        paid_until = (now_utc() + timedelta(days=period_days)).date().isoformat()
        billing_status = 'active'
        frozen_at = ''
    elif state == 'expired':
        paid_until = (now_utc() - timedelta(days=1)).date().isoformat()
        billing_status = 'blocked'
    elif state == 'blocked':
        billing_status = 'blocked'
        paid_until = ''
    elif state == 'frozen':
        billing_status = 'blocked'
        frozen_at = iso_now()
    elif state == 'pending':
        billing_status = 'pending_payment'
        paid_until = ''
    conn.execute(
        'UPDATE organizations SET tariff_code=?, tariff=?, billing_status=?, paid_until=?, max_users=?, max_sku=?, access_state=?, custom_tariff_label=?, custom_features_json=?, custom_price_month=?, frozen_at=?, blocked_reason=? WHERE id=?',
        (tariff_code, tariff_code, billing_status, paid_until, max_users, max_sku, state, custom_label, custom_features_json, price_month, frozen_at, blocked_reason, org_id)
    )
    if state in {'active', 'trial', 'vip'}:
        created_at = iso_now()
        conn.execute('INSERT INTO manual_payments(organization_id, actor_user_id, tariff_code, amount, period_days, payer_name, payment_channel, note, status, created_at, paid_until) VALUES(?,?,?,?,?,?,?,?,?,?,?)', (org_id, admin_user_id, tariff_code, price_month, period_days, '', '', state, 'confirmed', created_at, paid_until))
    log_action(conn, org_id, admin_user_id, 'Статус доступа обновлён главным администратором', 'billing', str(org_id), {'access_state': state, 'tariff_code': tariff_code, 'paid_until': paid_until, 'max_users': max_users, 'max_sku': max_sku, 'custom_tariff_label': custom_label, 'price_month': price_month, 'blocked_reason': blocked_reason})


def admin_stats_payload(conn):
    org_rows = conn.execute('SELECT * FROM organizations ORDER BY id DESC').fetchall()
    active = trial = expired = blocked = pending = vip = frozen = 0
    soon_expiring = 0
    total_expected_mrr = 0.0
    actual_received_30d = 0.0
    for row in org_rows:
        payload = admin_org_payload(conn, row)
        state = payload['effective_state']
        if state == 'active': active += 1
        elif state == 'trial': trial += 1
        elif state == 'expired': expired += 1
        elif state == 'blocked': blocked += 1
        elif state == 'vip': vip += 1
        elif state == 'frozen': frozen += 1
        else: pending += 1
        if isinstance(payload.get('billing_days_left'), int) and payload['billing_days_left'] <= 7 and payload['billing_days_left'] >= 0:
            soon_expiring += 1
        total_expected_mrr += float(payload.get('custom_price_month') or 0)
    pay_rows = conn.execute('SELECT amount, created_at FROM manual_payments ORDER BY created_at DESC').fetchall()
    for row in pay_rows:
        try:
            if datetime.fromisoformat(row['created_at']) >= now_utc() - timedelta(days=30):
                actual_received_30d += float(row['amount'] or 0)
        except Exception:
            pass
    total_connections = conn.execute('SELECT COUNT(*) AS c FROM marketplace_connections WHERE status = ?', ('connected',)).fetchone()['c']
    sync_errors = conn.execute("SELECT COUNT(*) AS c FROM marketplace_connections WHERE COALESCE(last_error,'') != ''").fetchone()['c']
    new_regs_7d = 0
    user_rows = conn.execute('SELECT created_at FROM users').fetchall()
    for row in user_rows:
        try:
            if row['created_at'] and datetime.fromisoformat(row['created_at']) >= now_utc() - timedelta(days=7):
                new_regs_7d += 1
        except Exception:
            pass
    return {
        'organization_count': len(org_rows),
        'active_count': active,
        'trial_count': trial,
        'expired_count': expired,
        'blocked_count': blocked,
        'pending_count': pending,
        'vip_count': vip,
        'frozen_count': frozen,
        'soon_expiring_count': soon_expiring,
        'expected_mrr': total_expected_mrr,
        'received_30d': actual_received_30d,
        'connected_marketplaces': int(total_connections or 0),
        'sync_error_count': int(sync_errors or 0),
        'new_registrations_7d': new_regs_7d,
    }


@app.get('/api/v1/admin/dashboard')
def admin_dashboard(authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    conn = db()
    stats = admin_stats_payload(conn)
    conn.close()
    return stats


@app.get('/api/v1/admin/notifications')
def admin_notifications(authorization: Optional[str] = Header(default=None), limit: int = Query(default=100, ge=1, le=500)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute('SELECT * FROM organizations ORDER BY id DESC').fetchall()
    notices = []
    for row in rows:
        payload = admin_org_payload(conn, row)
        if isinstance(payload.get('billing_days_left'), int) and 0 <= payload['billing_days_left'] <= 7 and payload['effective_state'] in {'active', 'trial', 'vip'}:
            notices.append({'organization_id': payload['id'], 'organization_name': payload['name'], 'level': 'warning', 'type': 'billing_expiry', 'title': 'Тариф скоро закончится', 'message': f"До конца доступа осталось {payload['billing_days_left']} дн."})
        for issue in payload['issues']:
            notices.append({'organization_id': payload['id'], 'organization_name': payload['name'], **issue})
    conn.close()
    severity = {'critical': 0, 'warning': 1, 'info': 2}
    notices.sort(key=lambda x: (severity.get(x.get('level'), 9), x['organization_name']))
    return notices[:limit]


@app.get('/api/v1/admin/issues')
def admin_issues(authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute('SELECT * FROM organizations ORDER BY id DESC').fetchall()
    out = []
    for row in rows:
        payload = admin_org_payload(conn, row)
        if payload['issues']:
            out.append({'organization_id': payload['id'], 'organization_name': payload['name'], 'issues': payload['issues']})
    conn.close()
    return out


@app.get('/api/v1/admin/activity')
def admin_activity(authorization: Optional[str] = Header(default=None), limit: int = Query(default=100, ge=1, le=500)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute('SELECT al.*, o.name AS organization_name, u.full_name AS actor_name, u.email AS actor_email FROM audit_logs al LEFT JOIN organizations o ON o.id = al.organization_id LEFT JOIN users u ON u.id = al.actor_user_id ORDER BY al.created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    out = []
    for row in rows:
        item = enrich_audit_row(row)
        item['organization_name'] = row['organization_name']
        item['actor_name'] = row['actor_name']
        item['actor_email'] = row['actor_email']
        out.append(item)
    return out


@app.get('/api/v1/admin/organizations')
def admin_list_organizations_v2(authorization: Optional[str] = Header(default=None), q: str = Query(default=''), status: str = Query(default='all'), stage: str = Query(default='all'), source: str = Query(default='all'), problem_only: int = Query(default=0), limit: int = Query(default=500, ge=1, le=1000)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute('SELECT o.*, u.full_name AS owner_name, u.email AS owner_email FROM organizations o LEFT JOIN users u ON u.id = o.owner_user_id ORDER BY o.id DESC LIMIT ?', (limit,)).fetchall()
    out = []
    q_norm = (q or '').strip().lower()
    for row in rows:
        payload = admin_org_payload(conn, row)
        payload['owner_name'] = row['owner_name']
        payload['owner_email'] = row['owner_email']
        if q_norm and q_norm not in f"{payload['name']} {payload.get('owner_email') or ''} {payload.get('owner_name') or ''} {payload.get('note') or ''}".lower():
            continue
        if status != 'all' and payload['effective_state'] != status:
            continue
        if stage != 'all' and (payload.get('stage') or 'new') != stage:
            continue
        if source != 'all' and (payload.get('source') or '') != source:
            continue
        if problem_only and not payload['issues']:
            continue
        out.append(payload)
    conn.close()
    return out




def admin_delete_organization_cascade(conn, org_id: int, actor_user_id: int):
    org = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
    if not org:
        raise HTTPException(status_code=404, detail='Organization not found')
    owner_email_row = conn.execute("SELECT email FROM users WHERE id = ?", (org["owner_user_id"],)).fetchone()
    owner_email = (owner_email_row["email"] if owner_email_row else '') or ''
    log_action(conn, org_id, actor_user_id, 'Организация удалена главным администратором', 'organization', str(org_id), {'organization_name': org['name'], 'owner_user_id': org['owner_user_id'], 'owner_email': owner_email})
    conn.execute("DELETE FROM marketplace_sync_logs WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM marketplace_connections WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM manual_payments WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM audit_logs WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM product_imports WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM products WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM invites WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM memberships WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM admin_client_meta WHERE organization_id = ?", (org_id,))
    conn.execute("DELETE FROM organizations WHERE id = ?", (org_id,))
    return {'ok': True, 'deleted_org_id': org_id, 'deleted_org_name': org['name']}


def admin_delete_user_account(conn, user_id: int, actor_user_id: int):
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if (user['email'] or '').strip().lower() == SUPERADMIN_EMAIL.strip().lower():
        raise HTTPException(status_code=400, detail='Нельзя удалить главного администратора')
    owned = conn.execute("SELECT id, name FROM organizations WHERE owner_user_id = ? ORDER BY id ASC", (user_id,)).fetchall()
    if owned:
        names = ', '.join([r['name'] for r in owned[:3]])
        suffix = '' if len(owned) <= 3 else '…'
        raise HTTPException(status_code=400, detail=f'Сначала удалите или передайте организации пользователя: {names}{suffix}')
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM invites WHERE lower(email) = ?", ((user['email'] or '').strip().lower(),))
    conn.execute("DELETE FROM memberships WHERE user_id = ?", (user_id,))
    conn.execute("UPDATE manual_payments SET actor_user_id = NULL WHERE actor_user_id = ?", (user_id,))
    conn.execute("UPDATE product_imports SET imported_by_user_id = 0 WHERE imported_by_user_id = ?", (user_id,))
    conn.execute("UPDATE audit_logs SET actor_user_id = NULL WHERE actor_user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return {'ok': True, 'deleted_user_id': user_id, 'deleted_user_email': user['email'], 'deleted_user_name': user['full_name']}

@app.get('/api/v1/admin/organizations/{org_id}')
def admin_get_organization(org_id: int, authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    conn = db()
    row = conn.execute('SELECT o.*, u.full_name AS owner_name, u.email AS owner_email FROM organizations o LEFT JOIN users u ON u.id = o.owner_user_id WHERE o.id = ?', (org_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail='Organization not found')
    payload = admin_org_payload(conn, row)
    payload['owner_name'] = row['owner_name']
    payload['owner_email'] = row['owner_email']
    payload['team'] = [membership_to_dict(r) for r in conn.execute('SELECT m.*, u.full_name, u.email FROM memberships m JOIN users u ON u.id = m.user_id WHERE m.organization_id = ? ORDER BY m.id ASC', (org_id,)).fetchall()]
    payload['recent_payments'] = [dict(r) for r in conn.execute('SELECT * FROM manual_payments WHERE organization_id = ? ORDER BY created_at DESC LIMIT 20', (org_id,)).fetchall()]
    payload['recent_imports'] = [dict(r) for r in conn.execute('SELECT * FROM product_imports WHERE organization_id = ? ORDER BY created_at DESC LIMIT 10', (org_id,)).fetchall()]
    payload['recent_logs'] = [enrich_audit_row(r) for r in conn.execute('SELECT * FROM audit_logs WHERE organization_id = ? ORDER BY created_at DESC LIMIT 30', (org_id,)).fetchall()]
    conn.close()
    return payload




@app.delete('/api/v1/admin/organizations/{org_id}')
def admin_delete_organization(org_id: int, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    result = admin_delete_organization_cascade(conn, org_id, int(admin_user['id']))
    conn.commit()
    conn.close()
    return result


@app.delete('/api/v1/admin/users/{user_id}')
def admin_delete_user(user_id: int, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    result = admin_delete_user_account(conn, user_id, int(admin_user['id']))
    conn.commit()
    conn.close()
    return result

@app.put('/api/v1/admin/organizations/{org_id}/meta')
def admin_update_meta(org_id: int, payload: AdminMetaUpdateIn, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    if not conn.execute('SELECT id FROM organizations WHERE id = ?', (org_id,)).fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail='Organization not found')
    stage = (payload.stage or 'new').strip().lower()
    if stage not in CLIENT_STAGES:
        stage = 'new'
    ensure_client_meta(conn, org_id)
    now = iso_now()
    conn.execute('UPDATE admin_client_meta SET source=?, stage=?, note=?, tags=?, internal_status=?, updated_at=? WHERE organization_id=?', ((payload.source or '').strip(), stage, (payload.note or '').strip(), (payload.tags or '').strip(), (payload.internal_status or '').strip(), now, org_id))
    log_action(conn, org_id, int(admin_user['id']), 'CRM-метаданные клиента обновлены', 'crm', str(org_id), {'source': payload.source, 'stage': stage, 'tags': payload.tags, 'internal_status': payload.internal_status})
    conn.commit()
    row = conn.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    result = admin_org_payload(conn, row)
    conn.close()
    return result


@app.post('/api/v1/admin/organizations/{org_id}/access')
def admin_update_access(org_id: int, payload: AdminAccessUpdateIn, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    apply_access_update(conn, org_id, int(admin_user['id']), payload)
    conn.commit()
    row = conn.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    result = admin_org_payload(conn, row)
    conn.close()
    return result


@app.post('/api/v1/admin/organizations/{org_id}/manual-payment')
def admin_manual_payment_v2(org_id: int, payload: ManualPaymentIn, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    access = AdminAccessUpdateIn(access_state='active', period_days=payload.period_days or 30, tariff_code=payload.tariff_code, price_month=float(payload.amount or 0))
    conn = db()
    apply_access_update(conn, org_id, int(admin_user['id']), access)
    conn.commit()
    row = conn.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    result = admin_org_payload(conn, row)
    conn.close()
    return result


@app.post('/api/v1/admin/organizations/{org_id}/block')
def admin_block_org_v2(org_id: int, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='blocked', blocked_reason='Заблокировано администратором'))
    conn.commit()
    row = conn.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    result = admin_org_payload(conn, row)
    conn.close()
    return result


@app.post('/api/v1/admin/bulk-action')
def admin_bulk_action(payload: AdminBulkActionIn, authorization: Optional[str] = Header(default=None)):
    admin_user = ensure_super_admin(authorization)
    conn = db()
    processed = []
    for org_id in payload.org_ids:
        if payload.action == 'extend30':
            apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='active', period_days=30, tariff_code=payload.tariff_code))
        elif payload.action == 'extend90':
            apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='active', period_days=90, tariff_code=payload.tariff_code))
        elif payload.action == 'extend365':
            apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='active', period_days=365, tariff_code=payload.tariff_code))
        elif payload.action == 'block':
            apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='blocked', blocked_reason='Массовая блокировка'))
        elif payload.action == 'trial':
            apply_access_update(conn, org_id, int(admin_user['id']), AdminAccessUpdateIn(access_state='trial', period_days=max(1, payload.period_days), tariff_code=payload.tariff_code))
        else:
            continue
        processed.append(org_id)
    conn.commit()
    conn.close()
    return {'ok': True, 'processed_org_ids': processed, 'action': payload.action}


@app.get('/api/v1/admin/tariffs')
def admin_list_tariffs(authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    conn = db()
    rows = conn.execute('SELECT * FROM tariff_presets ORDER BY id ASC').fetchall()
    conn.close()
    out = []
    for row in rows:
        try:
            features = json.loads(row['features_json'] or '{}')
        except Exception:
            features = {}
        out.append({**dict(row), 'features': features})
    return out


@app.post('/api/v1/admin/tariffs')
def admin_upsert_tariff(payload: TariffPresetIn, authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    code = (payload.code or '').strip().lower()
    if not code or code == 'none':
        raise HTTPException(status_code=400, detail='Некорректный код тарифа')
    now = iso_now()
    features = dict(payload.features or {})
    features.setdefault('label', payload.label)
    features.setdefault('max_users', int(payload.max_users))
    features.setdefault('max_sku', int(payload.max_sku))
    conn = db()
    existing = conn.execute('SELECT id FROM tariff_presets WHERE code = ?', (code,)).fetchone()
    values = (payload.label.strip(), float(payload.price_month or 0), int(payload.max_users), int(payload.max_sku), json.dumps(features, ensure_ascii=False), 1 if payload.is_active else 0, now)
    if existing:
        conn.execute('UPDATE tariff_presets SET label=?, price_month=?, max_users=?, max_sku=?, features_json=?, is_active=?, updated_at=? WHERE code=?', (*values, code))
    else:
        conn.execute('INSERT INTO tariff_presets(label, price_month, max_users, max_sku, features_json, is_active, created_at, updated_at, code) VALUES(?,?,?,?,?,?,?,?,?)', (*values, now, code))
    conn.commit()
    rows = conn.execute('SELECT * FROM tariff_presets ORDER BY id ASC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post('/api/v1/admin/impersonate/{org_id}')
def admin_impersonate(org_id: int, authorization: Optional[str] = Header(default=None)):
    ensure_super_admin(authorization)
    conn = db()
    row = conn.execute('SELECT owner_user_id FROM organizations WHERE id = ?', (org_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail='Organization not found')
    token = create_session(int(row['owner_user_id']))
    return {'access_token': token, 'user_id': int(row['owner_user_id']), 'organization_id': org_id}
