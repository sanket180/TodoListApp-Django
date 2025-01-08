from django.urls import path
from . import views
urlpatterns = [
    path("",views.index,name='Home'),
    path("create-todo/",views.create_todo,name='create-todo'),
    path("todo/<id>/",views.todo_detail,name="todo"),
    path("delete-task/<id>/",views.delete_task,name="delete-task"),
    path("edit-task/<id>/",views.edit_task,name="edit-task"),
]
   