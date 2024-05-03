from django.shortcuts import render
from django.contrib.auth import logout
from index.models import Profile, Interest

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
        return render(request, 'user/profile.html', {'interest_areas': interest_areas})
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
        if name != "":
            user.first_name = name
        if surname != "":
            user.last_name = surname
        if email != "":
            user.username = email
            user.email = email
        if interests != []:
            user_profile = Profile.objects.get(user=user)
            user_profile.interests.clear()
            for interest in interests:
                interest, created = Interest.objects.get_or_create(name=interest)
                user_profile.interests.add(interest)
        user.save()
        user_profile.save()
        return render(request, 'user/profile.html', {'interest_areas': interest_areas})




