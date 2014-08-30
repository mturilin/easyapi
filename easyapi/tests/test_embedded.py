import json

import pytest
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from easyapi.tests.factories import CompanyFactory, ProjectFactory, AddressFactory


__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_embedded(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].id, data={'_embedded': 'company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    # assert '_embedded' in response_data
    assert response_data['_embedded']['company']['id'] == company.id


@pytest.mark.django_db
def test_embedded_fail(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].id, data={'_embedded': 'id'})
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_embedded_in_embedded(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].id, data={'_embedded': 'company__category'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)


    company_dict = response_data['_embedded']['company']
    assert company_dict['id'] == company.id

    category_dict = company_dict['_embedded']['category']
    assert category_dict['id'] == company.category.id


@pytest.mark.django_db
def test_embedded_for_list(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/', data={'_embedded': 'company__category'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    project_dict = response_data[0]

    company_dict = project_dict['_embedded']['company']
    assert company_dict['id'] == company.id

    category_dict = company_dict['_embedded']['category']
    assert category_dict['id'] == company.category.id


@pytest.mark.django_db
def test_embedded_model_level(staff_api_client):

    project = ProjectFactory()

    response = staff_api_client.get('/auto-list/test_project/manager/%d/' % project.manager.id, data={'_embedded': 'projects'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)


    assert len(response_data['_embedded']['projects']) == 1



@pytest.mark.django_db
def test_embedded_related(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects']) == 3



@pytest.mark.django_db
def test_embedded_function(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects_embedded'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects_embedded']) == 3




@pytest.mark.django_db
def test_embedded_function_datatype(staff_api_client):
    company = CompanyFactory()

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'my_company_type'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert response_data['_embedded']['my_company_type'] == company.company_type.value




@pytest.mark.django_db
def test_embedded_function_custom(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects_embedded_custom_function'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects_embedded_custom_function']) == 3




@pytest.mark.django_db
def test_embedded_function_embedded(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects_embedded__company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects_embedded']) == 3
    assert response_data['_embedded']['projects_embedded'][0]['_embedded']['company']['id'] == company.id




@pytest.mark.django_db
def test_embedded_property(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects_embedded_prop'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects_embedded_prop']) == 3




@pytest.mark.django_db
def test_embedded_property_embedded(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects_embedded_prop__company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects_embedded_prop']) == 3
    assert response_data['_embedded']['projects_embedded_prop'][0]['_embedded']['company']['id'] == company.id



@pytest.mark.django_db
def test_embedded_related_when_none(staff_api_client):
    company = CompanyFactory()

    # projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert len(response_data['_embedded']['projects']) == 0



@pytest.mark.django_db
def test_embedded_one_to_one(staff_api_client):
    company = CompanyFactory(address=AddressFactory())

    # projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'address'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert response_data['_embedded']['address']['street']


@pytest.mark.django_db
def test_embedded_one_to_one_when_none(staff_api_client):
    company = CompanyFactory()

    # projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'address'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert 'address' in response_data['_embedded']
    assert not response_data['_embedded']['address']



@pytest.mark.django_db
def test_embedded_related_one_to_one(staff_api_client):
    address = AddressFactory()
    company = CompanyFactory(address=address)

    # projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/auto-api/address/%d/' % address.id, data={'_embedded': 'company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert response_data['_embedded']['company']['name']


@pytest.mark.django_db
def test_embedded_related_one_to_one_when_none(staff_api_client):
    address = AddressFactory()

    # projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/auto-api/address/%d/' % address.id, data={'_embedded': 'company'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert 'company' in response_data['_embedded']
    assert not response_data['_embedded']['company']


