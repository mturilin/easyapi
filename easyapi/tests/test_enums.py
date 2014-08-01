import json
import pytest
from easyapi.tests.factories import CompanyFactory, ProjectFactory
from easyapi.tests.test_project.models import ProjectScope

__author__ = 'mikhailturilin'




@pytest.mark.django_db
def test_enum_fields_properties(staff_api_client):
    company = CompanyFactory()
    project = ProjectFactory(company=company)

    response = staff_api_client.get('/auto-list/test_project/company/%d/' % company.id)

    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert 'company_type' in response_data

    assert response_data['company_type'] in [1,2]
    assert response_data['first_project_scope'] in [scope.value for scope in ProjectScope]