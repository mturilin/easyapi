from rest_framework.serializers import ModelSerializer

__author__ = 'mikhailturilin'


class AutoModelSerializer(ModelSerializer):
    def get_fields(self):
        the_fields = super(AutoModelSerializer, self).get_fields()
        model = self.opts.model

        try:
            the_fields.update(model.extra_rest_fields)
        except AttributeError:
            pass

        return the_fields