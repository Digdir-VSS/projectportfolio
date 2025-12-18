from typing import List
from nicegui import ui
from dataclasses import fields

from models.ui_models import OverviewUI

def create_columns(overview_fields: List[str]):
    columns = []
    for field_name in overview_fields:
            
            if field_name == "prosjekt_id":
                 columns.append({
                "name": "prosjekt_id", 
                "label": "",       
                "field": "__actions",
                "sortable": False,
                "align": "left",
                "headerClasses": "hidden",
            })
            elif field_name == "navn":
                 columns.append({
                    "name": field_name,
                    "label": field_name.replace("_", " ").title(),
                    "field": field_name,
                    "sortable": True,
                    "align": "left",
                    "classes": "break-words whitespace-normal",
                    "headerClasses": "break-words whitespace-normal",
                })
            else:
                columns.append({
                    "name": field_name,
                    "label": field_name.replace("_", " ").title(),
                    "field": field_name,
                    "sortable": True,
                    "align": "left",
                    "classes": "break-words whitespace-normal" if field_name == "navn" else "",
                    "headerClasses": "break-words whitespace-normal" if field_name == "navn" else "",
                })

    return columns



def overview_page(overview: List[OverviewUI]):

    with ui.column().classes("w-full gap-2"):

        columns = create_columns(OverviewUI.model_fields)

        rows = [
            {**prosjekt.model_dump()}
            for prosjekt in overview
        ]
        table = ui.table(
            columns=columns,
            rows=rows,
            row_key="prosjekt_id",
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
                "sortable": True,
                "filterable": True,
            },
        ).classes("w-full table-fixed")

    table.add_slot(
        "header",
        r""" <q-tr :props="props" class="bg-gray-200"> <q-th auto-width class="bg-gray-200"></q-th> <q-th v-for="col in props.cols" :key="col.name" :props="props" class="bg-gray-200 text-lg font-semibold"> {{ col.label }} </q-th> </q-tr> """,
    )
    table.add_slot(
    "body-cell-prosjekt_id",
    r"""
    <q-td auto-width>
        <q-btn
            size="sm"
            color="primary"
            round
            dense
            icon="edit"
            @click="location.href = '/project/' + props.row.prosjekt_id"
        />
    </q-td>
    """,
)   
    table.add_slot(
    "body-cell-planlagt_ferdig",
    r"""
    <q-td :props="props">
        {{ props.value ? new Date(props.value).toLocaleDateString() : '' }}
    </q-td>
    """
)

    table.add_slot(
        "body-cell-fase",
        r"""
        <q-td :props="props">
            <q-badge
                :color="
                    props.value === 'Konsept' ? 'blue' :
                    props.value === 'Planlegging' ? 'purple' :
                    props.value === 'Gjennomføring' ? 'green' :
                    props.value === 'Problem / idé' ? 'red' :
                    'grey'
                "
                outline
            >
                {{ props.value }}
            </q-badge>
        </q-td>
        """
    )
    table.add_slot(
        "body-cell-fremskritt_status",
        r"""
        <q-td :props="props">
            <q-badge
                :color="
                    props.value === 'Ikke startet' ? 'green' :
                    props.value === 'På plan eller foran plan' ? 'green' :
                    props.value === 'oppstart' ? 'green' :
                    props.value === 'Noen forsinkelse, men håndterbar' ? 'orange' :
                    props.value === 'Forsinket' ? 'red' :
                    'grey'
                "
                outline
            >
                {{ props.value }}
            </q-badge>
        </q-td>
        """
    )


