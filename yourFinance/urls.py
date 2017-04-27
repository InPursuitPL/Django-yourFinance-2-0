from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/register/$', views.register_page, name='register'),
    url(r'^add_data/$', views.add_data, name='add data'),
    url(r'^view_data/$', views.view_data, name='view data'),
    url(r'^edit_stash/(?P<pk>\d+)$', views.edit_stash, name='edit stash'),
    url(r'^edit_month/(?P<pk>\d+)$', views.edit_month, name='edit month'),
    url(r'^delete_stash/(?P<pk>\d+)$', views.delete_stash, name='delete stash'),
    url(r'^delete_month/(?P<pk>\d+)$', views.delete_month, name='delete month'),
    url(r'^delete_year/(?P<pk>\d+)$', views.delete_year, name='delete year'),
    url(r'^analyze_month/$', views.analyze_month, name='analyze month'),
    url(r'^configure_deposition_places/$',
        views.configure_deposition_places,
        name='configure deposition places'),
    url(r'^configure_monthly_costs/$',
        views.configure_monthly_costs,
        name='configure monthly costs'),
    url(r'^configure_cost_groups/$',
        views.configure_cost_groups,
        name='configure cost groups'),
]
