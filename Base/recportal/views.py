from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from recportal.models import *


@login_required
def Candidates(request):
    ''' the view to render the candidates page '''

    if request.method == 'GET':
        context = {}
        context['data'] = Candidate.objects.all()
        return render(request, 'recportal/candidates.html', context)

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def CandidateProfile(request, first_name, last_name):
    ''' the induvisual profile page for each candidate '''

    if request.method == 'GET':
        context = {}
        context['candidate'] = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        return render(request, 'recportal/profile.html', context)

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def Home(request):
    ''' the first page you go to after logging in '''

    if request.method == 'GET':
        return render(request, 'recportal/home.html')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def MyCandidates(request):
    ''' the view to render the mycandidates page '''

    if request.method == 'GET':
        context = {}
        context['data'] = request.user.senior.getCandidates()
        return render(request, 'recportal/mycandidates.html', context)

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def MyPitches(request):

    if request.method == 'GET':
        context = {}
        context['mypitches'] = request.user.pitches.all()
        return render(request, 'recportal/mypitches.html', context)

    if request.method == 'POST':
        data = request.POST
        candidate = get_object_or_404(Candidate, first_name=data['candidate'].split('-')[0], last_name=data['candidate'].split('-')[1])
        pitch = get_object_or_404(Pitch, candidate=candidate, senior=request.user)
        pitch.task.completion_date = datetime.datetime.strptime(data['doc'], '%Y-%m-%d').date()
        try:
            if data['approval']:
                pitch.approved = True
        except:
            pass
        pitch.task.save()
        pitch.save()
        messages.add_message(request, messages.INFO, 'Task updated successfully!')
        return redirect('recportal:mypitches')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def PitchCandidate(request, first_name, last_name):
    ''' the view for the form to pitch candidates '''

    if request.method == 'GET':
        context = {}
        context['candidate'] = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        return render(request, 'recportal/pitch.html', context)

    if request.method == 'POST':
        # don't forget to make a verification script
        data = request.POST
        # first, don't let the same senior pitch the same candidate
        try:
            candidate= get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
            p = Pitch.objects.get(candidate=candidate, senior=request.user)
            if p:
                messages.add_message(request, messages.ERROR, 'You have already pitched this candidate', extra_tags="pitch")
            return redirect('recportal:profile', first_name=first_name, last_name=last_name)
        except:
            pass
        # then, make sure that all of the data is valid and create the new pitch
        possible_teams = ['App Dev', 'Backend', 'Frontend', 'Graphics', 'Video']
        try:
            team = data['team']
            if team not in possible_teams:
                messages.add_message(request, messages.ERROR, 'Pitch cancelled due to providing an invalid team. Stay away from dev tools.', extra_tags="pitch")
                return redirect('recportal:profile', first_name=first_name, last_name=last_name)
            title = data['title']
            desc = data['description']

            isd = datetime.datetime.strptime(data['issuing_date'], '%Y-%m-%d').date()

            try:
                dd = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                task = Task.objects.create(title=title, description=desc, issuing_date=isd, due_date=dd)
            except:
                task = Task.objects.create(title=title, description=desc, issuing_date=isd)
            pitch = Pitch.objects.create(team=team, task=task, senior=request.user ,candidate=candidate)
            if pitch:
                messages.add_message(request, messages.INFO, 'Pitched successfully!', extra_tags="pitch")

            # one last thing to do is to self recommend the candidate so that s/he is in 'MyCandidates'
            # if they previously accepted a recommendation, just ignore it, otherwise make one
            try:
                Recommendation.objects.get(candidate=candidate, recommended_senior=request.user)
            except:
                Recommendation.objects.create(status=True, reason='Pitched by self', candidate=candidate, recommending_senior=request.user, recommended_senior=request.user )

            # finally, redirect them to the profile page along with the message
            return redirect('recportal:profile', first_name=first_name, last_name=last_name)

        except:
            return HttpResponse('missing credentials.')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})

@login_required
def Pitches(request):
    ''' A simple view to render the pitches page where all created pitches are visible '''

    if request.method == 'GET':
        context = {}
        context['pitches'] = Pitch.objects.all()
        return render(request, 'recportal/pitches.html', context)

    else:
        return JsonResponse({'error_message':'Invalid request method.'})

@login_required
def RecommendCandidate(request, first_name, last_name):
    ''' the view for the form to recommend candidates to other seniors '''

    if request.method == 'GET':
        context = {}
        context['candidate'] = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        context['all_seniors'] = User.objects.all()
        return render(request, 'recportal/recommend.html', context)

    if request.method == 'POST':
        data = request.POST
        fn = data["senior"].split("-")[0]
        ln = data["senior"].split("-")[1]
        candidate = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        try:
            senior = User.objects.get(first_name=fn, last_name=ln)
        except:
            messages.add_message(request, messages.ERROR, 'Senior does not exist. Stay away from dev tools.', extra_tags="recommend")
            return redirect('recportal:profile', first_name=first_name, last_name=last_name)
        reason = data['reason']
        rec = Recommendation.objects.create(reason=reason, recommending_senior=request.user, recommended_senior=senior, candidate=candidate)
        if rec:
            messages.add_message(request, messages.INFO, 'Recommended successfully!', extra_tags="recommend")
        return redirect('recportal:profile', first_name=first_name, last_name=last_name)

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
                    pass

        return redirect('recportal:recommendations')


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

    if request.method == 'GET':
        logout(request)
        messages.add_message(request, messages.INFO, 'Signed out successfully.')
        return redirect('recportal:signin')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})
