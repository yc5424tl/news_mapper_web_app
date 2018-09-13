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

    name = models.CharField(max_length=250)
    country = models.CharField(blank=True, null=True, max_length=30)
    country_alpha_code = models.CharField(blank=True, null=True, max_length=3)
    url = models.URLField(default=None, null=True, blank=True)
    api_id = models.CharField(default=None, null=True, blank=True, max_length=50)
    description = models.CharField(default=None, null=True, blank=True, max_length=2000)
    category = models.CharField(default=None, null=True, blank=True, choices=source_categories, max_length=50)
    language = models.CharField(blank=True, null=True, default=None, max_length=50)

    def __str__(self):
        return '%s - %s(%s)' % (self.name, self.country, self.country_alpha_code)


class Article(models.Model):
    author = models.CharField(blank=True, null=True, max_length=75, default=None)
    date_published = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=250)
    source = models.ForeignKey('Source', on_delete=models.PROTECT, blank=True, null=True)
    description = models.CharField(blank=True, null=True, max_length=2500)
    query = models.ForeignKey('NewsQuery', on_delete=models.CASCADE)
    image_url = models.URLField(default=None, blank=True, null=True)
    article_url = models.URLField(default=None, blank=True, null=True)

    def __str__(self):
        return '%s - %s, %s %s' % (self.title, self.author, self.date(), self.source.name)

    def date(self):
        if self.date_published:
            return '%s %s, %s' % (self.date_published.month, self.date_published.day, self.date_published.year)
        else:
            return ''


class NewsQuery(models.Model):

    query_types = (
        ('headlines', 'Headlines'),
        ('all', 'All')
    )

    # user = models.ForeignKey('User', null=False, on_delete=models.PROTECT)
    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,)
    query_type = models.CharField(default='headlines', choices=query_types, max_length=50)
    data = models.CharField(max_length=200000, null=True, blank=True)
    choropleth = models.FileField(upload_to='dociments/', null=True, blank=True, default=None)
    argument = models.CharField(max_length=500)
    date_range_start = models.DateField(default=None, null=True, blank=True)
    date_range_end = models.DateField(default=None, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    public = models.BooleanField(default=False)


class Post(models.Model):
    #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, )
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=2500)
    date_published = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(default=None)
    query = models.ForeignKey('NewsQuery', null=False, on_delete=models.PROTECT)

    def choro_map(self):
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


