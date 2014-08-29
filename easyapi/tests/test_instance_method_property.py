import json

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'

import pytest


@pytest.mark.django_db
def test_list_endpoint(staff_api_client):
    # create 3 companies
    for i in range(3):
        CompanyFactory()

    response = staff_api_client.get('/api/company/')
    response_data = json.loads(response.content)

    assert len(response_data) == 3


@pytest.mark.django_db
def test_instance_method_scalar_return(staff_api_client):
    # create 3 companies
    company = CompanyFactory()

    for i in range(3):
        ProjectFactory(company=company, budget=(i + 1) * 100)

    response = staff_api_client.get('/api/company/%d/total_budget/' % company.pk)
    print response.content
    response_data = json.loads(response.content)

    assert response_data == 600


@pytest.mark.django_db
@pytest.mark.parametrize("function", ["project_list", "project_qs"])
def test_instance_method_list_qs(staff_api_client, function):
    # create 3 companies
    company = CompanyFactory()

    for i in range(3):
        ProjectFactory(company=company, budget=(i + 1) * 100)

    response = staff_api_client.get('/api/company/%d/%s/' % (company.pk, function))
    response_data = json.loads(response.content)

    assert len(response_data) == 3
    for project_dict in response_data:
        check_project_dict(project_dict)


@pytest.mark.django_db
@pytest.mark.parametrize("function", ["project_list", "project_qs"])
def test_instance_method_list_qs_embed(staff_api_client, function):
    # create 3 companies
    company = CompanyFactory()

    for i in range(3):
        ProjectFactory(company=company, budget=(i + 1) * 100)

    response = staff_api_client.get('/api/company/%d/%s/' % (company.pk, function),
                                    data={'_embedded': 'company'})
    response_data = json.loads(response.content)

    assert len(response_data) == 3
    for project_dict in response_data:
        check_project_dict(project_dict)
        assert project_dict['_embedded']['company']['id'] == company.id


@pytest.mark.django_db
def test_instance_method_with_scalar_param(staff_api_client):
    # create 3 companies
    company = CompanyFactory()

    response = staff_api_client.post('/api/company/%d/multiply_by_100/' % company.pk, data={'number': 23})
    response_data = json.loads(response.content)

    assert response_data == 2300


def check_project_dict(project_dict):
    assert 'name' in project_dict
    assert 'budget' in project_dict
    assert 'start_date' in project_dict
    assert 'company_id' in project_dict
    assert 'is_open' in project_dict


@pytest.mark.django_db
def test_model_fields(staff_api_client):
    # create 3 companies
    projects = [ProjectFactory() for i in range(3)]

    response = staff_api_client.get('/api/project/%d/' % projects[0].pk)
    response_data = json.loads(response.content)

    project_dict = response_data
    check_project_dict(project_dict)


@pytest.mark.django_db
def test_string_property(staff_api_client):
    company = CompanyFactory()

    response = staff_api_client.get('/api/company/%d/' % company.pk)

    response_data = json.loads(response.content)

    assert 'title' in response_data
    assert response_data['title'] == company.title


@pytest.mark.django_db
def test_model_property(staff_api_client):
    company = CompanyFactory()
    for i in range(3):
        ProjectFactory(company=company, budget=(i + 1) * 100)

    response = staff_api_client.get('/api/company/%d/' % company.pk)

    response_data = json.loads(response.content)

    assert 'first_project' in response_data
    assert isinstance(response_data['first_project'], int)

    assert 'title' in response_data
    assert isinstance(response_data['title'], basestring)


@pytest.mark.django_db
def test_related_object_lookup(staff_api_client):
    project = ProjectFactory()

    response = staff_api_client.get('/api/project/%d/' % project.pk)

    response_data = json.loads(response.content)

    assert 'company_name' in response_data
    assert response_data['company_name'] == project.company.name


