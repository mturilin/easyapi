import json

import pytest

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
@pytest.mark.parametrize('factory,name', [
    (CompanyFactory, 'company'),
    (ProjectFactory, 'project'),
])
def test_list_endpoint(staff_api_client, factory, name):
    for i in range(3):
        factory()

    response = staff_api_client.get('/auto-list/test_project/%s/' % name)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3


@pytest.mark.django_db
@pytest.mark.parametrize('factory,name', [
    (CompanyFactory, 'company'),
    (ProjectFactory, 'project'),
])
def test_endpoint(staff_api_client, factory, name):
    for i in range(3):
        factory()

    response = staff_api_client.get('/auto-api/%s/' % name)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3

@pytest.mark.django_db
@pytest.mark.parametrize('root,app_prefix', [
    ('auto-api/', ''),
    ('auto-list/', 'test_project/'),
])
def test_namespaces_for_router_root_api(staff_api_client, root, app_prefix):
    response = staff_api_client.get('/%s' % root)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert app_prefix + 'company' in response_data
    assert response_data[app_prefix + 'company'] == "http://testserver/%s%scompany/" % (root, app_prefix)
    assert app_prefix + 'project' in response_data
    assert response_data[app_prefix + 'project'] == "http://testserver/%s%sproject/" % (root, app_prefix)
