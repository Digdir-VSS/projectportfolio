from sqlmodel import SQLModel, Field, Date
from nicegui import binding, ui
from datetime import date

@binding.bindable_dataclass
class PageAktivitetUI:
    prosjekt_id: str = ""
    starttidspunkt: date = date.today()
    aktivitet_navn: str = ""
    samarbeids_land: str = ""
    type_aktivitet: str = ""
    tidsbruk_for_digdir_bidrag: int = 0
    strategiske_føringer_Hovedinstruks: bool = False
    strategiske_føringer_Tildelingsbrev: bool = False
    strategiske_føringer_Digdirs_målbilde: bool = False
    strategiske_føringer_Digitaliseringsrundskriv: bool = False
    strategiske_føringer_Annet: bool = False
    budsjettbehov_for_digdir_bidrag: int = 0
    kapittelreferanse_foring: str = ""
    andre_norske_samarbeidspartner: str = ""
    digdirs_rolle_i_aktivitet: str = ""
    aktivitet_tid_fra: date = date.today()
    aktivitet_tid_til: date = date.today()


@binding.bindable_dataclass
class PageOverordnetInfoUI:
    prosjekt_id: str = ""
    starttidspunkt: date = date.today()
    initiativ_navn: str = ""
    e_post_adresse_kontakt_person: str = ""
    url_initiativ_nettside: str = ""
    hovedmålet_initiativet: str = ""
    initiative_type: str = ""
    geografiske_område: str = ""
    organisasjon_ansvar: str = ""
    fagområde_initiative: str = ""
    kontaktpunkt_overordnet_organisasjon: str = ""

@binding.bindable_dataclass
class PageLeveranseUI:
    prosjekt_id: str = ""
    starttidspunkt: date = date.today()
    leveranseområde: str = ""
    kontaktperson_for_aktivitet_in_digdir: str = ""
    avdeling_hovedansvar: str = ""
    høyrisikoområder: bool = False
    sikkerhetsmessig_vurdering: bool = False
    relevant_budskap: str = ""
    leveranse_id: str = ""

    # --- Aktører som er interessenter ---
    aktører_som_er_interessenter_Interne_i_Digdir: bool = False
    aktører_som_er_interessenter_Innbyggere: bool = False
    aktører_som_er_interessenter_Norsk_media: bool = False
    aktører_som_er_interessenter_Utenlandske_virksomheter: bool = False
    aktører_som_er_interessenter_Offentlige_statlige_virksomheter: bool = False
    aktører_som_er_interessenter_Offentlige_kommunale_virksomheter: bool = False
    aktører_som_er_interessenter_Privat_næringsliv: bool = False
    aktører_som_er_interessenter_Forskningsinstitusjoner_akademia: bool = False
    aktører_som_er_interessenter_Annet: str = ""   # free text instead of bool

    # --- Andre avdeling ansvar ---
    andre_avdeling_ansvar_FEL: bool = False
    andre_avdeling_ansvar_BOD: bool = False
    andre_avdeling_ansvar_DSS: bool = False
    andre_avdeling_ansvar_VIS: bool = False
    andre_avdeling_ansvar_KOM: bool = False
    andre_avdeling_ansvar_STL: bool = False
    andre_avdeling_ansvar_TUU: bool = False



