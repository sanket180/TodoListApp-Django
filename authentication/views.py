from django.shortcuts import render,redirect
from django.contrib import messages
from validate_email import validate_email
from .models import User
from django.contrib.auth import login,authenticate,logout
from helpers.decorators import logged_in_user_no_access

@logged_in_user_no_access
def log_in(request):
    if request.method == "POST":
        context = {"data":request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request,username=username,password=password)
        
        if not user :
            messages.add_message(request,messages.ERROR,"Invalid username or password")
            return render(request,'authentication/login.html',context)
        
        login(request,user)
        messages.add_message(request,messages.SUCCESS,f"Welcome {username} to Todo app")
        return redirect('Home')
        
    return render(request,'authentication/login.html')

@logged_in_user_no_access
def register(request):
    if request.method =="POST":
        context = {"has_error":False,"data":request.POST}
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if len(password) < 6 :
            messages.add_message(request,messages.ERROR,"Password should be atleast 6 characters")
            context['has_error'] = True
        if password != password2 :
            messages.add_message(request,messages.ERROR,"Password mismatched")
            context['has_error'] = True
            
        if not validate_email(email):
            messages.add_message(request,messages.ERROR,"Please enter a valid Email")
            context['has_error'] = True
        
        if User.objects.filter(username=username).exists():
            messages.add_message(request,messages.ERROR,"Username is taken choose another one")
            context['has_error'] = True
        
        if User.objects.filter(email=email).exists():
            messages.add_message(request,messages.ERROR,"Email is taken choose another one")
            context['has_error'] = True
            
        if context['has_error']:
            return render(request,'authentication/register.html',context)
        
        user = User.objects.create_user(email=email,username=username)
        user.set_password(password)
        user.save()
        
        messages.success(request,"Account created successfully.")
        
        return redirect('login')
            
        
    return render(request,'authentication/register.html')

def user_logout(request):
    logout(request)
    messages.success(request,"Logged out successfully.")
        
    return redirect('login')
