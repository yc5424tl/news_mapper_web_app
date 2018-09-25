from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Post, Comment, Query


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


# class CustomUserChangeForm(UserChangeForm):
#
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'email')
#
# class CustomAuthenticationForm(AuthenticationForm):
#
#     class Meta:
#         model = CustomUser
#         fields = 'username'


class NewPostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.fields['_body'].widget.attrs['readonly'] = True
        # self.fields['_query'].widget.attrs['readonly'] = True


    class Meta:
        model = Post
        fields = ('_title', '_public', '_body')
        disabled = '_body'


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('_body',)


class NewQueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ('_argument', '_query_type')


class SaveQueryForm(forms.ModelForm):
    #  add option to publish in this form
    class Meta:
        model = Query
        fields = ('_public',)


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('_title', '_body')


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class LogoutForm(forms.ModelForm):
    class Meta:
        model = None
        fields = None


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email',]


class UpdateUserForm(UserChangeForm):
    model = User
    fields = ['email']



