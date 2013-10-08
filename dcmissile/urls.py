from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from dcmissile.www.urls import urlpatterns as www_urls

urlpatterns = www_urls
urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
