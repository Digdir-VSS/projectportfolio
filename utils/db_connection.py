from typing import Any
import struct
import urllib
from sqlmodel import Session, select
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.exc import OperationalError
from azure.identity import ClientSecretCredential
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from dotenv import load_dotenv
from dataclasses import dataclass

from .project_loader import PortfolioProject, Fremskritt, Resursbehov, Samarabeid, Problemstilling, Tiltak, Risikovurdering, Malbilde, DigitaliseringStrategi, ProjectData, convert_list, apply_changes

load_dotenv()

@dataclass
class ProjectData:

    fremskritt: Fremskritt
    samarabeid: Samarabeid
    portfolioproject: PortfolioProject
    problemstilling: Problemstilling
    tiltak: Tiltak
    risikovurdering: Risikovurdering
    malbilde: Malbilde
    resursbehov: Resursbehov
    digitaliseringstrategi: DigitaliseringStrategi


def get_single_project_data(project_id: str, sql_models: dict):
    
    statement_dict = {}
    for schema_name, schema in sql_models.items():
        statement_dict[schema_name] = select(schema).where(schema.prosjekt_id == project_id and schema.er_gjeldende == True)
    return statement_dict
   

class DBConnector:
    engine: Engine
    #{"fremskritt": Fremskritt, "samarabeid": Samarabeid, "portfolioproject": PortfolioProject, "problemstilling": Problemstilling, "tiltak": Tiltak, "risikovurdering": Risikovurdering, "malbilde": Malbilde, "resursbehov": Resursbehov, "digitaliseringstrategi": DigitaliseringStrategi}

    def __init__(self, engine: Engine, sql_model_names: dict[str, Any]):
        self.engine = engine
        self.sql_model_names = sql_model_names

    @classmethod
    def create_engine(cls, driver_name: str, server_name: str, database_name: str, fabric_client_id: str, fabric_tenant_id: str, fabric_client_secret: str):
            # --- Connection string (NO auth here, token comes later) ---
        connection_string = (
            "Driver={};Server=tcp:{},1433;Database={};Encrypt=yes;"
            "TrustServerCertificate=no;Connection Timeout=30"
        ).format(driver_name, server_name, database_name)

        params = urllib.parse.quote(connection_string)
        odbc_str = f"mssql+pyodbc:///?odbc_connect={params}"

        engine = create_engine(odbc_str, echo=False, pool_pre_ping=True, pool_recycle=3600, pool_timeout=30)

        credential = ClientSecretCredential(tenant_id=fabric_tenant_id,client_id=fabric_client_id,client_secret=fabric_client_secret)  # or ClientSecretCredential if you prefer

        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            print("🔑 Requesting new Entra ID token for SQL Server...")
            token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
            token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}
        sql_model_names = {"fremskritt": Fremskritt, "samarabeid": Samarabeid, "portfolioproject": PortfolioProject, "problemstilling": Problemstilling, "tiltak": Tiltak, "risikovurdering": Risikovurdering, "malbilde": Malbilde, "resursbehov": Resursbehov, "digitaliseringstrategi": DigitaliseringStrategi}
        return cls(engine, sql_model_names)
    
    @retry(retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True)
    def get_projects(self, email: str | None = None):
        columns = [
            PortfolioProject.prosjekt_id,
            PortfolioProject.navn,
            PortfolioProject.avdeling,
            PortfolioProject.tiltakseier,
            PortfolioProject.epost_kontakt,
        ]

        with Session(self.engine) as session:
            if email:
                stmt = select(*columns).where(PortfolioProject.er_gjeldende == True, PortfolioProject.epost_kontakt == email)
            else:
                stmt = select(*columns).where(PortfolioProject.er_gjeldende == True)
            results = session.exec(stmt).all()
        return [
            {
                "prosjekt_id": r[0],
                "navn": r[1],
                "avdeling": r[2],
                "tiltakseier": r[3],
                "epost_kontakt": r[4],
            }
            for r in results
        ]

    @retry(retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True)
    def get_single_project(self, project_id: str):
        sql_model_dict = {}
        with Session(self.engine) as session:
            stmt_dict = get_single_project_data(project_id, self.sql_model_names)
            for sql_model_name, sql_statement in stmt_dict.items():
                result = session.exec(sql_statement).first()
                sql_model_dict[sql_model_name] = result
        
        project_data = ProjectData(
                **sql_model_dict
        )
        return project_data
    @retry(retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True)
    def update_project(self, new, diffs, user_name):
        with Session(self.engine) as session:
            apply_changes(diffs, session, new=new, endret_av=user_name)