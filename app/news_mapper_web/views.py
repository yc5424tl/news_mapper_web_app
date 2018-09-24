from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
# from django.urls import reverse_lazy
# from django.views import generic
# from django.conf import settings
from .models import Post, Comment, Query, Source, Article
from .forms import EditPostForm, NewQueryForm, NewPostForm, CustomUserCreationForm
import os
import json
from .forms import AuthenticationForm

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

#
# def index(request):
#
#     if request.method == 'GET':
#         user = request.user
#         print('type for user is ' + str(type(user)))
#         # form = LoginForm()
#         form = CustomAuthenticationForm()
#         print('type for form is ' + str(type(form)))
#         return render(request, 'news_mapper_web/index.html', {'user': user, 'form': form})


# class RegisterUser(generic.CreateView):
#     model = UserModel
#     form_class = UserCreationForm
#     # success_url = reverse_lazy('login')
#     # fields = ['unique_id', 'email', 'first_name', 'last_name', 'password']
#     success_url = reverse_lazy('login')
#     template_name = 'news_mapper_web/signup.html'
#     # def get_success_url(self):
#     #   return reverse_lazy('login')


def index(request):

    if request.method == 'GET':
        form = AuthenticationForm
        return render(request, 'news_mapper_web/index.html', {'form': form})

    # if request.method == 'GET':
    #     form = CustomAuthenticationForm()
    #     print('type for form is ' + str(type(form)))
    #     return render(request, 'news_mapper_web/index.html', {'form': form})

def register_user(request):
    #
    # if request.method == 'POST':
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         login(request, user)
    #         return redirect('view_user', user.pk)
    #     else:
    #         messages.info(request, message=form.errors)
    #         form = UserCreationForm()
    #     return render(request, 'news_mapper_web/new_user.html', {'form': form})

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

    # user = User.objects.create_user('firstname', 'email@example.com', 'examplePassword')


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


    # if request.method == 'POST':
    #     print('in login user method==post')
    #     form = CustomAuthenticationForm(request.POST)
    #     if form.is_valid():
    #         print('form is valid')
    #
    #         username = form.cleaned_data['username']
    #         print('username = ' + str(username))
    #         password = form.cleaned_data['password']
    #         print('password = ' + str(password))
    #         user = authenticate(request, username=username, password=password)
    #
    #         if user is not None:
    #             login(request, user)
    #             return redirect('view_user', user.pk)
            # user = authenticate(**request.POST)
            # if user is not None:
            #     login(request, user)
            #     return redirect('view_user', {'user_pk':user.pk})


        form = AuthenticationForm()
        messages.error(request, 'Incorrect Password and/or Username', extra_tags='error')
        return render(request, 'news_mapper_web/login_user.html', {'form': form})

    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'news_mapper_web/login_user.html', {'form': form})
    # username = request.POST.get('username')
    # print('username: ' + str(username))
    # password = request.POST.get('password')
    # print('password: ' + str(password))
    # user = authenticate(request, username=username, password=password)
    #
    # if user is not None:
    #     login(request, user)
    #     return redirect('view_user', {'member_pk': user.pk,})
    #     # latest_post = user.most_recent()
    #     # if latest_post is not False: # returns a Post object, or False if no posts have yet been made by the user
    #     #     return render(request, 'news_mapper_web/view_user.html', {
    #     #         'user': user,
    #     #         'last_post': latest_post,
    #     #         'logged_in': logged_in})
    #     # else:
    #     #     read_me = "You haven't made any posts yet!\n" \
    #     #               "Once you have, this area will display your most recent post. To start, click the 'New Query' button at the top of your screen."
    #     #     return render(request, 'news_mapper_web/view_user.html', {
    #     #         'user': user,
    #     #         'read_me': read_me,
    #     #         'logged_in': logged_in
    #     #     })
    # else:
    #     messages.error(request, 'Incorrect Password and/or Username', extra_tags='error')
    #     return redirect('login_user')
    #     # TODO - redirect to login page with invalid login message


