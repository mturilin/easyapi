from django.db import models
from rest_framework import fields as rest_fields

from easyapi.decorators import rest_method, rest_property
from easyapi.fields import PrimaryKeyReadOnlyField


__author__ = 'mikhailturilin'


class CompanyManager(models.Manager):

    @rest_method(arg_types={'country': str})
    def select_by_country(self, country):
        return self.filter(country=country)

class Category(models.Model):
    name = models.TextField()


class Company(models.Model):
    name = models.TextField()
    category = models.ForeignKey(Category)
    country = models.CharField(max_length=100)

    # extra_rest_fields = {
    #     # 'first_project': PrimaryKeyReadOnlyField(),
    #     # 'title': Field(),
    # }

    objects = CompanyManager()

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

    @rest_property(rest_fields.Field)
    def title(self):
        return self.name.title()

    @rest_property(PrimaryKeyReadOnlyField)
    def first_project(self):
        return self.projects.all().first()


class Project(models.Model):
    company = models.ForeignKey(Company, related_name="projects")
    name = models.TextField()
    budget = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    is_open = models.BooleanField(default=True)
    start_date = models.DateField()

    extra_rest_fields = {
        'company_name': rest_fields.Field(source='company.name'),
    }


