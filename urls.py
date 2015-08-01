from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from lionheart.utils import simple_url
from lionheart.utils import template_url
from lionheart.utils import home_url
from lionheart.utils import status_204

admin.autodiscover()

urlpatterns = patterns('app.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^204$', status_204),
    home_url('home', None, 'app'),
)

urlpatterns += staticfiles_urlpatterns()

