import os
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Senior(models.Model):
    ''' A user extention model for the seniors of the department who would
        be using this portal. It is associated with the Assessment model through a
        many-to-one relation.
        Note:
                1. Team must only be either:
                    a)  Backend
                    b)  Frontend
                    c)  App Dev
                    d)  Graphics
                    e)  Video

                2. The Seniority Level denotes how many years above the first
                   year a member is.
                    a)  1 = Second Year
                    b)  2 = Third Year
                    c)  3 = Fourth Year
                    d)  4 = Fifth Year '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.CharField(max_length=10, default='None', blank=True)
    seniority_level = models.IntegerField(default=0, blank=True)

    class Meta():
        verbose_name_plural = 'Senior Extention Data'

    def __str__(self):
        return self.user.get_full_name()

    def getActiveRecommendations(self):
        ''' return a dictionary where keys are candidates and the values are lists
            of tuples of (recommending seniors, reason for recommendation). The senior parameter is the recommended senior. '''
        payload = {}
        for recommendation in self.user.recommended.all():
            if recommendation.status == False:
                if recommendation.candidate not in payload.keys():
                    payload[recommendation.candidate] = [(recommendation.recommending_senior, recommendation.reason)]
                else:
                    payload[recommendation.candidate].append((recommendation.recommending_senior, recommendation.reason))
        return payload

    @property
    def active_recommendations_count(self):
        return len(self.getActiveRecommendations())

    def getCandidates(self):
        payload = set()
        for recommendation in self.user.recommended.all():
            if recommendation.status == True:
                payload.add(recommendation.candidate)
        return payload

class Candidate(models.Model):
    ''' The stand-alone model for each candidate appearing for the department's
        recruitments. It is associated with the Assessment model as a one-to-one relation.
        recommended is for the recommendations feature'''
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    ph = models.CharField(max_length=12, null=False)
    email = models.EmailField(null=False)
    about = models.TextField(default='', blank=True)
    skill1 = models.CharField(max_length=100, default='', blank=True)
    skill2 = models.CharField(max_length=100, default='', blank=True)
    pitched = models.BooleanField(default=False, blank=True) # approved by the DVM as a whole

    class meta():
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        string = "{} {}".format(self.first_name, self.last_name)
        return string

class Assessment(models.Model):
    ''' Whenever a candidate appears for recruitments they are surveyed by a senior
        department member and then if they are suitable, then they are assessd by
        that senior. During this time they are given a task and usually a deadline.
        This model accounts for these parameters. This model is in a way a mapping
        between seniors and the candidates they are reviewing.

        Note:
            The "approved" field denotes approval by THAT senior and is not equivalent
            to a comprehensive approval by the department, i.e. it is not the same as
            candidate.approved . This should be given after the completion of the task.

            Each senior - candidate relation is represented via. an assessment and multiple
            assessments would most-likely exist per candidate and per senior.

            However, each senior can only assess a particular candidate only once.

            Also, again, team must only be either:
                a)  Backend
                b)  Frontend
                c)  App Dev
                d)  Graphics
                e)  Video '''
    team = models.CharField(max_length=10, default='None', blank=True)
    task = models.OneToOneField('recportal.Task', null=True, blank=True, on_delete=models.CASCADE)
    senior = models.ForeignKey(User, related_name='assessments', null=False, on_delete=models.CASCADE)
    candidate = models.ForeignKey('recportal.Candidate', related_name='assessments', null=False, on_delete=models.CASCADE)
    pitched = models.BooleanField(default=False, blank=True) # approved by the assessing candidate

    class meta():
        order_with_respect_to = 'candidate'

    def __str__(self):
        string = "{} by  {}".format(self.candidate.get_full_name(), self.senior.get_full_name())
        return string


class Task(models.Model):
    ''' This model accounts for the task assigned by the senior to the candidate
        and is in a way an extention of the Assessment model. '''
    title = models.CharField(max_length=50, null=False)
    candidate = models.ForeignKey(Candidate, related_name="tasks", null=False, blank=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=100, null=False)
    issuing_date = models.DateField(null=False)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    rubric = models.FileField(upload_to="", default=None, blank=True)

    def __str__(self):
        return self.title

    @property               # doing this allows us to call it conveniently in templates
    def is_casual(self):
        ''' Casual tasks are those without any due date. This function will
            return a boolean value indicating if it is a casual task. '''
        if self.due_date:
            return False
        else:
            return True

    @property
    def is_ongoing(self):
        if self.completion_date:
            return False
        else:
            return True


    @property
    def is_overdue(self):
        ''' Returns a boolean value indicating if a task is overdue.
            Case I:     casual task - False
            Case II:    still ongoing - False
            Case III:   completed on time - False
            Case IV:    overdue - True '''
        if not self.due_date:
            return False    # case I
        else:
            if self.completion_date:
                dt = self.completion_date
            else:
                dt = datetime.date.today()
            if dt > self.due_date:
                return True # case IV
            else:
                return False # cases II and III

class Recommendation(models.Model):
    ''' To enable the recommendations feature we use this model. Seniors can
         recommend candidates to other seniors who can either accept to interview
         or the candidate or decline. '''
    status = models.BooleanField(default=False) # accepted to interview or pending recommendation
    reason = models.TextField(default="Just like that")
    candidate = models.ForeignKey('recportal.Candidate', related_name="candidates", null=False, on_delete=models.CASCADE)
    recommending_senior = models.ForeignKey(User, related_name='recommendations_made', null=False, on_delete=models.CASCADE)
    recommended_senior = models.ForeignKey(User, related_name='recommended', null=False, on_delete=models.CASCADE)

    def __str__(self):
        string = "{} to {}".format(self.candidate.first_name, self.recommended_senior.first_name)
        return string
