#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['easyapi/tests', '-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='easy-rest',
    version='0.4.1',
    author='mturilin',
    author_email='mturilin@gmail.com',
    description='Real Python Enums for Django.',
    license='MIT',
    url='https://github.com/mturilin/easyapi',
    long_description='',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'django',
        'djangorestframework',
        'python-dateutil',
        'isodate',
        'six',
        'enum34',
        'django-enumfields',
    ],
    tests_require=[
        'pytest',
        'pytest-django',
        'factory-boy',
    ],
    cmdclass={'test': PyTest},
)
