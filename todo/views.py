from django.shortcuts import render
from .forms import TodoForm
from .models import Todo
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
 

@login_required
def show_tasks(request, todos): 
    filters = { 'complete': todos.filter(is_completed=True),
               'incomplete': todos.filter(is_completed=False) }
    filter_value = request.GET.get('filter') 
    return filters.get(filter_value,todos)

@login_required
def index(request):
    todos=Todo.objects.filter(owner=request.user)
    completed = todos.filter(is_completed=True).count()
    incomplete = todos.filter(is_completed=False).count()
    all_count = todos.count()
    context={'todos':show_tasks(request,todos),'completed_count':completed,'incomplete_count':incomplete,'total':all_count}
    return render(request,'todo/index.html',context)

@login_required
def create_todo(request):
    form = TodoForm
    context = {"form":form}
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_completed = request.POST.get('is_completed',False)
         
        todo = Todo()
        
        todo.title=title
        todo.description=description
        todo.is_completed= True if is_completed=="on" else False
        todo.owner = request.user
        
        todo.save()
        
        messages.success(request,"Task added successfully.")
        
        return HttpResponseRedirect(reverse("Home"))
        
    return render(request,'todo/create_todo.html',context)


@login_required
def todo_detail(request,id):
        todo = get_object_or_404(Todo,pk=id)
        context = {'todo':todo}
        
        if todo.owner != request.user:
            raise PermissionDenied
        
        return render(request,"todo/todo-detail.html",context)

@login_required    
def delete_task(request,id):
        todo = get_object_or_404(Todo,pk=id)
        context = {'todo':todo}
        
        if request.method == 'POST':
            if todo.owner == request.user :
                todo.delete()
                messages.success(request,"Task deleted successfully.")
                return HttpResponseRedirect(reverse('Home'))
            
            return render(request,"todo/delete_task.html",context)
        
        return render(request,"todo/delete_task.html",context)
 
@login_required    
def edit_task(request,id):
        todo = get_object_or_404(Todo,pk=id)
        form = TodoForm(instance=todo)
        context = {'todo':todo,'form':form}
        
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            is_completed = request.POST.get('is_completed',False)
        
            todo.title=title
            todo.description=description
            todo.is_completed= True if is_completed=="on" else False
        
            todo.save()
            messages.success(request,"Task updated successfully.")
        
            return HttpResponseRedirect(reverse("todo",kwargs={'id':todo.pk}))
        
        
        return render(request,"todo/edit-task.html",context)
    

    
    