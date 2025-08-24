from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['uploaded_file']


class PostForm(forms.ModelForm):
    other_information = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        fields = [ "other_information", ]