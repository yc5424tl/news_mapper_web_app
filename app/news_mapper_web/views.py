

from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.urls import reverse_lazy
# from django.views import generic
# from django.conf import settings
from .models import Post, Comment, Query, Source, Article, CustomUser
from .forms import EditPostForm, LoginForm, NewQueryForm, NewPostForm
import os
import json
from .forms import UserCreationForm

from .api_mgr import QueryManager
from .map_mgr import GeoMapManager
from .metadata_mgr import MetadataManager

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
    return render(request, 'news_mapper_web/index.html', {'user': user, 'form': form})
# class RegisterUser(generic.CreateView):
#     model = UserModel
#     form_class = UserCreationForm
#     # success_url = reverse_lazy('login')
#     # fields = ['unique_id', 'email', 'first_name', 'last_name', 'password']
#     success_url = reverse_lazy('login')
#     template_name = 'news_mapper_web/signup.html'
#     # def get_success_url(self):
#     #   return reverse_lazy('login')

def signup_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('view_user', user.pk)
        else:
            form = UserCreationForm()
        return render(request, 'news_mapper_web/new_user.html', {'form': form})


def login_user(request):

    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect('view_user', {'member_pk': user.pk,})
        # latest_post = user.most_recent()
        # if latest_post is not False: # returns a Post object, or False if no posts have yet been made by the user
        #     return render(request, 'news_mapper_web/view_user.html', {
        #         'user': user,
        #         'last_post': latest_post,
        #         'logged_in': logged_in})
        # else:
        #     read_me = "You haven't made any posts yet!\n" \
        #               "Once you have, this area will display your most recent post. To start, click the 'New Query' button at the top of your screen."
        #     return render(request, 'news_mapper_web/view_user.html', {
        #         'user': user,
        #         'read_me': read_me,
        #         'logged_in': logged_in
        #     })
    else:
        messages.error(request, 'Incorrect Password and/or Username', extra_tags='error')
        return redirect('login_user')
        # TODO - redirect to login page with invalid login message


def logout_user(request):
    user = request.user
    logout(user)
    messages.info(request, 'You have been logged out.', extra_tags='alert')
    return redirect('index')


def new_query(request):

    if request.method == 'GET':
        form = NewQueryForm()
        return render(request, 'news_mapper_web/new_query.html', {'search_form': form})

    elif request.method == 'POST':

        # if meta_data_mgr.json_geo_data is None or meta_data_mgr.request_geo_data is None:
        #     meta_data_mgr.get_geo_data()
        #     meta_data_mgr.fix_cyprus_country_code()
        meta_data_mgr.check_geo_data()
        meta_data_mgr.write_json_to_file()
        meta_data_mgr.build_query_results_dict()

        try:
            Source.objects.get(pk=1)
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

        query_object = Query(_query_type=q_type, _data=articles_list, _argument=q_argument)
        query_object.save()

        if articles_list:
            for article in articles_list:
                # new_article = query_mgr.build_article_object(article, query_object)
                # if new_article is not False:
                #     new_article_pk = new_article.pk
                query_mgr.build_article_object(article, query_object)
                try:
                    country_a3_code = geo_map_mgr.get_country_alpha_3_code(article.source.country)
                    meta_data_mgr.query_data_dict[country_a3_code] += 1
                except AttributeError:
                    pass
                    #     article_source_country = new_article.get_source_country()
                    #     if article_source_country:
                    #         country_a3_code = geo_map_mgr.get_country_alpha_3_code(article_source_country)
                    #         meta_data_mgr.query_data_dict[country_a3_code] += 1
                    # except AttributeError:
                    #     try:
                    #         article = Article.objects.get(pk=new_article_pk)
                    #         country = article.get_source_country()
                    #         print('Country = ' + str(country))
                    #         if country:
                    #             country_a3_code = geo_map_mgr.get_country_alpha_3_code(country)
                    #             meta_data_mgr.query_data_dict[country_a3_code] += 1
                    #     except AttributeError:
                    #         pass

            choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)

            choropleth = choropleth_data_tuplet[0]
            choro_html = choropleth_data_tuplet[1]
            choro_filename = choropleth_data_tuplet[2]
            # choro_html_splice = str(choro_html[16:-1])
            # choro_html_updated = '<html lang="en">' + choro_html_splice
            query_pk = query_object.pk
            print('choro_html = ' + choro_html[0:1000])

            Query.objects.filter(pk=query_pk).update(_choropleth=choropleth, _choro_html=choro_html, _filename=choro_filename)

            query_object = Query.objects.get(pk=query_pk)

            html_pre = str(query_object.choro_html[0:1000])
            print('str(html_pre) = ' + str(html_pre))
            print('redirect.query_object.pk = ' + str(query_object.pk))

            article_instances = [x for x in Article.objects.filter(_query=query_object)]

            for x in article_instances:
                print('article_instance type = ' + str(type(x)))
            # return redirect('query_result_detail',  news_query_pk=query_object.pk, articles=article_instances)

            # return redirect('query_result_detail', news_query_pk=query_object.pk)
            choro_file_path = CHORO_MAP_ROOT + query_object.filename
            query_object.filepath = choro_file_path

            return render(request, 'news_mapper_web/view_query.html', {
                'query': query_object,
                'choro_filepath': choro_file_path,
            })


