from rest_framework.fields import Field

__author__ = 'mikhailturilin'


class PrimaryKeyReadOnlyField(Field):
    def to_native(self, value):
        return value and value.pk




