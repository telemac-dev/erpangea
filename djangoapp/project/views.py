from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    View principal do dashboard
    """
    context = {
        'title': 'Dashboard',
    }
    return render(request, 'dashboard.html', context)
