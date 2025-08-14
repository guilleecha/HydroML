from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import advanced_user_required
from .models import DatabaseConnection
from .forms import DatabaseConnectionForm

@login_required
@advanced_user_required
def database_connection_list(request):
    connections = DatabaseConnection.objects.filter(user=request.user)
    return render(request, 'connectors/database_connection_list.html', {'connections': connections})

@login_required
@advanced_user_required
def database_connection_create(request):
    if request.method == 'POST':
        form = DatabaseConnectionForm(request.POST)
        if form.is_valid():
            connection = form.save(commit=False)
            connection.user = request.user
            connection.save()
            return redirect('connectors:database_connection_list')
    else:
        form = DatabaseConnectionForm()
    return render(request, 'connectors/database_connection_form.html', {'form': form})

@login_required
@advanced_user_required
def database_connection_delete(request, pk):
    connection = get_object_or_404(DatabaseConnection, pk=pk, user=request.user)
    if request.method == 'POST':
        connection.delete()
        return redirect('connectors:database_connection_list')
    return render(request, 'connectors/database_connection_confirm_delete.html', {'connection': connection})
