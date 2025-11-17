from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        confirm = request.POST.get('confirm_password', None)

        if not username or not email or not password:
            return render(request, 'register.html', {
                'username': username,
                'email': email,
                'error': 'All fields are required!'
            })

        if password != confirm:
            return render(request, 'register.html', {
                'username': username,
                'email': email,
                'error': 'Password do not match!'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'email': email,
                'error': 'Username already exists!'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'username': username,
                'error': 'Email already exists!'
            })

        hash_password = make_password(password)
        user = User(username=username, email=email, password=hash_password)
        user.save()

        return redirect('login')  


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {
                'username': username,
                'error': 'All fields are required!'
            })

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/') 

        return render(request, 'login.html', {
            'username': username,
            'error': "User or password is incorrect!"
        })


def logout_view(request):
    try:
        logout(request)
        return redirect('login')  
    except Exception as err:
        return HttpResponse(str(err))
