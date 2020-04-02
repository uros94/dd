from django import forms
from .models import Post, Comment
from .models import Book, Profile, Term

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'cover', 'genre', 'description', 'language')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text',)

