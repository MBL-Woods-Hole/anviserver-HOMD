from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings

def show_index(request):
    print(settings.ENV)
    if settings.ENV == 'production':
        return render(request, 'index_homd.html')
    else:
        return render(request, 'index.html')

def show_error_page(request, exception):
    return render(request, 'error.html')
