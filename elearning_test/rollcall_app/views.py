from django.shortcuts import render


# Create your views here.
def info(request):
    context = {}
    return render(request, "rollcall/info.html", context)