import os
import struct
import urllib
from sqlmodel import SQLModel, Field, Session, select, Relationship
from sqlalchemy import create_engine, event, Column
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient

import uuid
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from collections import Counter
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()
# --- Azure creds ---
driver_name = "{ODBC Driver 18 for SQL Server}"
server_name = os.getenv("SERVER")      # e.g. "xxx.datawarehouse.fabric.microsoft.com"
database_name = os.getenv("DATABASE")

# --- Connection string (NO auth here, token comes later) ---
connection_string = (
    "Driver={};Server=tcp:{},1433;Database={};Encrypt=yes;"
    "TrustServerCertificate=no;Connection Timeout=30"
).format(driver_name, server_name, database_name)

params = urllib.parse.quote(connection_string)
odbc_str = f"mssql+pyodbc:///?odbc_connect={params}"

# --- Get SQLAlchemy engine ---
engine = create_engine(odbc_str, echo=True)

# --- Token injection hook ---
azure_client_id = os.getenv("AZURE_CLIENT_ID")
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url=os.getenv("KEY_VAULT_URL"), credential=credential
)
CLIENT_SECRET = client.get_secret(os.getenv("CLIENT_SECRET")).value
# client_secret_new = client.get_secret(os.getenv("CLIENT_SECRET")).value
azure_client_secret = client.get_secret(os.getenv("AZURE_CLIENT_SECRET")).value
azure_tenant_id = os.getenv("AZURE_TENANT_ID")
credential = ClientSecretCredential(tenant_id=azure_tenant_id,client_id=azure_client_id,client_secret=azure_client_secret)  # or ClientSecretCredential if you prefer

@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    print("🔑 Requesting new Entra ID token for SQL Server...")
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

# --- SQLModel tables ---

schema_name = os.getenv("SCHEMA")
class PortfolioProject(SQLModel, table=True):
    __tablename__ = "PortfolioProject"
    __table_args__ = {"schema": schema_name}
    prosjekt_sk_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    prosjekt_id: uuid.UUID
    navn: str | None = None
    oppstart: datetime | None = None
    avdeling: str | None = None
    kontaktpersoner: str | None = None
    epost_kontakt: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None


class DigitaliseringStrategi(SQLModel, table=True):
    __tablename__ = "DigitaliseringStrategi"
    __table_args__ = {"schema": schema_name}

    digitalisering_strategi_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    sammenheng_digital_strategi: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Finansiering(SQLModel, table=True):
    __tablename__ = "Finansering"
    __table_args__ = {"schema": schema_name}

    finansering_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    potensiell_finansering: float | None = None
    mnd_verk: float | None = None
    vedtatt_tildeling: float | None = None
    prognose_innmeldt: float | None = None
    prognose_tildelt: float | None = None
    tentatitv_forpliktelse: float | None = None
    estimert_budsjettbehov: float | None = None
    usikkerhet_estimat: str | None = None
    risiko_av_estimat_tall: float | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Fremskritt(SQLModel, table=True):
    __tablename__ = "Fremskritt"
    __table_args__ = {"schema": schema_name}

    fremskritt_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    fremskritt: str | None = None
    fase: str | None = None
    planlagt_ferdig: datetime | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Malbilde(SQLModel, table=True):
    __tablename__ = "Malbilde"
    __table_args__ = {"schema": schema_name}

    malbilde_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    malbilde_1_beskrivelse: str | None = None
    malbilde_1_vurdering: str | None = None
    malbilde_2_beskrivelse: str | None = None
    malbilde_2_vurdering: str | None = None
    malbilde_3_beskrivelse: str | None = None
    malbilde_3_vurdering: str | None = None
    malbilde_4_beskrivelse: str | None = None
    malbilde_4_vurdering: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Problemstilling(SQLModel, table=True):
    __tablename__ = "Problemstilling"
    __table_args__ = {"schema": schema_name}

    problem_stilling_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    problem: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Rapportering(SQLModel, table=True):
    __tablename__ = "Rapportering"
    __table_args__ = {"schema": schema_name}

    rapportering_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    email_rapportering: str | None = None
    viktige_endringer_kommentar: str | None = None
    konsulent_anskaffet: str | None = None
    konsulent_anskaffet_kommentar: str | None = None
    risiko_rapportert: str | None = None
    risiko_rapportert_begrunnet: str | None = None
    avhengigheter_rapportert: str | None = None
    risiko_rapportert_tall: float | None = None
    viktige_endringer: float | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )
