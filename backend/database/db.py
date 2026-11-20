import os
from dotenv import load_dotenv
from backend.database.db_connection import DBConnector
from models.azure_auth import get_azure_credential

load_dotenv()

db_connector = DBConnector.create_engine(
    driver_name="{ODBC Driver 18 for SQL Server}",
    server_name=os.getenv("SERVER"),
    database_name=os.getenv("DATABASE"),
    credential=get_azure_credential(),
)