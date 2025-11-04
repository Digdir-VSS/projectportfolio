import struct
import urllib
from sqlmodel import Session, select
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.exc import OperationalError
from azure.identity import ClientSecretCredential
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from dotenv import load_dotenv

from .project_loader import PortfolioProject, Fremskritt, Resursbehov, Samarabeid, Problemstilling, Tiltak, Risikovurdering, Malbilde, DigitaliseringStrategi, ProjectData, convert_list, apply_changes

load_dotenv()


def get_single_project_data(project_id: str):
    stmt = (
        select(*convert_list.values())
        .join(
            Fremskritt,
            (Fremskritt.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Fremskritt.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Samarabeid,
            (Samarabeid.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Samarabeid.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Problemstilling,
            (Problemstilling.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Problemstilling.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Tiltak,
            (Tiltak.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Tiltak.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Risikovurdering,
            (Risikovurdering.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Risikovurdering.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Malbilde,
            (Malbilde.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Malbilde.er_gjeldende == True),
            isouter=True,
        )
        .join(
            Resursbehov,
            (Resursbehov.prosjekt_id == PortfolioProject.prosjekt_id)
            & (Resursbehov.er_gjeldende == True),
            isouter=True,
        )
        .join(
            DigitaliseringStrategi,
            (DigitaliseringStrategi.prosjekt_id == PortfolioProject.prosjekt_id)
            & (DigitaliseringStrategi.er_gjeldende == True),
            isouter=True,
        )
        .where(
            PortfolioProject.prosjekt_id == project_id,
            PortfolioProject.er_gjeldende == True,
        )
    )
    return stmt

class DBConnector:
    engine: Engine

    def __init__(self, engine: Engine):
        self.engine = engine
    
    @classmethod
    def create_engine(cls, driver_name: str, server_name: str, database_name: str, fabric_client_id: str, fabric_tenant_id: str, fabric_client_secret: str):
            # --- Connection string (NO auth here, token comes later) ---
        connection_string = (
            "Driver={};Server=tcp:{},1433;Database={};Encrypt=yes;"
            "TrustServerCertificate=no;Connection Timeout=30"
        ).format(driver_name, server_name, database_name)

        params = urllib.parse.quote(connection_string)
        odbc_str = f"mssql+pyodbc:///?odbc_connect={params}"

        engine = create_engine(odbc_str, echo=True, pool_pre_ping=True, pool_recycle=3600, pool_timeout=30)

        credential = ClientSecretCredential(tenant_id=fabric_tenant_id,client_id=fabric_client_id,client_secret=fabric_client_secret)  # or ClientSecretCredential if you prefer

        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            print("🔑 Requesting new Entra ID token for SQL Server...")
            token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
            token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}
        return cls(engine)
    
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
        with Session(self.engine) as session:
            stmt = get_single_project_data(project_id)
            result = session.exec(stmt).first()
        if not result:
            return None
        
        project_data = ProjectData(
                **{alias: result[i] for i, (alias, col) in enumerate(convert_list.items())}
        )

        return project_data
    @retry(retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True)
    def update_project(self, new, diffs, user_name):
        with Session(self.engine) as session:
            apply_changes(diffs, session, new=new, endret_av=user_name)