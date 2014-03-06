#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import json
import requests
import urllib.parse
import re
import os
import difflib

#### * Essential functions
def get_url(url, data=None,method='GET'):
    html= ""
    requests.adapters.DEFAULT_RETRIES = 10
    try:
        if(data==None):
            html = requests.get(url, timeout=5)
            html.encoding = 'utf-8'
        else: #There are data to send
            if(method == 'POST'):
                html = requests.post(url, data=data).json()
            else: #Method: 'GET'
                html = requests.get(url, params=data, timeout=5)
                html.encoding = 'uft-8'
    except:
        pass
    return html

def create_dir(*values):
    #Creates a directory
    dir = ""
    for value in values:
        #Replace / with - and add a / for each value
        dir += value.replace('/','-') + "/"
    dir = './files/' + dir
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def save_file(text,filename,mode):
    if (mode == 'w'): #Save a new file
        f = open(filename,'w')
        f.write(text)
        f.close()
    elif (mode == 'e'): #For editing an existing file
        f = open(filename,'w')
        f.writelines(text)
        f.close()
    elif (mode == 'a'): #Append to an existing file
        f = open(filename,'a')
        f.write(text)
        f.close()

def save_item(filename, autopart_make, autopart_model,autopart_link, price):
    text =  autopart_make + '  ' + autopart_model + '  ' + autopart_link + '  ' + price + '  \n'
    if os.path.isfile(filename):
        #The file exists
        lines = open(filename,'r').readlines()
        found = False
        counter = 0
        for line in lines:
            if autopart_link in line:
                #The autopart_link exists, different price?
                found = True
                old_price = line.split('  ')[3]
                if (old_price != price):
                    print ("Price changed: old price:" + old_price + " new price:" + price)
                    lines[counter] = text
                    save_file(lines,filename,'e')
                break
            else:
                counter += 1
        if not found:
            #The autopart_link does not exist, append it to the file
            save_file(text,filename,'a')
    else:
        #The file does not exist
        save_file(text,filename,'w')
                   
def save_autopart_make_links(make, link):
    lines = open('./files/make_links', 'r').readlines()
    found = False
    counter = 0
    for line in lines:
        if link in line:
            found = True
            break
        else:
            counter += 1
    if not found:
        f = open('./files/make_links', 'a')
        f.write(make + "  "+ link+"  \n")
        f.close()

#### * www.recambiosviaweb.com
def get_recambiosviaweb(original_model, original_make, original_price, original_category):
    url = 'http://www.recambiosviaweb.com/referencia.html'
    data = {'ref' : original_model}
    html = get_url(url,data,'GET').text
    if (html != ''):
        begin = html.find('<div class="listado">')
        html = html[begin:]
        end = html.find('</ul>')
        html = html[:end]
        #html contains the important part of the web
        #pattern = re.compile(r'<p>Se han encontrado (\d{1,}) resultados')
        #count = re.search(pattern,html)
         
        #&nbsp; is non-breaking-space
        items_pattern = re.compile(r'<li>(.*?)</li>')
        for text in re.findall(items_pattern,html):
            #Parse the maybe compatible autoparts (check category and compatible vehicles)
            item_pattern = re.compile(r'<a href="(.*?)".*?title=""><span class="">(.*?)&nbsp;(.*?)&nbsp;ref\.([^<]*?)</span></a>&nbsp;\((\d{1,},\d{2})', re.DOTALL)
            for (link, category, make, model, price) in re.findall(item_pattern, text):
                if (difflib.SequenceMatcher(None,category,original_category).ratio() > 0.70):
                    #If the categories are quite similar, accept it
                    #print ("PARSED: "+link ,category, make,model,price)
                    #save(link, category,make, model, price)
                    pass
            #Parse the original model
            item_original = re.compile(r'<a href="(.*?)".*?title=""><span class="">(.*?)&nbsp;(.*?)&nbsp;ref\.<strong>%s</strong></span></a>&nbsp;\((\d{1,},\d{2})'%original_model, re.DOTALL)
            matched = re.search(item_original, text)
            if matched:
                link = matched.group(1)
                category = matched.group(2)
                make = matched.group(3)
                price = matched.group(4)
                print ("ORIGINAL: "+link ,category, make,original_model,price)
                print ("LOWER PRICE!!!")
                ##save (link,category, make,model,price)

#### * www.recambiosvictor.com
def get_recambiosvictor(original_model, original_make, original_price, original_category):
    url = 'http://www.recambiosvictor.com/tienda/productos.jsp'
    data = {'filtro_referencia' : original_model, 'directo': 1,'pagina': 1,'inicio_aplicacion': 1}
    html = get_url(url,data,'GET')
    if (html != ''):
        link = html.url
        print (link)
        html = html.text
        begin = html.find('<h2 class="h2_precio">')
        if (begin != -1):
            #The web has a price!
            html = html[begin:]
            #&#8364; is the € (Euro) symbol in html
            price_p = re.compile(r'(\d{1,},?\d{1,2})\s&#8364;</h2>')
            matched = re.search(price_p, html)
            if matched:
                #Has matched the original item
                price = matched.group(1)
                print ("En recambiosvictor a "+price+link)


