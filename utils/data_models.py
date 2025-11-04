import os
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from nicegui import binding
from dataclasses import field

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
    er_gjeldende: bool | None = None

@binding.bindable_dataclass
class PortfolioProjectUI:
    prosjekt_sk_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    navn: str = ''
    oppstart: datetime | None = None
    avdeling: str = ''
    tiltakseier: str = ''
    kontaktpersoner: str = ''
    epost_kontakt: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool = True


class DigitaliseringStrategi(SQLModel, table=True):
    __tablename__ = "DigitaliseringStrategi"
    __table_args__ = {"schema": schema_name}

    digitalisering_strategi_id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        )
    sammenheng_digital_strategi: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class DigitaliseringStrategiUI:
    digitalisering_strategi_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    sammenheng_digital_strategi: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool = True

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
    endret_av: str | None = None
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
    endret_av: str | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class FremskrittUI:
    digitalisering_strategi_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    fremskritt: str = ''
    fase: str = ''
    planlagt_ferdig: datetime | None = None
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None


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
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class MalbildeUI:
    malbilde_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    malbilde_1_beskrivelse: str = ''
    malbilde_1_vurdering: str = ''
    malbilde_2_beskrivelse: str = ''
    malbilde_2_vurdering: str = ''
    malbilde_3_beskrivelse: str = ''
    malbilde_3_vurdering: str = ''
    malbilde_4_beskrivelse: str = ''
    malbilde_4_vurdering: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None

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
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class ProblemstillingUI:
    problem_stilling_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    problem: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None

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
    endret_av: str | None = None
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
    endret_av: str | None = None
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class ResursbehovUI:
    ressursbehov_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default=uuid.uuid4)
    estimert_budsjet_forklaring: str = ''
    estimert_budsjet_behov: float | None = None
    antall_mandsverk_intern: float | None = None
    antall_mandsverk_ekstern: float | None = None
    antall_mandsverk_ekstern_betalt: float | None = None
    risiko_av_estimat: str = ''
    risiko_av_estimat_tall: float | None = None
    kompetanse_som_trengs: str = ''
    kompetanse_tilgjengelig: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None

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
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class RisikovurderingUI:
    risiko_vurdering_id: uuid.UUID = field(default=uuid.uuid4)
    prosjekt_id: uuid.UUID = field(default=uuid.uuid4)
    vurdering: str = ''
    sist_endret: datetime | None = None
    endret_av: str  = ''
    er_gjeldende: bool | None = None

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
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class SamarabeidUI:
    samarbeid_id: uuid.UUID = field(default=uuid.uuid4),
    prosjekt_id : uuid.UUID = field(default=uuid.uuid4),
    samarbeid_intern: str = ''
    samarbeid_eksternt: str = ''
    avhengigheter_andre: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None

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
    er_gjeldende: bool | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )

@binding.bindable_dataclass
class TiltakUI:
    tiltak_id: uuid.UUID = field(default=uuid.uuid4),
    prosjekt_id : uuid.UUID = field(default=uuid.uuid4),
    tiltak_beskrivelse: str = ''
    sist_endret: datetime | None = None
    endret_av: str = ''
    er_gjeldende: bool | None = None

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
    endret_av: str | None = None
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
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool | None = None
    mscw: str | None = None
    prosjekt_id : uuid.UUID = Field(
        foreign_key=f"{schema_name}.PortfolioProject.prosjekt_id",  # 👈 link to users
    )
