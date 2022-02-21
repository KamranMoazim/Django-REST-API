from django.shortcuts import render

# Create your views here.
# request -> response 
# request handler


from django.http import HttpResponse


def hello_world(request):
    # return HttpResponse("Hello World!")
    return render(request, "index.html", {"name":"Kamran Moazim"})