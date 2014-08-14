__author__ = 'mikhailturilin'

import json

import pytest

from easyapi.tests.factories import CompanyFactory


@pytest.mark.django_db
def test_list_endpoint(staff_api_client):
    for i in range(37):
        CompanyFactory()

    response = staff_api_client.get('/custom-api/company-paginator/')

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert response_data['count'] == 37
    assert response_data['num_pages'] == 8
    assert response_data['number'] == 1

    results = response_data['results']
    company = results[0]
    assert company['name']
    assert company['category_id']
    assert company['company_type']
    assert company['country']
    assert company['_meta']['app'] == 'test_project'
    assert company['_meta']['model'] == 'company'


