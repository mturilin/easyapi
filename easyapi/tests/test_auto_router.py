import json

import pytest

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
@pytest.mark.parametrize('factory,name', [
    (CompanyFactory, 'company'),
    (ProjectFactory, 'project'),
])
def test_list_endpoint(api_client, factory, name):
    for i in range(3):
        factory()

    response = api_client.get('/auto-api/test_project/%s/' % name)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3