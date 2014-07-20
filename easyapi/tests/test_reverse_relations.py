import json

import pytest

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'


@pytest.skip
@pytest.mark.django_db
def test_model_property(staff_api_client):
    company = CompanyFactory()
    for i in range(3):
        ProjectFactory(company=company, budget=(i + 1) * 100)

    response = staff_api_client.get('/api/company/%d/projects' % company.pk)

    assert response.status_code == 200
    response_data = json.loads(response.content)

    assert 'first_project' in response_data
    assert isinstance(response_data['first_project'], int)