class Resursbehov(SQLModel, table=True):
    __tablename__ = "Ressursbehov"
    __table_args__ = {"schema": schema_name}

    ressursbehov_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    estimert_budsjet_forklaring: str | None = None
    estimert_budsjet_behov: float | None = None
    antall_mandsverk_intern: float | None = None
    antall_mandsverk_ekstern: float | None = None
    antall_mandsverk_ekstern_betalt: float | None = None
    risiko_av_estimat: str | None = None
    risiko_av_estimat_tall: float | None = None
    kompetanse_som_trengs: str | None = None
    kompetanse_tilgjengelig: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Risikovurdering(SQLModel, table=True):
    __tablename__ = "Risikovurdering"
    __table_args__ = {"schema": schema_name}

    risiko_vurdering_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    vurdering: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Samarabeid(SQLModel, table=True):
    __tablename__ = "Samarbeid"
    __table_args__ = {"schema": schema_name}

    samarbeid_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    samarbeid_intern: str | None = None
    samarbeid_eksternt: str | None = None
    avhengigheter_andre: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Tiltak(SQLModel, table=True):
    __tablename__ = "Tiltak"
    __table_args__ = {"schema": schema_name}

    tiltak_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    tiltak_beskrivelse: str | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class UnderstøtteTildelingsbrev(SQLModel, table=True):
    __tablename__ = "UnderstøtteTildelingsbrev"
    __table_args__ = {"schema": schema_name}

    strategisk_forankring_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    mål_1_beskrivelse: str | None = None
    mål_2_beskrivelse: str | None = None
    mål_3_beskrivelse: str | None = None
    mål_1: float | None = None
    mål_2: float | None = None
    mål_3: float | None = None
    sist_endret: datetime | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Vurdering(SQLModel, table=True):
    __tablename__ = "Vurdering"
    __table_args__ = {"schema": schema_name}

    vurdering_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
    )
    gruppe: str | None = None
    pulje: int | None = None
    risiko_vurdering: str | None = None
    sist_endret: datetime
    er_gjeldende: bool | None = None
    mscw: str | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class ProjectData(BaseModel):
    prosjekt_id: UUID
    date_modified: Optional[datetime]
    navn_tiltak: Optional[str]
    kontaktperson: Optional[str]
    avdeling: Optional[str]
    fase_tiltak: Optional[str]
    oppstart_tid: Optional[datetime]
    ferdig_tid: Optional[datetime]
    samarbeid_intern: Optional[str]
    samarbeid_eksternt: Optional[str]
    avhengigheter_andre: Optional[str]
    problemstilling: Optional[str]
    beskrivelse: Optional[str]
    risiko: Optional[str]
    malbilde_1_beskrivelse: Optional[str]
    malbilde_2_beskrivelse: Optional[str]
    malbilde_3_beskrivelse: Optional[str]
    malbilde_4_beskrivelse: Optional[str]
    kompetanse_behov: Optional[str]
    kompetanse_internt: Optional[str]
    månedsverk_interne: Optional[int]
    månedsverk_eksterne: Optional[int]
    månedsverk_eksterne_2025: Optional[int]
    estimert_behov_utover_driftsrammen: Optional[float]
    estimert_behov_forklaring: Optional[str]
    hvor_sikkert_estimatene: Optional[str]
    sammenheng_med_digitaliseringsstrategien_mm: Optional[str]
    eier_epost: str