def view_query(request, query_pk):

    print('in newsquery views.py')
    print('news_query_pk = ' + str(query_pk))
    query = Query.objects.get(pk=query_pk)

    if query:
        html_pre = query.choro_html
        print('Meta Type: ' + str(type(query)))
        print('html = ' + (html_pre[0:300]))
        print('type = ' + query.query_type)
        # print('filename = ' + str(query.filename))
        print('type(choropleth = ' + str(type(query.choropleth)))
        print('argument = ' + query.argument)
        return render(request, 'news_mapper_web/view_query.html', {
            'query': query
        })

# @login_required()
def delete_query(request, query_pk):
    return None

# @login_required()
def view_user(request, member_pk):

    user = request.user
    try:
        member = CustomUser.objects.get(pk=member_pk)
        recent_posts = member.posts.order_by('-id')[1:5]  # https://stackoverflow.com/a/44575224
        last_post = member.posts.order_by('-id')[0]
        recent_comments = member.comments.order_by('-id')[0:4]

        return render(request, 'news_mapper_web/view_user.html', {
            'user': user,
            'member': member,
            'posts': recent_posts,
            'comments': recent_comments,
            'last_post': last_post
        })

    except CustomUser.DoesNotExist:
        raise Http404




def new_post(request, query_pk):

    if request.GET:

        form = NewPostForm()

        try:
            query = Query.objects.get(pk=query_pk)
        except Query.DoesNotExist:
            raise Http404

        return render(request, 'news_mapper_web/new_post.html', {
            'form': form,
            'query': query
        })

    if request.POST:
        form = NewPostForm(request.POST)

        try:
            pk = request.user.pk
            author = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

        if form.is_valid():
            title = form.cleaned_data['_title']
            public = form.cleaned_data['_public']
            body = form.cleaned_data['_body']
            query = form.cleaned_data['_query']

            post = Post(title=title, public=public, body=body, query=query, author=author)

            post.save()

            return render(request, 'news_mapper_web/new_post.html', {'post_pk': post.pk})



def update_post(request, post_pk):
    pass

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
        if post.author.id == request.user.id:
            edit_post_form = EditPostForm(instance=post) # Pre-populate form with the post's current field values
            return render(request, 'news_mapper_web/view_post.html', { 'post': post, 'edit_post_form': edit_post_form})
        else: # user is not OP
            return render(request, 'news_mapper_web/view_post.html', { 'post': post })

#@login_required()
def delete_post(request):
    pk = request.POST['post_pk']
    post = get_object_or_404(Post, pk=pk)
    if post.author.id == request.user.id:
        post.delete()
        messages.info(request, 'Post Removed')
        return redirect('index')
    else:
        messages.error(request, 'Action Not Authorized')


def new_comment(request, post_pk):
    pass


def view_comment(request, comment_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
        return render(request, 'news_mapper_web/view_comment.html', {'comment_pk': comment.pk})
    except Comment.DoesNotExist:
        raise Http404

#@login_required()
def delete_comment(request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        comment.delete()
        last_url = request.POST['redirect_url']
        messages.info(request, 'Failed to Delete Comment')
        return redirect(request, last_url)



def password_reset(request):
    pass

        # def choro_map(request, choro_file_name):
        #
        #     print('TYPE choro_file_name = ' + str(type(choro_file_name)))
        #     choro_path = CHORO_MAP_ROOT + choro_file_name
        #     return render(request, choro_path)
        # @login_required(login_url='/accounts/login/')