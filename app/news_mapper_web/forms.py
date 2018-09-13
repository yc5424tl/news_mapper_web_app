from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Post, Comment, NewsQuery, UserModel


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class NewQueryForm(forms.ModelForm):
    class Meta:
        model = NewsQuery
        fields = ('argument', 'query_type')


class SaveQueryForm(forms.ModelForm):
    #  add option to publish in this form
    class Meta:
        model = NewsQuery
        fields = ('public',)


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = []


class LogoutForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class NewUserForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = []


class UpdateUserForm(UserChangeForm):
    model = UserModel
    fields = []



