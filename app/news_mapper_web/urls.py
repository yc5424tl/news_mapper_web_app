from django.conf.urls import url
from django.urls import include, path

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.new_newsquery, name='search'),
    url(r'^post/(?P<post_pk>\d+)$', views.view_post, name='view_post'),
    url(r'delete_post/$', views.delete_post, name='delete_post'),
    url(r'delete_comment/$', views.delete_comment, name='delete_comment'),
    url(r'^signup/$', views.SignUp.as_view(), name='signup'),
    url(r'^accounts/login/$', views.user_login, name='login'),
    url(r'^media/news_mapper_web/html/(?P<choro_file_name>\d+)$', views.choro_map, name='choro_map'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# ----- Generated urls from accounts path above -----
#
# accounts/login/                  [name='login']
# accounts/logout/                 [name='logout']
# accounts/password_change/        [name='password_change']
# accounts/password_change/done/   [name='password_change_done']
# accounts/password_reset/         [name='password_reset']
# accounts/password_reset/done/    [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/             [name='password_reset_complete']