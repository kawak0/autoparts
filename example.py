#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import json
import requests
import urllib.parse
import re
import os


def getUrl(url, data=None):
    requests.adapters.DEFAULT_RETRIES = 5
    if(data==None):
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = html.text
    else: 
        html = requests.post(url, data=data).json()
    return html

#Get the makes
html=""
try:
    html = getUrl('http://www.oscaro.es')
    begin = html.find('<optgroup label="Todas las marcas :">')
    end = html.find('</select>')
    html = html[begin:end]
except:
    print ("No hay conexión")

def create_dir(*values):
    #Creates a directory
    dir = ""
    for value in values:
        dir += value.replace('/','-') + "/"
    
    if not os.path.exists('./files/' + dir):
        os.makedirs('./files/' + dir)


pattern = re.compile(r'<option.*?value="(\d+)">(.*?)</option>',re.DOTALL)
for (value, make) in re.findall(pattern, html):
   print (make, value)
   if not os.path.exists('./files/' + make):
       os.makedirs('./files/' + make)




#url = 'http://www.oscaro.es/Catalog/Vehicle/ModelsJson'
#codigoSeat = 192
#seat =  {'idOscManufacturer': codigoSeat }
#res = requests.post(url, data=seat)


#For a make, get the models and values
url = 'http://www.oscaro.es/Catalog/Vehicle/ModelsJson'
codigoSeat = 192
make = 'SEAT'
data =  {'idOscManufacturer': codigoSeat}
make_response = getUrl(url, data)
#print (response)

#Get the group model
pattern_group = re.compile(r'<optgroup label="(.*?)">(.*?)</optgroup>',re.DOTALL) 
for (model, rest ) in re.findall(pattern_group, make_response):
    #Get the exact_model
    pattern_model = re.compile(r'<option.*?value="(.+?)">(.+?)</option>',re.DOTALL)
    for (value_model, exact_model) in re.findall(pattern_model,rest):
        #print (model, exact_model, value)
        #Get the web of the exact_model
        url = 'http://www.oscaro.es/Catalog/Vehicle/TypesJson'
        data =  {'idOscModel': value_model }
        model_response = getUrl(url, data)
        pattern_type = re.compile(r'<optgroup label="(.*?)">(.*?)</optgroup>',re.DOTALL) 
        for (combustible, rest ) in re.findall(pattern_type, model_response):
            #Get the first word (Gasolina, Diesel, GPL, ...)
            combustible = combustible.partition(' ')[0]
            pattern = re.compile(r'<option.*?value="(.+?)">(.+?)</option>',re.DOTALL) 
            for (value_type, exact_type) in re.findall(pattern,rest):
                print (combustible, exact_model, value)
                create_dir(make,model,exact_model,combustible,exact_type)
        #      pass
        





#pattern = re.compile(r'<optgroup label="(.*?)">(.*?)</optgroup>',re.DOTALL) 
#for (combustible_cilindrada, rest ) in re.findall(pattern, response):
#   pattern = re.compile(r'<option.*?value="(.+?)">(.+?)</option>',re.DOTALL) 
#   for (value, exact_model) in re.findall(pattern,rest):
#       print (combustible_cilindrada, exact_model, value)
       #Save it in a file
       #f = open('./files/'+value, 'w')
       #value = value.split('_')
       #html = getUrl('http://www.oscaro.es/Catalog/VehicleCatalog/VehicleCatalog/' + value[0] + '/' + value[1])
       #f.write(html)
       #f.close()
       


#Example with Seat Ibiza II 1.4i 60cv value: 12183_1443
codigoCollage = '12183_1443'
codigoCollage = codigoCollage.split('_')

#Example with filtro de aire and filtro de aceite (p.ej)
html = getUrl('http://www.oscaro.es/Catalog/VehicleCatalog/VehicleCatalog/' + codigoCollage[0] + '/' + codigoCollage[1])
# Each item has this format
#<li><a class='FontGeneArt' href="http://www.oscaro.es/sensor-de-detonaciones-seat-ibiza-ii-1-4-i-60cv-3921-12183-1443-gt">Sensor de detonaciones</a></li>


#Each autopart....
matchObj = re.search(r'<a class.*? href="(.+?)">Filtro de aire</a>', html)
if matchObj:
   print (matchObj.group(1))
   htmlPart = getUrl(matchObj.group(1))
   pattern = re.compile(r"""
   <a\sname="article\d{1,}"\s>.*? #For every article
   <img\salt="(.+?)" #Parse the autopart_make name
   \s+src="(.+?)".*? #Pase the autopart_make image 
   <img\salt=".*?\1\s(.*?)" #Parse the autopart_model name
   \s+src="(.+?)".*? #Parse the autopart_model image
   <span\sclass="toprouge">.*?(\d{1,}).*?,.*?(\d{1,}).*?\s€.*?<hr\s/> #Parse the price and decimal_price
   """,re.X | re.S)
   for (autopart_make, make_image, autopart_model, autopart_image, price, decimal_price) in re.findall(pattern,htmlPart):
       print (autopart_make, make_image, autopart_model, autopart_image, price + "," + decimal_price)


matchObj = re.search(r'<a class.*? href="(.+?)">Filtro de aceite</a>', html)
if matchObj:
   print (matchObj.group(1))




