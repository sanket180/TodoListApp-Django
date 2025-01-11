from django.shortcuts import render,redirect
from django.contrib import messages
from validate_email import validate_email
from .models import User
from django.contrib.auth import login,authenticate,logout
from helpers.decorators import logged_in_user_no_access
from django.utils.cache import add_never_cache_headers
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from .utils import generate_token
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
import threading


class EmailThread(threading.Thread):
    
    def __init__(self, email):
        self.email = email 
        threading.Thread.__init__(self)
        
    def run(self):
        self.email.send()


def send_activation_mail(request,user):
    current_site = get_current_site(request)
    email_subject = 'Email verification'
    email_body = render_to_string('authentication/activate.html',{
        'user':user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : generate_token.make_token(user)
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,
                 from_email=settings.EMAIL_FROM_USER,
                 to=[user.email])
    EmailThread(email).start()
    

@logged_in_user_no_access
def log_in(request):
    
    if request.user.is_authenticated:
        return redirect('Home')
    
    if request.method == "POST":
        context = {"data":request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request,username=username,password=password)
        
        if not user.is_email_verified:
            messages.add_message(request,messages.ERROR,"Please verify your mail. A verfication message has been mailed to you.")
            return render(request,'authentication/login.html',context)
        
        if not user :
            messages.add_message(request,messages.ERROR,"Invalid username or password")
            return render(request,'authentication/login.html',context)
        
        login(request,user)
        messages.add_message(request,messages.SUCCESS,f"Welcome {username} to Todo app")
        return redirect('Home')
        
    response = render(request,'authentication/login.html')
    add_never_cache_headers(response)
    return response

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
        
        send_activation_mail(request,user)
        
        messages.success(request,"Account created successfully! Please verify your email by clicking on the link we have sent to you.")
        
        return redirect('login')
            
        
    return render(request,'authentication/register.html')

def user_logout(request):
    logout(request)
    messages.success(request,"Logged out successfully.")
        
    return redirect('login')

def verify_user(request,uidb64,token):
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
    except Exception as e:
        user = None
        
    if user and generate_token.check_token(user,token):
        user.is_email_verified = True
        
        user.save()
        
        messages.add_message(request,messages.SUCCESS,'Email verified, You can now Login. ')
        return redirect(reverse('login'))
    
    return render(request,'authentication/activation-failed.html',{"user":user})
