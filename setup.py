#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


README = read('README.md')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests', '-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='django-easy-api',
    version='0.1',
    author='mikhailturilin',
    author_email='webmaster@hzdg.com',
    description='Real Python Enums for Django.',
    license='MIT',
    url='https://github.com/mturilin/easyapi',
    long_description=README,
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
        'Django',
        'djangorestframework',
        'python-dateutil',
        'isodate',
        'six',
    ],
    tests_require=[
        'pytest',
        'pytest-django',
        'factory-boy',
    ],
    cmdclass={'test': PyTest},
)
