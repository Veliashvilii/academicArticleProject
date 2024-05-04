from django.shortcuts import render
from django.contrib.auth import logout
from index.models import Profile, Interest
from index.views import connect_to_mongodb, get_vector_for_person
import threading

def process_user_vector(email, interests):
    collection = connect_to_mongodb("user_fasttext")
    vector = get_vector_for_person(interests)
    result = collection.update_one({"_id": email}, {"$set": {"vector": vector.tolist()}})
    if result.modified_count > 0:
        print("Belge güncellendi.")
    else:
        print("Belge güncellenemedi.")

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
                vector_thread.start()
        user.save()
        user_profile.save()
        return render(request, 'user/profile.html', {'interest_areas': interest_areas})




