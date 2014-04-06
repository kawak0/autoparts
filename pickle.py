#!/usr/bin/python3
import jsonpickle


class Autopart:


    def __init__(self,model, make, image, category):
        self._id = model
        self.make = make
        self.image = image
        self.category = category
        self.links = {}

    def add(self, link, price):
        if (link not in self.links):
            self.links[link] = price
        else:
            #Compare price
            old_price = self.links[link]
            if price != old_price:
                self.links[link] = price
    
    def remove(self, link):
        del self.links[link]


recambio = Autopart("LX 158","KNETCH","http://www.laimagen.com","Filtro de aire")
recambio.add('oscaro.es/blablabla',10.07)
recambio.add('recambiosviaweb/blebleble',8.99)

recambio2 = Autopart("WK 614/10","MANN-FILTER","laotraimagen.com","Filtro de combustible")
recambio2.add('oscaro.es/wk-614/10',12.21)
recambio2.add('recambiosviaweb/wk-614/10', 13.30)
recambio.add('oscaro.es/blablabla',10.01)


a = jsonpickle.encode(recambio,unpicklable=True)
b = jsonpickle.encode(recambio2,unpicklable=True)


f = open('ficherojson.txt','w')
f.write(a + '\n')
f.write(b + '\n')
f.close()

# leer fichero
lines = open('ficherojson.txt','r').readlines()
for line in lines:
    new_obj = jsonpickle.decode(line)
    if recambio2._id == new_obj._id:
        print ("SON IGUALES")
        print (recambio2._id)
        print (new_obj._id)
    else:
        print ("SON DIFERENTES")
        print (recambio2._id)
        print (new_obj._id)



