from django.shortcuts import render
from django.contrib.auth import logout
from index.models import Profile, Interest
from index.views import connect_to_mongodb, get_vector_for_person, get_vector_for_person_scibert, get_data_from_mongodb_user, get_data_from_mongodb
import threading
import numpy as np

def process_user_vector(email, interests):
    collection = connect_to_mongodb("user_fasttext")
    vector = get_vector_for_person(interests)
    result = collection.update_one({"_id": email}, {"$set": {"vector": vector.tolist()}})
    if result.modified_count > 0:
        print("FastText Belge güncellendi.")
    else:
        print("FastText Belge güncellenemedi.")

def process_user_vector_scibert(email, interests):
    collection = connect_to_mongodb("user_scibert")
    vector = get_vector_for_person_scibert(interests)
    result = collection.update_one({"_id": email}, {"$set": {"vector": vector.tolist()}})
    if result.modified_count > 0:
        print("SCIBERT Belge güncellendi.")
    else:
        print("SCIBERT Belge güncellenemedi.")

def update_user_vector_to_mongodb(collection, id, vector):
    result = collection.update_one({"_id": id}, {"$set": {"vector": vector.tolist()}})
    if result.modified_count > 0:
        print("User Belge güncellendi.")
    else:
        print("User Belge güncellenemedi.")

def user_logout(request):
    logout(request)
    return render(request, 'index/index.html')

def user_profile(request):
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
    if request.method == "GET":
        user = request.user
        user_profile = Profile.objects.get(user=user)

        name = user.first_name
        surname = user.last_name
        email = user.email
        interests = user_profile.interests.all()
        current_interests = []

        for interest in interests:
            current_interests.append(interest.name)

        return render(request, 'user/profile.html', {'interest_areas': interest_areas, 'user': user, 'current_interests': current_interests})
    elif request.method == "POST":
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        interests = request.POST.getlist('interests')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        user = request.user
        if password != "" and repassword != "":
            if password == repassword:
                user.set_password(password)
            else:
                return render(request, 'user/profile.html',
                            {"error": "Passwords do not match. Please enter matching passwords.",
                                'interest_areas': interest_areas},
                            )
        elif password != "" and repassword == "":
            return render(request, 'user/profile.html',
                    {"error": "Please confirm your password",
                      'interest_areas': interest_areas},
                    )
        elif password == "" and repassword != "":
            return render(request, 'user/profile.html',
                    {"error": "Please enter your password",
                      'interest_areas': interest_areas},
                    )
        if name != "" and user.first_name != name:
            user.first_name = name
        if surname != "" and user.last_name != surname:
            user.last_name = surname
        if email != "" and user.email != email:
            user.username = email
            user.email = email
        if interests != []:
            user_profile = Profile.objects.get(user=user) 
            if set(interests) != set(user_profile.interests.values_list('name', flat=True)):
                user_profile.interests.clear()
                for interest in interests:
                    interest, created = Interest.objects.get_or_create(name=interest)
                    user_profile.interests.add(interest)
                vector_thread = threading.Thread(target=process_user_vector, args=(email, interests))
                vector_scibert_thread = threading.Thread(target=process_user_vector_scibert, args=(email, interests))
                vector_thread.start()
                vector_scibert_thread.start()
        user.save()
        user_profile.save()
        return render(request, 'user/profile.html', {'interest_areas': interest_areas})