convert_list = {"prosjekt_id": PortfolioProject.prosjekt_id,
"date_modified": PortfolioProject.sist_endret,
"navn_tiltak" : PortfolioProject.navn,
"kontaktperson"	: PortfolioProject.kontaktpersoner,
"avdeling" : PortfolioProject.avdeling,
"fase_tiltak": Fremskritt.fase,
"oppstart_tid": PortfolioProject.oppstart,
"ferdig_tid": Fremskritt.planlagt_ferdig,
"samarbeid_intern": Samarabeid.samarbeid_intern,
"samarbeid_eksternt": Samarabeid.samarbeid_eksternt,
"avhengigheter_andre": Samarabeid.avhengigheter_andre,
"problemstilling": Problemstilling.problem,
"beskrivelse": Tiltak.tiltak_beskrivelse,
"risiko": Risikovurdering.vurdering,
"malbilde_1_beskrivelse": Malbilde.malbilde_1_beskrivelse,
"malbilde_2_beskrivelse": Malbilde.malbilde_2_beskrivelse,
"malbilde_3_beskrivelse": Malbilde.malbilde_3_beskrivelse,
"malbilde_4_beskrivelse": Malbilde.malbilde_4_beskrivelse,
"kompetanse_behov": Resursbehov.kompetanse_som_trengs,
"kompetanse_internt": Resursbehov.kompetanse_tilgjengelig,
"månedsverk_interne": Resursbehov.antall_mandsverk_intern,
"månedsverk_eksterne": Resursbehov.antall_mandsverk_ekstern,
"månedsverk_eksterne_2025": Resursbehov.antall_mandsverk_ekstern_betalt,
"estimert_behov_utover_driftsrammen": Resursbehov.estimert_budsjet_behov,
"estimert_behov_forklaring": Resursbehov.estimert_budsjet_forklaring,	
"hvor_sikkert_estimatene": Resursbehov.risiko_av_estimat,
"sammenheng_med_digitaliseringsstrategien_mm": DigitaliseringStrategi.sammenheng_digital_strategi,
"eier_epost": PortfolioProject.epost_kontakt}


convert_list_rapport = {"prosjekt_id": Rapportering.prosjekt_id,
"sist_levert": Rapportering.sist_endret,
"email_rapportert": Rapportering.email_rapportering,
"viktige_endringer": Rapportering.viktige_endringer,
"viktige_endringer_kommentar": Rapportering.viktige_endringer_kommentar,
"fase_rapportering": Fremskritt.fase,
"fremskritt_rapportering": Fremskritt.fremskritt,
"fremskritt_rapportering_kommentar": Rapportering.viktige_endringer_kommentar,
"konsulent_anskaffet": Rapportering.konsulent_anskaffet,
"konsulent_anskaffet_kommentar": Rapportering.konsulent_anskaffet_kommentar,
"risiko_rapportert": Rapportering.risiko_rapportert,
"risiko_rapportert_tall": Rapportering.risiko_rapportert_tall,
"risiko_rapportert_begrunnet": Rapportering.risiko_rapportert_begrunnet,
"avhengigheter_rapportert": Rapportering.avhengigheter_rapportert
}

field_to_table_col = {"prosjekt_id": (PortfolioProject,PortfolioProject.prosjekt_id),
"date_modified": (PortfolioProject,PortfolioProject.sist_endret),
"navn_tiltak" : (PortfolioProject,PortfolioProject.navn),
"kontaktperson"	: (PortfolioProject,PortfolioProject.kontaktpersoner),
"avdeling" : (PortfolioProject,PortfolioProject.avdeling),
"fase_tiltak": (Fremskritt,Fremskritt.fase),
"oppstart_tid": (PortfolioProject,PortfolioProject.oppstart),
"ferdig_tid": (Fremskritt,Fremskritt.planlagt_ferdig),
"samarbeid_intern": (Samarabeid,Samarabeid.samarbeid_intern),
"samarbeid_eksternt": (Samarabeid,Samarabeid.samarbeid_eksternt),
"avhengigheter_andre": (Samarabeid,Samarabeid.avhengigheter_andre),
"problemstilling": (Problemstilling,Problemstilling.problem),
"beskrivelse": (Tiltak,Tiltak.tiltak_beskrivelse),
"risiko": (Risikovurdering,Risikovurdering.vurdering),
"malbilde_1_beskrivelse": (Malbilde,Malbilde.malbilde_1_beskrivelse),
"malbilde_2_beskrivelse": (Malbilde,Malbilde.malbilde_2_beskrivelse),
"malbilde_3_beskrivelse": (Malbilde,Malbilde.malbilde_3_beskrivelse),
"malbilde_4_beskrivelse": (Malbilde,Malbilde.malbilde_4_beskrivelse),
"kompetanse_behov": (Resursbehov,Resursbehov.kompetanse_som_trengs),
"kompetanse_internt": (Resursbehov,Resursbehov.kompetanse_tilgjengelig),
"månedsverk_interne": (Resursbehov,Resursbehov.antall_mandsverk_intern),
"månedsverk_eksterne": (Resursbehov,Resursbehov.antall_mandsverk_ekstern),
"månedsverk_eksterne_2025": (Resursbehov,Resursbehov.antall_mandsverk_ekstern_betalt),
"estimert_behov_utover_driftsrammen": (Resursbehov,Resursbehov.estimert_budsjet_behov),
"estimert_behov_forklaring": (Resursbehov,Resursbehov.estimert_budsjet_forklaring),    
"hvor_sikkert_estimatene": (Resursbehov,Resursbehov.risiko_av_estimat),
"sammenheng_med_digitaliseringsstrategien_mm": (DigitaliseringStrategi,DigitaliseringStrategi.sammenheng_digital_strategi),
"eier_epost": (PortfolioProject,PortfolioProject.epost_kontakt)}

