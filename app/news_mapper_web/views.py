
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplo

from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from .models import Post, Comment, UserModel, NewsQuery, Source, Article
from .forms import EditPostForm, LoginForm, NewQueryForm
import os
import json
from .forms import UserCreationForm

from .api_mgr import QueryManager
from .map_mgr import GeoMapManager
from .metadata_mgr import MetadataManager

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplo


json_file = 'geo_data_for_news_choropleth.txt'

query_mgr = QueryManager()
geo_map_mgr = GeoMapManager()
meta_data_mgr = MetadataManager(json_file)

settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/templates/news_mapper_web/choropleths/')


def index(request):
    user = request.user
    form = LoginForm()
    if request.user.is_authenticated:
        logged_in = True
    else:
        logged_in = False

    return render(request, 'news_mapper_web/index.html', {
        'user': user,
        'logged_in': logged_in,
        'form': form
    })


class SignUp(generic.CreateView):
    model = UserModel
    form_class = UserCreationForm
    # success_url = reverse_lazy('login')
    # fields = ['unique_id', 'email', 'first_name', 'last_name', 'password']
    success_url = reverse_lazy('login')
    template_name = 'news_mapper_web/signup.html'
    # def get_success_url(self):
    #   return reverse_lazy('login')


def user_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('index')
    else:
        messages.error(request, 'Incorrect Password and/or Username')
        return redirect('index')
        # TODO - redirect to login page with invalid login message


def user_logout(request):
    logout(request)
    redirect(None)  # TODO - redirect to home


def new_newsquery(request):

    if request.method == 'GET':
        form = NewQueryForm()
        return render(request, 'news_mapper_web/search.html', {'search_form': form})

    elif request.method == 'POST':

        if meta_data_mgr.json_geo_data is None or meta_data_mgr.request_geo_data is None:
            meta_data_mgr.get_geo_data()
            meta_data_mgr.fix_cyprus_country_code()

        meta_data_mgr.write_json_to_file(
            meta_data_mgr.json_filename,
            meta_data_mgr.json_geo_data
        )

        meta_data_mgr.build_query_results_dict()

        try:
            source = Source.objects.get(pk=1)
        except UnicodeDecodeError:
            try:
                with open('./news_mapper_web/static/js/sources.json') as sources:
                    source_list = json.load(sources)
                    for source in source_list['sources'][0]:
                        api_id = source['id']
                        name = source['name']
                        description = source['description']
                        url = source['url']
                        category = source['category']
                        language = source['language']
                        country = source['country']

                        new_source = Source(api_id=api_id, category=category, country=country, description=description, language=language, name=name, url=url)
                        new_source.save()
            except (FileNotFoundError, Exception):
                source_list_txt = query_mgr.fetch_and_build_sources()
                query_mgr.write_sources_json_to_file(source_list_txt)

        except Source.DoesNotExist:
            try:
                with open('./news_mapper_web/static/js/sources.json') as sources:
                    source_list = json.load(sources)
                    for source in source_list['sources'][0]:
                        api_id = source['id']
                        name = source['name']
                        description = source['description']
                        url = source['url']
                        category = source['category']
                        language = source['language']
                        country = source['country']

                        new_source = Source(api_id=api_id, category=category, country=country, description=description, language=language, name=name,
                                            url=url)
                        new_source.save()

            except (FileNotFoundError, Exception):
                source_list_txt = query_mgr.fetch_and_build_sources()
                query_mgr.write_sources_json_to_file(source_list_txt)

        q_argument = request.POST.get('_argument')
        q_type = request.POST.get('_query_type')

        articles_list = query_mgr.query_api(query_argument=q_argument, query_type=q_type)

        query_object = NewsQuery(_query_type=q_type, _data=articles_list, _argument=q_argument)
        query_object.save()

        if articles_list:
            for article in articles_list:
                new_article = query_mgr.build_article_object(article, query_object)
                if new_article is not False:
                    new_article_pk = new_article.pk
                    try:
                        article_source_country = new_article.get_source_country()
                        if article_source_country:
                            country_a3_code = geo_map_mgr.get_country_alpha_3_code(article_source_country)
                            meta_data_mgr.query_data_dict[country_a3_code] += 1
                    except AttributeError:
                        try:
                            article = Article.objects.get(pk=new_article_pk)
                            country = article.get_source_country()
                            print('Country = ' + str(country))
                            if country:
                                country_a3_code = geo_map_mgr.get_country_alpha_3_code(country)
                                meta_data_mgr.query_data_dict[country_a3_code] += 1
                        except AttributeError:
                            pass

            choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)

            choropleth = choropleth_data_tuplet[0]
            choro_html = choropleth_data_tuplet[1]
            choro_filename = choropleth_data_tuplet[2]
            # choro_html_splice = str(choro_html[16:-1])
            # choro_html_updated = '<html lang="en">' + choro_html_splice
            query_pk = query_object.pk
            print('choro_html = ' + choro_html[0:1000])

            NewsQuery.objects.filter(pk=query_pk).update(_choropleth=choropleth, _choro_html=choro_html, _filename=choro_filename)

            query_object = NewsQuery.objects.get(pk=query_pk)

            html_pre = str(query_object.choro_html[0:1000])
            print('str(html_pre) = ' + str(html_pre))
            print('redirect.query_object.pk = ' + str(query_object.pk))

            article_instances = [x for x in Article.objects.filter(_query=query_object)]

            for x in article_instances:
                print('article_instance type = ' + str(type(x)))

            # return redirect('query_result_detail',  news_query_pk=query_object.pk, articles=article_instances)

            # return redirect('query_result_detail', news_query_pk=query_object.pk)

            choro_file_path = CHORO_MAP_ROOT + query_object.filename

            return render(request, 'news_mapper_web/query_results.html', {'news_query': query_object, 'articles': article_instances, 'choro_filepath': choro_file_path})



