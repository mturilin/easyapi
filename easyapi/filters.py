from django.db.models.fields.related import ForeignKey

from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend

from easyapi.params import smart_bool, model_param


__author__ = 'mikhail turilin'

FILTER_ALL = {
    'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte', 'in',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'range', 'year',
    'month', 'day', 'week_day', 'isnull', 'search', 'regex', 'iregex',
}

FILTER_EXACT = 'exact'
FILTER_IN = 'in'


def in_converter(base_converter):
    def inner(joined_value):
        value_list = joined_value.split(',')
        return map(base_converter, value_list)

    return inner


class Filter(object):
    def __init__(self, key, base_converter, field_path, condition):
        self.key = key
        self.condition = condition
        self.field_path = field_path
        self.base_converter = base_converter

    @property
    def full_converter(self):
        if self.condition == FILTER_IN:
            return in_converter(self.base_converter)

        return self.base_converter


def get_model_field(model, field_name):
    field = model._meta.get_field(field_name)
    return field


class QuerySetFilter(object):
    def __init__(self, queryset, request, filtering, ordering=None):
        self.ordering = ordering
        self.filtering = filtering
        self.request = request
        self.queryset = queryset

    @property
    def model_fields(self):
        return [field for field in self.get_model()._meta.fields]

    @property
    def model_fields_names(self):
        return set([field.name for field in self.model_fields])

    @property
    def all_params(self):
        return self.request.GET

    @property
    def filter_params(self):
        return {key[1:]: value for key, value in self.all_params.iteritems() if key.startswith('@')}

    def filtered_queryset(self):
        queryset = self.queryset

        for filter_key, value in self.filter_params.iteritems():
            queryset = queryset.filter(**{
                filter_key: self.get_converter(filter_key)(value)
            })

        try:
            order_by = self.all_params['order_by']
            order_fields = order_by.split(',')
            if '*' not in self.ordering and set(f.rstrip('-') for f in order_fields) <= set(self.ordering):
                raise ParseError("Invalid ordering %s" % order_by)

            queryset = queryset.order_by(*order_fields)
        except KeyError:
            pass

        return queryset


    def get_model(self):
        return self.queryset.model


    def get_main_field(self, main_field_name):
        model = self.get_model()
        field = get_model_field(model, main_field_name)
        return field


    def get_converter(self, filter_key):
        return self.get_filter(filter_key).full_converter

    def get_filter(self, filter_key):
        components = filter_key.split("__")
        main_field_name = components[0]

        # if the field is unknown - filtering is not allowed
        if main_field_name not in self.model_fields_names:
            raise ParseError("Invalid filter key %s" % filter_key)

        if len(components) == 1:
            return Filter(key=filter_key, base_converter=self.get_main_field_converter(main_field_name),
                          field_path=[main_field_name],
                          condition=[FILTER_EXACT])

        if len(components) == 2 and components[1] in self.get_conditions(main_field_name):
            return Filter(key=filter_key, base_converter=self.get_main_field_converter(main_field_name),
                          field_path=[main_field_name],
                          condition=components[1])


        # we might have foreign key chain field1__field2__field3__field4__condition
        model = self.get_model()
        field = self.get_main_field(main_field_name)

        for index, component in enumerate(components):
            is_last = index == len(components) - 1

            if is_last and index > 1 and component in FILTER_ALL:
                return Filter(key=filter_key, base_converter=self.get_field_converter(field),
                              field_path=components[:-1],
                              condition=component)

            field = get_model_field(model, component)

            if is_last:
                return Filter(key=filter_key, base_converter=self.get_field_converter(field),
                              field_path=components,
                              condition=[FILTER_EXACT])

            if not isinstance(field, ForeignKey):
                raise ParseError("Invalid filter key %s" % filter_key)

            model = field.rel.to

        raise RuntimeError("We should never be here")


    def get_main_field_converter(self, main_field_name):
        definition = self.get_filtering_def(main_field_name)
        try:
            return definition['datatype']
        except KeyError:
            return self.get_field_converter(self.get_main_field(main_field_name))


    def get_field_converter(self, field):
        internal_type = field.get_internal_type()
        if internal_type == 'BooleanField':
            return smart_bool

        if internal_type == 'IntegerField' or internal_type == 'AutoField':
            return int

        if internal_type in {'FloatField', 'DecimalField'}:
            return float

        if internal_type in {'CharField', 'TextField'}:
            return str

        if internal_type in {'ForeignKey'}:
            return model_param(field.rel.to)

        raise ParseError("Unsupported field type '%s' for model field '%s'" % (internal_type, field))

    def get_filtering_def(self, main_field_name):
        try:
            filtering_def = self.filtering[main_field_name]
        except KeyError:
            try:
                filtering_def = self.filtering['*']
            except KeyError:
                raise ParseError("Unknown field %s" % main_field_name)
        return filtering_def

    def get_conditions(self, main_field):
        try:
            return self.get_filtering_def(main_field)['filters']
        except KeyError:
            return [FILTER_EXACT]


class QuerySetFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        ordering = getattr(view, 'ordering', set())

        try:
            filtering = view.filtering
        except AttributeError:
            return queryset

        return QuerySetFilter(queryset, request, filtering, ordering).filtered_queryset()


