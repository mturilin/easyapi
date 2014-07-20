from easyapi.router import EasyApiRouter, AutoAppRouter, AutoAppListRouter
from easyapi.tests.test_project.models import Company, Project
from easyapi.viewsets import InstanceViewSet

__author__ = 'mikhailturilin'

class CompanyViewSet(InstanceViewSet):
    model = Company

class ProjectViewSet(InstanceViewSet):
    model = Project

router = EasyApiRouter()
router.register('company', CompanyViewSet)
router.register('project', ProjectViewSet)



