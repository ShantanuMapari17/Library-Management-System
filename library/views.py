from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from .models import Members,Book,Transactions
# Create your views here.
from django.http import HttpResponse
from .forms import ModelForm,MemberForm,AddBookForm,BookIssueForm,BookReturnForm
from .forms import *
import requests
from django.contrib import messages
from datetime import date
from django.db.models import Q


page = 1

#HomePage
def index(request):
    # return HttpResponse("Hello, world. Welcome to Library Management Service.")
    context={
        "name" : "shantanu",
    }
    return render(request,"library/main.html",context)

# books home page
def books_home(request):
    
    if request.GET.get('q'):
        q=request.GET['q']
    else:
        q=''
    books = Book.objects.filter(
        Q(title__icontains = q)|
        Q(authors__icontains = q)|
        Q(isbn__icontains=q)
    )

    context={}
    context['books'] = books
    return render(request,'library/books.html',context)

def add_books(request):
    global page
    if request.method=="POST":
        form=AddBookForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data['title']
            authors=form.cleaned_data['authors']
            isbn=form.cleaned_data['isbn']
            publisher=form.cleaned_data['publisher']
            quantity=form.cleaned_data['quantity']
            page=form.cleaned_data['page']
            if not page:
                page=1           

            books=[]
            #randomly add given quantity of books in db
            #no of times we need to loop
            n=int(quantity/20)
            #remaining books to parse
            remain=quantity%20
            # looping to for numbers of pages to get desired number of books
            for i in range(n):
                #defining params
                params = {
                    'title': title,
                    'authors': authors,
                    'isbn': isbn,
                    'publisher': publisher,
                    'page':page
                }
                #api call
                api_url = 'https://frappe.io/api/method/frappe-library'
                response = requests.get(api_url,params).json()['message']
                #need to insert each book in books[], so parse response
                for book in response:
                    books.append(book)
                page=(page+1)


            # for remiaing entris
            if remain:
                params = {
                    'title': title,
                    'authors': authors,
                    'isbn': isbn,
                    'publisher': publisher,
                    'page':page
                }
                api_url = 'https://frappe.io/api/method/frappe-library'
                response = requests.get(api_url,params).json()['message']
                for k in range(remain):
                    book=response[k]
                    books.append(book)

            #for importing specific books needs clarification about statement
            # while len(books) < quantity:
            #     params = {
            #         'title': title,
            #         'authors': authors,
            #         'isbn': isbn,
            #         'publisher': publisher,
            #         'page':page
            #     }
            #     #api call
            #     api_url = 'https://frappe.io/api/method/frappe-library'
            #     response = requests.get(api_url,params).json()['message']
            #     #need to insert each book in books[], so parse response
            #     for book in response:
            #         books.append(book)
            #         if len(books)>=quantity:
            #             break
            #     page=(page+1)
                
            #if no books found then return 
            if len(books)==0:
                return HttpResponse("No books found found")
            
            #add books to db
            for book in books:
                cur_title=book['title']
                cur_authors=book['authors']
                cur_isbn=book['isbn']
                cur_publisher=book['publisher']
                queried_books=Book.objects.filter(title=cur_title,authors=cur_authors,isbn=cur_isbn)
                if queried_books:
                    for prev_book in queried_books:
                        prev_book.quantity=prev_book.quantity+1
                        prev_book.save()
                else:
                    new_book = Book(title=cur_title,authors=cur_authors,isbn=cur_isbn,quantity=1,publisher=cur_publisher)
                    new_book.save()
            
            return HttpResponse("Added books")
    else:
        form = AddBookForm()

    context={}
    context['form']=form
    return render(request,'library/add_books.html',context)


def confirm_delete_book(request,pk):
    book = Book.objects.filter(id=pk)
    book.delete()
    messages.success(request,"Book deleted Successfully!!")
    return redirect('index')


def delete_book(request,pk):
    book = Book.objects.get(id=pk)
    context={}
    context['book']=book
    return render(request,'library/confirm_delete_book.html',context)

def issue_book(request):
    form = BookIssueForm()
    if request.method=="POST":
        form = BookIssueForm(request.POST)
        if form.is_valid():
            transaction=form.save(commit=False)            
            transaction.return_date=None
            book = transaction.book
            member = transaction.member
            
            #need to check if user has already taken the same book
            temp = Transactions.objects.filter(book=book, member=member)
            # breakpoint()
            if(temp):
                messages.error(request,"Can not issue the same book")
                return redirect('issue_book')

            #check for the debt
            if member.debt>=500:
                messages.error(request,"Members Debt more than 500 ! Can not issue book")
                return redirect('issue_book')
            book.quantity=book.quantity-1

            #check for book quantity
            if book.quantity<0:
                messages.error(request,"Not sufficient Quantity of Book!")
                return redirect('issue_book')
            book.save()
            transaction.save()
            messages.success(request,"Book Issued Succesfully")
            return redirect('issue_book')
    
    context={}
    context['form']=form
    return render(request,'library/issue_book.html',context)


