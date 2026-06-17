"""
utils/auth.py — Fungsi autentikasi: login, register, hash password
"""

import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import create_engine, text


@st.cache_resource(show_spinner=False)
def get_db_engine():
    try:
        db_url = (
            f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}"
            f"@{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
        )
        return create_engine(db_url), None
    except Exception as e:
        return None, str(e)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def login_user(email: str, password: str):
    engine, err = get_db_engine()
    if err:
        return None, f"Koneksi database gagal: {err}"
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM user_profiles WHERE email = :email AND is_active = TRUE"),
                {"email": email.strip().lower()}
            )
            row = result.fetchone()
        if row is None:
            return None, "Email tidak ditemukan atau akun tidak aktif."
        user = dict(row._mapping)
        if not verify_password(password, user["password"]):
            return None, "Password salah."
        user.pop("password", None)
        return user, None
    except Exception as e:
        return None, f"Gagal login: {str(e)}"


def register_user(nama: str, email: str, password: str, role: str = "viewer"):
    engine, err = get_db_engine()
    if err:
        return False, f"Koneksi database gagal: {err}"
    try:
        hashed = hash_password(password)
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO user_profiles (nama, email, password, role)
                    VALUES (:nama, :email, :password, :role)
                """),
                {"nama": nama.strip(), "email": email.strip().lower(),
                 "password": hashed, "role": role}
            )
            conn.commit()
        return True, None
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return False, "Email sudah terdaftar."
        return False, f"Gagal registrasi: {str(e)}"


def get_all_users():
    engine, err = get_db_engine()
    if err:
        return None, err
    try:
        df = pd.read_sql(
            "SELECT id, nama, email, role, is_active, created_at FROM user_profiles ORDER BY created_at DESC",
            engine
        )
        return df, None
    except Exception as e:
        return None, str(e)


def update_user_role(user_id: int, role: str):
    engine, err = get_db_engine()
    if err:
        return False, err
    try:
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE user_profiles SET role = :role WHERE id = :id"),
                {"role": role, "id": user_id}
            )
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def toggle_user_active(user_id: int, is_active: bool):
    engine, err = get_db_engine()
    if err:
        return False, err
    try:
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE user_profiles SET is_active = :is_active WHERE id = :id"),
                {"is_active": is_active, "id": user_id}
            )
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)