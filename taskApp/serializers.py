from .models import Customer, Team, Workspace, List, Relationship_tables, Task, Attachments, SubmittedList
from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email',
                  'first_name',
                  'last_name'
                  )

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('team_name',
                  )

class   WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = (
                    'name',
                  )

class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = (
                    'name',
                  )

class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship_tables
        fields = (
                    'workspace',
                    'customer',
                    'role',
                    'list',
                    'task',
                    'check_status',
                    'priority'
                  )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
                    'name',
                    'frequency',
                    'dute_date',
                    'description',
                  )

class AttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = (
                    'task',
                    'file',
                    'name',
                  )

class SubmittedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedList
        fields = (
                    'submit_log',
                  )
