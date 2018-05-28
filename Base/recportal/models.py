import datetime

from django.db import models
from django.contrib.auth.models import User

class Senior(models.Model):
    ''' A user extention model for the seniors of the department who would
        be using this portal. It is associated with the Pitch model through a
        many-to-one relation.
        Note:
                1. Team must only be either:
                    a)  Backend
                    b)  Frontend
                    c)  App
                    d)  Graphics
                    e)  Video

                2. The Seniority Level denotes how many years above the first
                   year a member is.
                    a)  1 = Second Year
                    b)  2 = Third Year
                    c)  3 = Fourth Year
                    d)  4 = Fifth Year '''
    user = models.OneToOneField(User)
    team = models.CharField(max_length=10, default='None', blank=True)
    seniority_level = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name_plural = 'Senior Extention Data'

    def __str__(self):
        return self.user.get_full_name()

    def generateRecommendations(self):
        ''' return a dictionary where keys are candidates and the values are lists
            are recommending seniors. The senior parameter is the recommended senior. '''
        payload = {}
        for recommendation in self.user.recommended.all():
            if recommendation.candidate not in payload.keys():
                payload[recommendation.candidate] = [recommendation.recommending_senior]
            else:
                payload[recommendation.candidate].append(recommendation.recommending_senior)
        return payload


class Candidate(models.Model):
    ''' The stand-alone model for each candidate appearing for the department's
        recruitments. It is associated with the Pitch model as a one-to-one relation.
        recommended is for the recommendations feature'''
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    about = models.TextField(default='', blank=True)
    skill1 = models.CharField(max_length=100, default='', blank=True)
    skill2 = models.CharField(max_length=100, default='', blank=True)
    approved = models.BooleanField(default=False, blank=True)
    def get_full_name(self):
        string = "{} {}".format(self.first_name, self.last_name)
        return string

    def __str__(self):
        return self.get_full_name()

class Pitch(models.Model):
    ''' Whenever a candidate appears for recruitments they are surveyed by a senior
        department member and then if they are suitable, then they are "pitched" by
        that senior. During this time they are given a task and usually a deadline.
        This model accounts for these parameters. This model is in a way a mapping
        between seniors and the candidates they are reviewing.

        Note:
            The "approved" field denotes approval by THAT senior and is not equivalent
            to a comprehensive approval by the department, i.e. it is not the same as
            candidate.approved .

            Each senior - candidate relation is models via. a pitch and multiple
            pitches would most-likely exist per candidate and per senior.

            Also, again, team must only be either:
                a)  Backend
                b)  Frontend
                c)  App
                d)  Graphics
                e)  Video '''
    team = models.CharField(max_length=10, default='None', blank=True)
    task = models.OneToOneField('recportal.Task', null=True, blank=True)
    senior = models.ForeignKey(User, related_name='pitches', null=False)
    candidate = models.ForeignKey('recportal.Candidate', related_name='pitches', null=False)
    approved = models.BooleanField(default=False, blank=True)

    def __str__(self):
        string = "{} by  {}".format(self.candidate.get_full_name(), self.senior.get_full_name())
        return string

class Task(models.Model):
    ''' This model accounts for the task assigned by the senior to the candidate
        and is in a way an extention of th Pitch model. '''
    title = models.CharField(max_length=50, null=False)
    description = models.TextField(max_length=100, null=False)
    issuing_date = models.DateField(null=False)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    def is_casual(self):
        ''' Casual tasks are those without any due date. This function will
            return a boolean value indicating if it is a casual task. '''
        if self.due_date:
            return False
        else:
            return True

    def is_overdue(self):
        ''' Returns a boolean value indicating if a task is overdue.
            Case I:     casual task - False
            Case II:    still ongoing - False
            Case III:   completed on time - False
            Case IV:    overdue - True '''
        if not self.due_date:
            return False
        else:
        # this else may seem redundent but it improves readability, I often do this.
            if due_date - datetime.date.now() > 0:
                # before it's due
                return False
            else:
                # after the due date
                if due_date - completion_date > 0:
                    return False
                else:
                    return True

class Recommendation(models.Model):
    ''' To enable the recommendations feature we use this model. Seniors can
         recommend candidates to other seniors who can either accept to interview
         or the candidate or decline. Several much-needed methods are provided.
         (desc provided with each method)  '''
    status = models.BooleanField(default=False) # accepted to interview or not
    candidate = models.ForeignKey('recportal.Candidate', related_name="candidates", null=False)
    recommending_senior = models.ForeignKey(User, related_name='recommendations_made', null=False)
    recommended_seniors = models.ForeignKey(User, related_name='recommended', null=False)

    def __str__(self):
        string = "{} to {}".format(self.candidate.first_name, self.recommended_seniors.first_name)
        return string