#### * www.oscaro.es
def get_makes():
    #Get the makes of the cars
    html = get_url('http://www.oscaro.es').text
    if (html != ''):
        begin = html.find('<optgroup label="Todas las marcas :">')
        end = html.find('</select>')
        html = html[begin:end]
        pattern = re.compile(r'<option.*?value="(\d+)">(.*?)</option>',re.DOTALL)
        for (value, make) in re.findall(pattern, html):
            print (make, value)
            #make = make.replace('/','-')
            #if not os.path.exists('./files/' + make):
            #    os.makedirs('./files/' + make)
            #MAYBE REMOVE THE LINES ABOVE
            #TODO: call a function to get the models for each make


def get_models(make_name , make_value):
    url = 'http://www.oscaro.es/Catalog/Vehicle/ModelsJson'
    data =  {'idOscManufacturer': make_value}
    make_response = get_url(url, data, 'POST')
    if (make_response != ''):
        #Get the group model
        pattern_group = re.compile(r'<optgroup label="(.*?)">(.*?)</optgroup>',re.DOTALL) 
        for (group_model, rest ) in re.findall(pattern_group, make_response):
            #Get the exact_model
            pattern_model = re.compile(r'<option.*?value="(.+?)">(.+?)</option>',re.DOTALL)
            for (value_model, exact_model) in re.findall(pattern_model,rest):
                get_types(exact_model,value_model, group_model, make_name)

def get_types(exact_model,value_model,group_model,make):
    #Get the types for an exact model
    url = 'http://www.oscaro.es/Catalog/Vehicle/TypesJson'
    data =  {'idOscModel': value_model }
    model_response = get_url(url, data, 'POST')
    if (model_response != ''):
        pattern_type = re.compile(r'<optgroup label="(.*?)">(.*?)</optgroup>',re.DOTALL) 
        for (fuel, rest ) in re.findall(pattern_type, model_response):
            #Get the first word (Gasolina, Diesel, GPL, ...)
            fuel = fuel.partition(' ')[0]
            pattern = re.compile(r'<option.*?value="(.+?)">(.+?)</option>',re.DOTALL) 
            for (value_type, exact_type) in re.findall(pattern,rest):
                print (fuel, exact_model, exact_type, value_type)
                dir = create_dir(make,group_model,exact_model,fuel,exact_type)
                get_items(value_type,dir)
        

def get_items(value_type,dir):
    url = 'http://www.oscaro.es/Catalog/VehicleCatalog/VehicleCatalog/'
    items_list = ['Filtro de aire','Filtro de aceite','Bujía de encendido']
    value_type = value_type.split('_')
    html_items = get_url(url + value_type[0] + '/' + value_type[1]).text
    #print (html_items)
    if (html_items != ''):
        #Each autopart....(Example filtro de aire)
        for item_name in items_list:
            item_link = re.search(r'<li><a class.*? href="(.+?)">%s</a>'%item_name, html_items)
            if item_link:
                print (item_link.group(1))
                line = ''
                html_item = get_url(item_link.group(1)).text
                pattern_item = re.compile(r'<a\sname="article\d{1,}"\s>(.+?)<hr\s/>',re.S)
                for rest in re.findall(pattern_item, html_item):
                    #Remove annoying <span> between price (it could goes before the for loop)
                    rest = rest.replace('<span style="display:none">1</span>','')
                    pattern = re.compile(r"""
                    img\salt="(.+?)" #Parse the autopart_make name
                    \s+src="(.+?)".*? #Pase the autopart_make image 
                    <img\salt=".*?\1\s(.*?)" #Parse the autopart_model name
                    \s+src="(.+?)".*? #Parse the autopart_model image
                    <td.*?<a\shref="(.*?)".*? #Parse the autopart_link
                    <span\sclass="toprouge">.*?(\d{1,}).*?,.*?(\d{1,}).*?\s€ #Parse the price and decimal_price
                    """,re.X | re.S)
            
                    filename = item_name + '.txt'
                    
                
                    for (autopart_make, make_image, autopart_model, autopart_image, autopart_link, price, decimal_price) in re.findall(pattern,rest):
                        #Text without the make_image and autopart_image
                        price = price + ',' + decimal_price
                        save_item(dir+ '' + filename, autopart_make, autopart_model, autopart_link,price)
                        get_recambiosviaweb(autopart_model, autopart_make, price, item_name)
                        get_recambiosvictor(autopart_model, autopart_make, price,item_name)
                        #Save the makes images in a file
                        save_autopart_make_links(autopart_make,make_image)
                        
            

#### * Main
get_makes()
get_models('SEAT', 192)


