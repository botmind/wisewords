from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<quote_id>[0-9]+)/$', views.quote_detail, name='quote_detail'),
	url(r'^(?P<quote_id>[0-9]+)/vote/$', views.vote, name='vote'),
	url(r'^authors/(?P<author_id>[0-9]+)/$', views.author_quotes, name='author_quotes'),

]