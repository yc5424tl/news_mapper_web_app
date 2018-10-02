
import os
from django.conf import settings
from django.db import models


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
        ('technology', 'Technology'))

    _api_id = models.CharField(max_length=50)
    _category = models.CharField(max_length=50, choices=source_categories)
    _country = models.CharField(max_length=30)
    _country_alpha_code = models.CharField(max_length=3)
    _description = models.CharField(max_length=2000)
    _language = models.CharField(max_length=50)
    _name = models.CharField(max_length=250)
    _url = models.URLField()

    def __str__(self):
        return '%s - %s(%s)' % (self._name, self._country, self._country_alpha_code)

    @property
    def api_id(self):
        return self._api_id

    @api_id.setter
    def api_id(self, new_id):
        self._api_id = new_id

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category):
        self._category = new_category

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, new_country):
        self._country = new_country

    @property
    def country_alpha_code(self):
        return self._country_alpha_code

    @country_alpha_code.setter
    def country_alpha_code(self, new_code):
        self._country_alpha_code = new_code

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_desc):
        self._description = new_desc

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, new_lang):
        self._language = new_lang

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url):
        self._url = new_url


class QueryManager(models.Manager):

    def create_query(self, argument, date_created, query_type, author=None, choropleth=None, choro_html=None, data=None, date_range_end=None, date_range_start=None,public=False):

        news_query = self.create(
            _argument =argument,
            _author=author,
            _choropleth=choropleth,
            _choro_html=choro_html,
            _data=data,
            _date_created=date_created,
            _date_range_end=date_range_end,
            _date_range_start=date_range_start,
            _filename=self.filename,
            _public=public,
            _query_type=query_type)

        return news_query


class Query(models.Model):

    query_types = ( ('headlines', 'Headlines'), ('all', 'All') )

    _argument = models.CharField(max_length=500)
    _choropleth = models.FileField(upload_to=CHORO_MAP_ROOT, null=True, blank=True, default=None)
    _choro_html = models.TextField(max_length=200000, blank=True)
    _data = models.CharField(max_length=200000, blank=True)
    _date_created = models.DateField(auto_now_add=True)
    _date_range_end = models.DateField(default=None, null=True, blank=True)
    _date_range_start = models.DateField(default=None, null=True, blank=True)
    _filename = models.TextField(max_length=700, blank=True)
    _filepath = models.TextField(max_length=1000, blank=True)
    _public = models.BooleanField(default=False)
    _query_type = models.CharField(default='all', choices=query_types, max_length=50)
    _author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='queries')
    _archived = models.BooleanField(default=False)

    objects = QueryManager

    def __str__(self):
        details = 'Argument = ' + self._argument + '\n' + '' \
                  'Query Type = ' + str(self._date_created) + '\n' + \
                  'Author = ' + str(self._author) + '\n' + \
                  'Archived = ' + str(self._archived) + '\n' + \
                  'Public = ' + str(self._public) + '\n' + \
                  'Data[:500] = ' + self._data[:500] + '\n' + \
                  'Choropleth HTML[:500] = ' + self._choro_html[:500]

        if self.filename:
            details = details + '\n' + 'Filename = ' + self._filename

        return details


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
        return '%s/%s/%s' % (self._date_created.month, self._date_created.day, self._date_created.year)

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, new_author):
        self._author = new_author

    @property
    def archived(self):
        return self._archived

    @archived.setter
    def archived(self, is_archived:bool):
        if isinstance(is_archived, bool):
            self._archived = is_archived
        else:
            raise TypeError('Property "archived" must be type bool.')

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, path): # path to directory containing the file
        self._filepath = path


class Article(models.Model):

    _article_url = models.URLField()
    _author = models.CharField(max_length=75)
    _date_published = models.DateTimeField()
    _description = models.CharField(max_length=2500)
    _image_url = models.URLField(default=None, blank=True, null=True)
    _query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='articles')
    _source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name='articles')
    _title = models.CharField(max_length=250)

    def __str__(self):
        return '%s - %s, %s %s' % \
               (self._title, self._author, self.get_date_published, self._source.name)

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

    @property
    def get_date_published(self):
        if self._date_published:
            return '%s %s, %s' % (self._date_published.month, self._date_published.day, self._date_published.year)
        else:
            return None

    @property
    def get_source_country(self):
        return self.source.country


class Post(models.Model):

    _title = models.CharField(max_length=150)
    _body = models.CharField(max_length=50000)
    _date_published = models.DateTimeField(auto_now_add=True)
    _author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='posts')
    _date_last_edit = models.DateTimeField(auto_now_add=True)
    _query = models.OneToOneField(Query, on_delete=models.PROTECT)
    _public = models.BooleanField(default=False)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new_title):
        self._title = new_title

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, new_body):
        self._body = new_body

    @property
    def date_published(self):
        return self._date_published

    @date_published.setter
    def date_published(self, new_date):
        self._date_published = new_date

    @property
    def date_last_edit(self):
        return self._date_last_edit

    @date_last_edit.setter
    def date_last_edit(self, new_date):
        self._date_last_edit = new_date

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, new_query):
        self._query = new_query

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, new_author):
        self._author = new_author

    @property
    def public(self):
        return self._public

    @public.setter
    def public(self, state):
        self._public = state

    def get_choro_map(self):
        if self._query.choropleth:
            return self._query.choropleth


class Comment(models.Model):
    _post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='comments')
    _body = models.CharField(max_length=2500)
    _date_published = models.DateTimeField(auto_now_add=True)
    _date_last_edit = models.DateTimeField(auto_now_add=True)
    _author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comments')

    def __str__(self):
        return "comment from " + self.author.first_name + ' ' +  self.author.last_name + ' on the post ' + "'" + self.post.title + "', made " + str(self.date_published)

    @property
    def post(self):
        return self._post

    @post.setter
    def post(self, new_post):
        self._post = new_post

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, new_body):
        self._body= new_body

    @property
    def date_published(self):
        return self._date_published

    @date_published.setter
    def date_published(self, new_date):
        self._date_published = new_date

    @property
    def date_last_edit(self):
        return self._date_last_edit

    @date_last_edit.setter
    def date_last_edit(self, new_date):
        self._date_last_edit = new_date

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, new_author):
        self._author = new_author


#======================================================================================#

# enum help from
#   https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63


