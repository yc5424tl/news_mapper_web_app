from django.db import models
# from django.contrib.auth.models import User
from datetime import datetime


class Source(models.Model):
    name = models.CharField(max_length=250)
    country = models.CharField(blank=True, null=True, max_length=100)
    country_alpha_code = models.CharField(blank=True, null=True, max_length=3)

    def __str__(self):
        return '%s - %s(%s)' % (self.name, self.country, self.country_alpha_code)


class Article(models.Model):
    author = models.CharField(blank=True, null=True, max_length=75, default='')
    date_published = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=250)
    source = models.ForeignKey('Source', on_delete=models.PROTECT, blank=True, null=True)
    body = models.CharField(blank=True, null=True, max_length=2500)
    query = models.ForeignObject('Query', on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s, %s %s' % (self.title, self.author, self.date(), self.source.name)

    def date(self):
        if self.date_published:
            return '%s %s, %s' % (self.date_published.month, self.date_published.day, self.date_published.year)
        else:
            return ''

class NewsQuery(models.Model):
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    argument = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)
    public = models.BooleanField(default=False)
    choropleth = models.ImageField(upload_to='images/')
    type = models.CharField('Headlines', 'All')


class Post(models.Model):
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=2500)
    date_published = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(default=None)
    query = models.ForeignKey('Query', null=False, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

class Comment(models.Model):
    user = models.ForeignKey('auth.User', null=False, on_delete=models.PROTECT)
    post = models.ForeignKey('Post', null=False, blank=False, on_delete=models.PROTECT)
    body = models.CharField(max_length=2500)
    date_published = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(default=None)


# class Member(models.Model):
#     user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    #  it seems that the use of auth.User as a FK within the other classes negates the need of this class:
    # fields = queries, maps, posts, comments, (e-mail)






