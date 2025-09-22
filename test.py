from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert
import os
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import FileSystemClient

azure_client_id = os.getenv("AZURE_CLIENT_ID")
azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
azure_tenant_id = os.getenv("AZURE_TENANT_ID")
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
driver="ODBC Driver 18 for SQL Server"
connection_string = (f"mssql+pyodbc://{azure_client_id}:{azure_client_secret}@{server}:1433/{database}"
f"?driver={driver}"
"&authentication=ActiveDirectoryServicePrincipal"
"&timeout=120"
"&Encrypt=yes"
"&TrustServerCertificate=no"
)


cred = ClientSecretCredential(tenant_id=azure_tenant_id,
                              client_id=azure_client_id,
                              client_secret=azure_client_secret)

file_system_client = FileSystemClient(
    account_url="https://onelake.dfs.fabric.microsoft.com",
    file_system_name="Project-portfolio",
    credential=cred)
paths = file_system_client.get_paths(path="/ProjectPortfolio.Lakehouse/Tables/")
for p in paths:
    print(p.name)