from types import SimpleNamespace

import pytest

from frontend.utils.authentorize import validate_access


def project(epost_kontakt):
    return SimpleNamespace(portfolioproject=SimpleNamespace(epost_kontakt=epost_kontakt))


ADMINS = ["admin@digdir.no"]


def test_admin_has_access_without_being_a_contact():
    assert validate_access(project(None), "admin@digdir.no", ADMINS) is True


@pytest.mark.parametrize("epost_kontakt", [
    "['ola@digdir.no', 'kari@digdir.no']",
    "ola@digdir.no",
    "['Ola@Digdir.no']",
])
def test_contact_has_access(epost_kontakt):
    assert validate_access(project(epost_kontakt), "ola@digdir.no", ADMINS) is True


def test_a_similar_email_gives_no_access():
    assert validate_access(project("['kola@digdir.no']"), "ola@digdir.no", ADMINS) is False


@pytest.mark.parametrize("epost_kontakt", [None, "", "[]"])
def test_project_without_contacts_gives_no_access_and_no_crash(epost_kontakt):
    assert validate_access(project(epost_kontakt), "ola@digdir.no", ADMINS) is False
