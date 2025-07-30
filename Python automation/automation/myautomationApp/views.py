from django.shortcuts import render, redirect
from myautomationApp.models import MostWanted
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scraper import compare_data, apply_changes_to_db
import logging 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    db_data = list(MostWanted.objects.all().order_by('-created_at').values())
    return render(request, 'index.html', {'records': db_data} )

@csrf_exempt #for testing purposes
def updates_handler(request):
    if request.method == 'POST':
        changes = request.session.get('pending_changes')
        if not changes:
            return JsonResponse(
                {'status': 'error', 'message': 'No pending changes'}, 
                status=400
            )
        
        try:
            apply_changes_to_db(changes)
            del request.session['pending_changes']
            return redirect("index")
        except Exception as e:
            print(f"Error saving changes: {str(e)}")
            logging.exception(f"Error saving changes: {str(e)}")
            return redirect("index")
    
    # GET request
    try:
        changes = changes = compare_data()
        request.session['pending_changes'] = changes
        return render(request, 'update_modal.html', {
            'new_records': changes['new'],
            'deleted_records': changes['deleted']
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
