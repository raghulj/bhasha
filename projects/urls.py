from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('projects.views',
            url(r'^$','home'),
            url(r'^(?P<project_id>\d+)/languages/$','list_languages'),
            url(r'^(?P<project_id>\d+)/catalogue/$','catalogue'),
            url(r'^(?P<project_id>\d+)/translations/(?P<language_id>\d+)/list/$','list_catalogue'),

            url(r'^(?P<project_id>\d+)/languages/(?P<language_id>\d+)/translations/$','translations'),
            url(r'^(?P<project_id>\d+)/translations/(?P<language_id>\d+)/$','update_translations'),
            # url(r'^create/$','create'),
            # url(r'^socialinfo/create/(?P<eid>\d+)/$','create_socialinfo'),
            # url(r'^socialinfo/edit/(?P<eid>\d+)/$','edit_socialinfo'),
            # url(r'^new/$','new'),
            # url(r'^view/(?P<eid>\d+)/$','view'),
            # url(r'^edit/(?P<eid>\d+)/$','edit_event'),
            # url(r'^get/$','get_events'),
            # url(r'^public/(?P<eid>\d+)/$','public_page'),
            # url(r'^publish/$','publish'),            
            # url(r'^unpublish/$','unpublish'),        
            # url(r'^delete/(?P<eid>\d+)/$','delete'),
            # url(r'^verify_domain/$','verify_subdomain'),
            )

