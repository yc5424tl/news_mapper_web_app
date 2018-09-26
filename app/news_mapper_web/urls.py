from django.conf.urls import url
from django.contrib.auth import views as auth_views
#
from django.conf import settings
#
from django.urls import include, path
from .models import User
from django.urls import path

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^query/new/$', views.new_query, name='new_query'),
    url(r'^query/view/(?P<query_pk>\d+)$', views.view_query, name='view_query'),
    url(r'^query/delete/(?P<query_pk>\d+)$', views.delete_query, name='delete_query'),

    # url(r'^save_query/(?P<news_query_pk>\d+)$', views.save_query, name='delete_query'),

    url(r'^post/new/$', views.new_post, name='new_post'),
    url(r'^post/view/(?P<post_pk>\d+)$', views.view_post, name='view_post'),
    url(r'^post/update/(?P<post_pk>\d+)$', views.update_post, name='update_post'),
    url(r'^post/delete/(?P<post_pk>\d+)$', views.delete_post, name='delete_post'),

    url(r'^comment/new/(?P<post_pk>\d+)$', views.new_comment, name='new_comment'),
    url(r'^comment/view/(?P<comment_pk>\d+)$', views.view_comment, name='view_comment'),
    url(r'^comment/delete/(?P<comment_pk>\d+)$', views.delete_comment, name='delete_comment'),

    url(r'^accounts/register/$', views.register_user, name='register_user'),
    # url(r'^accounts/login/$', views.login_user, name='login_user'),
    # url(r'^accounts/logout/$', views.logout_user, name='logout_user'),
    url(r'^accounts/view/(?P<member_pk>\d+)$', views.view_user, name='view_user'),

    url(r'^sources/$', views.view_sources, name='view_sources'),

    url(r'^test_page/$', views.view_test_page, name='view_test_page'),

    # url(r'^login_user/$', views.login_user, name='login_user'),
    # url(r'^logout_user/$', views.logout_user, name='logout_user'),
]



# ----- Generated urls from import django.contrib.auth.views in project.urls -----
#
# accounts/login/                  [name='login']
# accounts/logout/                 [name='logout']
# accounts/password_change/        [name='password_change']
# accounts/password_change/done/   [name='password_change_done']
# accounts/password_reset/         [name='password_reset']
# accounts/password_reset/done/    [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/             [name='password_reset_complete']