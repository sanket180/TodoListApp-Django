from django.contrib.auth.decorators import user_passes_test

def check_user(user):
    return not user.is_authenticated

user_logout_required = user_passes_test(check_user,'/',None)

def logged_in_user_no_access(view_fun):
     return user_logout_required(view_fun)   