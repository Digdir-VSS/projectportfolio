import uuid
from typing import Dict, Type, Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER


# --- Type mapping: Python str -> (Python type, SQLAlchemy column type) ---
TYPE_MAP = {
    "int": (Optional[int], Integer),
    "str": (Optional[str], String(255)),  # default varchar(255)
}


def create_table_class(name: str, columns: Dict[str, str]) -> Type[SQLModel]:
    """
    Dynamically create a SQLModel table class with a UUID primary key.
    """

    # annotations dict required by Pydantic
    annotations = {"id": Optional[uuid.UUID]}

    attrs = {
        "__tablename__": name,
        "__table_args__": {"schema": "dbo", "extend_existing": True},
        "__annotations__": annotations,

        # UUID primary key
        "id": Field(
            default_factory=uuid.uuid4,
            sa_column=Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4),
        ),
    }

    for col_name, col_type in columns.items():
        if col_type not in TYPE_MAP:
            raise ValueError(f"Unsupported type: {col_type}")
        py_type, sa_type = TYPE_MAP[col_type]
        annotations[col_name] = py_type
        attrs[col_name] = Field(default=None, sa_column=Column(sa_type))


    attrs["__annotations__"] = annotations

    # Use table=True to mark as a table
    return type(
        name.capitalize(),
        (SQLModel,),
        {**attrs, "__module__": __name__},
        table=True
    )
