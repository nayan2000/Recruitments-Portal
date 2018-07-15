import os
import re
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from recportal.mimeTypes import MIME_TYPES
from recportal.models import *


@login_required
def Candidates(request):
    ''' the view to render the candidates page '''

    if request.method == 'GET':
        context = {}
        context['data'] = Candidate.objects.all()
        return render(request, 'recportal/candidates.html', context)

    if request.method == 'POST':
        # for when the candidate is being updated
        data = request.POST
        try:
            first_name = data['first_name'].replace(' ', '_')

            last_name = data['last_name'].replace(' ', '_')

            ph = data["ph"]
            if not re.match(r'(^[0-9]{10}$)', ph):
                if not re.match(r'^91([0-9]{10})$', ph):
                	messages.add_message(request, messages.ERROR, 'Invalid phone number.')
                	return redirect('recportal:candidates')

            email = data["email"]
            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email):
                messages.add_message(request, messages.ERROR, 'Invalid email address.')
                return redirect('recportal:candidates')

            try:
                skill1 = data['skill1']
            except:
                skill1 = ''
            try:
                skill2 = data['skill2']
            except:
                skill2 = ''
            try:
                about = data['about']
            except:
                about = ''

        except Exception as err:
            print(err)
            messages.add_message(request, messages.ERROR, 'Essential data missing.')
            return redirect('recportal:candidates')

        Candidate.objects.create(first_name=first_name, last_name=last_name, ph=ph, email=email, skill1=skill1, skill2=skill2, about=about ,pitched=False)
        messages.add_message(request, messages.INFO, 'Candidate successfully created!')
        return redirect('recportal:candidates')

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
def Download(request, filename):
    try:
        filetype = filename.split(".")[-1]
    except IndexError: # default to text
        filetype = "txt"
    try:
        mimetype = MIME_TYPES[filetype]
    except KeyError:
        filetype = "txt"
        mimetype = "text/plain"
    with open(os.path.join(settings.MEDIA_ROOT, filename), "rb") as f:
        response = HttpResponse(f.read(), content_type=mimetype)
        response["Content-Disposition"] = "inline; filename=" + filename
    return response



@login_required
def EditCandidate(request, first_name, last_name):

    if request.method == "POST":
        candidate = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        data = request.POST
        try:
            candidate.first_name = data['first_name'].replace(' ', '_')

            candidate.last_name = data['last_name'].replace(' ', '_')

            ph = data["ph"]
            if not re.match(r'(^[0-9]{10}$)', ph):
                if not re.match(r'^91([0-9]{10})$', ph):
                    messages.add_message(request, messages.ERROR, 'Invalid phone number.', extra_tags="edit")
                    return redirect('recportal:profile', first_name, last_name)
            else:
                candidate.ph = ph

            email = data["email"]
            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email):
                messages.add_message(request, messages.ERROR, 'Invalid email address.', extra_tags="edit")
                return redirect('recportal:profile', first_name, last_name)
            else:
                candidate.email = email

            try:
                candidate.skill1 = data['skill1']
            except:
                candidate.skill1 = ''
            try:
                candidate.skill2 = data['skill2']
            except:
                candidate.skill2 = ''
            try:
                candidate.about = data['about']
            except:
                candidate.about = ''

        except Exception as err:
            print(err)
            messages.add_message(request, messages.ERROR, 'Essential data missing.', extra_tags="edit")
            return redirect('recportal:profile', candidate.first_name, candidate.last_name)

        print(data);
        candidate.save()
        messages.add_message(request, messages.INFO, 'Candidate successfully edited!', extra_tags="edit")
        return redirect('recportal:profile', candidate.first_name, candidate.last_name)

    else:
        return JsonResponse({"message": "invalid request method."})

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
def MyAssessments(request):

    if request.method == 'GET':
        context = {}
        context['myassessments'] = request.user.assessments.all()
        return render(request, 'recportal/myassessments.html', context)

    if request.method == 'POST':
        data = request.POST
        candidate = get_object_or_404(Candidate, first_name=data['candidate'].split('-')[0], last_name=data['candidate'].split('-')[1])
        assessment = get_object_or_404(Assessment, candidate=candidate, senior=request.user)
        assessment.task.completion_date = datetime.datetime.strptime(data['doc'], '%Y-%m-%d').date()
        try:
            if data['pitched']:
                assessment.pitched = True
        except:
            pass
        assessment.task.save()
        assessment.save()
        messages.add_message(request, messages.INFO, 'Task updated successfully!')
        return redirect('recportal:myassessments')

    else:
        return JsonResponse({'error_message':'Invalid request method.'})


