from django.forms import ModelForm
from django import forms
from .models import Post, Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        labels = {
            'content': '',
            'image': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'cols': 200, 'rows': 10}),
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'cols': 200, 'rows': 2}),
        }


