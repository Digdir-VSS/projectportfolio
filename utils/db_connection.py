from typing import Any
import struct
from datetime import datetime
import urllib
from sqlmodel import SQLModel, Session, select, update, and_
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.exc import OperationalError
from azure.identity import ClientSecretCredential
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from dotenv import load_dotenv
from dataclasses import dataclass, is_dataclass, asdict

from utils.data_models import PortfolioProject, PortfolioProjectUI, Fremskritt, FremskrittUI, Resursbehov, ResursbehovUI, Samarabeid, SamarabeidUI, Problemstilling, ProblemstillingUI, Tiltak, TiltakUI, Risikovurdering, RisikovurderingUI, Malbilde,  MalbildeUI, DigitaliseringStrategi, DigitaliseringStrategiUI
load_dotenv()

@dataclass
class ProjectData:
    fremskritt: FremskrittUI | None
    samarabeid: SamarabeidUI | None
    portfolioproject: PortfolioProjectUI | None
    problemstilling: ProblemstillingUI | None
    tiltak: TiltakUI | None
    risikovurdering: RisikovurderingUI | None
    malbilde: MalbildeUI | None
    resursbehov: ResursbehovUI | None
    digitaliseringstrategi: DigitaliseringStrategiUI | None


def get_single_project_data(project_id: str, sql_models: dict):
    statement_dict = {}
    for schema_name, schema in sql_models.items():
        statement_dict[schema_name] = select(schema).where(
                schema.prosjekt_id == project_id, schema.er_gjeldende == True
            )
    return statement_dict
   
def ui_to_sqlmodel(ui_obj, sqlmodel_cls: type[SQLModel]) -> SQLModel:

    if ui_obj is None:
        return None

    if not is_dataclass(ui_obj):
        raise TypeError(f"Expected dataclass instance, got {type(ui_obj)}")

    ui_dict = asdict(ui_obj)

    # Filter out any keys that are not defined in the SQLModel class
    sqlmodel_fields = {name for name in sqlmodel_cls.__fields__}
    filtered_data = {k: v for k, v in ui_dict.items() if k in sqlmodel_fields}

    return sqlmodel_cls(**filtered_data)   

class DBConnector:
    engine: Engine
    sql_models: dict
    ui_models: dict

    def __init__(self, engine: Engine, sql_models: dict[str, Any], ui_models: dict[str, Any]):
        self.engine = engine
        self.sql_models = sql_models
        self.ui_models = ui_models


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
        sql_models = {"fremskritt": Fremskritt, "samarabeid": Samarabeid, "portfolioproject": PortfolioProject, "problemstilling": Problemstilling, "tiltak": Tiltak, "risikovurdering": Risikovurdering, "malbilde": Malbilde, "resursbehov": Resursbehov, "digitaliseringstrategi": DigitaliseringStrategi}
        ui_models = {"fremskritt": FremskrittUI, "samarabeid": SamarabeidUI, "portfolioproject": PortfolioProjectUI, "problemstilling": ProblemstillingUI, "tiltak": TiltakUI, "risikovurdering": RisikovurderingUI, "malbilde": MalbildeUI, "resursbehov": ResursbehovUI, "digitaliseringstrategi": DigitaliseringStrategiUI}
        return cls(engine, sql_models, ui_models)
    
    def create_empty_project(self, email, prosjekt_id):
        empty_populated_schemas = {}
        dict_of_schemas = self.ui_models.copy()
        dict_of_schemas.pop("portfolioproject")
        for name, schema in dict_of_schemas.items():
            empty_populated_schemas[name] = schema(prosjekt_id=prosjekt_id)
        empty_populated_schemas["portfolioproject"] = PortfolioProjectUI(epost_kontakt=email, prosjekt_id=prosjekt_id)
        return ProjectData(**empty_populated_schemas)

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
            stmt_dict = get_single_project_data(project_id, self.sql_models)
            for sql_model_name, sql_statement in stmt_dict.items():
                result = session.exec(sql_statement).first()
                if result:
                    sql_model_dict[sql_model_name] = result
                else: 
                    sql_model_dict[sql_model_name] = self.sql_models[sql_model_name](prosjekt_id=project_id)
        project_data = ProjectData(
            fremskritt=FremskrittUI(**sql_model_dict["fremskritt"].dict()),
            resursbehov=ResursbehovUI(**sql_model_dict["resursbehov"].dict()),
            samarabeid=SamarabeidUI(**sql_model_dict["samarabeid"].dict()),
            portfolioproject=PortfolioProjectUI(**sql_model_dict["portfolioproject"].dict()),
            tiltak=TiltakUI(**sql_model_dict["tiltak"].dict()),
            problemstilling=ProblemstillingUI(**sql_model_dict["problemstilling"].dict()),
            risikovurdering=RisikovurderingUI(**sql_model_dict["risikovurdering"].dict()),
            malbilde=MalbildeUI(**sql_model_dict["malbilde"].dict()),
            digitaliseringstrategi=DigitaliseringStrategiUI(**sql_model_dict["digitaliseringstrategi"].dict()),
        )
        return project_data
    
    @retry(retry=retry_if_exception_type(OperationalError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True)
    def update_project(self, project: ProjectData, e_mail: str):
        with Session(self.engine) as session:
            prosjekt_id = project.portfolioproject.prosjekt_id if project.portfolioproject else None

            for model_name, ui_model in self.ui_models.items():
                ui_obj = getattr(project, model_name)
                if ui_obj is None:
                    continue

                sql_cls = self.sql_models[model_name]
                print(ui_obj)
                print(sql_cls)
                sql_obj = ui_to_sqlmodel(ui_obj, sql_cls)

                # Step 1: deactivate previous rows for same prosjekt_id
                session.exec(
                    update(sql_cls)
                    .where(sql_cls.prosjekt_id == prosjekt_id)
                    .values(er_gjeldende=False)
                )

                # Step 2: set audit fields and mark as current
                sql_obj.er_gjeldende = True
                sql_obj.sist_endret = datetime.utcnow()
                sql_obj.endret_av = e_mail

                # Step 3: add to session
                session.add(sql_obj)

            # Commit once at the end
            session.commit()