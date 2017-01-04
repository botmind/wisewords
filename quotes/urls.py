from django.conf.urls import url

from . import views

app_name = 'quotes' #add a namespace in order to differentiate this app from others on the same site
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<quote_id>[0-9]+)/$', views.quote_detail, name='quote_detail'),
	url(r'^(?P<quote_id>[0-9]+)/vote/$', views.vote, name='vote'),
	url(r'^authors/(?P<author_id>[0-9]+)/$', views.author_quotes, name='author_quotes'),
	url(r'^new_quote/$', views.new_quote, name='new_quote'),

]