import json

import pytest
from rest_framework.status import HTTP_200_OK

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_meta(staff_api_client):
    company = CompanyFactory()

    link = '/api/company/%d/' % company.id
    response = staff_api_client.get(link)
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    # assert '_embedded' in response_data

    meta = {
        'app': 'test_project',
        'model': 'company',
    }

    assert response_data['_meta'] == meta
