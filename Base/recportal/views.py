from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from recportal.models import *

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
        return render(request, 'recportal/home.html')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})

@login_required
def Recommendations(request):
    ''' A page where you can view your recommendations made by other seniors.
        A page under the "Senior Panel" tabs on the page (see base.html in
        recportal/templates) '''

    if request.method == 'GET':
        context = {}
        context['data'] = request.user.senior.getActiveRecommendations()
        return render(request, 'recportal/recommendations.html', context)

    if request.method == 'POST':
        for key in request.POST:
            if key.split('.')[0] == 'candidate':
                name = key.split('.')[1]
                first_name = name.split(' ')[0]
                last_name = name.split(' ')[1]
                try:
                    candidate = Candidate.objects.get(first_name=first_name, last_name=last_name)
                    recommendations = Recommendation.objects.filter(candidate=candidate, recommended_senior=request.user)

                    if request.POST[key] == 'accepted':
                        for recommendation in recommendations:
                            recommendation.status = True
                            recommendation.save()
                    elif request.POST[key] == 'declined':
                        for recommendation in recommendations:
                            recommendation.delete()
                    else: # neutral
                        pass

                except Exception as error:
                    print(error)
                    print('not found: \"{} {}\"'.format(first_name, last_name))
                    pass

        return redirect('recportal:recommendations')

@login_required
def MyCandidates(request):
    context = {}
    context['data'] = request.user.senior.getCandidates()
    return render(request, 'recportal/mycandidates.html', context)

@login_required
def Candidates(request):
    context = {}
    context['data'] = Candidate.objects.all()
    return render(request, 'recportal/candidates.html', context)

@login_required
def CandidateProfile(request, first_name, last_name):
    context = {}
    context['candidate'] = Candidate.objects.get(first_name=first_name, last_name=last_name)
    return render(request, 'recportal/profile.html', context)
