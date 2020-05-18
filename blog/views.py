from django.shortcuts import render, get_object_or_404, redirect
from .models import Comment, Profile, Term, Book, User
from .forms import BookForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
import random
from . import commentSemantics
import datetime
import os

#remove old guest accounts
#Profile.removeGuests(repeat=10, repeat_until=None)

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
            profile = request.user.profile
            profile.textToTerminal("\n"+str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")) + " " + profile.user.username + " left a comment: \"" + comment+ "\", sentiment: "+str(sentiment))

            if sentiment != 0:

                """terms_list = []
                terms_list.append(book.author)
                terms_list.append(book.language)
                terms_list.extend(book.genre)
                print("Sending: ", request.user.pk, terms_list, sentiment)
                Profile.updateTerms1(request.user.pk, terms_list, sentiment)  # run async
                #asyncio.run(Profile.updateTerms(request.user.profile, terms_list, sentiment))  # run async
        
                if sentiment == 1:
                    user.likedBooks.add(book)
                elif sentiment == -1:
                    user.dislikedBooks.add(book)"""

                if sentiment == 1:
                    return redirect('book_like', pk)
                elif sentiment == -1:
                    return redirect('book_dislike', pk)

            return redirect('book_detail', pk)
    else:
        form = BookForm(instance=book)
    allBooksuser1 = list(request.user.profile.likedBooks.all())
    allBooksuser1.extend(list(request.user.profile.dislikedBooks.all()))
    comments = list(Comment.objects.filter(book=book))
    if allBooksuser1:
        read = book in allBooksuser1
    return render(request, 'blog/book_detail.html', {'form': form, 'book': book, 'read': read, 'comments': comments})

def terminal(request):
    return render(request, 'blog/terminal.html', {})

def book_like(request, pk):
    if (not request.user.is_authenticated):
        return redirect('first')
    object = get_object_or_404(Book, id=pk)
    terms_list = []
    terms_list.append(object.author)
    terms_list.append(object.language)
    terms_list.extend(object.genre)
    print("Sending: ",request.user.pk, terms_list, 1)
    request.user.profile.textToTerminal("\n"+str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")) + " " + request.user.username + " liked: "+str(object))
    Profile.updateTerms1(request.user.pk, terms_list, 1)  # run async
    #asyncio.run(Profile.recommendBooks(request.user.profile))  # run async
    #asyncio.ensure_future(Profile.updateTerms(request.user.profile, terms_list, 1))  # run async
    request.user.profile.likedBooks.add(object)
    return redirect('home')

def book_dislike(request, pk):
    if (not request.user.is_authenticated):
        return redirect('first')
    object = get_object_or_404(Book, id=pk)
    terms_list = []
    terms_list.append(object.author)
    terms_list.append(object.language)
    terms_list.extend(object.genre)
    print("Sending: ",request.user.pk, terms_list, -1)
    request.user.profile.textToTerminal("\n"+str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")) + " " + request.user.username + " disliked: "+str(object))
    Profile.updateTerms1(request.user.pk, terms_list, -1)  # run async
    #asyncio.run(Profile.updateTerms(request.user.profile, terms_list, -1))  # run async
    #asyncio.run(Profile.recommendBooks(request.user.profile))  # run async
    request.user.profile.likedBooks.add(object)
    return redirect('home')

def home(request):
    if(not request.user.is_authenticated):
        return redirect('first')
    profile = Profile.objects.get(user=request.user)
    recBooks = list(profile.recommendedBooks.all())
    allBooksuser1 = list(profile.likedBooks.all())
    allBooksuser1.extend(list(profile.dislikedBooks.all()))
    if len(allBooksuser1)>2: #do not show any recs if the user haven't liked more than 2 books
        for book in recBooks:
            if book in allBooksuser1:
                recBooks.remove(book)
    else:
        recBooks=[] #do not show any recs if the user haven't liked more than 2 books
    books=Book.objects.all()
    query = request.GET.get("search")
    if query:
        request.user.profile.textToTerminal("\n" + str(datetime.datetime.now().strftime(
            "%Y-%m-%d at %H:%M:%S")) + " " + request.user.username + " searched for: " + str(query))
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

    return render(request, 'blog/home1.html', {'profile': profile, 'recBooks': recBooks[0:6], 'books': books, 'read': allBooksuser1})

def first(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                user.profile.resetTerminal(str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"))+ " " + user.username + " logged in")
                return redirect('home')
            #else:
            #    return HttpResponse("Your account was inactive.")
        else:
            print("Username or password incorrect!")

            return render(request, 'registration/home.html', {'error': "Username or password incorrect!"})
    else:
        return render(request, 'registration/home.html', {})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            form.save()
            user = authenticate(username=username, password=raw_password)
            user.profile.resetTerminal(str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"))+ " " + user.username + " logged in")
            login(request, user)
            return redirect('home')
        else:
            print("failed", form.errors)
            return render(request, 'registration/signup.html', {'error': form.errors})
    #else:
        #form = UserCreationForm()
    return render(request, 'registration/signup.html', {})

def guest(request):
    seed = datetime.datetime.now().strftime("%H%M%S")
    random.seed(seed)

    #make sure this is unique guest ID
    while True:
        username = "guest" + str(random.randint(0, 9999))
        raw_password = "1234"
        if not User.objects.filter(username=username):
            break

    User.objects.create_user(username=username, password=raw_password)
    user = authenticate(username=username, password=raw_password)
    user.profile.resetTerminal(str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"))+ " "+ user.username + " logged in")
    login(request, user)
    return redirect('home')

def test(request):
    root = os.getcwd()
    directory = root+'\dataset'
    imgs = root+'\imgs'
    for filename in os.listdir(directory):
        try:
            f = open(directory+'\\'+filename, "r", encoding='utf-8')
            x = f.read()
        except:
            print("error --- reading ", filename)
            continue

        try:
            x=x.split("\n")
        except:
            print(f.read())
            print("error --- splitting", filename)
            continue

        try:
            title = filename.split(".")[0]
            author=x[0]
            language=x[1]
            genre=x[2].split(" ")
            description='\n'.join(x[3:])
            img=imgs+'\\'+title+'.jpg'
            newBook = Book(title=title, author=author, genre=genre, cover=img, description=description, language=language)
            newBook.save()
            print("added --- ", filename)
        except:
            print("error --- ",filename)
            continue

    return redirect('home')

