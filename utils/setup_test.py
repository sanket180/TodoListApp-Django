from django.test import TestCase
from authentication.models import User
from faker import Faker

class TestSetup(TestCase):
    
    def setUp(self):
        self.fake = Faker()
        password = self.fake.password()
        
        self.user ={
            "username" : self.fake.name().split(" ")[0],
            "email" : self.fake.email(),
            "password" : password ,
            "password2" : password 
        }
        
        self.user_instance = self.create_verified_user()
        
    def create_test_user(self):
        user = User.objects.create_user(username="Example",email="testing@app.com")
        user.set_password("Passwors321")
        user.save()
        return user 
    
    def create_verified_user(self): 
        user = User.objects.create_user(username="verified_user", email="verified@example.com") 
        user.set_password("VerifiedPass123") 
        user.is_email_verified = True 
        user.save() 
        return user
    
    
    def tearDown(self):
        return super().tearDown()