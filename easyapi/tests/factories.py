from easyapi.tests.test_project.models import Project, Company
from datetime import timedelta, date
from django.utils import timezone

import factory
from factory import django as factory_django
from factory import fuzzy

__author__ = 'mikhailturilin'


class CompanyFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Company

    name = fuzzy.FuzzyText()


SIX_MONTH_EARLIER = date.today() - timedelta(days=int(30.5*6))

class ProjectFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Project

    company = factory.SubFactory(CompanyFactory)
    name = fuzzy.FuzzyText()
    budget = fuzzy.FuzzyInteger(1000,9000)
    start_date = fuzzy.FuzzyDate(start_date=SIX_MONTH_EARLIER)