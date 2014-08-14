import json

import pytest

from easyapi.tests.factories import CompanyFactory, ProjectFactory
from easyapi.tests.test_project.models import ProjectScope


__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_enum_fields_properties(staff_api_client):
    company = CompanyFactory()
    project = ProjectFactory(company=company)

    response = staff_api_client.get('/auto-list/test_project/company/%d/' % company.id)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert 'company_type' in response_data

    assert response_data['company_type'] in [1, 2]
    assert response_data['first_project_scope'] in [scope.value for scope in ProjectScope]

@pytest.mark.django_db
def test_enum_root(staff_api_client):
    response = staff_api_client.get('/enums/')

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert 'CompanyType' in response_data
    assert response_data['CompanyType'].endswith('/enums/companytype/')

    assert 'ProjectScope' in response_data
    assert response_data['ProjectScope'].endswith('/enums/projectscope/')

@pytest.mark.django_db
def test_enum_list(staff_api_client):
    response = staff_api_client.get('/enums/companytype/')

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 2

    for first in response_data:
        assert 'type' in first
        assert 'value' in first
        assert 'full_name' in first
        assert 'name' in first

        assert first['type'] == 'CompanyType'
        assert first['name'] in ['PUBLIC', 'PRIVATE']
        assert first['full_name'].startswith('CompanyType.')
        assert first['value'] in [1,2]



