from rest_framework.fields import Field


__author__ = 'mikhailturilin'


class PrimaryKeyReadOnlyField(Field):
    def to_native(self, value):
        return value and value.pk


class MetaField(Field):
    def __init__(self, label=None, help_text=None):
        super(MetaField, self).__init__('*', label, help_text)

    def to_native(self, obj):
        return {
            'app': type(obj)._meta.app_label,
            'model': type(obj)._meta.model_name
        }


