from django.shortcuts import render, redirect


# Create your views here.

def view404(request, exception=None):
    return redirect('swagger-ui')

