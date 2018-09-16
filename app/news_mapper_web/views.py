from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from .models import Post, Comment, UserModel, NewsQuery, Source
from .forms import EditPostForm, EditCommentForm, LoginForm, NewQueryForm
import os
from .forms import UserCreationForm

from .api_mgr import QueryManager
from .map_mgr import GeoMapManager
from .metadata_mgr import MetadataManager

from sqlite3 import OperationalError

json_file = 'geo_data_for_news_choropleth.txt'

query_mgr = QueryManager()
geo_map_mgr = GeoMapManager()
meta_data_mgr = MetadataManager(json_file)

settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/media/news_mapper_web/html/')


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
            print('source: ' + str(source))
        except Source.DoesNotExist:
            source_list_txt = query_mgr.fetch_and_build_sources()
            query_mgr.write_sources_json_to_file(source_list_txt)

        q_argument = request.POST.get('_argument')
        q_type = request.POST.get('_query_type')

        articles_list = query_mgr.query_api(query_argument=q_argument, query_type=q_type)
        # query_mgr.query_api('Scientists', )

        #  user_model = UserModel.objects.get(email=request.user.email)

        # query_object = NewsQuery(user=user_model, query_type=q_type, data=articles_list, argument=argument)

        query_object = NewsQuery(_query_type=q_type, _data=articles_list, _argument=q_argument)
        query_object.save()

        if articles_list:

            #print('Articles List: ')
            #print(articles_list)
            for article in articles_list:
                #print('article from article in articles (views.py 114) == ' + str(article))
                new_article = query_mgr.build_article_object(article, query_object)
                #print('new_article.source: ' + str(new_article.source))
                article_source_country = new_article.get_source_country()
                if article_source_country:
                    country_a3_code = geo_map_mgr.get_country_alpha_3_code(article_source_country)
                    meta_data_mgr.query_data_dict[country_a3_code] += 1

            #####choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)
            #
            # choro_file = choropleth_data_tuplet[0]
            # choro_file_name = choropleth_data_tuplet[1]
            # choro_html = choropleth_data_tuplet[2]

            # choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)
            #
            # choro_file_name = choropleth_data_tuplet[0]
            # choro_html = choropleth_data_tuplet[1]

            #######choropleth_map.save(os.path.join('media', '/news_mapper_web/html'))
            # save_choro_to_file(q_argument, q_type, choropleth_map)

            ######print('choropleth_file type = ' + str(type(choro_file)))
            # choropleth_file.save()
            # meta_data_mgr.build_query_results_dict()

            #####query_object.choropleth = choro_file

            # query_object.save()

            ######## return render(request, 'news_mapper_web/query_results.html', {
            #     'news_query': query_object,
            #     'choropleth': choro_file_name,
            #     'choro_html': choro_html
            # })

            choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)

            query_object.choropleth = choropleth_data_tuplet[0]
            query_object.choro_html = choropleth_data_tuplet[1]
            query_object.filename = choropleth_data_tuplet[2]
            # query_object.save()

           # return redirect('query_details', query_pk=query_object.pk)

            return render(request, 'news_mapper_web/query_results.html', {'news_query': query_object})



            #meta_data_mgr.build_query_results_dict()

            # return render(request, 'news_mapper_web/query_results.html', {
            #     'news_query': query_object,
            #     'choropleth': choro_file_name,
            #     'choro_html': choro_html
            # })

            # redirect('choro_map_embed', {'choro_file_name': choro_file_name})





def choro_map(request, choro_file_name):

    print('TYPE choro_file_name = ' + str(type(choro_file_name)))
    choro_path = CHORO_MAP_ROOT + choro_file_name
    return render(request, choro_path)


# @login_required(login_url='/accounts/login/')
def view_newsquery(request, query_pk):

    query = get_object_or_404(NewsQuery, pk=query_pk)

    if query:
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