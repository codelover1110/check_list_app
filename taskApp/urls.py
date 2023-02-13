from django.contrib import admin
from django.urls import include, re_path as url
from . import views
from django.urls import path

admin.site.site_title = "Qatar Foundation"
admin.site.site_header = "Admin Panel"
admin.site.index_title = "Welcome to the portal"


urlpatterns = [ 
    url(r'^api/customer_signup$', views.customer_signup),
    url(r'^api/customer_signin$', views.customer_signin),
    url(r'^api/customer_verify$', views.customer_verify),
    url(r'^api/customer_list$', views.customer_list),

    # Workspace
    url(r'^api/create_workspace$', views.create_workspace),
    url(r'^api/get_all_workspaces$', views.get_all_workspaces),
    url(r'^api/get_workspace_users$', views.get_workspace_users),

    # List
    url(r'^api/create_list$', views.create_list),
    url(r'^api/get_list/workspace_id/(?P<pk>[0-9]+)$', views.get_list),
    url(r'^api/get_list_users$', views.get_list_users),

    # Task
    url(r'^api/create_task$', views.create_task),
    url(r'^api/submit_list$', views.submit_list),
    url(r'^api/get_task_by_list$', views.get_task_by_list),
    url(r'^api/check_task$', views.check_task),
    url(r'^api/remove_task$', views.remove_task),
    url(r'^api/uncheck_task$', views.uncheck_task),
    path('api/uncheck_task/frequency/<str:frequency>', views.uncheck_task_frequency),
    path('api/check_task/frequency/<str:frequency>', views.check_task_frequency),

    # Member
    url(r'^api/invite_member_workspace$', views.invite_member_workspace),

]