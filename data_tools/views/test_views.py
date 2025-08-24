# data_tools/views/test_views.py
from django.shortcuts import render
from django.http import JsonResponse

def tanstack_test_view(request):
    """
    Vista simple para probar TanStack Table implementación
    """
    return render(request, 'data_tools/tanstack_test.html')