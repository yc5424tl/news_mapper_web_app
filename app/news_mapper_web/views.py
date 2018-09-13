from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from .models import Post, Comment, UserModel, NewsQuery, Source
from .forms import EditPostForm, EditCommentForm, LoginForm, NewQueryForm

from .forms import UserCreationForm

from .api_mgr import QueryManager
from .map_mgr import GeoMapManager
from .metadata_mgr import MetadataManager

from sqlite3 import OperationalError

json_file = 'txt/geo_data_for_news_choropleth.txt'

query_mgr = QueryManager()
geo_map_mgr = GeoMapManager()
meta_data_mgr = MetadataManager(json_file)


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

        try:
            Source.objects.get(pk=1)
        except Source.DoesNotExist:
        # except OperationalError:
            source_list_txt = query_mgr.fetch_and_build_sources()
            query_mgr.write_sources_json_to_file(source_list_txt)

        argument = request.POST.get('argument')
        q_type = request.POST.get('query_type')

        articles_list = query_mgr.query_api(query_argument=argument, query_type=q_type)
        query_mgr.query_api('Scientists', )

        #  user_model = UserModel.objects.get(email=request.user.email)

        # query_object = NewsQuery(user=user_model, query_type=q_type, data=articles_list, argument=argument)

        query_object = NewsQuery(query_type=q_type, data=articles_list)

        if articles_list is not None:
            for article in articles_list:
                query_mgr.build_article_object(article, query_object)
                # source_country = article.source.country
                geo_map_mgr.get_source_country(article.source.name)
                if geo_map_mgr.map_source(article.source.country) is not None:
                    meta_data_mgr.query_data_dict[article.source.country] += 1

        choropleth = geo_map_mgr.build_choropleth(argument, q_type)

        meta_data_mgr.build_query_results_dict()

        query_object.choropleth = choropleth
        query_object.save()

        return render(request, 'news_mapper_web/query_results.html', {
            'news_query': query_object,
            'choropleth': query_object.choropleth
        })


#@login_required(login_url='/accounts/login/')
def view_newsquery(request):
    return None


#@login_required()
def save_query(request):
    return None


#@login_required()
def user_page(request):
    return None


#@login_required()
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