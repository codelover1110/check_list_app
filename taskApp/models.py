from django.db import models

# Create your models here.
class Customer(models.Model):
    email = models.CharField(max_length=350, blank=True, default='')
    first_name = models.CharField(max_length=350, blank=True, default='')
    last_name = models.CharField(max_length=350, blank=True, default='')
    verify_code = models.CharField(max_length=70, blank=True, default='')
    verify_token = models.CharField(max_length=70, blank=True, default='')

# Create your models here.
class Team(models.Model):
    team_name = models.CharField(max_length=350, blank=True, default='')

class TeamMember(models.Model):
    team_id = models.ForeignKey(Team, related_name='teammembers', on_delete=models.CASCADE, blank=True,
                                       null=True)
    email = models.CharField(max_length=350, blank=True, default='')

class Workspace(models.Model):
    name = models.CharField(max_length=350, blank=True, default='')


class List(models.Model):
    name = models.CharField(max_length=350, blank=True, default='')
    # workspace_id = models.ForeignKey(Workspace, related_name='workspace', on_delete=models.CASCADE, blank=True,
    #                                    null=True)

class Task(models.Model):
    name = models.CharField(max_length=350, blank=True, default='')
    frequency = models.CharField(max_length=350, blank=True, default='', null=True)
    dute_date = models.DateField(blank= True,null=True)
    description = models.CharField(max_length=350, blank=True, default='', null=True)

class Attachments(models.Model):
    task = models.ForeignKey(Task, related_name='task_id', on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='media/', max_length=254, blank=True, default='')
    name = models.CharField(max_length=350, blank=True, default='')

class Relationship_tables(models.Model):
    workspace = models.ForeignKey(Workspace, related_name='workspace', on_delete=models.CASCADE, blank=True,
                                       null=True)
    role = models.CharField(max_length=350, blank=True, default='')
    customer = models.ForeignKey(Customer, related_name='user', on_delete=models.CASCADE, blank=True,
                                       null=True)
    list = models.ForeignKey(List, related_name='list', on_delete=models.CASCADE, blank=True,
                                       null=True)
    task = models.ForeignKey(Task, related_name='task', on_delete=models.CASCADE, blank=True,
                                       null=True)
    priority = models.CharField(max_length=350, blank=True, default='')
    check_status= models.BooleanField(default=0)
    
class SubmittedList(models.Model):
   submit_log = models.JSONField(null=False)
#    submit_log = models.TextField(null=False)

