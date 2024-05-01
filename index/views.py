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
            return HttpResponse("Bu mail zaten var!")
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
            for interest_name in interests:
              #interest = Interest.objects.get(pk=interest_id)
              interest, _ = Interest.objects.get_or_create(name=interest_name)
              user_extra.interests.add()
            
            ## İşlem burada olacak
            return HttpResponse("Kayıt Başarılı Abi!")
        else:
          """
          Şifreler uyuşmuyor uyarı ver!
          """
          return HttpResponse("Şifreler de aynı değil ki abi!")

def login(request):
    return render(request, 'index/signin.html')
