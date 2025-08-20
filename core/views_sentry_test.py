from django.http import HttpResponse


def sentry_test_error(request):
    """Deliberately raise an exception to verify Sentry integration."""
    # This will produce a ZeroDivisionError and should be captured by Sentry
    1 / 0
    return HttpResponse('unreachable')
