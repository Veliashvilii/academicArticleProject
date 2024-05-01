from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Interest, Profile


def index(request):
    if request.method == 'GET':
        interest_areas = [
            "Artificial Intelligence and Machine Learning",
            "Data Science and Big Data Analytics",
            "Cybersecurity",
            "Blockchain and Cryptocurrency",
            "Computer Vision and Image Processing",
            "Parallel and Distributed Computing",
            "Computer Networks and Communications",
            "Computer Graphics and Virtual Reality",
            "Distributed Systems and Cloud Computing",
            "Automated Programming and Code Generation"
        ]
        return render(request, 'index/index.html', {'interest_areas': interest_areas})
    elif request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        repassword = request.POST.get('confirm_password')
        interests = request.POST.getlist('interests')

        if password == repassword:
          if User.objects.filter(email = email).exists():
            """
            Kullanıcının girdiği mail kullanılıyor!
            """
            return render(request, 'index/index.html',
              {
                "error": "This email address is already registered. Please use a different email address."
              },
              )
          else:
            """
            Kullanıcı oluşturulabilir!
            """
            user = User.objects.create_user(
              username=email,
              email=email,
              password=password,
              first_name=name,
              last_name=surname)
            user_extra = Profile.objects.create(user=user)
            user.profile.interests.clear()
            for interest_name in interests:
              interest, _ = Interest.objects.get_or_create(name=interest_name)
              user_extra.interests.add(interest)
            return render(request, 'index/signin.html')
        else:
          """
          Şifreler uyuşmuyor uyarı ver!
          """
          return render(
             request,
             'index/index.html',
             {"error": "Passwords do not match. Please enter matching passwords."},
             )

def login(request):
    return render(request, 'index/signin.html')
