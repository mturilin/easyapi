from django.conf import settings
from django.db.models import FieldDoesNotExist, Q
from rest_framework.filters import BaseFilterBackend

__author__ = 'mikhail turilin'

FILTER_ALL = {
    'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte', 'in',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'range', 'year',
    'month', 'day', 'week_day', 'isnull', 'search', 'regex', 'iregex',
}

FILTER_EXACT = 'exact'
FILTER_IN = 'in'

ICONTAINS_SPLIT = getattr(settings, 'QUERY_SET_FILTERS_ICONTAINS_SPLIT', True)


def convert(value, datatype):
    if datatype == 'bool':
        val = value.lower()
        if val == "true":
            return True

        if val == "false":
            return False

        raise ValueError("Expected 'true' or 'false', received '%s'" % value)

    if datatype == "string":
        return value

    if datatype == "int":
        return int(value)

    if datatype == "float":
        return float(value)

    raise ValueError("Unknown datatype %s" % datatype)


def get_filters(definition):
    if not definition:
        return [FILTER_EXACT]

    if isinstance(definition, basestring):
        return [FILTER_EXACT]

    if isinstance(definition, dict):
        return definition.get('filters', [FILTER_EXACT])

    if isinstance(definition, (list, set, tuple)):
        if set(definition) <= FILTER_ALL:
            return definition
        raise ValueError("Defininition containes unknown filter rules %s" % str(definition))

    raise ValueError("Filter definition could de only list or dict")


class UnknownDatatype(Exception): pass


def get_datatype(field, definition, queryset):
    if isinstance(definition, basestring):
        return definition

    if isinstance(definition, dict) and 'datatype' in definition:
        return definition['datatype']

    try:
        internal_type = queryset.model._meta.get_field(field).get_internal_type()
        if internal_type == 'BooleanField':
            return 'bool'

        if internal_type == 'IntegerField' or internal_type == 'AutoField':
            return 'int'

        if internal_type in {'FloatField', 'DecimalField'}:
            return 'float'

        if internal_type in {'CharField', 'TextField'}:
            return 'string'

        raise UnknownDatatype("Field type is unknown '%s' for model field '%s'" % (internal_type, field))

    except (AttributeError, FieldDoesNotExist):
        pass

    raise UnknownDatatype("Filter datatype is missing for non-model field '%s'" % field)


def filter_queryset(queryset, request, filtering, ordering=None):
    """

    :param queryset: Django QuerySet
    :param request: HttpRequest
    :param filtering: should be a map of django query criteria (or '*') to filtering definition. Definition could be:
      1. String = datatype (bool, int, float, string)
      2. Dict having the following fields:
        - 'datatype' - automatically resolved if it's the field of the queryset's model
        - 'filters' - list of the filter keywords ('in', 'exact' etc)
    :param ordering: queryset's order_by argument
    :return: queryset with added filters
    """
    ordering = set(ordering) or set()

    fields = set(filtering.keys())
    filters = {field: get_filters(definition) for field, definition in filtering.iteritems()}

    model_fields = [field.name for field in queryset.model._meta.fields]

    for p, v in request.GET.iteritems():
        field = p
        value = v
        query_term = "exact"

        # chech if we have a case of filter ending with query term, such as __contains or __gte
        p_split = p.split("__")
        if len(p_split) > 1:  # it's possible we have a query term (otherwise we will use just a field)
            term_candidate = p_split[-1]
            field_candidate = '__'.join(p_split[:-1])
            if {field_candidate, '*'}.intersection(fields) and term_candidate in FILTER_ALL:
                field = field_candidate
                query_term = term_candidate
                if term_candidate == 'in':  # for in we need to split the list
                    v = v.split(',')

        if field in fields or ('*' in fields and field in model_fields):
            try:
                datatype = get_datatype(field, filtering.get(field, None), queryset)
            except UnknownDatatype:
                # meaining this is not a filter field - some other
                continue
        else:
            continue  # field is not in the filtering

        if not any(query_term in filters.get(f, []) for f in {field, '*'}):
            raise ValueError("Filtering for field '%s' with query term '%s' is not allowed" % (field, query_term))

        # for contains and icontains queries we should split them
        if query_term in ('contains', 'icontains') and datatype == 'string' and ICONTAINS_SPLIT:
            q = Q()

            for subvalue in v.split():
                q &= Q(**{p: subvalue})
            print q
            queryset = queryset.filter(q)
        else:
            queryset = queryset.filter(**{p: convert(v, datatype)})

    if 'order_by' in request.GET:
        order_fields = []
        for order_field_source in request.GET['order_by'].split(','):
            if order_field_source[0] == '-':
                order_field = order_field_source[1:]
            else:
                order_field = order_field_source

            if not {order_field, '*'}.intersection(ordering):
                raise ValueError("Ordering for field '%s' is not allowed" % order_field)

            order_fields.append(order_field_source)

        queryset = queryset.order_by(*order_fields)

    return queryset


class QuerySetFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        ordering = getattr(view, 'ordering', set())

        try:
            filtering = view.filtering
        except AttributeError:
            return queryset

        return filter_queryset(queryset, request, filtering, ordering)


