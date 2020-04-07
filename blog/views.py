from django.shortcuts import render, get_object_or_404, redirect
from .models import Comment, Profile, Term, Book, User
from .forms import CommentForm, BookForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from . import commentSemantics
import datetime

def book_detail(request, pk):
    book = get_object_or_404(Book, id=pk)
    read = False
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES or None, instance=book)
        comment = request.POST.get('comment')
        if comment:
            sentiment = commentSemantics.classify(comment)
            now = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M")
            newComment = Comment(comment=comment, book=book, user=request.user.username, semantics=sentiment, date=str(now))
            newComment.save()

            user = request.user.profile
            user.updateTerms(book.author, float(sentiment) * 0.8)
            user.updateTerms(book.genre, float(sentiment) * 1.0)
            user.updateTerms(book.language, float(sentiment) * 0.2)
            if sentiment == 1:
                user.likedBooks.add(book)
            else:
                user.dislikedBooks.add(book)
            user.recommendBooks()
            return redirect('book_detail', pk)
    else:
        form = BookForm(instance=book)
    allBooksuser1 = list(request.user.profile.likedBooks.all())
    allBooksuser1.extend(list(request.user.profile.dislikedBooks.all()))
    comments = list(Comment.objects.filter(book=book))
    if allBooksuser1:
        read = book in allBooksuser1
    return render(request, 'blog/book_detail.html', {'form': form, 'book': book, 'read': read, 'comments': comments})

def book_like(request, pk):
    object = get_object_or_404(Book, id=pk)
    Profile.updateTerms(request.user.profile,object.author, 0.8) #run async
    Profile.updateTerms(request.user.profile,object.genre, 1.0) #run async
    Profile.updateTerms(request.user.profile,object.language, 0.2) #runasync
    request.user.profile.likedBooks.add(object)
    Profile.recommendBooks(request.user.profile) #run async
    return redirect('home')

def book_dislike(request, pk):
    object = get_object_or_404(Book, id=pk)
    Profile.updateTerms(request.user.profile, object.author, -0.8)  # run async
    Profile.updateTerms(request.user.profile, object.genre, -1.0)  # run async
    Profile.updateTerms(request.user.profile, object.language, -0.2)  # runasync
    request.user.profile.likedBooks.add(object)
    Profile.recommendBooks(request.user.profile)  # run async
    return redirect('home')

def home(request):
    profile = Profile.objects.get(user=request.user)
    recBooks = list(profile.recommendedBooks.all())
    allBooksuser1 = list(profile.likedBooks.all())
    allBooksuser1.extend(list(profile.dislikedBooks.all()))
    if allBooksuser1:
        for book in allBooksuser1:
            if book in recBooks:
                recBooks.remove(book)
    books=Book.objects.all()
    query = request.GET.get("search")
    if query:
        books=books.filter(Q(title__icontains=query) | Q(author__icontains=query)).distinct()
    return render(request, 'blog/home.html', {'profile': profile, 'recBooks': recBooks[0:6], 'books': books})

def first(request):
    return render(request, 'registration/home.html', {})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def add_comment_to_post(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('book_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('book_detail', pk=comment.post.pk)