# import os
# import struct
# import urllib
# from sqlalchemy import create_engine, event, select
# from sqlmodel import Session
# from azure.identity import ClientSecretCredential
# from dotenv import load_dotenv

# load_dotenv()

# # --- Azure creds ---
# driver_name = "{ODBC Driver 18 for SQL Server}"
# server_name = os.getenv("SERVER")      # e.g. "xxx.datawarehouse.fabric.microsoft.com"
# database_name = os.getenv("DATABASE")
# print(server_name)
# # --- Connection string (NO auth here, token comes later) ---
# connection_string = (
#     "Driver={};Server=tcp:{},1433;Database={};Encrypt=yes;"
#     "TrustServerCertificate=no;Connection Timeout=30"
# ).format(driver_name, server_name, database_name)

# params = urllib.parse.quote(connection_string)
# odbc_str = f"mssql+pyodbc:///?odbc_connect={params}"

# # --- Get SQLAlchemy engine ---
# engine = create_engine(odbc_str, echo=True)

# # --- Token injection hook ---
# azure_client_id = os.getenv("AZURE_CLIENT_ID")
# azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
# azure_tenant_id = os.getenv("AZURE_TENANT_ID")
# credential = ClientSecretCredential(tenant_id=azure_tenant_id,client_id=azure_client_id,client_secret=azure_client_secret)    # or ClientSecretCredential if you prefer

# @event.listens_for(engine, "do_connect")
# def provide_token(dialect, conn_rec, cargs, cparams):
#     print("🔑 Requesting new Entra ID token for SQL Server...")
#     token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
#     token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
#     SQL_COPT_SS_ACCESS_TOKEN = 1256
#     cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

# # --- CRUD utilities ---
# def add_row(obj):
#     """Insert a new row (SQLModel object)."""
#     with Session(engine) as session:
#         session.add(obj)
#         session.commit()
#         session.refresh(obj)
#         return obj

# def delete_row(model, row_id):
#     """Delete row by UUID primary key."""
#     with Session(engine) as session:
#         row = session.get(model, row_id)
#         if row:
#             session.delete(row)
#             session.commit()
#             return True
#         return False

# def get_all(model):
#     """Retrieve all rows for a model."""
#     with Session(engine) as session:
#         return session.exec(select(model)).all()