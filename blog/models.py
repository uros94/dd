from multiselectfield import MultiSelectField
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from background_task import background
from django.utils import timezone
import datetime
import math

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True)
    likedBooks = models.ManyToManyField(
        "Book",
        null=True,
        blank=True,
        default = None,
        related_name='likedBy'
    )
    dislikedBooks = models.ManyToManyField(
        "Book",
        null=True,
        blank=True,
        default = None,
        related_name='dislikedBy'
    )
    recommendedBooks = models.ManyToManyField(
        "Book",
        null=True,
        blank=True,
        default = None,
        related_name='recommendedTo'
    )
    similarUsers = models.ManyToManyField(
        to='self',
        null=True,
        blank=True,
        default = None,
        related_name='similarTo',
        symmetrical=False
    )
    terminal = models.TextField(blank = True)

    # @background(schedule=0)
    def textToTerminal(self, text):
        self.terminal=self.terminal+"\n"+text
        self.save()

    #@background(schedule=0)
    def resetTerminal(self, text):
        self.terminal = text
        self.save()

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        terms = Term.objects.select_related().filter(user = self)
        return "Name : "+ self.user.username + "\t(terms: "+str(list(terms))+")"#+ "\t(similarUsers: "+str(users)+")"

    def recommendBooks1(user1):
        print("\nrecomendation start!!!")

        booksColl = Profile.recommendBooksColl(user1)
        print("\ncollaborative: " + str(booksColl))
        #user1.textToTerminal("\ncollaborative based list: " + str(booksColl))

        booksCont = Profile.recommendBooksCont(user1)
        print("\ncontent: " + str(booksCont))
        #user1.textToTerminal("\ncontent based list: " + str(booksCont))

        rec=[]
        for b1 in booksCont:
            for b2 in booksColl:
                if b1[1]==b2[1]:
                    rec.append([b1[0]+b2[0],b1[1]])
                    booksColl.remove(b2)
                    booksCont.remove(b1)
                    break

        rec.extend(booksCont)
        rec.extend(booksColl)

        rec.sort(key=lambda x: x[0], reverse=True)
        print("\nreccomended: " + str(rec))

        user1.recommendedBooks.clear()
        for book in rec[0:6]:
            user1.recommendedBooks.add(book[1])
        user1.textToTerminal("\nfinal list: " + str(rec[0:6]))
        return rec

    """def recommendBooks(user1):
        print("\nrecomendation start!!!")
        #timestamp = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M")
        user1.textToTerminal("\nrecomendation start!!!")
        booksColl = Profile.recommendBooksColl(user1)
        print("\ncollaborative: " + str(booksColl))
        user1.textToTerminal("\ncollaborative: " + str(booksColl))
        booksCont = Profile.recommendBooksCont(user1)
        print("\n\ncontent: " + str(booksCont))
        user1.textToTerminal("\ncontent: " + str(booksCont))
        rec = list(set(booksColl) & set(booksCont))
        if not rec: #if intersection rec empty - use union
            rec = list(set(booksColl) | set(booksCont))

        user1.recommendedBooks.clear()
        for book in rec:
            user1.recommendedBooks.add(book)
        print("\nreccomended: " + str(rec))
        return rec"""

    # @background(schedule=0)
    def updateTerms1(pk, terms, sign):
        print("Background started\n")
        user1 = User.objects.get(pk=pk)
        user1 = user1.profile
        print(pk,"identified as Profile: ", user1)
        Profile.updateTerm(user1, terms[0], 0.8 * sign)  # author
        Profile.updateTerm(user1, terms[1], 0.2 * sign)  # language
        for term in terms[2:]:  # genres
            Profile.updateTerm(user1, term, 1 * sign)
        print("Updated terms ", user1)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        user1.textToTerminal("\n" + timestamp + " New terms " + str(terms) + "\nAll terms after update "+str(user1))
        Profile.recommendBooks1(user1)

    async def updateTerms(user1, terms, sign):
        Profile.updateTerm(user1, terms[0], 0.8*sign)  # author
        Profile.updateTerm(user1, terms[1], 0.2*sign)  # language
        for term in terms[2:]:  #genres
            Profile.updateTerm(user1, term, 1*sign)

    def updateTerm(user1, term, newValue):
        termsOld = Term.objects.filter(user=user1)  # ovde moze da se upotrebi Q biblioteka
        termOld = termsOld.filter(term=term)
        if (termOld):
            termOld[0].value = termOld[0].value + newValue
            termOld[0].save()
        else:
            termNew = Term(term=term, value=newValue, user=user1)
            termNew.save()
        return

    def recommendBooksCont(user1):
        terms = list(Term.objects.filter(user=user1))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        user1.textToTerminal("\n"+timestamp + " Content based rec:")
        # normalize term values
        tmax = 0
        for t in terms:
            if abs(t.value)>tmax:
                tmax=abs(t.value)
        if tmax:
            for t in terms:
                t.value = t.value/tmax
        #print("max value:",tmax, "\nNormalized: ",terms) #DEBUG
        user1.textToTerminal("Normalized terms: " + str(terms)+"\n")

        #exclude less significant terms
        #terms.sort(key=lambda x: abs(x.value), reverse=True)
        #terms = [t for t in terms if abs(t.value) > 0.3]

        allBooks = list(Book.objects.all())
        allBooksuser1 = list(user1.likedBooks.all())
        allBooksuser1.extend(list(user1.dislikedBooks.all()))
        allBooksuser1 = list(set(allBooksuser1)) #remove duplicates
        #if allBooksuser1:
        #    for book in allBooksuser1:
        #        allBooks.remove(book)
        recBooks = []
        for term in terms:
            for book in allBooks:
                if (term.term in book.terms()):
                    if book not in allBooksuser1:
                        recBooks.append([book.evaluate(terms), book])
                        allBooks.remove(book)
                        print("eval cont --- ", book, book.evaluate(terms)) # DEBUG

        recBooks.sort(key=lambda x: x[0], reverse=True)
        for r in recBooks[0:8]:
            user1.textToTerminal("eval cont --- " + str(r[1]) + " " + str(r[0]))
        if len(recBooks)>8:
            user1.textToTerminal("... "+str(len(recBooks)-8)+" more books recommended")

        return recBooks

    def recommendBooksColl(user1):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        user1.textToTerminal("\n" + timestamp + " Collaborative based rec:")
        similarity = Profile.updateSimilarUsers(user1)

        for s in similarity[0:4]:
            user1.textToTerminal("similarity to "+s[1].user.username+": "+str(s[0]))
        if len(similarity)>4:
            user1.textToTerminal("... "+str(len(similarity)-4)+" more similar users\n")

        allBooksuser1 = list(set(user1.likedBooks.all()) | set(user1.dislikedBooks.all()))
        #print("This user ",user1.user.username, allBooksuser1) # DEBUG
        recBooks = []
        recBooksTmp = []
        for s in similarity:
            user = s[1]
            coef = s[0] * 3.5 # 3.5 is a configured value
            # avoid making duplicates
            dif = list(set(user.likedBooks.all()) - set(recBooksTmp))
            # exclude books user already liked/disliked
            dif = list(set(dif) - set(allBooksuser1))

            #print(user.user.username, user.likedBooks.all())  # DEBUG
            #print("dif: ",dif) # DEBUG

            for r in dif:
                print("eval col --- ", r,coef)
                recBooks.append([coef,r])
                recBooksTmp.append(r)

        recBooks.sort(key=lambda x: x[0], reverse=True)
        for r in recBooks[0:8]:
            user1.textToTerminal("eval coll --- " + str(r[1]) + " " + str(r[0]))
        if len(recBooks)>8:
            user1.textToTerminal("... "+str(len(recBooks)-8)+" more books recommended")

        return recBooks

    def updateSimilarUsers(user1):
        allUsers = Profile.objects.all()
        similarity = [[] * 2 for i in range(len(allUsers) - 1)]
        i = 0
        for u in allUsers:
            if (u != user1):
                commonTermsValues = Profile.commonTerms(user1, u)
                pc = Profile.pearsonCoef(commonTermsValues[0], commonTermsValues[1])
                similarity[i].append(pc)
                similarity[i].append(u)
                i = i + 1
        similarity.sort(key=lambda x: x[0], reverse=True)
        similarity = [s for s in similarity if s[0]>0.5]
        # for s in similarity:
        #    print("similarity",s[0], s[1].user.username) # DEBUG

        #user1.similarUsers.clear()
        # debug
        #for newSimilarUser in similarity:
        #    user1.similarUsers.add(newSimilarUser[1])
        return similarity

    def commonTerms(user1, otherProfile):
        terms1stUser = Term.objects.filter(user=user1)
        terms2ndUser = Term.objects.filter(user=otherProfile)
        commonTermsValues = [[] * (len(terms1stUser)) for i in range(2)]
        for t1 in terms1stUser:
            for t2 in terms2ndUser:
                if (t1.term == t2.term):
                    commonTermsValues[0].append(t1.value)
                    commonTermsValues[1].append(t2.value)
        return commonTermsValues

    def pearsonCoef(termsValues1st, termsValues2nd):
        if (len(termsValues1st) != len(termsValues2nd)):
            return -1
        if (len(termsValues1st) == 0):
            return 0
        sum1 = sum(termsValues1st)
        sum2 = sum(termsValues2nd)
        avg1 = sum1 / len(termsValues1st)
        avg1 = [avg1] * len(termsValues1st)
        avg2 = sum2 / len(termsValues2nd)
        avg2 = [avg2] * len(termsValues2nd)
        sqrSum1 = sum(map(lambda el, avg: (el - avg) ** 2, termsValues1st, avg1))
        sqrSum2 = sum(map(lambda el, avg: (el - avg) ** 2, termsValues2nd, avg2))
        complexSum = sum(
            map(lambda el1, avg1, el2, avg2: (el1 - avg1) * (el2 - avg2), termsValues1st, avg1, termsValues2nd, avg2))
        if math.sqrt(sqrSum1 * sqrSum2) == 0:
            return 0
        coef = complexSum / math.sqrt(sqrSum1 * sqrSum2)
        return coef

    @background(schedule=0)
    def removeGuests(self):
        print("started - removing guests background")
        for user in User.objects.all():
            try:
                numOfBooks = len(user.profile.likedBooks.all())+len(user.profile.dislikedBooks.all())
                if user.username.find('guest')!=-1:
                    if timezone.now() - user.last_login > timezone.timedelta(days=5) and numOfBooks>5:
                        print("deleted - ", user.username, " - last login -", user.last_login)
                        user.delete()
                elif timezone.now() - user.last_login > timezone.timedelta(days=30) and numOfBooks>3:
                        print("deleted - ", user.username, " - last login -", user.last_login)
                #if timezone.now() - user.last_login > timezone.timedelta(days=5):
            except:
                print("error --- ",user)
        print("done - removing guests background")

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=60)
    genre_list =  (
        ('Classic','Classic'),
        ('Fiction','Fiction'),
        ('Romance','Romance'),
        ('History','History'),
        ('Drama','Drama'),
        ('Politics','Politics'),
        ('Thriler','Thriler'),
        ('Poetry','Poetry'),
        ('Philosophy','Philosophy'),
        ('Psychology','Psychology'),
        ('Science-Fiction','Science-Fiction'),
        ('Nonfiction','Nonfiction'),
        ('Religion','Religion'),
        ('Cultural','Cultural'),
        ('Mystery','Mystery'),
        ('Crime','Crime'),
        ('War','War'),
        ('Adult','Adult'),
        ('American','American'),
        ('European','European'),
        ('Biography','Biography'),
        ('Art','Art'),
        ('Politics','Politics'),
        ('Science','Science'),
        ('Spanish','Spanish'),
        ('Business','Business'),
        ('Academic','Academic'),
        ('Magical-Realism','Magical-Realism'),
        ('Short-Stories','Short-Stories'),
        ('Self-Help','Self-Help'),
        ('Fantasy','Fantasy'),
        ('Young-Adult','Young-Adult')
    )
    genre = MultiSelectField(choices=genre_list,
                                 max_choices=5,
                                 max_length= 5 * 20)
    cover = models.ImageField()
    description = models.TextField()
    language = models.CharField(max_length=30)

    def __str__(self):
        return self.title+" by "+self.author

    def terms(self):
        terms = []
        terms.append(self.author)
        terms.append(self.language)
        terms.extend(self.genre)
        return terms

    #use list of terms to evaluate book value by summing users terms
    def evaluate(self, terms):
        e = 0
        for t in terms:
            if t.term in self.terms():
                e+=t.value
        # debug
        #print(self.terms(), "\n", terms,"\n",e)
        return e

class Term(models.Model):
    term = models.CharField(max_length=60)
    value = models.FloatField()
    user = models.ForeignKey(Profile, related_name='terms', on_delete=models.CASCADE)

    def get_terms(self):
        return ', '.join(self.terms_set.values_list('name', flat=True))

    def __str__(self):
        return self.term+": "+str(self.value)

    def filterBy(termsList):
        filtered=[]
        for term in termsList:
            for t in Term.objects.filter(term=term):
                filtered.append(t.user)
        print(filtered)

class Comment(models.Model):
    comment = models.TextField()
    user = models.CharField(max_length=60)
    date = models.CharField(max_length=30)
    semantics = models.CharField(max_length=1)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    #user = models.ForeignKey(Profile, related_name='comments')

    def __str__(self):
        return self.comment