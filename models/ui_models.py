import os
from typing import Optional, Annotated, Dict
from pydantic import BaseModel, BeforeValidator

import uuid
from datetime import datetime

from models.validators import to_datetime, convert_to_int


class PortfolioProjectUI(BaseModel):
    prosjekt_sk_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    navn: str | None = None
    oppstart: Annotated[datetime | None, BeforeValidator(to_datetime)] = None
    avdeling: str | None = None
    tiltakseier: str | None = None
    kontaktpersoner: str | None = None
    epost_kontakt: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True


class DigitaliseringStrategiUI(BaseModel):
    digitalisering_strategi_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    sammenheng_digital_strategi: str | None = None
    digital_strategi_kommentar: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True


class FinansieringUI(BaseModel):
    finansering_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
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
    er_gjeldende: bool = True
    

class FremskrittUI(BaseModel):
    fremskritt_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    fremskritt: str | None = None
    fase: str | None = None
    planlagt_ferdig: Annotated[datetime | None, BeforeValidator(to_datetime)] = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool | None = None


class MalbildeUI(BaseModel):
    malbilde_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    malbilde_1_beskrivelse: str | None = None
    malbilde_1_vurdering: str | None = None
    malbilde_2_beskrivelse: str| None = None
    malbilde_2_vurdering: str | None = None
    malbilde_3_beskrivelse: str | None = None
    malbilde_3_vurdering: str | None = None
    malbilde_4_beskrivelse: str | None = None
    malbilde_4_vurdering: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True

class ProblemstillingUI(BaseModel):
    problem_stilling_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    problem: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True


class ResursbehovUI(BaseModel):
    ressursbehov_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    estimert_budsjet_forklaring: str | None = None
    estimert_budsjet_behov: Annotated[int | None, BeforeValidator(convert_to_int)] = None
    antall_mandsverk_intern: Annotated[int | None, BeforeValidator(convert_to_int)] = None
    antall_mandsverk_ekstern: Annotated[int | None, BeforeValidator(convert_to_int)] = None
    antall_mandsverk_ekstern_betalt:Annotated[int | None, BeforeValidator(convert_to_int)] = None
    risiko_av_estimat: str | None = None
    risiko_av_estimat_tall: int | None = None
    kompetanse_som_trengs: str | None = None
    kompetanse_tilgjengelig: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True


class RessursbrukUI(BaseModel):
    ressursbruk_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    year: int | None = None
    predicted_resources: Annotated[int | None, BeforeValidator(convert_to_int)] = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True

class RisikovurderingUI(BaseModel):
    risiko_vurdering_id: uuid.UUID = uuid.uuid4()
    prosjekt_id: uuid.UUID | None = None
    vurdering: str | None = None
    sist_endret: datetime | None = None
    endret_av: str  | None = None
    er_gjeldende: bool = True


class SamarabeidUI(BaseModel):
    samarbeid_id: uuid.UUID = uuid.uuid4() 
    prosjekt_id : uuid.UUID | None = None
    samarbeid_intern: str | None = None
    samarbeid_eksternt: str | None = None
    avhengigheter_andre: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True

class TiltakUI(BaseModel):
    tiltak_id: uuid.UUID = uuid.uuid4()
    prosjekt_id : uuid.UUID | None = None
    tiltak_beskrivelse: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True

class VurderingUI(BaseModel):
    vurdering_id: uuid.UUID = uuid.uuid4()
    prosjekt_id : uuid.UUID | None = None
    gruppe: str | None = None
    pulje: int | None = None
    risiko_vurdering: str | None = None
    sist_endret: datetime | None = None
    endret_av: str | None = None
    er_gjeldende: bool = True
    mscw: str | None = None

class VurderingData(BaseModel):
    finansiering: FinansieringUI | None
    vurdering: VurderingUI | None


class ProjectData(BaseModel):
    fremskritt: Optional[FremskrittUI]
    samarabeid: Optional[SamarabeidUI]
    portfolioproject: Optional[PortfolioProjectUI]
    problemstilling: Optional[ProblemstillingUI]
    tiltak: Optional[TiltakUI]
    risikovurdering: Optional[RisikovurderingUI]
    malbilde: Optional[MalbildeUI]
    resursbehov: Optional[ResursbehovUI]
    digitaliseringstrategi: Optional[DigitaliseringStrategiUI]
    ressursbruk: Dict[int, RessursbrukUI] | None

    class Config:
        arbitrary_types_allowed = True  # allows your UI dataclasses