def logout_user(request):
    if request.user.is_authenticated:
        messages.info(request, 'You have been logged out.', extra_tags='alert')
    form = AuthenticationForm({'_author': request.user})
    return render('news_mapper_web/index.html', {'form': form})


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
                            # print('id = ' + str(id))
                            # print('name = ' + str(name))
                            # print('description = ' + str(description))
                            # print('url = ' + str(url))
                            # print('category = ' + str(category))
                            # print('language = ' + str(language))
                            # print('country = ' + str(country))
                            new_source = Source(_api_id=api_id, _category=category, _country=country, _description=description, _language=language, _name=name, _url=url)
                            new_source.save()
                        except TypeError:
                            print(TypeError, ' error building a source')
                            pass
            except (FileNotFoundError, Exception, UnicodeDecodeError):
                source_list_txt = query_mgr.fetch_and_build_sources()
                query_mgr.write_sources_json_to_file(source_list_txt)

        # except Source.DoesNotExist:
        #     try:
        #         with open('./news_mapper_web/static/js/sources.json') as sources:
        #             source_list = json.load(sources)
        #             for source in source_list['sources'][0]:
        #                 api_id = source['id']
        #                 name = source['name']
        #                 description = source['description']
        #                 url = source['url']
        #                 category = source['category']
        #                 language = source['language']
        #                 country = source['country']
        #
        #                 new_source = Source(_api_id=api_id, _category=category, _country=country, _description=description, _language=language, _name=name, _url=url)
        #                 new_source.save()
        #
        #     except (FileNotFoundError, Exception):
        #         source_list_txt = query_mgr.fetch_and_build_sources()
        #         query_mgr.write_sources_json_to_file(source_list_txt)

        q_argument = request.POST.get('_argument')
        q_type = request.POST.get('_query_type')
        # q_author = request.POST.get('_author')

        articles_list = query_mgr.query_api(query_argument=q_argument, query_type=q_type)
        query_in_progress = Query.objects.create(_query_type=q_type, _data=articles_list, _argument=q_argument)

        if request.user.is_authenticated:  # TODO after adding @login-required => adjust this
            query_in_progress.author = request.user
            query_in_progress.save()

        if articles_list:
            #print('in if articles_list')
            for article in articles_list:
                #print('in for article in articles_list')
                #print(article)
                # new_article = query_mgr.build_article_object(article, query_object)
                # if new_article is not False:
                #     new_article_pk = new_article.pk
                #
                new_article = query_mgr.build_article_object(article, query_in_progress)
                #print('type for new_article = ' + str(type(new_article)))
                if new_article is not False:
                    new_article.save()
                    #print('article country = ' + str(new_article.source.country))
                    country_a3_code = geo_map_mgr.get_country_alpha_3_code(new_article.source.country)
                    #print('article alpha_3_code = ' + country_a3_code)
                    #print('before adding to query_data_dic, total = ' + str(meta_data_mgr.query_data_dict[country_a3_code]))
                    meta_data_mgr.query_data_dict[country_a3_code] += 1
                    #print('after = ' + str(meta_data_mgr.query_data_dict[country_a3_code]))

                    # try:
                    #     print('article country = ' + article.source.country)
                    #     country_a3_code = geo_map_mgr.get_country_alpha_3_code(new_article.source.country)
                    #
                    #     print('article alpha_3_code = ' + country_a3_code)
                    #     print('before adding to query_data_dic, total = ' + str(meta_data_mgr.query_data_dict[country_a3_code]))
                    #     meta_data_mgr.query_data_dict[country_a3_code] += 1
                    #     print('after = ' + str(meta_data_mgr.query_data_dict[country_a3_code]))
                    # except AttributeError:
                    #     print(AttributeError)
                    #     pass
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
            #print('After all articles: ' + str(meta_data_mgr.query_data_dict))

            choropleth_data_tuplet = geo_map_mgr.build_choropleth(q_argument, q_type, meta_data_mgr)
            choropleth = choropleth_data_tuplet[0]
            choro_html = choropleth_data_tuplet[1]
            choro_filename = choropleth_data_tuplet[2]
            # choro_html_splice = str(choro_html[16:-1])
            # choro_html_updated = '<html lang="en">' + choro_html_splice
            query_pk = query_in_progress.pk
            #print('choro_html = ' + choro_html[0:1000])

            Query.objects.filter(pk=query_pk).update(_choropleth=choropleth, _choro_html=choro_html, _filename=choro_filename)
            query_in_progress.save()
            #html_pre = str(query_object.choro_html[0:1000])
            #print('str(html_pre) = ' + str(html_pre))
            #print('redirect.query_object.pk = ' + str(query_object.pk))

            # article_instances = [Article.objects.filter(_query=query_object)]

            # for x in article_instances:
            #     print('article_instance type = ' + str(type(x)))
            # return redirect('query_result_detail',  news_query_pk=query_object.pk, articles=article_instances)

            # return redirect('query_result_detail', news_query_pk=query_object.pk)
            choro_file_path = CHORO_MAP_ROOT + query_in_progress.filename
            #print('choro file path = ' + choro_file_path)
            query_in_progress.filepath = choro_file_path
            query_in_progress.save()

            return redirect('view_query', query_in_progress.pk)

            # query_object.save()
            # print('past .save()')


            # articles = [x for x in Article.objects.all().select_related(query_object)]

            # articles = Article.objects.filter(_query=query_in_progress)
            #print('articles as str: ')
            #print(str(articles))

            # print('query.author = ' + str(query_in_progress.author))
            #
            #
            # print('after building articles, before return')
            # return render(request, 'news_mapper_web/view_query.html', {
            #     'query_pk': query_in_progress.pk,
            #     'query': query_in_progress,
            #     'choro_filepath': choro_file_path,
            #     'articles': articles,
            #     'query_author': query_in_progress.author
            # })

            # print('type query_in_progress = ' + str(type(query_in_progress)))


            # return render(request, 'news_mapper_web/view_query.html', query_in_progress.pk,
            #                 {'query': query_in_progress,
            #                  'choro_filepath': choro_file_path,
            #                  'articles': articles,
            #                  'query_author': query_in_progress.author})


