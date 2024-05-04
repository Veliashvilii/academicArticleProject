from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Interest, Profile
from django.contrib.auth import authenticate, login, logout
import pymongo
import numpy as np
import fasttext
import threading

def connect_to_mongodb(collection):
    client = pymongo.MongoClient("mongodb://localhost:27017/") 
    db = client["vectors"]
    collection = db[collection]
    return collection

def save_user_vector_to_mongodb(collection, email, vector):
    user_data = {
        "_id": email,
        "vector": vector.tolist()
    }
    collection.insert_one(user_data)
    print("Kullanıcı vektörü başarıyla MongoDB'ye kaydedildi.")

def get_vector_for_person(person):
    model = fasttext.load_model("cc.en.300.bin")
    person_vector = np.mean([model.get_word_vector(word) for word in person], axis=0)
    return person_vector

def process_user_vector(email, interests):
    collection = connect_to_mongodb("user_fasttext")
    vector = get_vector_for_person(interests)
    save_user_vector_to_mongodb(collection, email, vector)

def index(request):
    if request.user.is_authenticated:
      return render(request, 'user/main.html', {"num_of_cards": range(5)})
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
        """
        Üyelik İşleminin Gerçekleştirilmesi..
        """
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
            
            # To optimize the project, vector operations should be run asynchronously.
            vector_thread = threading.Thread(target=process_user_vector, args=(email, interests))
            vector_thread.start()

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

def user_login(request):
    if request.user.is_authenticated:
       return render(request, 'user/main.html', {"num_of_cards": range(5)})

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'user/main.html', {"num_of_cards": range(5)})
        else:
            return render(request, 'index/signin.html', {"error": "Invalid email or password."})
    elif request.method == 'GET':
        return render(request, 'index/signin.html')
    
def user_logout(request):
    logout(request)
    return render(request, 'index/index.html')

