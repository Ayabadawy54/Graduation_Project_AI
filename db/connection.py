"""Database connection module."""
import pyodbc

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=db39807.public.databaseasp.net;"
    "DATABASE=db39807;"
    "UID=db39807;"
    "PWD=Ya8@_Dt4o9N=;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

def get_conn():
    """Return a new pyodbc connection."""
    return pyodbc.connect(CONNECTION_STRING)
