import json

import pytest
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from easyapi.tests.factories import CompanyFactory, ProjectFactory, ManagerFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_foreign_keys_end_with_id(staff_api_client):
    company = CompanyFactory()
    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/')
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    for proj_dict in response_data:
        assert 'company_id' in proj_dict
        assert proj_dict['company_id'] == company.id


@pytest.mark.django_db
def test_create_with_foreign_keys_end_with_id(staff_api_client):
    company = CompanyFactory()
    manager = ManagerFactory()

    response = staff_api_client.post('/api/project/',
                                     {'name': 'aaaa', 'company_id': company.id, 'manager_id': manager.id,
                                      'start_date': '2014-05-19', 'scope': "Company"})
    assert response.status_code == HTTP_201_CREATED
    response_data = json.loads(response.content)

    proj_dict = response_data
    assert 'company_id' in proj_dict
    assert proj_dict['company_id'] == company.id