def return_book(request):
    form = BookReturnForm()
    if request.method=="POST":
        form = BookReturnForm(request.POST)     
        cur_transaction=form.save(commit=False)
        book=cur_transaction.book
        member = cur_transaction.member

       
        temp = Transactions.objects.filter(book = book, member=member)
        #if transaction does not exit in the db return with error message
        if not temp:
            messages.error(request," This user has not borrowed this book!")
            return redirect('return_book')
        
        temp=temp[0]
        if temp.return_date is not None:
            messages.error(request,"This book has been returned already")
            return redirect('return_book')
        # breakpoint()
        return_date = cur_transaction.return_date
        issue_date = temp.issue_date
        #update the transation return date
        temp.return_date = return_date
        #calculate the debt for the user and add to db
        no_of_days_book_used = (return_date-issue_date).days
        if no_of_days_book_used < 0:
            messages.error(request,"Can not use previous date for return!!")
            return redirect('return_book')
        debt = no_of_days_book_used*5
        member.debt=debt
        book.quantity=book.quantity+1
        book.save()
        member.save()
        temp.delete()

        messages.success(request,"Book returned Successfully")
        return redirect('index')
    
    context={}
    context['form']=form
    return render(request,'library/return_book.html',context)

#displaying books details
def show_book_detail(request,pk):
    book = Book.objects.filter(id=pk)
    
    temp = Transactions.objects.filter(book = book[0])
    
    members=[]
    for transaction in temp:
        if not transaction.return_date:
            member = transaction.member
            members.append(member)
    # breakpoint()
    context={}
    context['book']=book[0]
    context['members']=members
    context['transactions']=temp
    return render(request,'library/book_details.html',context)

#redirecting to members home page
def members_home(request):
    if request.GET.get('q'):
        q=request.GET['q']
    else:
        q=''
    members = Members.objects.filter(
        Q(first_name__icontains = q)|
        Q(last_name__icontains = q)|
        Q(email__icontains=q)
    )

    # members = Members.objects.all()
    context={
        'members':members
    }
    return render(request,"library/members.html",context)

#function to add new member
def add_member(request):
    if(request.method=='POST'):
        form = MemberForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            #need to check if member already exists
            temp = Members.objects.filter(first_name=first_name,last_name=last_name,email=email)
            if temp:
                messages.error(request,"User already exists!!")
                return redirect('add_member')

            member = Members(first_name=first_name,last_name=last_name,email=email)
            member.save()
            return redirect('index')
    else:
        form = MemberForm()
    
    context={}
    context['form']=form
    context['name']="shantanu"
    return render(request,'library/add_members.html',context)

#showing members details
def members_detail(request,pk):
    member = Members.objects.get(id = pk)
    transactions = Transactions.objects.filter(member=member)
    books=[]
    for transaction in transactions:
        books.append(transaction.book)
    context={}
    context['member']=member
    context['books']=books
    context['transactions']=transactions
    return render(request,'library/members_detail.html',context)

#function to render a page for confirming delete operation
def delete_member(request,pk):
    member = Members.objects.get(id=pk)
    context={}
    context['member']=member    
    return render(request,'library/confirm_delete_member.html',context)

#perform delete operation based on pk
def confirm_delete_member(request,pk):
    member = Members.objects.get(id=pk)
    member.delete()
    messages.success(request,"Deleted Member Successfully")
    return redirect('index')

#function to render confirmation form whether to clear debt or not
def clear_debt(request):
    # breakpoint()
    #get user and redirect it to confirm delete page
    if request.method=="POST":
        member_id = request.POST['mem_id']
        member = Members.objects.filter(id=member_id)[0]
        context={}
        context['member']=member
        return render(request,'library/confirm_debt_clear.html',context)
    
    members = Members.objects.all()
    context={}
    context['members']=members
    return render(request,'library/clear_debt.html',context)


#after confirmation to delete the debt 
def confirm_debt_clear(request,pk):
    member = Members.objects.get(id=pk)
    member.debt=0
    member.save()
    messages.success(request,f"Cleared debt successfull of member {member.first_name} {member.last_name}")
    return redirect('index')