from django.db import models
# from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
# from django.contrib.auth.models import User
# from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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

    article_url = models.URLField(default=None, blank=True, null=True)
    author = models.CharField(blank=True, null=True, max_length=75, default=None)
    date_published = models.DateTimeField(blank=True, null=True)
    description = models.CharField(blank=True, null=True, max_length=2500)
    image_url = models.URLField(default=None, blank=True, null=True)
    query = models.ForeignKey('NewsQuery', on_delete=models.CASCADE)
    source = models.ForeignKey('Source', on_delete=models.PROTECT, blank=True, null=True)
    title = models.CharField(max_length=250)

    def __str__(self):
        return '%s - %s, %s %s' % (self.title, self.author, self.get_date_published(), self.source.name)

    def get_date_published(self):
        if self.date_published:
            return '%s %s, %s' % (self.date_published.month, self.date_published.day, self.date_published.year)
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


class NewsQuery(models.Model):

    query_types = (
        ('headlines', 'Headlines'),
        ('all', 'All')
    )

    # user = models.ForeignKey('User', null=False, on_delete=models.PROTECT)
    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,)
    _argument = models.CharField(max_length=500)
    _choropleth = models.FileField(upload_to='dociments/', null=True, blank=True, default=None)
    _data = models.CharField(max_length=200000, null=True, blank=True)
    _date = models.DateField(auto_now_add=True)
    _date_range_end = models.DateField(default=None, null=True, blank=True)
    _date_range_start = models.DateField(default=None, null=True, blank=True)
    _public = models.BooleanField(default=False)
    _query_type = models.CharField(default='headlines', choices=query_types, max_length=50)

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


