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

    # assert '_embedded' in response_data
    assert 'company' in response_data
    assert response_data['company']['id'] == company.id


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

    assert 'company' in response_data

    company_dict = response_data['company']
    assert company_dict['id'] == company.id

    assert 'category' in company_dict
    category_dict = company_dict['category']
    assert category_dict['id'] == company.category.id


@pytest.mark.django_db
def test_embedded_for_list(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/project/', data={'_embedded': 'company__category'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    project_dict = response_data[0]

    assert 'company' in project_dict

    company_dict = project_dict['company']
    assert company_dict['id'] == company.id

    assert 'category' in company_dict
    category_dict = company_dict['category']
    assert category_dict['id'] == company.category.id


@pytest.mark.django_db
def test_embedded_related(staff_api_client):
    company = CompanyFactory()

    projects = [ProjectFactory(company=company) for i in range(3)]

    response = staff_api_client.get('/api/company/%d/' % company.id, data={'_embedded': 'projects'})
    assert response.status_code == HTTP_200_OK

    response_data = json.loads(response.content)

    assert 'projects' in response_data

    assert len(response_data['projects']) == 3


