from django.urls import reverse
from django.contrib.messages import get_messages
from utils.setup_test import TestSetup
from todo.models import Todo
from todo.forms import TodoForm
from authentication.models import User

class TodoViewsTest(TestSetup):

    def setUp(self):
        super().setUp()
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            is_completed=False,
            owner=self.user_instance
        )
        self.client.login(username=self.user_instance.username, password='VerifiedPass123')

    def test_index_view(self):
        response = self.client.get(reverse('Home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index.html')

    def test_create_todo_view_get(self):
        response = self.client.get(reverse('create-todo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/create_todo.html')
        self.assertIsInstance(response.context['form'], TodoForm)

    def test_create_todo_view_post(self):
        response = self.client.post(reverse('create-todo'), {
            'title': 'New Todo',
            'description': 'New Description',
            'is_completed': 'off'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())

    def test_todo_detail_view(self):
        response = self.client.get(reverse('todo', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo-detail.html')

    def test_delete_task_view_get(self):
        response = self.client.get(reverse('delete-task', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/delete_task.html')

    def test_delete_task_view_post(self):
        response = self.client.post(reverse('delete-task', args=[self.todo.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(id=self.todo.id).exists())

    def test_edit_task_view_get(self):
        response = self.client.get(reverse('edit-task', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/edit-task.html')
        self.assertIsInstance(response.context['form'], TodoForm)

    def test_edit_task_view_post(self):
        response = self.client.post(reverse('edit-task', args=[self.todo.id]), {
            'title': 'Updated Todo',
            'description': 'Updated Description',
            'is_completed': 'on'
        })
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        self.assertTrue(self.todo.is_completed)

    def tearDown(self):
        self.client.logout()
        User.objects.all().delete()
        Todo.objects.all().delete()
