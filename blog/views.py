from django.shortcuts import render, get_object_or_404, redirect
from .models import Comment, Profile, Term, Book, User
from .forms import CommentForm, BookForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
import random
from . import commentSemantics
import datetime

def book_detail(request, pk):
    if (not request.user.is_authenticated):
        return redirect('first')
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

def new_user(request):
    if(not request.user.is_authenticated):
        return redirect('first')
    profile = Profile.objects.get(user=request.user)
    books=Book.objects.all()

    if 'like' in request.POST:
        print("LIKE")
        return redirect('new_user')
    elif 'dislike' in request.POST:
        print("DISLIKE")
        return redirect('new_user')
    allBooksuser1 = list(profile.likedBooks.all())
    allBooksuser1.extend(list(profile.dislikedBooks.all()))
    if allBooksuser1:
        for book in allBooksuser1:
            if book in books:
                books.remove(book)

    query = request.GET.get("search")
    if query:
        books=books.filter(Q(title__icontains=query) | Q(author__icontains=query)).distinct()
    return render(request, 'blog/new_user.html', {'profile': profile, 'books': books})

def book_like(request, pk):
    if (not request.user.is_authenticated):
        return redirect('first')
    object = get_object_or_404(Book, id=pk)
    Profile.updateTerms(request.user.profile,object.author, 0.8) #run async
    Profile.updateTerms(request.user.profile,object.genre, 1.0) #run async
    Profile.updateTerms(request.user.profile,object.language, 0.2) #runasync
    request.user.profile.likedBooks.add(object)
    Profile.recommendBooks(request.user.profile) #run async
    return redirect('home')

def book_dislike(request, pk):
    if (not request.user.is_authenticated):
        return redirect('first')
    object = get_object_or_404(Book, id=pk)
    Profile.updateTerms(request.user.profile, object.author, -0.8)  # run async
    Profile.updateTerms(request.user.profile, object.genre, -1.0)  # run async
    Profile.updateTerms(request.user.profile, object.language, -0.2)  # runasync
    request.user.profile.likedBooks.add(object)
    Profile.recommendBooks(request.user.profile)  # run async
    return redirect('home')

def home(request):
    if(not request.user.is_authenticated):
        return redirect('first')
    profile = Profile.objects.get(user=request.user)
    recBooks = list(profile.recommendedBooks.all())
    allBooksuser1 = list(profile.likedBooks.all())
    allBooksuser1.extend(list(profile.dislikedBooks.all()))
    if len(allBooksuser1)>2: #do not show any recs if the user haven't liked more than 2 books
        for book in allBooksuser1:
            if book in recBooks:
                recBooks.remove(book)
    else:
        recBooks=[] #do not show any recs if the user haven't liked more than 2 books
    books=Book.objects.all()
    query = request.GET.get("search")
    if query:
        books=books.filter(Q(title__icontains=query) | Q(author__icontains=query)).distinct()

    ## paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 12)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    return render(request, 'blog/home1.html', {'profile': profile, 'recBooks': recBooks[0:6], 'books': books})

def first(request):
    return render(request, 'registration/home.html', {}) ##

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

def guest(request):
    seed = datetime.datetime.now().strftime("%H%M%S")
    random.seed(seed)
    username = "guest" + str(random.randint(0, 9999))
    raw_password = "1234"
    User.objects.create_user(username=username, password=raw_password)
    user = authenticate(username=username, password=raw_password)
    login(request, user)
    return redirect('home')