def choro_map(request, choro_file_name):

    print('TYPE choro_file_name = ' + str(type(choro_file_name)))
    choro_path = CHORO_MAP_ROOT + choro_file_name
    return render(request, choro_path)


# @login_required(login_url='/accounts/login/')
def view_newsquery(request, news_query_pk):

    print('in newsquery views.py')
    print('news_query_pk = ' + str(news_query_pk))
    query = NewsQuery.objects.get(pk=news_query_pk)

    if query:
        html_pre = query.choro_html
        print('Meta Type: ' + str(type(query)))
        print('html = ' + (html_pre[0:300]))
        print('type = ' + query.query_type)
        # print('filename = ' + str(query.filename))
        print('type(choropleth = ' + str(type(query.choropleth)))
        print('argument = ' + query.argument)
        return render(request, 'news_mapper_web/query_results.html', {'news_query': query})


# @login_required()
def save_query(request):
    return None


# @login_required()
def user_page(request):
    return None


# @login_required()
def view_post(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.info(request, 'Post Details Updated')
        else:
            messages.error(request, form.errors)
        return redirect('post_details', post_pk=post_pk)

    else: # GET request
        if post.user.id == request.user.id:
            edit_post_form = EditPostForm(instance=post) # Pre-populate form with the post's current field values
            return render(request, 'news_mapper_web/post_details.html', { 'post': post, 'edit_post_form': edit_post_form})
        else: # user is not OP
            return render(request, 'news_mapper_web/post_details.html', { 'post': post })


#@login_required()
def delete_post(request):
    pk = request.POST['post_pk']
    post = get_object_or_404(Post, pk=pk)
    if post.user.id == request.user.id:
        post.delete()
        messages.info(request, 'Post Removed')
        return redirect('index')
    else:
        messages.error(request, 'Action Not Authorized')


#@login_required()
def delete_comment(request):
    pk = request.POST['comment_pk']
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user.id == request.user.id:
        comment.delete()
        messages.info(request, 'Comment Removed')
        return redirect('index')
    else:
        messages.error(request, 'Action Not Authorized')