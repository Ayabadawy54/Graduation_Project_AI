# ============================================================
# Talentree AI Service — Configuration
# Reads from environment variables (Docker) or falls back to defaults (local dev)
# ============================================================
import os

_server   = os.getenv("DB_SERVER",     "db39807.public.databaseasp.net")
_name     = os.getenv("DB_NAME",       "db39807")
_user     = os.getenv("DB_USER",       "db39807")
_password = os.getenv("DB_PASSWORD",   "Ya8@_Dt4o9N=")
_encrypt  = os.getenv("DB_ENCRYPT",    "yes")
_trust    = os.getenv("DB_TRUST_CERT", "yes")

DB_CONNECTION = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={_server};"
    f"DATABASE={_name};"
    f"UID={_user};"
    f"PWD={_password};"
    f"Encrypt={_encrypt};"
    f"TrustServerCertificate={_trust};"
)