@login_required
def AssessCandidate(request, first_name, last_name):
    ''' the view for the form to assess candidates '''

    if request.method == 'GET':
        context = {}
        context['candidate'] = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        return render(request, 'recportal/assess.html', context)

    if request.method == 'POST':
        # don't forget to make a verification script
        data = request.POST
        # first, don't let the same senior assess the same candidate more than once
        try:
            candidate= get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
            p = Assessment.objects.get(candidate=candidate, senior=request.user)
            if p:
                messages.add_message(request, messages.ERROR, 'You have already assessed this candidate', extra_tags="assessment")
            return redirect('recportal:profile', first_name=first_name, last_name=last_name)
        except:
            pass
        # then, make sure that all of the data is valid and create the new assessment
        possible_teams = ['App Dev', 'Backend', 'Frontend', 'Graphics', 'Video']
        try:
            team = data['team']
            if team not in possible_teams:
                messages.add_message(request, messages.ERROR, 'Assessment cancelled due to providing an invalid team. Stay away from dev tools.', extra_tags="assessment")
                return redirect('recportal:profile', first_name=first_name, last_name=last_name)
            title = data['title']
            desc = data['description']

            isd = datetime.datetime.strptime(data['issuing_date'], '%Y-%m-%d').date()

            if "rubric" in data.keys():
                rubric = data["rubric"]
                # no extra security measures are taken to check the type of the file uploaded
                # since this webapp is closed only to member of a department, there is no need for it.
            else:
                rubric = None

            try:
                dd = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                task = Task.objects.create(title=title, description=desc, issuing_date=isd, due_date=dd, candidate=candidate, rubric=rubric)
            except:
                task = Task.objects.create(title=title, description=desc, issuing_date=isd, candidate=candidate, rubric=rubric)
            assessment = Assessment.objects.create(team=team, task=task, senior=request.user ,candidate=candidate)
            if assessment:
                messages.add_message(request, messages.INFO, 'Assessment added successfully!', extra_tags="assessment")

            # one last thing to do is to self recommend the candidate so that s/he is in 'MyCandidates'
            # if they previously accepted a recommendation, just ignore it, otherwise make one
            try:
                Recommendation.objects.get(candidate=candidate, recommended_senior=request.user)
            except:
                Recommendation.objects.create(status=True, reason='Assessed by self', candidate=candidate, recommending_senior=request.user, recommended_senior=request.user )

            # finally, redirect them to the profile page along with the message
            return redirect('recportal:profile', first_name=first_name, last_name=last_name)

        except Exception as err:
            return HttpResponse('missing credentials. {}'.format(err))

    else:
        return JsonResponse({'error_message':'Invalid request method.'})

@login_required
def Assessments(request):
    ''' A simple view to render the assessments page where all created assessments are visible '''

    if request.method == 'GET':
        context = {}
        context['assessments'] = Assessment.objects.all()
        return render(request, 'recportal/assessments.html', context)

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
        mode = data["mode"]
        reason = data['reason']
        candidate = get_object_or_404(Candidate, first_name=first_name, last_name=last_name)
        if mode == "induvisual":
            fn = data["senior"].split("-")[0]
            ln = data["senior"].split("-")[1]
            try:
                senior = User.objects.get(first_name=fn, last_name=ln)
            except:
                messages.add_message(request, messages.ERROR, 'Senior does not exist. Stay away from dev tools.', extra_tags="recommend")
                return redirect('recportal:profile', first_name=first_name, last_name=last_name)
            rec = Recommendation.objects.create(reason=reason, recommending_senior=request.user, recommended_senior=senior, candidate=candidate)
        elif mode == "team":
            for senior in Senior.objects.filter(team=data["team"]):
                Recommendation.objects.create(reason=reason, recommending_senior=request.user, recommended_senior=senior.user, candidate=candidate)
            rec = True
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
