from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Interest, Profile
from django.contrib.auth import authenticate, login, logout
import pymongo
import numpy as np
import fasttext
import threading, os
from transformers import AutoTokenizer, AutoModel
import torch

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

def get_data_from_mongodb(collection):
    data = []
    cursor = collection.find({})
    for document in cursor:
        data.append(document)
    return data

def get_data_from_mongodb_user(collection, email):
    data = collection.find_one({"_id": email})
    return data if data else {}

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity

def get_top_similar_articles(user_vector, article_vectors):
    similarities = []
    for article_id, article_vector in article_vectors.items():
        similarity = cosine_similarity(user_vector, article_vector)
        similarities.append((article_id, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_similar_articles = similarities[:5]
    return top_similar_articles

def get_suggest_to_fasttext(email):
    collectionArticle = connect_to_mongodb("fastext_collection")
    collectionUser = connect_to_mongodb("user_fasttext")

    article_data = get_data_from_mongodb(collectionArticle)
    user_data = get_data_from_mongodb_user(collectionUser, email)

    user_vector = user_data.get('vector')

    article_vectors = {article['_id']: article['vector'] for article in article_data}

    top_similar_articles = get_top_similar_articles(user_vector, article_vectors)
    return top_similar_articles

def get_suggest_to_scibert(email):
    collectionArticle = connect_to_mongodb("scibert_collection")
    collectionUser = connect_to_mongodb("user_scibert")

    article_data = get_data_from_mongodb(collectionArticle)
    user_data = get_data_from_mongodb_user(collectionUser, email)

    user_vector = user_data.get('vector')

    article_vectors = {article['_id']: article['vector'] for article in article_data}

    top_similar_articles = get_top_similar_articles(user_vector, article_vectors)
    return top_similar_articles

def get_vector_for_person(person):
    model = fasttext.load_model("cc.en.300.bin")
    person_vector = np.mean([model.get_word_vector(word) for word in person], axis=0)
    return person_vector

def get_vector_for_person_scibert(person):
    personToText = ""
    for interest in person:
        personToText = personToText + " " + interest
    print(f"Oldu mu: {personToText}")
    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

    inputs = tokenizer(personToText, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    text_vector = np.array(outputs.last_hidden_state.mean(dim=1).squeeze())
    return text_vector

def process_user_vector(email, interests):
    collection = connect_to_mongodb("user_fasttext")
    vector = get_vector_for_person(interests)
    save_user_vector_to_mongodb(collection, email, vector)

def process_user_vector_scibert(email, interests):
    collection = connect_to_mongodb("user_scibert")
    vector = get_vector_for_person_scibert(interests)
    save_user_vector_to_mongodb(collection, email, vector)


def get_article_text(article_id):
    base_path = "/Users/veliashvili/Desktop/Krapivin2009/docsutf8"
    file_path = os.path.join(base_path, f"{article_id}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            article_text = file.read()
        return article_text
    else:
        return None



def index(request):
    if request.user.is_authenticated:
      fasttextSuggest = get_suggest_to_fasttext(request.user.email)
      scibertSuggest = get_suggest_to_scibert(request.user.email)
      return render(request, 'user/main.html', {"fastTextSuggest": fasttextSuggest, "scibertSuggest": scibertSuggest})
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
            vector_scibert_thread = threading.Thread(target=process_user_vector_scibert, args=(email, interests))
            vector_thread.start()
            vector_scibert_thread.start()

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
        
def read_article(request):
    """
    Tıklanan Makalenin Ekranda işlenmesi
    """
    if request.method == 'POST':  
      article_name = request.POST.get('article_name')
      article_text = get_article_text(article_name)
      return render(request, 'user/article.html', {"article_name":article_name, "article_text":article_text})

def user_login(request):
    if request.user.is_authenticated:
      fasttextSuggest = get_suggest_to_fasttext(request.user.email)
      scibertSuggest = get_suggest_to_scibert(request.user.email)
      return render(request, 'user/main.html', {"fastTextSuggest": fasttextSuggest, "scibertSuggest": scibertSuggest})

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            fasttextSuggest = get_suggest_to_fasttext(request.user.email)
            scibertSuggest = get_suggest_to_scibert(request.user.email)
            return render(request, 'user/main.html', {"fastTextSuggest": fasttextSuggest, "scibertSuggest": scibertSuggest})
        else:
            return render(request, 'index/signin.html', {"error": "Invalid email or password."})
    elif request.method == 'GET':
        return render(request, 'index/signin.html')
    
def user_logout(request):
    logout(request)
    return render(request, 'index/index.html')

