from django.conf.urls import url, include, handler400, handler403, handler404, handler500
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
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/settings/$', settings.show_settings, name="user_settings"),
    url(r'^accounts/register/$', MyRegistrationView.as_view(form_class=UserRegForm), {'backend': 'registration.backends.simple.DefaultBackend'}, name='registration_register'),
    #url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegForm)),
    
    url(r'^accounts/', include('registration.backends.simple.urls')),


    url(r'^(?P<access_type>public|private)/(?P<username>\w+)/(?P<share_name>\w+)', redirect.redirect_view, name="redirect_view"),

    url(r'^projects/new', projects.new_project, name="projects_new"),
    url(r'^projects/details/(?P<project_slug>\w+)', projects.details_project, name="projects_details"),
    url(r'^projects/share/(?P<project_slug>\w+)', projects.share_project, name="projects_share"),
    url(r'^projects', projects.list_projects, name="projects"),

    url(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/members', teams.list_members, name="teams_members"),
    url(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/projects', teams.list_projects, name="teams_projects"),
    url(r'^teams', teams.list_teams, name="teams"),
    
    url(r'^pangenomes', pangenomes.list_pangenomes, name="pangenomes"),
    #url(r'^(?P<pangenome>\w+)', interactive.show_pangenome_interactive, name="show_pangenome_interactive"),
    
    url(r'^p/(?P<short_link_key>\w+)', interactive.short_link_redirect, name='short_link_redirect'),
    url(r'^ajax/(?P<username>\w+)/(?P<project_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler),
    url(r'^(?P<username>\w+)/(?P<project_slug>\w+)/download', interactive.download_zip, name="download_zip"),
    url(r'^(?P<username>\w+)/(?P<project_slug>\w+)/(?P<inspection_type>\w+)', interactive.show_inspect, name="show_inspect"),
    url(r'^(?P<username>\w+)/(?P<project_slug>\w+)', interactive.show_interactive, name="show_interactive"),

    url(r'^(?P<username>\w+)', profile.show_user_profile, name="user_profile"),

    url(r'^$', index.show_index, name='index'),
]

# handler400 = index.show_error_page
# handler403 = index.show_error_page
# handler404 = index.show_error_page
# handler500 = index.show_error_page
