from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404


def SignIn(request):
    if request.method == 'GET':
        ''' Render the signin page '''
        context = {}
        return render(request, 'recportal/signin.html', context)

    if request.method == 'POST':
        ''' validate the provided credentials and login the user if valid else
            return to the same page with a corresponding error message. '''
        try:
            username=request.POST['username']
            password=request.POST['password']
            if username == '' or password == '':
                raise KeyError
        except KeyError:
            messages.add_message(request, messages.ERROR, 'Sign in credentials missing.')
            return redirect('recportal:signin')

        user = authenticate(username=username, password=password)

        if user == None:
            messages.add_message(request, messages.ERROR, 'Invalid credentials.')
            return redirect('recportal:signin')
        else:
            login(request, user)
            return redirect('recportal:home')

    else:
        ''' ideal, this should never be triggered '''
        return JsonResponse({'error_message':'Invalid request method.'})

def SignOut(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Signed out successfully.')
    return redirect('recportal:signin')

@login_required
def Home(request):
    ''' the first page you go to after logging in '''

    if request.method == 'GET':
        context = {}
        context["data"] = request.user.senior.generateRecommendations()
        print(context)
        return render(request, 'recportal/home.html', context)

    else:
        return JsonResponse({'error_message':'Invalid request method.'})
