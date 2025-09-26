import uuid
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Any

from utils.project_loader import field_to_table_col, table_pk_map



def diff_projects(
    original: List[Any],
    edited: List[Any],
    key_field: str = "prosjekt_id",
    include_change_type: bool = False) -> List[dict]:
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
            if old != new:
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
def apply_changes(diffs, session):
    for diff in diffs:
        prosjekt_id = diff["prosjekt_id"]
        changes = diff["changes"]

        # 1️⃣ Group changes by table
        changes_by_table = defaultdict(dict)
        for field, change in changes.items():
            table_cls, col_attr = field_to_table_col[field]
            changes_by_table[table_cls][field] = change

        # 2️⃣ Apply updates per table
        for table_cls, table_changes in changes_by_table.items():
            stmt = select(table_cls).where(
                table_cls.prosjekt_id == prosjekt_id,
                table_cls.er_gjeldende == True
            )
            current = session.exec(stmt).one_or_none()
            if not current:
                print(f"⚠️ No current row found for {table_cls.__tablename__}, prosjekt_id={prosjekt_id}")
                continue

            # Mark old row as not current
            current.er_gjeldende = False
            session.add(current)

            # Copy current row values
            new_row_data = current.dict() if hasattr(current, "dict") else current.__dict__.copy()
            pk_col = table_pk_map[table_cls]
            new_row_data.pop(pk_col, None)  # remove surrogate key
            new_row_data[pk_col] = str(uuid.uuid4())  # or let DB autogenerate
            new_row_data["sist_endret"] = datetime.utcnow()
            new_row_data["er_gjeldende"] = True

            # Apply all changes for this table
            for field, change in table_changes.items():
                _, col_attr = field_to_table_col[field]
                col_name = col_attr.key  # SQLAlchemy column name
                new_row_data[col_name] = change["new"]

            # Insert new row
            new_row = table_cls(**new_row_data)
            session.add(new_row)

    session.commit()

