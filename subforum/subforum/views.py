from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Projects
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import dropbox, requests
import random, os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

def index(request):
    return render(request, "subforum/index.html")

def addNewProject(request):
    if not request.user.is_staff:
        project = Projects.objects.filter(user=request.user)
        if project:
            return redirect('dashboard')
    if request.method == 'POST':
        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        student_id = request.POST.get("student_id")
        email = request.POST.get("email")
        
        project_title = request.POST.get("title")
        url = request.POST.get("url")
        description = request.POST.get("message")
        uploaded_file = request.FILES['file']
        
        dbx = dropbox.Dropbox(refresh_dropbox_token())
        
        try:
            
            dropbox_path = f'/Projects/{random.randint(1, 100000000000000000)}-{uploaded_file.name}'
            
            dbx.files_upload(uploaded_file.read(), dropbox_path)
            
            # Create a shared link for the uploaded file
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            file_url = shared_link_metadata.url.replace("?dl=0", "?dl=1")  # Direct download link
            
            print(file_url)
            
            Projects.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                email=email,
                user=request.user,
                title=project_title,
                url=url,
                description=description,
                file=file_url
            )
            return render(request, "subforum/new_prjct.html", {
                    'success_message': 'Project submitted successfully!',
                })
        except IntegrityError as e:
                # Check the exact error type
                error_message = "An error occurred."
                if "student_id" in str(e):
                    error_message = "The Student ID is already in use."
                elif "email" in str(e):
                    error_message = "The Email is already in use."

                #return HttpResponseRedirect(f"{request.path}?error={error_message}")
                return render(request, "subforum/new_prjct.html", {
                    'first_name': first_name,
                    'last_name': last_name,
                    'student_id': student_id,
                    'email': email,
                    
                    'project_title': project_title,
                    'url': url,
                    'description': description,
                    'files': file_url,
                    'error_message': error_message,
                })

    return render(request, "subforum/new_prjct.html")


def project_detail(request, id):
    if request.method == "POST":
        project = get_object_or_404(Projects, id=id)
        grade = request.POST.get("grade")
        note = request.POST.get("note")

        # Update the project with the grade, note, status, and timestamp
        project.grade = grade
        project.grading_note = note
        project.status = "Graded"
        project.graded_at = now()
        project.save()
    context = {
        'project': get_object_or_404(Projects, id=id)
    }
    return render(request, "subforum/projectDetails.html", context)


@login_required
def dashboard(request):
    if request.user.is_staff:
        # Fetch all projects for teachers
        context = {
            'projects': Projects.objects.all(),
            'projects_count': Projects.objects.count(),
        }
    else:
        # Fetch only the logged-in student's projects
        context = {
            'projects': Projects.objects.filter(user=request.user),
            'projects_count': Projects.objects.filter(user=request.user).count(),
        }
    return render(request, "subforum/dashboard.html", context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            email = request.POST.get("email")
            identifier = request.POST.get("identifier")
            is_teacher = request.POST.get("is_teacher") == "on"
            first_name = request.POST.get("fname")
            last_name = request.POST.get("lname")

        return render(request, "subforum/login.html")

def logout_user(request):
    logout(request)
    return redirect('login')



def loginStudent(request):
    if request.method == 'POST':
        email = request.POST.get("semail")
        identifier = request.POST.get("spassword")
        if User.objects.filter(username=identifier).exists():
            user = authenticate(request, username=identifier, email=email, password=identifier)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                error_message = "Your credentials are invalid!"
                return render(request, "subforum/login.html", {'error_message': error_message})
        else:
            user = User.objects.create_user(username=identifier, email=email, password=identifier)
            login(request, user)
            return redirect('dashboard')
    return render(request, "subforum/login.html")

def loginTeacher(request):
    if request.method == 'POST':
        email = request.POST.get("temail")
        identifier = request.POST.get("tpassword")
        
        user = authenticate(request, username=email, password=identifier)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = "Your credentials are invalid!"
            return render(request, "subforum/login.html", {'error_message': error_message})
    return redirect('login')




def refresh_dropbox_token():
    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": "-lF6WO3Rb1oAAAAAAAAAATho8cs2ROEVs4XSrxj2cO5rKHMldqhiZWwVBdWuUljR",
        "client_id": "rxe4763bnpqcxjq",
        "client_secret": "woy7lkp6cizi7p5",
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        new_access_token = response.json().get('access_token')
        return new_access_token
    else:
        raise Exception("Failed to refresh access token")