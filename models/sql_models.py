import os
from sqlmodel import SQLModel, Field
from sqlalchemy import Column

import uuid
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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
    tiltakseier: str | None = None
    kontaktpersoner: str | None = None
    epost_kontakt: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False


class DigitaliseringStrategi(SQLModel, table=True):
    __tablename__ = "DigitaliseringStrategi"
    __table_args__ = {"schema": schema_name}

    digitalisering_strategi_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    sammenheng_digital_strategi: str | None = None
    digital_strategi_kommentar: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    potensiell_finansering: int | None = None
    mnd_verk: int | None = None
    vedtatt_tildeling: int | None = None
    prognose_innmeldt: int | None = None
    prognose_tildelt: int | None = None
    tentatitv_forpliktelse: int | None = None
    estimert_budsjettbehov: int | None = None
    usikkerhet_estimat: str | None = None
    risiko_av_estimat_tall: int | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    risiko_rapportert_tall: int | None = None
    viktige_endringer: int | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    estimert_budsjet_behov: int | None = None
    antall_mandsverk_intern: int | None = None
    antall_mandsverk_ekstern: int | None = None
    antall_mandsverk_ekstern_betalt: int | None = None
    risiko_av_estimat: str | None = None
    risiko_av_estimat_tall: int | None = None
    kompetanse_som_trengs: str | None = None
    kompetanse_tilgjengelig: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Ressursbruk(SQLModel, table=True):
    __tablename__ = "Ressursbruk"
    __table_args__ = {"schema": schema_name}

    ressursbruk_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    year: int | None = None
    predicted_resources: int | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    mål_1: int | None = None
    mål_2: int | None = None
    mål_3: int | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
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
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = False
    mscw: str | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

class Overview(SQLModel, table=True):
    __tablename__ = "vw_oversikt"
    __table_args__ = {"schema": schema_name}
    prosjekt_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    navn: str | None = None
    avdeling: str | None = None
    fase: str | None = None
    planlagt_ferdig: datetime | None = None
    fremskritt_status: str | None = None
    estimert_budsjet_behov: int | None = None
    antall_mandsverk_intern: int | None = None
    antall_mandsverk_ekstern: int | None = None
    estimert_bruk_2025: int | None = None
    estimert_bruk_2026: int | None = None   
    estimert_bruk_2027: int | None = None   