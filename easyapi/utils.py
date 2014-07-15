__author__ = 'mikhailturilin'


def this_domain_url(request, location):
    if not location.startswith("/"):
        location = "/" + location
    return '%s://%s%s' % (request.is_secure() and 'https' or 'http', request.get_host(), location)

