from django import forms
from .models import Post, Comment
from .models import Book, Profile, Term

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'cover', 'genre', 'description', 'language')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text',)

