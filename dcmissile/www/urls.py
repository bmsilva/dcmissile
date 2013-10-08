from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dcmissile.www.views',
    url(r'^$', 'home', name="home"),
)
