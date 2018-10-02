import json
import os

import pycountry
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect, get_object_or_404, Http404

from .api_mgr import QueryManager
from .forms import AuthenticationForm
from .forms import EditPostForm, NewQueryForm, NewPostForm, CustomUserCreationForm, NewCommentForm
from .map_mgr import GeoMapManager
from .metadata_mgr import MetadataManager
from .models import Post, Comment, Query, Source, Article

json_file = 'geo_data_for_news_choropleth.txt'

query_mgr = QueryManager()
geo_map_mgr = GeoMapManager()
meta_data_mgr = MetadataManager(json_file)

settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/templates/news_mapper_web/choropleths/')


def index(request):

    if request.method == 'GET':
        form = AuthenticationForm
        return render(request, 'news_mapper_web/index.html', {'form': form})


def register_user(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('view_user', user.pk)

        else:
            messages.info(request, message=form.errors)
            form = CustomUserCreationForm()
            return render(request, 'news_mapper_web/new_user.html', {'form': form})

    if request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'news_mapper_web/new_user.html', {'form': form})


def login_user(request):

    if request.method == 'POST':
        form = AuthenticationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('view_user', user.pk)

        form = AuthenticationForm()
        messages.error(request, 'Incorrect Password and/or Username', extra_tags='error')
        return render(request, 'news_mapper_web/login_user.html', {'form': form})

    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'news_mapper_web/login_user.html', {'form': form})



def logout_user(request):

    if request.user.is_authenticated:
        messages.info(request, 'You have been logged out.', extra_tags='alert')
    form = AuthenticationForm({'_author': request.user})
    return render('news_mapper_web/index.html', {'form': form})


@login_required()
def new_query(request):

    if request.method == 'GET':
        form = NewQueryForm()
        return render(request, 'news_mapper_web/new_query.html', {'search_form': form})

    elif request.method == 'POST':
        meta_data_mgr.check_geo_data()
        meta_data_mgr.write_json_to_file()
        meta_data_mgr.build_query_results_dict()

        get_or_build_sources()

        q_argument = request.POST.get('_argument')
        q_type = request.POST.get('_query_type')

        articles_list = query_mgr.query_api(query_argument=q_argument, query_type=q_type)

        query_in_progress = Query.objects.create(_query_type=q_type, _argument=q_argument, _data=articles_list, _author=request.user)
        query_in_progress.save()

        if request.user.is_authenticated:  # TODO after adding @login-required => adjust this -- DONT -- removing this breaks it -- even with _author declared and saved just a few lines ago...??
            query_in_progress.author = request.user
            query_in_progress.save()

        if articles_list:

            for article in articles_list:
                new_article = query_mgr.build_article_object(article, query_in_progress)

                if new_article is not False:
                    new_article.save()
                    country_a3_code = geo_map_mgr.get_country_alpha_3_code(new_article.source.country)
                    meta_data_mgr.query_data_dict[country_a3_code] += 1

            choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)
            choropleth = choropleth_data_tuplet[0]
            choro_html = choropleth_data_tuplet[1]
            choro_filename = choropleth_data_tuplet[2]

            query_pk = query_in_progress.pk
            Query.objects.filter(pk=query_pk).update(_choropleth=choropleth, _choro_html=choro_html, _filename=choro_filename, _author=request.user.pk)
            Query.objects.filter(pk=query_pk).update(_filepath=(CHORO_MAP_ROOT + choro_filename))

            return redirect('view_query', query_pk)


@login_required()
def view_query(request, query_pk):

    query = Query.objects.get(pk=query_pk)
    query_author = query.author
    query_articles = Article.objects.filter(_query=query)

    if query:
        return render(request, 'news_mapper_web/view_query.html', {
            'query': query,
            'query_author': query_author,
            'articles': query_articles
        })


@login_required()
def view_public_posts(request):

    posts = Post.objects.order_by('-id').all()
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'news_mapper_web/view_public_posts.html', {'posts': posts})


@login_required()
def delete_comment(request, comment_pk):

    if request.method == 'POST':
        comment = Comment.objects.get(pk=comment_pk)
        post_pk = comment.post.pk

        if comment.author.pk == request.user.pk:
            comment.delete()
            messages.info(request, 'Comment Deleted')

        return redirect('view_post', post_pk)


@login_required()
def delete_query(request, query_pk):

    if query_pk:
        return None


@login_required()
def view_user(request, member_pk):

    try:
        member = User.objects.get(pk=member_pk)
        recent_posts = member.posts.order_by('-id')[1:5]  # https://stackoverflow.com/a/44575224

        try:
            last_post = member.posts.order_by('-id')[0]
        except IndexError:
            last_post = None

        recent_comments = member.comments.order_by('-id')[0:4]
        queries = member.queries.order_by('-id')[0:4]

        return render(request, 'news_mapper_web/view_user.html', {
            'member': member,
            'posts': recent_posts,
            'comments': recent_comments,
            'last_post': last_post,
            'queries': queries
        })

    except User.DoesNotExist:
        raise Http404


