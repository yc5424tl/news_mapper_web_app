from django.db import models
# from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
# from django.contrib.auth.models import User
# from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplo

settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/media/news_mapper_web/html/')

class Source(models.Model):

    source_categories = (
        ('businiess', 'Business'),
        ('entertainment', 'Entertainment'),
        ('general', 'General'),
        ('health', 'Health'),
        ('science', 'Science'),
        ('sports', 'Sports'),
        ('technology', 'Technology')
    )

    api_id = models.CharField(             default=None, null=True, blank=True, max_length=50)
    category = models.CharField(           default=None, null=True, blank=True, max_length=50, choices=source_categories )
    country = models.CharField(                          null=True, blank=True, max_length=30)
    country_alpha_code = models.CharField(               null=True, blank=True, max_length=3)
    description = models.CharField(        default=None, null=True, blank=True, max_length=2000)
    language = models.CharField(           default=None, null=True, blank=True, max_length=50)
    name = models.CharField(                                                    max_length=250)
    url = models.URLField(                 default=None, null=True, blank=True)

    def __str__(self):
        return '%s - %s(%s)' % (self.name, self.country, self.country_alpha_code)

    def get_api_id(self):
        return self.api_id

    def get_category(self):
        return self.category

    def get_country(self):
        return self.country

    def get_country_alpha_code(self):
        return self.country_alpha_code

    def get_description(self):
        return self.description

    def get_language(self):
        return self.language

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url



class Article(models.Model):

    _article_url = models.URLField(default=None, blank=True, null=True)
    _author = models.CharField(blank=True, null=True, max_length=75, default=None)
    _date_published = models.DateTimeField(blank=True, null=True)
    _description = models.CharField(blank=True, null=True, max_length=2500)
    _image_url = models.URLField(default=None, blank=True, null=True)
    _query = models.ForeignKey('NewsQuery', on_delete=models.CASCADE)
    _source = models.ForeignKey('Source', on_delete=models.PROTECT, blank=True, null=True)
    _title = models.CharField(max_length=250)

    def __str__(self):
        return '%s - %s, %s %s' % \
               (self._title, self._author, self.get_date_published(), self._source.name)

    @property
    def article_url(self):
        return self._article_url

    @article_url.setter
    def article_url(self, new_url):
        self._article_url = new_url

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, new_author):
        self._author = new_author

    @property
    def date_published(self):
        return self._date_published

    @date_published.setter
    def date_published(self, new_date):
        self._date_published = new_date

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_desc):
        self._description = new_desc

    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, new_url):
        self._image_url = new_url

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, new_query):
        self._query = new_query

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        self._source = new_source

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new_title):
        self._title = new_title

    def get_date_published(self):
        if self._date_published:
            return '%s %s, %s' % (self._date_published.month, self._date_published.day, self._date_published.year)
        else:
            return None

    def get_source_country(self):
        return self.source.country

    def get_source_name(self):
        return self.source.name

    def get_source(self):
        return self.source

    def get_parent_query(self):
        return self.query

    def get_author(self):
        return self.author

    def get_article_url(self):
        return self.article_url

    def get_description(self):
        return self.get_description

    def get_image_url(self):
        return self.image_url

    def get_title(self):
        return self.title


class NewsQueryManager(models.Manager):

    def create_news_query(self, argument, date_created, query_type, choropleth=None, choro_html=None, data=None, date_range_end=None,date_range_start=None, filename=None,public=False):

        news_query = self.create(_argument=argument, _choropleth=choropleth, _choro_html=choro_html, _data=data, _date_created=date_created, _date_range_end=date_range_end,  _date_range_start=date_range_start, _filename=filename, _public=public, _query_type=query_type )

        return news_query


class NewsQuery(models.Model):

    query_types = (
        ('headlines', 'Headlines'),
        ('all', 'All')
    )

    # user = models.ForeignKey('User', null=False, on_delete=models.PROTECT)
    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,)
    _argument = models.CharField(max_length=500)
    _choropleth = models.FileField(upload_to=CHORO_MAP_ROOT, null=True, blank=True, default=None)
    _choro_html = models.TextField(max_length=200000, null=True, blank=True)
    _data = models.CharField(max_length=200000, null=True, blank=True)
    _date_created = models.DateField(auto_now_add=True)
    _date_range_end = models.DateField(default=None, null=True, blank=True)
    _date_range_start = models.DateField(default=None, null=True, blank=True)
    _filename = models.TextField(max_length=700, null=True, blank=True)
    _public = models.BooleanField(default=False)
    _query_type = models.CharField(default='headlines', choices=query_types, max_length=50)

    objects = NewsQueryManager


    @property
    def argument(self):
        return self._argument

    @argument.setter
    def argument(self, new_argument):
        if isinstance(new_argument, str):
            self._argument = new_argument
        else:
            raise Exception("Invalid Value for argument")

    @property
    def choropleth(self):
        return self._choropleth

    @choropleth.setter
    def choropleth(self, new_choropleth):
        self._choropleth = new_choropleth

    @property
    def query_type(self):
        return self._query_type

    @query_type.setter
    def query_type(self, new_query_type):
        self._query_type = new_query_type

    @property
    def date(self):
        return self._date_created

    @date.setter
    def date(self, new_date):
        self._date_created = new_date

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, new_filename):
        self._filename = new_filename

    @property
    def choro_html(self):
        return self._choro_html

    @choro_html.setter
    def choro_html(self, new_choro_html):
        self._choro_html = new_choro_html

    @property
    def date_created_readable(self):
        return '%s %s, %s' % (self._date_created.month, self._date_created.day, self._date_created.year)


class Post(models.Model):

    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, )
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=2500)
    date_published = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(default=None)
    query = models.ForeignKey('NewsQuery', null=False, on_delete=models.PROTECT)

    def get_choro_map(self):
        if self.query.choropleth:
            return self.query.choropleth


class Comment(models.Model):
    # user = models.ForeignKey('User', null=False, on_delete=models.PROTECT)
    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    post = models.ForeignKey('Post', null=False, blank=False, on_delete=models.PROTECT)
    body = models.CharField(max_length=2500)
    date_published = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(default=None)


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def create_superuser(self, email, is_staff, password):
        user = self.model(
            email=email,
            is_staff=is_staff,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserModel(AbstractBaseUser):
    sys_id = models.AutoField(primary_key=True, blank=True)
    email = models.EmailField(max_length=127, unique=True, null=False, blank=False)
    is_staff = models.BooleanField()
    is_active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['is_staff']

    class Meta:
        app_label = 'news_mapper_web'
        db_table = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff




# class User(AbstractUser):
#     username = models.CharField(max_length=40, unique=True)
#     email = models.EmailField(unique=True, max_length=75)
#     first_name = models.CharField(max_length=150)
#     last_name = models.CharField(max_length=150)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#     # groups = models.ForeignKey('Permission', null=True, blank=True, on_delete=models.CASCADE)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name']
#
#     def __str__(self):
#         return self.email


# class Member(models.Model):
#     user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    #  it seems that the use of auth.User as a FK within the other classes negates the need of this class:
    # fields = queries, maps, posts, comments, (e-mail)



#======================================================================================#

# enum help from
#   https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63


