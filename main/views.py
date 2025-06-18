from django.http import HttpResponse
# Create your views here.

def index(request):
    print("Index view called!")
    return HttpResponse("hello world")