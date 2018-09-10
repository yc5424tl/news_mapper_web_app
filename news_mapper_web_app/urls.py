from django.conf.urls import url

from . import views

urlpatters = [
    url(r'^$', views.front_page, name='front_page'),
    url(r'^search$', views.new_search, name='new_search'),
    url(r'^post/(?P<post_pk>\d+)$', views.post_details, name='post_details'),
    url(r'delete_post/$', views.delete_post, name='delete_post'),
    url(r'delete_comment/$', views.delete_comment, name='delete_comment')
]