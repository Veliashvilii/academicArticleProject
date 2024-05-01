from django.shortcuts import render
from django.http import HttpResponse

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
    """
    Request in post olduğu durumda yapılacak işlemler
    """
    return render(request, 'index/signin.html')


def login(request):
  return render(request, 'index/signin.html')