@login_required
def new_post(request):

    if request.method == 'GET':
        form = NewPostForm()
        query_pk = request.POST.get('query_pk')

        try:
            query = Query.objects.get(pk=query_pk)
        except Query.DoesNotExist:
            raise Http404

        return render(request, 'news_mapper_web/new_post.html', {
            'form': form,
            'query': query
        })

    elif request.method == 'POST':
        form = NewPostForm(request.POST)

        if request.user.is_authenticated:
            try:
                pk = request.user.pk
                author = User.objects.get(pk=pk)

                if form.is_valid():
                    title = form.cleaned_data['_title']
                    public = form.cleaned_data['_public']
                    body = form.cleaned_data['_body']
                    query_pk = request.POST['query_pk']
                    query = Query.objects.get(pk=query_pk)

                    post = Post(title=title, public=public, body=body, query=query, author=author)
                    post.save()
                    return redirect('view_post', post.pk)

                else: # TODO actually do something
                    print('Errors = ' + form.errors)

            except User.DoesNotExist:
                raise Http404
    else:
        raise Http404


@login_required()
def update_post(request, post_pk):

    return render(request, 'news_mapper_web/update_post.html')


@login_required()
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

    else:  # GET request
        post = Post.objects.get(pk=post_pk)
        query = post.query

        if post.author.id == request.user.id:
            edit_post_form = EditPostForm(instance=post)  # Pre-populate form with the post's current field values
            return render(request, 'news_mapper_web/view_post.html', {'post': post, 'edit_post_form': edit_post_form, 'query': query})

        else:  # user is not OP
            return render(request, 'news_mapper_web/view_post.html', {'post': post, 'query': query})

def view_sources(request):

    get_or_build_sources()

    source_dict_list = [{'''country''': country_a2_to_name(source),
                         '''country_a2''': source.country,
                         '''name''': source.name,
                         '''language''': str(source.language),
                         '''full_lang''': lang_a2_to_name(source),
                         '''category''': str(source.category),
                         '''url''': str(source.url)}
                        for source in Source.objects.all()]

    return render(request, 'news_mapper_web/view_sources.html', {'sources': source_dict_list})


def lang_a2_to_name(source):
    try:
        name = pycountry.languages.lookup(source.language).name
        return name
    except LookupError:
        return source.language


def country_a2_to_name(source):
    try:
        name = pycountry.countries.lookup(source.country).name
        return name
    except LookupError:
        return source.country


@login_required()
def delete_post(request):

    pk = request.POST['post_pk']
    post = get_object_or_404(Post, pk=pk)

    if post.author.id == request.user.id:
        post.delete()
        messages.info(request, 'Post Removed')
        return redirect('index')
    else:
        messages.error(request, 'Action Not Authorized')


@login_required()
def new_comment(request, post_pk):

    if request.method == 'GET':
        form = NewCommentForm()
        post = Post.objects.get(pk=post_pk)
        return render(request, 'news_mapper_web/new_comment.html', {
            'post': post,
            'form': form
        })

    elif request.method == 'POST':
        c_post = Post.objects.get(pk=post_pk)
        c_body = request.POST.get('_body')
        c_author = User.objects.get(pk=request.user.pk)
        c = Comment.objects.create(_post=c_post, _body=c_body, _author=c_author)
        return redirect('view_comment', c.pk)


@login_required()
def view_comment(request, comment_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
        return render(request, 'news_mapper_web/view_comment.html', {'comment': comment})
    except Comment.DoesNotExist:
        raise Http404


@login_required()
def delete_comment(request, comment_pk):

    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.delete()
    last_url = request.POST['redirect_url']
    messages.info(request, 'Failed to Delete Comment')
    return redirect(request, last_url)


def password_reset(request):
    pass


def view_choro(request, query_pk):
    query = Query.objects.get(pk=query_pk)
    return render(request, 'news_mapper_web/view_choro.html', {'query': query})


@login_required()
def view_test_page(request):
    return render(request, 'news_mapper_web/test_choro.html')


def get_or_build_sources():

    try:
        test_db_has_sources = Source.objects.get(pk=1)

    except (UnicodeDecodeError, FileNotFoundError, Source.DoesNotExist, TypeError):
        try:
            with open('./news_mapper_web/static/js/sources.json') as sources:
                source_list = json.load(sources)
                for source in source_list['sources'][0]:

                    try:
                        api_id = source['id']
                        name = source['name']
                        description = source['description']
                        url = source['url']
                        category = source['category']
                        language = source['language']
                        country = source['country']

                        new_source = Source(_api_id=api_id, _category=category, _country=country, _description=description, _language=language, _name=name, _url=url)
                        new_source.save()

                    except TypeError:
                        print(TypeError, ' error building a source')
                        pass

                return True

        except (FileNotFoundError, Exception, UnicodeDecodeError):
            source_list_txt = query_mgr.fetch_and_build_sources()
            query_mgr.write_sources_json_to_file(source_list_txt)
            return True