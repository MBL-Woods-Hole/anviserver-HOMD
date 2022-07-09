from django.conf.urls import include, handler400, handler403, handler404, handler500
from django.urls import path, re_path
from django.contrib import admin
from registration.forms import RegistrationForm
from registration.backends.simple.views import RegistrationView

from main.views import projects, index, interactive, teams, profile, redirect, settings, pangenomes
from main.forms import UserRegForm
from main import backend

class MyRegistrationView(RegistrationView):
        def get_success_url(self, request):
            return '/'
            
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^accounts/settings/$', settings.show_settings, name="user_settings"),
    re_path(r'^accounts/register/$', MyRegistrationView.as_view(form_class=UserRegForm), {'backend': 'registration.backends.simple.DefaultBackend'}, name='registration_register'),
    re_path(r'^accounts/', include('registration.backends.simple.urls')),
    re_path(r'^(?P<access_type>public|private)/(?P<username>\w+)/(?P<share_name>\w+)', redirect.redirect_view, name="redirect_view"),
    re_path(r'^projects/new', projects.new_project, name="projects_new"),
    re_path(r'^projects/details/(?P<project_slug>\w+)', projects.details_project, name="projects_details"),
    re_path(r'^projects/share/(?P<project_slug>\w+)', projects.share_project, name="projects_share"),
    re_path(r'^projects', projects.list_projects, name="projects"),
    re_path(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/members', teams.list_members, name="teams_members"),
    re_path(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/projects', teams.list_projects, name="teams_projects"),
    re_path(r'^teams', teams.list_teams, name="teams"),
    
    re_path(r'^p/(?P<short_link_key>\w+)', interactive.short_link_redirect, name='short_link_redirect'),
    
    
    
    re_path(r'^(?P<username>\w+)/(?P<project_slug>\w+)/download', interactive.download_zip, name="download_zip"),
    #re_path('ajax/(?P<username>\w+)/(?P<project_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler),
    #re_path('ajax_pangenome/(?P<pangenome_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler_pangenome),
    re_path('ajax_pangenome/(?P<pangenome_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler_pangenome, name='ajax_pangenome'),
    path('pangenomes/<pangenome>', interactive.show_pangenome_interactive, name="show_pangenome_interactive"),
    path('pangenomes/<pangenome>', interactive.anvi_display_pan_testing, name="anvi_display_pan_testing"),
    
    
    path('home', index.show_index),
    path('pangenomes', pangenomes.list_pangenomes, name="pangenomes"),
    path('anviserver/pangenomes', pangenomes.list_pangenomes, name="pangenomes"),
    path('anviserver/<pangenome>', interactive.anvi_display_pan_testing, name="anvi_display_pan_testing" ),
    
    path('pangenomes/<pangenome>/download', pangenomes.download_pangenome_zip, name="download_pangenome_zip"),
   
    
   
    re_path(r'^$', index.show_index, name='index'),
]

# handler400 = index.show_error_page
# handler403 = index.show_error_page
# handler404 = index.show_error_page
# handler500 = index.show_error_page