class JustProject(SQLModel):
    prosjekt_id: UUID
    navn: Optional[str]
    avdeling: Optional[str]
    kontaktpersoner: Optional[str]
    epost_kontakt: str

project_names = {"prosjekt_id": PortfolioProject.prosjekt_id,
                 "navn_tiltak" : PortfolioProject.navn,
                 "avdeling" : PortfolioProject.avdeling,
                 "kontaktperson"	: PortfolioProject.kontaktpersoner,
                 "epost_kontakt": PortfolioProject.epost_kontakt}

table_pk_map = {
    PortfolioProject: "prosjekt_sk_id",
    DigitaliseringStrategi: "digitalisering_strategi_id",
    Finansiering: "finansering_id",
    Fremskritt: "fremskritt_id",
    Problemstilling: "problem_stilling_id",
    Rapportering: "rapportering_id",
    Resursbehov: "ressursbehov_id",
    Risikovurdering: "risiko_vurdering_id",
    Samarabeid: "samarbeid_id",
    Tiltak: "tiltak_id",
    Malbilde: "malbilde_id",
    Vurdering: "vurdering_id",
}
def create_empty_project(eier_epost: str, pid: UUID) -> ProjectData:
    return ProjectData(
        prosjekt_id=pid,
        date_modified=None,
        navn_tiltak="",
        kontaktperson="",
        avdeling=None,
        fase_tiltak=None,
        oppstart_tid=None,
        ferdig_tid=None,
        samarbeid_intern="",
        samarbeid_eksternt="",
        avhengigheter_andre="",
        problemstilling="",
        beskrivelse="",
        risiko="",
        malbilde_1_beskrivelse=None,
        malbilde_2_beskrivelse=None,
        malbilde_3_beskrivelse=None,
        malbilde_4_beskrivelse=None,
        kompetanse_behov="",
        kompetanse_internt=None,
        månedsverk_interne=None,
        månedsverk_eksterne=None,
        månedsverk_eksterne_2025=None,
        estimert_behov_utover_driftsrammen=None,
        estimert_behov_forklaring="",
        hvor_sikkert_estimatene="",
        sammenheng_med_digitaliseringsstrategien_mm="",
        eier_epost=eier_epost,
    )

def get_projects(session, email: str | None = None):
    columns = [
        PortfolioProject.prosjekt_id,
        PortfolioProject.navn,
        PortfolioProject.avdeling,
        PortfolioProject.kontaktpersoner,
        PortfolioProject.epost_kontakt,
    ]
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
            "kontaktpersoner": r[3],
            "epost_kontakt": r[4],
        }
        for r in results
    ]
    # projects = [
    #     JustProject(
    #         **{alias: row[i] for i, (alias, col) in enumerate(project_names.items())}
    #     )
    #     for row in results
    # ]
    # return projects
    # return results
def get_single_project_data(session, project_id: str):
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

    result = session.exec(stmt).first()
    if not result:
        return None

    # Build a ProjectData instance directly from the first row
    project_data = ProjectData(
        **{alias: result[i] for i, (alias, col) in enumerate(convert_list.items())}
    )

    return project_data
