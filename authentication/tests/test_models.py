from authentication.models import User
from utils.setup_test import TestSetup

class TestModel(TestSetup):
    
    
    def test_user_should_be_created(self):
        user = self.create_test_user()
        self.assertEqual(str(user),user.email)