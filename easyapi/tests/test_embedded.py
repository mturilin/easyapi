import json

import pytest
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_embedded(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].id, data={'_embedded': 'company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert '_embedded' in response_data
    assert 'company' in response_data['_embedded']
    assert response_data['_embedded']['company']['id'] == company.id


@pytest.mark.django_db
def test_embedded_fail(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].id, data={'_embedded': 'id'})
    assert response.status_code == HTTP_400_BAD_REQUEST
