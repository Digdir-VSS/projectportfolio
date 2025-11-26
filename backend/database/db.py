import os
from dotenv import load_dotenv
from backend.database.db_connection import DBConnector

load_dotenv()

db_connector = DBConnector.create_engine(
    driver_name="{ODBC Driver 18 for SQL Server}",
    server_name=os.getenv("SERVER"),
    database_name=os.getenv("DATABASE"),
    fabric_client_id=os.getenv("FABRIC_CLIENT_ID"),
    fabric_tenant_id=os.getenv("TENANT_ID"),
    fabric_client_secret=os.getenv("FABRIC_SECRET"),
)