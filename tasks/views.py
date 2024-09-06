from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login
from .models import Task
from .serializers import TaskSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from .forms import CreateUserForm

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'due_date']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def signup(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
    else:
        form = CreateUserForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    due_date = request.GET.get('due_date')

    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    if due_date:
        tasks = tasks.filter(due_date=due_date)

    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_create(request):    
    if request.method == 'POST':        
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('tasks')
        else:            
            print("Form errors:", form.errors)
            messages.error(request, form.errors)
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {'form': form, 'task': task})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)    
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('tasks')