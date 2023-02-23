from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm    # Formulario de creación y autenticación de usuarios importados desde Django. 
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate # Platillas de Django preexistentes usadas para el ingreso a la aplicación
from django.db import IntegrityError
from .forms import TaskForm       # Formulario creado por el desarrollador para las tareas
from .models import Task           # Modelo creado por el desarrollador para la tareas
from django.utils import timezone
from django.contrib.auth.decorators import login_required  #Formulario Django
#from django.http import HttpResponse

# Create your views here.


def home(request):                         #Si se presiona Home en la navegación se carga el inicio de nuestra página de planificador de tareas
    return render(request, 'home.html')


def signup(request):                  #Función para el registro de usuarios nuevos en la aplicación

    if request.method == 'GET':                  #Si se obtienen datos, cargue el formulario de Singup (Registro)
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:                 # Si los datos ingresados en los campos de contraseña y confimar
            try:                                                                   #contraseña coinciden se registra el usuario y se direacciona a la
                # registrar usuario                                                #página de Taks
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:                                   #Se despliega los mensajes de error si se trata de registrar un usuario que ya se
                return render(request, 'signup.html', {              #encontraba registrado en la base de datos con un mensaje de advertencia: "El usuario"
                    'form': UserCreationForm,                        #ya existe y de igual manera si la contraseña ingresada no coincide al confirmarse
                    "error": 'Username already exists'               #le advierte al usuario que revise.
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password do no match'
        })


@login_required                                                    #Si se encuentra logueado el usuario puede acceder a la lista de tareas pendientes
def tasks(request):                                                
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required                                                    #Si se encuentra logueado el usuario puede acceder a la lista de tareas que tiene 
def tasks_completed(request):                                      #completas. Se muestra el nombre de la tarea, la descripción, la fecha en la que 
    tasks = Task.objects.filter(                                   #terminó la tarea.
        user=request.user, datecompleted__isnull=False).order_by
    ('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required                                #Si se esta logueado, se puede acceder a la págin create_task donde se asignan las tareas con los 
def create_task(request):                      #la información que se desee y que se encuentre dentro del formulario. Además se hace validacciones 
                                                #en el fomulario solicitando que la información que se ingrese sea correcta.
    if request.method == 'GET':
        return render(request, 'createTask.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'createTask.html', {
                'form': TaskForm,
                'error': 'Please provide valide data'
            })


@login_required                                                      #En esta sección se encuentra la opción de actualizar una tarea. Como los campos
def task_detail(request, task_id):                                   #deben actualizarse se realizan unas validaciones para que cumplan con los formatos.
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form,
                                                        'error': "Error updating task"})


@login_required                              #Se utiliza para visualizar el cambio de pagina al indicar que se completó la tarea
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required                              #Si se elimina una tarea se redirecciona a la misma página.
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required              #Funcion para cerrar sesión, al presionar SingOut.
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):                               #Función para crear el formulario Signin, se importa un formnulario desde Django, si se obtienen
    if request.method == 'GET':                      #datos, es decir el usuario llena los campos, se carga la misma página.
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(                                                                 #Se validan los datos ingresados advirtiendo si la contraseña
            request, username=request.POST['username'], password=request.POST['password']     #es incorrecta.
        )

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)                #Si todo esta correcto se salta a la vista de Tasks, ingresando a la aplicación.
            return redirect('tasks')
