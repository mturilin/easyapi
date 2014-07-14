from django.db import models
from rest_framework.fields import Field

from easyapi.decorators import rest_method
from easyapi.fields import PrimaryKeyReadOnlyField


__author__ = 'mikhailturilin'


class CompanyManager(models.Manager):
    def select_by_country(self, country):
        return self.filter(country=country)


class Company(models.Model):
    name = models.TextField()
    country = models.CharField(max_length=100)

    extra_rest_fields = {
        'first_project': PrimaryKeyReadOnlyField(),
        'title': Field(),
    }


    @rest_method()
    def total_budget(self):
        return sum([float(project.budget) for project in self.projects.filter(is_open=True)])

    @rest_method()
    def project_list(self):
        return list(self.projects.filter(is_open=True))

    @rest_method()
    def project_qs(self):
        return self.projects.filter(is_open=True)

    @rest_method(rest_verbs=['POST'], arg_types={'number': int})
    def multiply_by_100(self, number):
        return number * 100

    @property
    def title(self):
        return self.name.title()

    @property
    def first_project(self):
        return self.projects.all().first()


class Project(models.Model):
    company = models.ForeignKey(Company, related_name="projects")
    name = models.TextField()
    budget = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    is_open = models.BooleanField(default=True)
    start_date = models.DateField()

    extra_rest_fields = {
        'company_name': Field(source='company.name'),
    }


