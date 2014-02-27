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


def save_file(text,filename, dir):
    #Save a file
    f = open('./files/' + dir + filename,'a')
    f.write(text)
    f.close()



def get_sections():
    #Get the sections and items per section
    url = 'http://recambios-coche.oscaro.es/'
    html = get_url(url)
    begin = html.find('Todos nuestros recambios de coches')
    html = html[begin:]
    #print (html)
    pattern = re.compile(r'<h2 class="cat">.*?a href="(.*?)".*?alt="(.*?)"',re.DOTALL)
    for (link, category) in re.findall(pattern,html):
        print ("\nCATEGORY: " + category)
        get_category(link,category)
        

def get_category(url, category):
    cat_html = get_url(url)
    result = re.findall(r'<h2 class="sousTitre">',cat_html)
    #If it is a category page it has 1 <h2 class="sousTitre">, otherwise it has 3
    is_category = len(result)
    if (is_category == 1):
        pattern = re.compile(r'<div class="ElementPlan".*?a href="(.*?)".*?alt="(.*?)"',re.DOTALL)
        for (link, subcategory) in re.findall(pattern,cat_html):
            print ("Subcategory: " + subcategory)
            get_category(link,category + ' --> '+ subcategory)

    else: #It's a final item
        begin = cat_html.find('<div id="divListingPlan">')
        end = cat_html.find('<div id="divListingPlan">',begin+1)
        cat_html = cat_html[begin:end]
        pattern_item = re.compile(r'<div class="ElementPlan">.*?alt="(.*?)"',re.DOTALL)
        for autopart_name in re.findall(pattern_item, cat_html):
            save_file(category + '--> ' + autopart_name+ '\n','sections.txt','')
            #print (autopart_name)

#Empty file    
f = open('./files/sections.txt','w')
f.close()
                      
get_sections()
