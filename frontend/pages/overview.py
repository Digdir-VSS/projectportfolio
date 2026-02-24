from typing import List
from nicegui import ui
from datetime import datetime
from io import BytesIO
import pandas as pd

from models.ui_models import OverviewUI

def download_excel_file(overview_data: List[OverviewUI]):
     dataframe = pd.DataFrame([row.model_dump() for row in overview_data])

     buffer = BytesIO()
     dataframe.to_excel(buffer, index=False)
     buffer.seek(0)
     ui.download.content(buffer.read(), "uttrekk.xlsx")

def create_columns(overview_fields: List[str]):
    columns = []
    for field_name in overview_fields:
            
            if field_name == "prosjekt_id":
                 columns.append({
                "name": "prosjekt_id", 
                "label": "",       
                "field": "prosjekt_id",
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
                    "sort": "asc",
                })
            else:
                columns.append({
                    "name": field_name,
                    "label": field_name.replace("_", " ").title(),
                    "field": field_name,
                    "sortable": True,
                    "align": "left",
                    "classes": "break-words whitespace-normal",
                    "headerClasses": "break-words whitespace-normal",
                })

    return columns



def overview_page(overview: List[OverviewUI]):

    with ui.column().classes("w-full gap-2"):

        columns = [
            {"name": "expand", "label": "", "field": "expand"},
            *create_columns(OverviewUI.model_fields),
        ]
        # columns = create_columns(OverviewUI.model_fields)

        rows = sorted(
            [
                {**prosjekt.model_dump(), "__row_id": str(prosjekt.prosjekt_id)}
                for prosjekt in overview
            ],
            key=lambda r: r["planlagt_ferdig"] or datetime.max  # None goes last
        )
        table = ui.table(
            columns=columns,
            rows=rows,
            row_key="prosjekt_id",
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
                "headerStyle": "color: #0D2B5B; font-weight: bold;",
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
        <q-btn-dropdown
            size="sm"
            color="primary"
            dense
            icon="menu"
            dropdown-icon="arrow_drop_down"
        >
            <q-list>
                <q-item 
                    clickable 
                    v-close-popup
                    :href="'/project/' + props.row.prosjekt_id"
                >
                    <q-item-section avatar>
                        <q-icon name="edit" color="primary" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Rediger prosjekt</q-item-label>
                    </q-item-section>
                </q-item>
                
                <q-item 
                    clickable 
                    v-close-popup
                    :href="'/status_rapportering/' + props.row.prosjekt_id"
                >
                    <q-item-section avatar>
                        <q-icon name="assessment" color="orange" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Rapportering</q-item-label>
                    </q-item-section>
                </q-item>
                
                <q-item 
                    clickable 
                    v-close-popup
                    :href="'/vurdering/' + props.row.prosjekt_id"
                >
                    <q-item-section avatar>
                        <q-icon name="fact_check" color="green" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Vurdering</q-item-label>
                    </q-item-section>
                </q-item>
            </q-list>
        </q-btn-dropdown>
    </q-td>
    """
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
    table.add_slot(
        "body-cell-expand",
        r"""
        <q-td auto-width>
            <q-btn
                size="sm"
                flat
                dense
                icon="expand_more"
                @click="props.expand = !props.expand"
            />
        </q-td>
        """
    )
    table.add_slot(
        "body-row",
        r"""
        <q-tr :props="props">
            <q-td auto-width>
                <q-btn
                    size="sm"
                    flat
                    dense
                    icon="expand_more"
                    @click="props.expand = !props.expand"
                />
            </q-td>

            <q-td v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.value }}
            </q-td>
        </q-tr>

        <q-tr v-show="props.expand" :props="props">
            <q-td colspan="100%">
                <div class="q-pa-md">
                    <div class="text-subtitle2 q-mb-sm">
                        Detaljer for brukt 2025 / 2026 (TODO)
                    </div>

                    <!-- Here you will render another table or list -->
                    <div>
                        Klikk for å hente saldo-detaljer fra backend.
                    </div>
                </div>
            </q-td>
        </q-tr>
        """
    )
    ui.button('Last ned oversikt', on_click=lambda: download_excel_file(overview))


