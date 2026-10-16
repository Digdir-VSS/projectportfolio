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

# Display names for columns whose field name doesn't read well as a header
COLUMN_LABELS = {
    "avdeling": "Enhet",
    "fremskritt_status": "Fremdrift",
    "estimert_budsjet_behov": "Totale Budsjettbehov",
    "risikostatus": "Risikostatus",
    "antall_mandsverk_intern": "Månedsverk Intern",
    "antall_mandsverk_ekstern": "Månedsverk Ekstern",
    "brukt_2025": "Forbruk 2025",
    "brukt_2026": "Forbruk 2026",
    "estimert_bruk_2026": "Budsjettbehov 2026",
    "estimert_bruk_2027": "Budsjettbehov 2027",
    "estimert_bruk_2028": "Budsjettbehov 2028",
}

# Amount columns shown with Norwegian thousand separators (1 234 567)
NUMBER_FIELDS = {
    "estimert_budsjet_behov",
    "brukt_2025",
    "brukt_2026",
    "estimert_bruk_2026",
    "estimert_bruk_2027",
    "estimert_bruk_2028",
}
NUMBER_FORMAT = "value => value == null ? '' : Number(value).toLocaleString('nb-NO', {maximumFractionDigits: 0})"

# Numeric columns are right-aligned so the digits line up
RIGHT_ALIGNED_FIELDS = NUMBER_FIELDS | {"antall_mandsverk_intern", "antall_mandsverk_ekstern"}

# Quasar expects a compare function for "sort"; localeCompare puts Æ, Ø and Å in Norwegian order
NAME_SORT = "(a, b) => (a || '').localeCompare(b || '', 'nb')"

# Columns that get a filter menu in the header
FILTER_FIELDS = {"avdeling", "fase", "fremskritt_status", "risikostatus", "beslutningsstatus"}
EMPTY_FILTER_VALUE = "(tom)"

def column_label(field_name: str) -> str:
    return COLUMN_LABELS.get(field_name, field_name.replace("_", " ").title())

def filter_value(value) -> str:
    return EMPTY_FILTER_VALUE if value in (None, "") else str(value)

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
                    "label": column_label(field_name),
                    "field": field_name,
                    "sortable": True,
                    "align": "left",
                    "classes": "break-words whitespace-normal",
                    "headerClasses": "break-words whitespace-normal",
                    ":sort": NAME_SORT,
                })
            else:
                column = {
                    "name": field_name,
                    "label": column_label(field_name),
                    "field": field_name,
                    "sortable": True,
                    "align": "left",
                    "classes": "break-words whitespace-normal",
                    "headerClasses": "break-words whitespace-normal",
                }
                if field_name in NUMBER_FIELDS:
                    column[":format"] = NUMBER_FORMAT
                if field_name in RIGHT_ALIGNED_FIELDS:
                    column["align"] = "right"
                columns.append(column)

    return columns



def overview_page(overview: List[OverviewUI], access_allowance: bool):

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
        for column in columns:
            if column["name"] in FILTER_FIELDS:
                values = {filter_value(row[column["name"]]) for row in rows}
                column["filterOptions"] = sorted(values, key=lambda v: (v == EMPTY_FILTER_VALUE, v))
                column["filterSelected"] = []

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
        r"""
        <q-tr :props="props" class="bg-gray-200">
            <q-th auto-width class="bg-gray-200"></q-th>
            <q-th v-for="col in props.cols" :key="col.name" :props="props" class="bg-gray-200 text-lg font-semibold">
                {{ col.label }}
                <q-btn
                    v-if="col.filterOptions"
                    flat round dense size="sm"
                    icon="filter_list"
                    :color="col.filterSelected.length ? 'orange-9' : 'grey-7'"
                    @click.stop
                >
                    <q-badge v-if="col.filterSelected.length" color="orange-9" floating rounded>
                        {{ col.filterSelected.length }}
                    </q-badge>
                    <q-menu>
                        <q-list dense style="min-width: 180px">
                            <q-item
                                v-for="option in col.filterOptions"
                                :key="option"
                                clickable
                                @click="$parent.$emit('toggle_filter', {column: col.name, value: option})"
                            >
                                <q-item-section side>
                                    <q-checkbox dense class="no-pointer-events" :model-value="col.filterSelected.includes(option)" />
                                </q-item-section>
                                <q-item-section>{{ option }}</q-item-section>
                            </q-item>
                            <q-separator v-if="col.filterSelected.length" />
                            <q-item
                                v-if="col.filterSelected.length"
                                clickable
                                v-close-popup
                                @click="$parent.$emit('clear_filter', {column: col.name})"
                            >
                                <q-item-section>Fjern filter</q-item-section>
                            </q-item>
                        </q-list>
                    </q-menu>
                </q-btn>
            </q-th>
        </q-tr>
        """,
    )

    def apply_filters():
        active = {c["name"]: set(c["filterSelected"]) for c in table.columns if c.get("filterSelected")}
        table.rows = [
            row for row in rows
            if all(filter_value(row[name]) in selected for name, selected in active.items())
        ]
        table.update()

    def find_column(name: str) -> dict:
        return next(c for c in table.columns if c["name"] == name)

    def toggle_filter(e):
        selected = find_column(e.args["column"])["filterSelected"]
        value = e.args["value"]
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        apply_filters()

    def clear_filter(e):
        find_column(e.args["column"])["filterSelected"] = []
        apply_filters()

    table.on("toggle_filter", toggle_filter)
    table.on("clear_filter", clear_filter)
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
                        <q-item-label>Vis prosjekt</q-item-label>
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
                        v-if='""" + str(access_allowance).lower() + r"""'
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
        "body-cell-beslutningsstatus",
        r"""
        <q-td :props="props">
            <q-badge
                v-if="props.value"
                :color="
                    props.value === 'Vedtatt' ? 'green' :
                    props.value === 'Ikke vedtatt' ? 'orange' :
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
        "body-cell-risikostatus",
        r"""
        <q-td :props="props">
            <q-badge
                v-if="props.value"
                :color="
                    props.value === 'Lav' ? 'green' :
                    props.value === 'Medium' ? 'orange' :
                    props.value === 'Høy' ? 'red' :
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