# def get_single_project_data(session, project_id: str):
#     stmt = (
#         select(*convert_list.values())
#         .join(Fremskritt, Fremskritt.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(Samarabeid, Samarabeid.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(Problemstilling, Problemstilling.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(Tiltak, Tiltak.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(Risikovurdering, Risikovurdering.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(UnderstøtteTildelingsbrev, UnderstøtteTildelingsbrev.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(Resursbehov, Resursbehov.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .join(DigitaliseringStrategi, DigitaliseringStrategi.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
#         .where(
#             PortfolioProject.prosjekt_id == project_id,
#             PortfolioProject.er_gjeldende == True,
#             DigitaliseringStrategi.er_gjeldende == True,
#             Fremskritt.er_gjeldende == True,
#             Problemstilling.er_gjeldende == True,
#             Resursbehov.er_gjeldende == True,
#             Risikovurdering.er_gjeldende == True,
#             Samarabeid.er_gjeldende == True,
#             Tiltak.er_gjeldende == True,
#             UnderstøtteTildelingsbrev.er_gjeldende == True,
#         )
#     )

#     # only filter by email if it’s provided
#     # if email:
#     #     stmt = stmt.where(PortfolioProject.epost_kontakt == email)

#     result = session.exec(stmt).first()
#     if not result:
#         return None

#     # Build a ProjectData instance directly from the first row
#     project_data = ProjectData(
#         **{alias: result[i] for i, (alias, col) in enumerate(convert_list.items())}
#     )

