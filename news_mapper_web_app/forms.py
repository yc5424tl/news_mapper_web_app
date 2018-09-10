from django import forms
from .models import Post, Comment, NewsQuery


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'image')


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class NewQueryForm(forms.ModelForm):
    class Meta:
        model = NewsQuery
        fields = ('argument', 'type')


class SaveQueryForm(forms.ModelForm):
    #  add option to publish in this form
    class Meta:
        model = NewsQuery
        fields = ('public',)


class EditPostForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class LoginForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class LogoutForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None



