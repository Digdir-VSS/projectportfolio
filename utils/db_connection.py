from azure.identity import ClientSecretCredential
import pyodbc, struct
import os

azure_client_id = os.getenv("AZURE_CLIENT_ID")
azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
azure_tenant_id = os.getenv("AZURE_TENANT_ID")
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
driver="ODBC Driver 18 for SQL Server"
AUTHORITY = f"https://login.microsoftonline.com/{azure_tenant_id}"
connection_string = f'Driver={driver};Server=tcp:{server},1433;Database={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
credential = ClientSecretCredential(tenant_id=azure_tenant_id,
                              client_id=azure_client_id,
                              client_secret=azure_client_secret)

token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
conn = pyodbc.connect(connection_string, attrs_before={1256: token_struct})
cursor = conn.cursor()
cursor.execute("SELECT * FROM [dbo].[new_table] WHERE name = 'Test User'")

row = cursor.fetchall()
for ro in row:
    print(f"{ro.age}, {ro.name}")
# cursor.execute("INSERT INTO [dbo].[new_table] (age, name) VALUES (25, 'Test User')")
# conn.commit()