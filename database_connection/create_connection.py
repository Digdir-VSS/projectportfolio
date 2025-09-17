#from sqlalchemy import create_engine
import struct
from itertools import chain, repeat
import urllib
from azure.core.credentials import AccessToken
from sqlalchemy.engine import Engine
from sqlmodel import create_engine, select, Session


def build_engine(connection_string: str, azure_token: AccessToken) -> Engine:
    params = urllib.parse.quote(connection_string)
    # Retrieve an access token
    token_as_bytes = bytes(
        azure_token.token, "UTF-8"
    )  # Convert the token to a UTF-8 byte string
    encoded_bytes = bytes(
        chain.from_iterable(zip(token_as_bytes, repeat(0)))
    )  # Encode the bytes to a Windows byte string
    token_bytes = (
        struct.pack("<i", len(encoded_bytes)) + encoded_bytes
    )  # Package the token into a bytes object
    attrs_before = {
        1256: token_bytes
    }  # Attribute pointing to SQL_COPT_SS_ACCESS_TOKEN to pass access token to the driver

    # build the connection
    return create_engine(
        "mssql+pyodbc:///?odbc_connect={0}".format(params),
        connect_args={"attrs_before": attrs_before},
    )