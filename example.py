#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import json
import requests
import urllib.parse
import re
import os


def get_url(url, data=None):
    requests.adapters.DEFAULT_RETRIES = 10
    if(data==None):
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = html.text
    else: 
        html = requests.post(url, data=data).json()
    return html

def create_dir(*values):
    #Creates a directory
    dir = ""
    for value in values:
        dir += value.replace('/','-') + "/"
    if not os.path.exists('./files/' + dir):
        os.makedirs('./files/' + dir)
    return dir

def save_file(text,filename, dir):
    #Save a file
    f = open('./files/' + dir + filename,'w')
    f.write(text)
    f.close()

def get_makes():
    #Get the makes
    html=""
    try:
        html = get_url('http://www.oscaro.es')
        begin = html.find('<optgroup label="Todas las marcas :">')
        end = html.find('</select>')
        html = html[begin:end]
    except:
        print ("There is no connection")

    pattern = re.compile(r'<option.*?value="(\d+)">(.*?)</option>',re.DOTALL)
    for (value, make) in re.findall(pattern, html):
        print (make, value)
        if not os.path.exists('./files/' + make):
            os.makedirs('./files/' + make)
        #TODO: call a function to get the models for each make


def get_models(make_name , make_value):
    url = 'http://www.oscaro.es/Catalog/Vehicle/ModelsJson'
    data =  {'idOscManufacturer': make_value}
    make_response = get_url(url, data)
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
    model_response = get_url(url, data)
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
    html_items = get_url(url + value_type[0] + '/' + value_type[1])
    #print (html_items)
    #Each autopart....(Example filtro de aire)
    for item_name in items_list:
        match_obj = re.search(r'<li><a class.*? href="(.+?)">%s</a>'%item_name, html_items)
        if match_obj:
            print (match_obj.group(1))
            text = ''
            html_item = get_url(match_obj.group(1))
            pattern_item = re.compile(r'<a\sname="article\d{1,}"\s>(.+?)<hr\s/>',re.S)
            for rest in re.findall(pattern_item, html_item):
                pattern = re.compile(r"""
                <img\salt="(.+?)" #Parse the autopart_make name
                \s+src="(.+?)".*? #Pase the autopart_make image 
                <img\salt=".*?\1\s(.*?)" #Parse the autopart_model name
                \s+src="(.+?)".*? #Parse the autopart_model image
                <span\sclass="toprouge">.*?(\d{1,}).*?,.*?(\d{1,}).*?\s€ #Parse the price and decimal_price
            """,re.X | re.S)
        
                filename = item_name + '.txt'
                
            
                for (autopart_make, make_image, autopart_model, autopart_image, price, decimal_price) in re.findall(pattern,rest):
                    text += autopart_make+' '+make_image+' '+autopart_model+' '+price+','+decimal_price+'\n'
                    save_file(text, filename, dir)
                    



get_makes()
get_models('SEAT', 192)


