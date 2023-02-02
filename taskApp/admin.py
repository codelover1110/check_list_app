from django.contrib import admin, messages
from django.db.models import Subquery
from django.http import HttpResponseRedirect
from django.views import generic
from pyparsing import Or
import stripe
from django.shortcuts import render, redirect
from django.core.mail import send_mail

# Register your models here.
from .models import Customer, Team, Workspace, List, Relationship_tables
from django.urls import path

import requests
import json


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('email',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name',)
    search_fields = ('team_name',)
    list_filter = ('team_name',)

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

class ListAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'role', 'customer', 'list')
    search_fields = ('workspace', 'role', 'customer', 'list')
    list_filter = ('workspace', 'role', 'customer', 'list')
    





admin.site.register(Customer, CustomerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(Relationship_tables, RelationshipAdmin)
