from typing import Any, Optional
from uuid import UUID, uuid4
import struct
from pydantic import BaseModel
from datetime import datetime, date
import urllib
import ast
from sqlmodel import SQLModel, Session, select, update
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.exc import OperationalError
from azure.identity import ClientSecretCredential
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_exponential,
    stop_after_attempt,
)
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict

from models.ui_models import (
    PortfolioProjectUI,
    FremskrittUI,
    ResursbehovUI,
    SamarabeidUI,
    ProblemstillingUI,
    TiltakUI,
    RisikovurderingUI,
    MalbildeUI,
    DigitaliseringStrategiUI,
    RessursbrukUI,
    FinansieringUI,
    VurderingUI,
    ProjectData,
    VurderingData,
    OverviewUI
)
from models.sql_models import (
    PortfolioProject,
    Fremskritt,
    Resursbehov,
    Samarabeid,
    Problemstilling,
    Tiltak,
    Risikovurdering,
    Malbilde,
    DigitaliseringStrategi,
    Ressursbruk,
    Finansiering,
    Vurdering,
    Overview
)

load_dotenv()


def prune_unchanged_fields(original_obj, modified_obj):
    """Compare original and modified ProjectData, and remove unchanged submodels."""
    for field_name, original_value in original_obj.__dict__.items():
        modified_value = getattr(modified_obj, field_name, None)

        # Skip if the modified field doesn't exist
        if modified_value is None:
            continue

        # Handle ressursbruk separately (it's a dict of year → RessursbrukUI)
        if field_name == "ressursbruk":
            new_dict = {}
            original_ressurs = getattr(original_obj, field_name, {}) or {}

            for year, modified_year_obj in modified_value.items():
                original_year_obj = original_ressurs.get(year)


                if original_year_obj is None:
                    new_dict[year] = modified_year_obj
                    continue
                
                orig_clean = clean_dict(original_year_obj)
                mod_clean = clean_dict(modified_year_obj)
                if orig_clean != mod_clean:
                    new_dict[year] = modified_year_obj
            # If nothing changed for any year, clear the entire dict
            if not new_dict:
                setattr(modified_obj, field_name, None)
            else:
                setattr(modified_obj, field_name, new_dict)
            continue

        # Compare regular dataclass models
        if isinstance(modified_value, BaseModel) and isinstance(original_value, BaseModel):
            if clean_dict(original_value) == clean_dict(modified_value):
                setattr(modified_obj, field_name, None)
    return modified_obj


def get_single_project_data(project_id: str, sql_models: dict):
    statement_dict = {}
    for schema_name, schema in sql_models.items():
        if schema_name == "ressursbruk":
            # Multiple current rows
            statement_dict[schema_name] = (
                select(schema)
                .where(schema.prosjekt_id == project_id, schema.er_gjeldende == True)
                .order_by(schema.year)
            )
        else:
            statement_dict[schema_name] = select(schema).where(
                schema.prosjekt_id == project_id, schema.er_gjeldende == True
            )
    return statement_dict


def ui_to_sqlmodel(ui_obj, sqlmodel_cls: type[SQLModel]) -> SQLModel:

    if ui_obj is None:
        return None

    if not isinstance(ui_obj, BaseModel):
        raise TypeError(f"Expected dataclass instance, got {type(ui_obj)}")

    ui_dict = ui_obj.model_dump()

    # Filter out any keys that are not defined in the SQLModel class
    sqlmodel_fields = {name for name in sqlmodel_cls.__fields__}
    filtered_data = {k: v for k, v in ui_dict.items() if k in sqlmodel_fields}

    return sqlmodel_cls(**filtered_data)

def clean_dict(d):
    IGNORED_FIELDS = {
        "sist_endret",
        "endret_av",
        "er_gjeldende",
        "prosjekt_id",
        "ressursbruk_id",
    }

    if isinstance(d,BaseModel):
        d = d.model_dump()
   
    return {k: v for k, v in d.items() if k not in IGNORED_FIELDS}