def like_article(request):
    if request.method == 'POST':
        article_like = request.POST.get('article_like')
        article_name = request.POST.get('article_name')
        article_text = request.POST.get('article_text')
        email = request.user.email
        suggest_type = request.POST.get('suggest_type')
        id = int(article_name)

        print(f"Makale Türü: {suggest_type}")

        if suggest_type == "FastText":
            collectionFastText = connect_to_mongodb("fastext_collection")
            collectionUserFastText = connect_to_mongodb("user_fasttext")
            userFastText = get_data_from_mongodb_user(collectionUserFastText, email)
            articleFastText = get_data_from_mongodb_user(collectionFastText, id)
            fastTextArticleVector = articleFastText['vector']
            fastTextUserVector = userFastText['vector']

            newFastTextVector = update_user_vector_like(fastTextUserVector, fastTextArticleVector)
            print("Makale Beğenildi!")

            update_user_vector_to_mongodb(collectionUserFastText, email, newFastTextVector)
        elif suggest_type == "SCIBERT":
            collectionSCIBERT = connect_to_mongodb("scibert_collection")
            collectionUserSCIBERT = connect_to_mongodb("user_scibert")
            userSCIBERT = get_data_from_mongodb_user(collectionUserSCIBERT, email)
            articleSCIBERT = get_data_from_mongodb_user(collectionSCIBERT, id)
            SCIBERTArticleVector = articleSCIBERT['vector']
            SCIBERTUserVector = userSCIBERT['vector']

            newSCIBERTVector = update_user_vector_like(SCIBERTUserVector, SCIBERTArticleVector)
            print("SCIBERT Makale beğenildi.")

            update_user_vector_to_mongodb(collectionUserSCIBERT, email, newSCIBERTVector)

        return render(request, 'user/article.html', {"article_name": article_name,
                                                     "article_text": article_text,
                                                     "suggest_type": suggest_type
                                                     }
                                                     )
    else:
        pass

def dislike_article(request):
    if request.method == 'POST':
        article_like = request.POST.get('article_like')
        article_name = request.POST.get('article_name')
        article_text = request.POST.get('article_text')
        email = request.user.email
        id = int(article_name)
        suggest_type = request.POST.get('suggest_type')

        if suggest_type == "FastText":
            collectionFastText = connect_to_mongodb("fastext_collection")
            collectionUserFastText = connect_to_mongodb("user_fasttext")
            userFastText = get_data_from_mongodb_user(collectionUserFastText, email)
            articleFastText = get_data_from_mongodb_user(collectionFastText, id)
            fastTextArticleVector = articleFastText['vector']
            fastTextUserVector = userFastText['vector']

            newFastTextVector = update_user_vector_dislike(fastTextUserVector, fastTextArticleVector)
            print("Makale Beğenilmedi!")

            update_user_vector_to_mongodb(collectionUserFastText, email, newFastTextVector)
        elif suggest_type == "SCIBERT":
            collectionSCIBERT = connect_to_mongodb("scibert_collection")
            collectionUserSCIBERT = connect_to_mongodb("user_scibert")
            userSCIBERT = get_data_from_mongodb_user(collectionUserSCIBERT, email)
            articleSCIBERT = get_data_from_mongodb_user(collectionSCIBERT, id)
            SCIBERTArticleVector = articleSCIBERT['vector']
            SCIBERTUserVector = userSCIBERT['vector']

            newSCIBERTVector = update_user_vector_dislike(SCIBERTUserVector, SCIBERTArticleVector)
            print("SCIBERT Makale beğenilmedi.")

            update_user_vector_to_mongodb(collectionUserSCIBERT, email, newSCIBERTVector)

        return render(request, 'user/article.html', {"article_name": article_name,
                                                      "article_text": article_text,
                                                      "suggest_type": suggest_type,
                                                      }
                                                      )
    else:
        pass

def update_user_vector_like(vec1, vec2):
    """
    Birinci vektör kullanıcı vektörü, ikinciyse makale vektörü olmalıdır.
    """
    user_weight = 0.7
    article_weight = 0.3

    user_vector = np.array(vec1)
    article_vector = np.array(vec2)

    new_user_vector = (user_weight * user_vector) + (article_weight * article_vector)
    return new_user_vector

def update_user_vector_dislike(vec1, vec2):
    """
    Birinci vektör kullanıcı vektörü, ikinciyse makale vektörü olmalıdır.
    """
    user_weight = 0.7
    article_weight = -0.3

    user_vector = np.array(vec1)
    article_vector = np.array(vec2)

    new_user_vector = (user_weight * user_vector) + (article_weight * article_vector)
    return new_user_vector