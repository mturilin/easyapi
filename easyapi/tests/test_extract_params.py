from datetime import date
import types

from isodate import parse_date, parse_datetime

import pytest

from easyapi.params import extract_rest_params, iso_datetime, iso_date, model_param, list_param
from easyapi.tests.factories import CompanyFactory
from easyapi.tests.test_project.models import Company


__author__ = 'mikhailturilin'


@pytest.mark.parametrize('dt_str', [
    "2014-W28",
    "2014-W28-7",
    "2014-194",
])
def test_extract_date(api_request_factory, dt_str):
    param_types = {
        'dt': iso_date
    }

    request = api_request_factory.post('/', data={'dt': dt_str}, format='json')

    params = extract_rest_params(request, param_types)

    assert 'dt' in params
    assert isinstance(params['dt'], date)
    assert params['dt'] == parse_date(dt_str)


@pytest.mark.parametrize('dt_str', [
    "2014-07-13T18:02:49+00:00",
    "2014-07-13T18:02:49Z",
])
def test_extract_datetime(api_request_factory, dt_str):
    param_types = {
        'dt': iso_datetime
    }

    request = api_request_factory.post('/', data={'dt': dt_str}, format='json')

    params = extract_rest_params(request, param_types)

    assert 'dt' in params
    assert isinstance(params['dt'], date)
    assert params['dt'] == parse_datetime(dt_str)


@pytest.mark.django_db
def test_extract_model(api_request_factory):
    company = CompanyFactory()
    param_types = {
        'company': model_param(Company)
    }

    request = api_request_factory.post('/', data={'company': company.pk}, format='json')

    params = extract_rest_params(request, param_types)

    assert 'company' in params
    assert isinstance(params['company'], Company)
    assert params['company'] == company


@pytest.mark.parametrize('list_str, result', [
    ([1, 2, 3], [1, 2, 3]), # list as list
    ("[1,2,3]", [1, 2, 3]), # list as JSON
    ("one,two,three", ['one','two','three']), # comma-separated
])
def test_extract_list(api_request_factory, list_str, result):
    param_types = {
        'my_list': list_param
    }

    request = api_request_factory.post('/', data={'my_list': list_str}, format='json')

    params = extract_rest_params(request, param_types)

    assert 'my_list' in params
    assert isinstance(params['my_list'], types.ListType)
    assert params['my_list'] == result