def get_single_page(engine, project_id: str, sql_models: dict):
    sql_model_dict = {}
    project_id = UUID(project_id)

    with Session(engine) as session:
        stmt_dict = get_single_project_data(project_id, sql_models)

        for sql_model_name, sql_statement in stmt_dict.items():
            if sql_model_name == "ressursbruk":
                result = session.exec(sql_statement).all()
                sql_model_dict[sql_model_name] = result or []
            else:
                result = session.exec(sql_statement).first()
                if result:
                    sql_model_dict[sql_model_name] = result
                else:
                    sql_model_dict[sql_model_name] = sql_models[sql_model_name](prosjekt_id=project_id)
    return sql_model_dict

class DBConnector:
    engine: Engine
    sql_models: dict
    ui_models: dict

    def __init__(self, engine: Engine, model_groups: dict[str, Any]):
        self.engine = engine
        self.model_groups = model_groups

    @classmethod
    def create_engine(
        cls,
        driver_name: str,
        server_name: str,
        database_name: str,
        fabric_client_id: str,
        fabric_tenant_id: str,
        fabric_client_secret: str,
    ):
        # --- Connection string (NO auth here, token comes later) ---
        connection_string = (
            "Driver={};Server=tcp:{},1433;Database={};Encrypt=yes;"
            "TrustServerCertificate=no;Connection Timeout=30; encoding=utf8"
        ).format(driver_name, server_name, database_name)

        params = urllib.parse.quote(connection_string)
        odbc_str = f"mssql+pyodbc:///?odbc_connect={params}"

        engine = create_engine(
            odbc_str, echo=False, pool_pre_ping=True, pool_recycle=3600, pool_timeout=30
        )

        credential = ClientSecretCredential(
            tenant_id=fabric_tenant_id,
            client_id=fabric_client_id,
            client_secret=fabric_client_secret,
        )  # or ClientSecretCredential if you prefer

        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            print("🔑 Requesting new Entra ID token for SQL Server...")
            token_bytes = credential.get_token(
                "https://database.windows.net/.default"
            ).token.encode("utf-16-le")
            token_struct = struct.pack(
                f"<I{len(token_bytes)}s", len(token_bytes), token_bytes
            )
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

        sql_models = {
            "fremskritt": Fremskritt,
            "samarabeid": Samarabeid,
            "portfolioproject": PortfolioProject,
            "problemstilling": Problemstilling,
            "tiltak": Tiltak,
            "risikovurdering": Risikovurdering,
            "malbilde": Malbilde,
            "resursbehov": Resursbehov,
            "digitaliseringstrategi": DigitaliseringStrategi,
            "ressursbruk": Ressursbruk,
        }
        ui_models = {
            "fremskritt": FremskrittUI,
            "samarabeid": SamarabeidUI,
            "portfolioproject": PortfolioProjectUI,
            "problemstilling": ProblemstillingUI,
            "tiltak": TiltakUI,
            "risikovurdering": RisikovurderingUI,
            "malbilde": MalbildeUI,
            "resursbehov": ResursbehovUI,
            "digitaliseringstrategi": DigitaliseringStrategiUI,
            "ressursbruk": RessursbrukUI
        }
        model_groups = {
                "project": {
                    "sql": sql_models,
                    "ui": ui_models,
                    "dataclass": ProjectData,
                },
                "vurdering": {
                    "sql": {
                        "finansiering": Finansiering,
                        "vurdering": Vurdering,
                    },
                    "ui": {
                        "finansiering": FinansieringUI,
                        "vurdering": VurderingUI,
                    },
                    "dataclass": VurderingData,
                },
            }
        
        return cls(engine, model_groups)

    def create_empty_project(self, email, prosjekt_id, group: str = "project") -> ProjectData:
        empty_populated_schemas = {}
        ui_models = self.model_groups[group]["ui"]
        dict_of_schemas = ui_models.copy()
        dict_of_schemas.pop("portfolioproject")
        for name, schema in dict_of_schemas.items():
            if name == "ressursbruk":
                empty_populated_schemas[name] = {}
            else:
                empty_populated_schemas[name] = schema(prosjekt_id=prosjekt_id)
        empty_populated_schemas["portfolioproject"] = PortfolioProjectUI(
            epost_kontakt=email, prosjekt_id=prosjekt_id
        )
        return ProjectData(**empty_populated_schemas)

    @retry(
        retry=retry_if_exception_type(OperationalError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
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
                email_in_list = f"%{email}%"
                print(email_in_list)
                stmt = select(*columns).where(
                    PortfolioProject.er_gjeldende == True,
                    PortfolioProject.epost_kontakt.like(email_in_list),
                )
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

    @retry(
        retry=retry_if_exception_type(OperationalError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def get_single_project(self, project_id: str, group: str = "project") -> ProjectData:
        sql_models = self.model_groups[group]["sql"]
        sql_model_dict = get_single_page(self.engine, project_id, sql_models)
        

        # Construct UI layer
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
            ressursbruk={r.year: RessursbrukUI(**r.dict()) for r in sql_model_dict["ressursbruk"]},  # 👈 list of UI objects
        )
        return project_data

    def has_changes(existing_obj, new_obj) -> bool:
        """Return True if there are meaningful differences between existing and new object fields."""
        if not existing_obj:
            return True  # Entirely new record

        ignored_fields = {
            "sist_endret",
            "endret_av",
            "er_gjeldende",
            "prosjekt_id",
            "ressursbruk_id",
        }

        for field_name, new_val in vars(new_obj).items():
            if field_name.startswith("_") or field_name in ignored_fields:
                continue
            if not hasattr(existing_obj, field_name):
                continue

            old_val = getattr(existing_obj, field_name)

            # Normalize datatypes (e.g., None vs empty string, float vs int)
            if (old_val is None or old_val == "") and (
                new_val is None or new_val == ""
            ):
                continue
            if str(old_val) != str(new_val):
                return True

        return False

    @retry(
        retry=retry_if_exception_type(OperationalError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def update_project(self, mod_proj: ProjectData, prosjekt_id: UUID, e_mail: str, group: str = "project"):
        org_proj = self.get_single_project(str(prosjekt_id))
        mod_proj = prune_unchanged_fields(org_proj, mod_proj)
        now = datetime.utcnow()
        ui_models = self.model_groups[group]["ui"]
        sql_models = self.model_groups[group]["sql"]
        with Session(self.engine) as session:
            objs = []

            for model_name, ui_model in ui_models.items():
                ui_obj = getattr(mod_proj, model_name)
                if ui_obj is None:
                    continue

                sql_cls = sql_models[model_name]

                # --- Handle ressursbruk specially (dict of years) ---
                if model_name == "ressursbruk":
                    for year, res_obj in ui_obj.items():
                        # Deactivate previous row only for this year
                        session.execute(
                            update(sql_cls)
                            .where(sql_cls.prosjekt_id == str(prosjekt_id).lower())
                            .where(sql_cls.year == year)
                            .where(sql_cls.er_gjeldende == True)
                            .values(er_gjeldende=False)
                        )

                        sql_obj = ui_to_sqlmodel(res_obj, sql_cls)
                        sql_obj.prosjekt_id = str(prosjekt_id).lower()
                        sql_obj.er_gjeldende = True
                        sql_obj.sist_endret = now
                        sql_obj.endret_av = e_mail
                        sql_obj.ressursbruk_id = str(uuid4())  # always new ID
                        objs.append(sql_obj)

                else:
                    # Deactivate previous record(s) for this specific model only
                    session.execute(
                        update(sql_cls)
                        .where(sql_cls.prosjekt_id == str(prosjekt_id).lower())
                        .where(sql_cls.er_gjeldende == True)
                        .values(er_gjeldende=False)
                    )

                    sql_obj = ui_to_sqlmodel(ui_obj, sql_cls)
                    sql_obj.prosjekt_id = str(prosjekt_id).lower()
                    sql_obj.er_gjeldende = True
                    sql_obj.sist_endret = now
                    sql_obj.endret_av = e_mail
                    objs.append(sql_obj)

            # ✅ Use session for both update + insert to ensure atomicity
            session.add_all(objs)
            session.commit()

    def get_overview(self):
        with Session(self.engine) as session:
            stmt = select(Overview)
            results = session.exec(stmt).all()
        return [r.dict() for r in results]
