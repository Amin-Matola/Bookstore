#-----------------------------------------------------------------------------|
#--------------------- Views for handling the interact -----------------------|
#--------------------- Last Touched By: Amin Matola    -----------------------|
#--------------------- Last Modified  : 07/16/2019     -----------------------|
#-----------------------------------------------------------------------------|

from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Users,Book,Download
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User,Group
from .serializers import UserSerializer,GroupSerializer
from rest_framework import viewsets
from django.conf import settings
import os
import stripe
from django.core.files.storage import default_storage
#from django.core.servers.basehttp import FileWrapper
import mimetypes
from urllib import request as req
import requests as rt
#------------------------------------------------------------------------
#.........................Adding Views...................................|
#------------------------------------------------------------------------
def handler404(request):
    #--------------------------Handle Not Found Errors ------------------|
    return render(request,"404.html",{'url':request.path})

#-----------The home Page: http://coders.pythonanywhere.com--------------|
def index(request):
    #----------------For a new comer, retrieve only 5 books -------------|
    books            = Book.objects.all().order_by('pk')[:5]
    return render(request,
                  'data/books.html',
                  {'buks':books,
                   'current_user':request.user})


#-------------- About Us: http://coders.pythonanywhere.com/about --------|
def about(request):
    return render(request,'about.html',{})

#---------- Handle Contacts: http://coders.pythonanywhere.com/contact----|
def contact(request):
    if request.method=='GET':
        return render(request,"contact.html",{})

    sender      = request.POST.get('email','')
    message     = request.POST.get('message','')
    phone       = request.POST.get('phone','')
    rq=rt.post('someUrlToHandleContacts",
              data={'email':sender,'message':message,'phone':phone},
              )
    if rq.status_code == 200:
        return render(request,"contact.html",{'success':True})
    return render(request,"contact.html",{})
#------------------------------- Pause -----------------------------------


#------------------Make loading a user easy task -------------------------
def load_user(clas,email):
    try:
        user            = clas.objects.get(email=email)
        return user
    except Exception as e:
        return False


#------Handle Registrations: http://coders.pythonanywhere.com/register----|
def register(request):
    if request.method=='GET':
        if request.GET.get('login',''):
            return render(request,'data/people.html',{'login':False})

        return render(request,'data/people.html',{'login':True})
    if request.GET.get('register',''):
        return logn(request)
    try:
        username        = request.POST.get('username','')
        fname           = request.POST.get('fname',"")
        lname           = request.POST.get('lname',"")
        mobile          = request.POST.get('mobile','')
        email           = request.POST.get('email','')
        gender          = request.POST.get('gender',"")
        address         = request.POST.get('address','')
        role            = request.POST.get('role','')
        password        = request.POST.get('password','')
    except Exception as e:
        return HttpResponse("<h2>Hello %s, please fill your form correctly............</h2>"%request.POST.get('fname',''))

    if load_user(User,email):
        return HttpResponse("<h2>You are already registered, please <a href='/login'>login</a></h2>")
    else:
        logging_user    = User(username=username,first_name=fname,last_name=lname,email=email,password=password)
        logging_user.set_password(password)
        logging_user.save()

    if gender:
        gender          = 'male'
    else:
        gender          = 'female'

    user                = Users(user=logging_user, mobile=mobile, gender=gender, address=address)


    try:
        user.save()
    except Exception as e:
        return HttpResponse("Some Error Message In here")
    return redirect('/')



#-----------------------------Handle Logins ------------------------------|
def logn(r):
    email           = r.POST.get('email','')
    password        = r.POST.get('password','')
    userv           = False
    user            = False
    if r.GET.get('out',''):
            logout(r)
            return redirect('register')

    if email.__contains__("@"):
        try:
            user        = User.objects.get(email=email)
            userv       = user.check_password(password)
        except:
            pass
    else:
            user            = authenticate(username=email,password=password)
    if user or userv:
        login(r,user)
        books            = Book.objects.all().order_by('pk')
        return render(r,'books.html',{'buks':books,'current_user':user})

    return render(r,'people.html',{'login':True,'error':True,'u':email})


#--------------------------- Search A Book ----------------------------------|
def search(request):
    if request.method=='GET':
        user        = request.user
        data        = request.GET.get('q','')
        try:
            book    = Book.objects.filter(book_title__contains=data.title()).all()
        except Exception as e:
            return HttpResponse("That was an error :<hr>!%s"%e)

    return render(request,'books.html',{'search':book,'current_user':user,'total':len(book)})


#----------------------------------- Book Registration ------------------------------------
def book(request):

    buks        = Book.objects.all()[:5]
    people      = Users.objects.all()
    user        = request.user
    if request.method=='GET':
        if not request.user.is_authenticated:
            return register(request)
        return render(request,'data/books.html',{'buks':buks,'current_user':user})

    if not request.user.is_authenticated:
        return register(request)

    title       = request.POST['title'].title()
    auther      = request.POST.get('auther','')
    image       = request.FILES.get('image','')
    date        = request.POST.get('date','')
    category    = request.POST.get('category','')


    if image:
        #if request.user.is_superuser:
            path    = os.path.join(settings.MEDIA_ROOT,image.name)
            #image  = req.urlretrieve(url,path)
            savedto = default_storage.save(path,image)
        # else:
        #     image = req.urlretrieve('http://coders.pythonanywhere.com/media/net.jpg',image.name)

    #book           = Books(book_title=title,auther=auther,book_image=path)
    documents       = ['pdf','docx']
    file_type=image.name.split('.')[-1]
    #if file_type in documents:
    #    book       = Book(book_title=title,auther=auther,book_image='https://amix.pythonanywhere.com/static/icon.jpg' ,date_published=date,category=category)
    #else:
    book            = Book(book_title=title,auther=auther,book_image=image.name,date_published=date,category=category)
    book.save()
    try:
        return render(request,'books.html',{'book':True,'current_user':user,'buks':buks})
    except Exception as e:
        return render(request,'uploads/librarian.html',{'error':True})

#----------------------------------- Download A Book ---------------------------------------
def download(request):
    if request.method=='GET':
        if not request.user.is_authenticated:
            return redirect('register')
        ruser  = User.objects.get(pk=request.user.pk)
        user   = Users.objects.get(user=ruser)
        if not user.paid:
            #-------------------- Non-Paid Users are limited to only 5 Downloads ------------------
            if user.downloads   >=  5:
                return render(request,'data/books.html',{'buks':Book.objects.all()[:5],'etype':True})
            
        #------- Otherwise even if he is unpaid, but have less than 5 downloads --------------------
        f               = request.GET.get('img','')
        book            = Book.objects.get(pk=f)
        f_file          = book.book_image.url
        #------------- Increment book downloads by 1 and let him continue --------------------------
        book.downloads += 1
        book.save()
        file            = open(settings.MEDIA_ROOT+"/"+f_file.split('/')[-1],'rb')
        #wrapper        = FileWrapper(file(file))
        response        = HttpResponse(file.read(),content_type="application/pdf") #mimetypes.guess_type(file)[0])
        #response['Content-Length']=os.path.getsize(file)
        response['Content-Disposition'] =   'attachment; filename=%s'%f_file.split('/')[-1]
        #------------- Increment the User's downloads by 1 ------------------------------------------
        user.downloads      +=   1
        user.save()
        #------------- Everything is done, return the successful download to the browser -------------
        return response
    
   
