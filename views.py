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
