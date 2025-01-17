from authentication.models import User
from todo.models import Todo
from utils.setup_test import TestSetup

class TestModel(TestSetup):
    
    
    def test_user_should_be_created(self):
        user = self.create_test_user()
        
        todo = Todo(owner=user,title = "learn" , description = "django")
        todo.save()
        
        self.assertEqual(str(todo),'learn')