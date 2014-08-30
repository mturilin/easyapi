from easyapi.tests.test_project.models import Project, Company, Category, CompanyType, ProjectScope, Address, Manager
from datetime import timedelta, date
from django.utils import timezone

import factory
from factory import django as factory_django
from factory import fuzzy

__author__ = 'mikhailturilin'


class CategoryFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Category

    name = fuzzy.FuzzyText()


class AddressFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Address

    street = fuzzy.FuzzyText()

class CompanyFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Company

    category = factory.SubFactory(CategoryFactory)
    name = fuzzy.FuzzyText()
    country = fuzzy.FuzzyText(length=20)
    company_type = fuzzy.FuzzyChoice(CompanyType)
    address = None


SIX_MONTH_EARLIER = date.today() - timedelta(days=int(30.5*6))

class ManagerFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Manager

    name = fuzzy.FuzzyText()

class ProjectFactory(factory_django.DjangoModelFactory):
    class Meta:
        model = Project

    company = factory.SubFactory(CompanyFactory)
    name = fuzzy.FuzzyText()
    budget = fuzzy.FuzzyInteger(1000,9000)
    start_date = fuzzy.FuzzyDate(start_date=SIX_MONTH_EARLIER)
    scope = fuzzy.FuzzyChoice(ProjectScope)
    manager = factory.SubFactory(ManagerFactory)