import json

import pytest

from easyapi.tests.factories import CompanyFactory, ProjectFactory


__author__ = 'mikhailturilin'



@pytest.mark.django_db
def test_filtering_exact_str(staff_api_client):
    # create 3 companies with known country and 6 with random
    country = 'Prussia'
    for i in range(3):
        CompanyFactory(country=country)

    for i in range(6):
        CompanyFactory()



    response = staff_api_client.get('/api/company/', data={'@country': country})
    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3

@pytest.mark.django_db
def test_filtering_foreign_key(staff_api_client):
    # create 3 companies with known country and 6 with random
    company = CompanyFactory()
    for i in range(3):
        ProjectFactory(company=company)

    for i in range(6):
        ProjectFactory()


    response = staff_api_client.get('/api/project/', data={'@company': company.pk})
    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3


@pytest.mark.django_db
def test_filtering_subselect(staff_api_client):
    country = 'Prussia'
    company = CompanyFactory(country=country)
    for i in range(3):
        ProjectFactory(company=company)

    for i in range(6):
        ProjectFactory()


    response = staff_api_client.get('/api/project/', data={'@company__country': country})
    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 3



@pytest.mark.django_db
def test_filtering_str_in(staff_api_client):
    # create 3 companies with known country and 6 with random
    countries = ['Prussia','Jugoslavia']
    for country in countries:
        for i in range(3):
            CompanyFactory(country=country)

    for i in range(19):
        CompanyFactory()



    response = staff_api_client.get('/api/company/', data={'@country__in': ','.join(countries)})
    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert len(response_data) == 6



@pytest.mark.django_db
def test_ordering(staff_api_client):
    for i in range(19):
        CompanyFactory()



    response = staff_api_client.get('/api/company/', data={'order_by': '-pk'})
    assert response.status_code == 200

    response_data = json.loads(response.content)

    for index in range(len(response_data)-1):
        assert response_data[index]['id'] > response_data[index+1]['id']