def view_query(request, query_pk):


    query = Query.objects.get(pk=query_pk)
    query_author = query.author
    query_articles = Article.objects.filter(_query=query)
    # query_filename = query.filename
    # query_choro_path = CHORO_MAP_ROOT

    if query:
        return render(request, 'news_mapper_web/view_query.html', {
            'query': query,
            'query_author': query_author,
            'articles': query_articles
        })


    # if query:
    #     html_pre = query.choro_html
    #     print('Meta Type: ' + str(type(query)))
    #     print('html = ' + (html_pre[0:300]))
    #     print('type = ' + query.query_type)
    #     # print('filename = ' + str(query.filename))
    #     print('type(choropleth = ' + str(type(query.choropleth)))
    #     print('argument = ' + query.argument)
    #     print('before render view_quiery in views.view_query')
    #     return render(request, 'news_mapper_web/view_query.html', {
    #         'query': query,
    #         'query_author': query_author
    #     })

# @login_required()
def delete_query(request, query_pk):
    if query_pk:
        return None


# @login_required()
def view_user(request, member_pk):

    print('member_pk = ' + str(member_pk))

    # user = request.user
    try:
        member = User.objects.get(pk=member_pk)
        print('member.first_name = ' + str(member.first_name))
        recent_posts = member.posts.order_by('-id')[1:5]  # https://stackoverflow.com/a/44575224

        posts = [x for x in recent_posts if x is not (None or False)]
        print('len recent_posts = ' + str(len(recent_posts)))
        print('len posts = ' + str(len(posts)))
        print('posts ' + str(posts))

        try:
            last_post = member.posts.order_by('-id')[0]
        except IndexError:
            last_post = None

        print('last post = ' + str(last_post))


        recent_comments = member.comments.order_by('-id')[0:4]

        comments = [comment for comment in recent_comments if comment is not (None or False)]
        print('comments = ' + str(comments))
        print('len recent_comments = ' + str(len(recent_comments)))
        print('len comments = ' + str(len(comments)))

        return render(request, 'news_mapper_web/view_user.html', {
            # 'user': user,
            'member': member,
            'posts': recent_posts,
            'comments': recent_comments,
            'last_post': last_post
        })

    except User.DoesNotExist:
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

        if request.user.is_authenticated:

            try:
                pk = request.user.pk
                author = User.objects.get(pk=pk)

                if form.is_valid():
                    title = form.cleaned_data['_title']
                    public = form.cleaned_data['_public']
                    body = form.cleaned_data['_body']
                    query = form.cleaned_data['_query']

                    post = Post(title=title, public=public, body=body, query=query, author=author)
                    post.save()
                    # return redirect('view_post', {'post_pk': post.pk})
                    return render('')

            # return render(request, 'news_mapper_web/new_post.html', {'post_pk': post.pk})
            except User.DoesNotExist:
                raise Http404


def update_post(request, post_pk):
    return render(request, 'news_mapper_web/update_post.html')

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
    if post_pk:
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