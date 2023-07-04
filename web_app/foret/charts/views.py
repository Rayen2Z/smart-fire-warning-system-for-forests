from django.http import HttpResponse
from django.template import loader
import json
from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse


/*
* Fonction appelé lors de la première consultation de la page
*/
def index(request):
    // Initialiser le dictionnaire qui contiendra les donnees
    data_set = {} 
    with connection.cursor() as cursor:
        // Retourne la liste des identifiants des capteurs  
        cursor.execute("select distinct(t.id_capteur) from temperatures t ")     
        row = cursor.fetchall() 
        j = 0
        // Pour chaque capteur on cherche la liste des temperatures quil a capté
        for i in row : 
            data = []
            data_lablels = []
            // retourne la liste des temperatures pour un capteur
            cursor.execute("select t.temperature, to_char(t.date_time,'dd/mm/yy hh:mm:ss') from temperatures t where t.id_capteur = %s ",[i[0]])
            row = cursor.fetchall() 
            for i in row :
                data.append( i[0] )
                data_lablels.append(str(i[1]))
            data_set["capteur"+str(j)] = data
            j = j+1
    //Convertir les donnees en format JSON  et les mettre dans un dictionnaire       
    data_json = json.dumps(data_set)
    context ={  'data_set' : data_json,
                'nb' : j,
                 }
    //retourner la page web index.html et les données 
    return render(request,'charts/index.html',context)


/*
* Fonction appelé lors de la mise a jour du graph
*/
def update_chart(request):
    // Initialiser le dictionnaire qui contiendra les donnees
    data_set = {}
    with connection.cursor() as cursor:
        // Retourne la liste des identifiants des capteurs  
        cursor.execute("select distinct(t.id_capteur) from temperatures t ")     
        row = cursor.fetchall()
        j = 0
        // Pour chaque capteur on cherche la liste des temperatures quil a capté
        for i in row : 
            data = []
            data_lablels = []
             // retourne la liste des temperatures pour un capteur
            cursor.execute("select t.temperature, to_char(t.date_time,'dd/mm/yy hh:mm:ss') from temperatures t where t.id_capteur = %s ",[i[0]])
            row = cursor.fetchall()
            for i in row :
                data.append( i[0] )
                data_lablels.append(str(i[1]))
            data_set["capteur"+str(j)] = data
            j = j+1
             
    
    data ={  'data_set' : data_set,
                'nb' : j
                 }
    //retourner uniquement les donnees en format json 
    return JsonResponse(data)
