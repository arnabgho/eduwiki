from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eduwiki.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^mongonaut/', include('mongonaut.urls')),

    url(r'^$', include('autoassess.urls')),
    url(r'^autoassess/', include('autoassess.urls')),
)
