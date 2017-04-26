from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/register/$', views.register_page, name='register'),
    url(r'^add_data/$', views.add_data, name='add data'),
    url(r'^view_data/$', views.view_data, name='view data'),
    url(r'^edit_stash/(?P<pk>\d+)$', views.edit_stash, name='edit stash'),
]
