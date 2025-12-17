from nicegui import ui, run
from datetime import datetime, date
import ast
import json
from utils.azure_users import load_users
from models.ui_models import VurderingData
import ast, asyncio
import copy
from dataclasses import asdict, is_dataclass



def vurdering_detail(prosjekt_id: str, email: str, project: ProjectData, brukere_list):
    if new:
        project = db_connector.create_empty_project(email=email, prosjekt_id=prosjekt_id)
    else:
        project = db_connector.get_single_project(prosjekt_id)
        if not project:
            ui.label('Project not found or you do not have access to it.')
            return