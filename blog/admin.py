from django.contrib import admin
from .models import Comment, Term, Profile, Book

admin.site.register(Term)
admin.site.register(Book)
admin.site.register(Profile)
admin.site.register(Comment)