
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), //Routage vers la fonction qui retourne la page web au navigateur
    path('update_chart/', views.update_chart, name='update_chart'),//Routage vers la fonction qui retourne les temperature pour la mise a jour en temps reel
]
