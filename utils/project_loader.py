import os
import struct
import urllib
from sqlmodel import SQLModel
from sqlalchemy import create_engine, event
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from typing import Optional
from uuid import UUID
from collections import Counter
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

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
        IGNORED_FIELDS = {"endret_av"}
        for field in keys - IGNORED_FIELDS:
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