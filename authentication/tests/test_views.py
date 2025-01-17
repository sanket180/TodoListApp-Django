from django.urls import reverse
from django.contrib.messages import get_messages
from utils.setup_test import TestSetup
from authentication.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from authentication.utils import generate_token

class TestViews(TestSetup):

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/register.html")

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")

    def test_should_signup_user(self):
        response = self.client.post(reverse("register"), data=self.user)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.user["username"]).exists())

    def test_should_not_signup_user_with_taken_username(self):
        self.client.post(reverse("register"), data=self.user)
        response = self.client.post(reverse("register"), data=self.user)
        self.assertEqual(response.status_code, 409)
        storage = get_messages(response.wsgi_request)
        self.assertIn("Username is taken choose another one", list(map(lambda x: x.message, storage)))

    def test_should_not_signup_user_with_taken_email(self):
        self.client.post(reverse("register"), data=self.user)
        user2 = {
            "username": "another_user",
            "email": self.user["email"],
            "password": "password12",
            "password2": "password12"
        }
        response = self.client.post(reverse("register"), data=user2)
        self.assertEqual(response.status_code, 409)
        storage = get_messages(response.wsgi_request)
        self.assertIn("Email is taken choose another one", list(map(lambda x: x.message, storage)))

    def test_login_view_authenticated_redirect(self):
        self.client.force_login(self.user_instance)
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('Home'))

    def test_login_view_invalid_credentials(self):
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        storage = get_messages(response.wsgi_request)
        self.assertIn("Invalid username or password", list(map(lambda x: x.message, storage)))

    def test_login_view_email_not_verified(self):
        self.user_instance.is_email_verified = False
        self.user_instance.save()
        response = self.client.post(reverse('login'), {'username': self.user_instance.username, 'password': 'VerifiedPass123'})
        self.assertEqual(response.status_code, 200)
        storage = get_messages(response.wsgi_request)
        self.assertIn("Please verify your mail. A verification message has been mailed to you.", list(map(lambda x: x.message, storage)))

    def test_login_view_success(self):
        self.user_instance.is_email_verified = True
        self.user_instance.save()
        response = self.client.post(reverse('login'), {'username': self.user_instance.username, 'password': 'VerifiedPass123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('Home'))

    def test_user_logout_view(self):
        self.client.force_login(self.user_instance)
        response = self.client.get(reverse('user_logout'))
        self.assertEqual(response.status_code, 302)

    def test_verify_user_view(self):
        self.user_instance.is_email_verified = False
        self.user_instance.save()
        uid = urlsafe_base64_encode(force_bytes(self.user_instance.pk))
        token = generate_token.make_token(self.user_instance)
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(response.status_code, 302)
        self.user_instance.refresh_from_db()
        self.assertTrue(self.user_instance.is_email_verified)