#     return project_data
def get_project_data(session, email: str | None = None):
    stmt = (
        select(*convert_list.values())
        .join(Fremskritt, Fremskritt.prosjekt_id == PortfolioProject.prosjekt_id, isouter=False)
        .join(Samarabeid, Samarabeid.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
        .join(Problemstilling, Problemstilling.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
        .join(Tiltak, Tiltak.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
        .join(Risikovurdering, Risikovurdering.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
        .join(Malbilde, Malbilde.prosjekt_id == Malbilde.prosjekt_id, isouter=True)
        .join(Resursbehov, Resursbehov.prosjekt_id == PortfolioProject.prosjekt_id, isouter=False)
        .join(DigitaliseringStrategi, DigitaliseringStrategi.prosjekt_id == PortfolioProject.prosjekt_id, isouter=True)
        .where(
            PortfolioProject.er_gjeldende == True,
            DigitaliseringStrategi.er_gjeldende == True,
            Fremskritt.er_gjeldende == True,
            Problemstilling.er_gjeldende == True,
            Resursbehov.er_gjeldende == True,
            Risikovurdering.er_gjeldende == True,
            Samarabeid.er_gjeldende == True,
            Tiltak.er_gjeldende == True,
            Malbilde.er_gjeldende == True,
        )
    )

    # only filter by email if it’s provided
    if email:
        stmt = stmt.where(PortfolioProject.epost_kontakt == email)

    results = session.exec(stmt).all()
    projects = [
        ProjectData(
            **{alias: row[i] for i, (alias, col) in enumerate(convert_list.items())}
        )
        for row in results
    ]
    return projects

def normalize_value(val):
    """Normalize text values to avoid false differences."""
    if isinstance(val, str):
        # Strip leading/trailing whitespace and normalize newlines
        return val.strip().replace('\r\n', '\n').replace('\r', '\n')
    return val

def diff_projects(
    original: List[Any],
    edited: List[Any],
    key_field: str = "prosjekt_id",
    include_change_type: bool = False,
) -> List[dict]:
    """
    Compare two lists of Pydantic/SQLModel objects by the given key_field (default 'prosjekt_id').

    Returns a list of dicts:
      - For modified rows: {"prosjekt_id": <UUID>, "changes": {field: {"old":..., "new":...}}, (optional) "change_type": "modified"}
      - For newly added rows: {"prosjekt_id": <UUID>, "changes": {...}, (optional) "change_type": "added"}
      - For removed rows (present in original but not in edited): {"prosjekt_id": <UUID>, "changes": None, (optional) "change_type": "removed", "old_record": <original_obj>}

    Notes:
      - Compares fields present in either original or edited model (union).
      - If duplicate prosjekt_id values exist in either list, raises ValueError to avoid ambiguous matches.
    """

    # === 1) sanity: check duplicates ===
    def _find_dupes(lst):
        keys = [getattr(x, key_field) for x in lst]
        return [k for k, c in Counter(keys).items() if c > 1]

    dup_orig = _find_dupes(original)
    dup_edit = _find_dupes(edited)
    if dup_orig or dup_edit:
        raise ValueError(
            f"Duplicate {key_field} found in input lists. "
            f"original duplicates: {dup_orig}, edited duplicates: {dup_edit}"
        )

    # === 2) build maps by prosjekt_id ===
    orig_map = {getattr(o, key_field): o for o in original}
    edit_map = {getattr(e, key_field): e for e in edited}

    results = []

    # === 3) handle added and modified (iterate edited) ===
    for pid, e in edit_map.items():
        o = orig_map.get(pid)
        # determine field names to compare: union of model_fields if available, else __dict__ keys
        keys = set()
        if hasattr(e, "model_fields"):
            keys.update(e.model_fields.keys())
        else:
            keys.update(k for k in vars(e).keys() if not k.startswith("_"))

        if o is not None:
            if hasattr(o, "model_fields"):
                keys.update(o.model_fields.keys())
            else:
                keys.update(k for k in vars(o).keys() if not k.startswith("_"))

        # compute diffs
        diffs = {}
        for field in keys:
            old = getattr(o, field, None) if o is not None else None
            new = getattr(e, field, None)
            old_norm = normalize_value(old)
            new_norm = normalize_value(new)
            if old_norm != new_norm:
                diffs[field] = {"old": old, "new": new}

        if diffs:
            entry = {"prosjekt_id": pid, "changes": diffs}
            if include_change_type:
                entry["change_type"] = "modified" if o is not None else "added"
            results.append(entry)

    # === 4) handle removed ===
    for pid, o in orig_map.items():
        if pid not in edit_map:
            entry = {"prosjekt_id": pid, "changes": None}
            if include_change_type:
                entry["change_type"] = "removed"
                entry["old_record"] = o
            results.append(entry)

    return results


from collections import defaultdict
def apply_changes(diffs, session, new=False):
    for diff in diffs:
        prosjekt_id = str(diff["prosjekt_id"]).lower()
        changes = diff["changes"]

        # Group changes by table
        changes_by_table = defaultdict(dict)
        for field, change in changes.items():
            table_cls, col_attr = field_to_table_col[field]
            changes_by_table[table_cls][field] = change

        for table_cls, table_changes in changes_by_table.items():
            new_row_data = {}

            if not new:
                # Find current active row
                stmt = select(table_cls).where(
                    table_cls.prosjekt_id == prosjekt_id,
                    table_cls.er_gjeldende == True
                ).with_for_update()
                current = session.exec(stmt).one_or_none()

                if current:
                    # Mark old row as inactive
                    current.er_gjeldende = False
                    session.add(current)
                    session.flush()
                    # Copy all old values
                    new_row_data = (
                        current.dict() if hasattr(current, "dict") else current.__dict__.copy()
                    )

                    # Clean up
                    pk_col = table_pk_map[table_cls]
                    new_row_data.pop(pk_col, None)
                    new_row_data[pk_col] = str(uuid.uuid4()).lower()
                    new_row_data["sist_endret"] = datetime.utcnow()
                    new_row_data["er_gjeldende"] = True

                else:
                    # No current row exists — create new one
                    new_row_data = {
                        "prosjekt_id": prosjekt_id,
                        "er_gjeldende": True,
                        "sist_endret": datetime.utcnow(),
                    }

                    pk_col = table_pk_map[table_cls]
                    new_row_data[pk_col] = str(uuid.uuid4()).lower()

                    if table_cls == PortfolioProject:
                        # skip if missing portfolio project
                        print(f"⚠️ No current row found for {table_cls.__tablename__}, prosjekt_id={prosjekt_id}")
                        continue

            else:
                # new project entirely
                new_row_data = {
                    col.name: None for col in table_cls.__table__.columns
                }
                pk_col = table_pk_map[table_cls]
                new_row_data[pk_col] = str(uuid.uuid4()).lower()
                new_row_data["prosjekt_id"] = prosjekt_id
                new_row_data["sist_endret"] = datetime.utcnow()
                new_row_data["er_gjeldende"] = True

            # Apply changed values
            for field, change in table_changes.items():
                _, col_attr = field_to_table_col[field]
                col_name = getattr(col_attr, "key", None) or field
                new_row_data[col_name] = change["new"]

            # Add single new row per table
            new_row = table_cls(**new_row_data)
            session.add(new_row)

        session.commit()

# def apply_changes(diffs, session, new = False):
#     for diff in diffs:
#         prosjekt_id = str(diff["prosjekt_id"]).lower()
#         changes = diff["changes"]

#         # 1️⃣ Group changes by table
#         changes_by_table = defaultdict(dict)
#         for field, change in changes.items():
#             table_cls, col_attr = field_to_table_col[field]
#             changes_by_table[table_cls][field] = change

#         # 2️⃣ Apply updates per table
#         for table_cls, table_changes in changes_by_table.items():
#             new_row_data = {}
#             if not new:
#                 stmt = select(table_cls).where(
#                     table_cls.prosjekt_id == prosjekt_id,
#                     table_cls.er_gjeldende == True
#                 )
#                 current = session.exec(stmt).one_or_none()
            
#                 if current:    
#                     # Mark old row as not current
#                     current.er_gjeldende = False
#                     session.add(current)

#                     # Copy current row values
#                     new_row_data = current.dict() if hasattr(current, "dict") else current.__dict__.copy()
#                     pk_col = table_pk_map[table_cls]
#                     new_row_data.pop(pk_col, None)  # remove surrogate key
#                     new_row_data[pk_col] = str(uuid.uuid4()).lower()  # or let DB autogenerate
#                     new_row_data["sist_endret"] = datetime.utcnow()
#                     new_row_data["er_gjeldende"] = True

#                     # Apply all changes for this table
#                     for field, change in table_changes.items():
#                         _, col_attr = field_to_table_col[field]
#                         col_name = col_attr.key  # SQLAlchemy column name
#                         new_row_data[col_name] = change["new"]

#                     # Insert new row
#                     new_row = table_cls(**new_row_data)
#                     session.add(new_row)
#                 elif not current:
#                     if table_cls == PortfolioProject:
#                         print(f"⚠️ No current row found for {table_cls.__tablename__}, prosjekt_id={prosjekt_id}")
#                         continue
#                     new_row_data = {
#                     "prosjekt_id": prosjekt_id,
#                     "er_gjeldende": True,
#                     "sist_endret": datetime.utcnow(),}

#                     # Apply all changed values for this table
#                     for field, change in table_changes.items():
#                         _, col_attr = field_to_table_col[field]
#                         col_name = col_attr.key
#                         new_row_data[col_name] = change["new"]

#                     # If table has its own surrogate PK, generate one
#                     pk_col = table_pk_map[table_cls]
#                     new_row_data[pk_col] = str(uuid.uuid4()).lower()

#                     new_row = table_cls(**new_row_data)
#                     session.add(new_row)
#             else:
#                 # new project: create an empty/new row for this table
#                 new_row_data = {}
#                 for col in table_cls.__table__.columns:
#                     # Initialize columns with None (or column.default if you want)
#                     new_row_data[col.name] = None

#                 pk_col = table_pk_map[table_cls]
#                 new_row_data[pk_col] = str(uuid.uuid4()).lower()
#                 new_row_data["prosjekt_id"] = prosjekt_id
#                 new_row_data["sist_endret"] = datetime.utcnow()
#                 new_row_data["er_gjeldende"] = True

#             # Apply all changes for this table
#             for field, change in table_changes.items():
#                 _, col_attr = field_to_table_col[field]
#                 # col_attr is SQLAlchemy InstrumentedAttribute; .key is the column name
#                 col_name = getattr(col_attr, "key", None) or getattr(col_attr, "name", None) or field
#                 new_row_data[col_name] = change["new"]

#             # Create object and insert
#             new_row = table_cls(**new_row_data)
#             session.add(new_row)

#         session.commit()

def update_project_from_diffs(project: ProjectData, diffs: list) -> ProjectData:
    """
    Update a ProjectData instance in memory using a diff list from diff_projects.

    Only applies changes belonging to this project's prosjekt_id.
    """
    for diff in diffs:
        if isinstance(diff.get("prosjekt_id"), UUID) and diff["prosjekt_id"] == project.prosjekt_id:
            for field, change in diff.get("changes", {}).items():
                setattr(project, field, change["new"])
    return project