import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript cats_load

from colls.models import Coll, Museum, Country, Culture, Category, Artist

def run():
    fhand = open('colls/test.csv', encoding="utf-8")
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    Museum.objects.all().delete()
    Country.objects.all().delete()
    Culture.objects.all().delete()
    Category.objects.all().delete() 
    Artist.objects.all().delete()
    Coll.objects.all().delete()
    
    # 0 id, 1 title, 2 image, 3 [artist], 4 [culture], 5 [country/place], 6 [category], 7 date, 8 [museum], 9 description 
    
    for row in reader:
        print(row)

        if row[3]=="":
            artist, create = Artist.objects.get_or_create(name='Anonymous')
        else:
            artist, create = Artist.objects.get_or_create(name=row[3])

        if row[4]=="":
            culture, create = Culture.objects.get_or_create(name='Undefined')
        else:
            culture, create = Culture.objects.get_or_create(name=row[4])

        if row[5]=="":
            country, create = Country.objects.get_or_create(name='Undefined')
        else:
            country, create = Country.objects.get_or_create(name=row[5])

        category, create = Category.objects.get_or_create(name=row[6])

        museum, create = Museum.objects.get_or_create(name=row[8])


        c = Coll(coll_id=row[0], title=row[1], image=row[2], artist=artist, date=row[7], description=row[9], culture=culture, museum=museum, country=country, category=category)
        c.save()