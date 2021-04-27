import datetime as dt
from dateutil.parser import parse 
from pathlib import Path


file_name = "datasets/selected/satdi_info_complete2.csv"
file_out_path = Path(__file__).parent / file_name
authors = {} #name: [(repo, name, mail), (rpeo, name, mail), ...]
satdi_names = set()

with open(file_out_path, "r") as the_file:
    for line in the_file.readlines():
        data = line.replace("\n", "").split(";")

        if data[0] == 'repository': continue

        repo = data[0]
        name = data[-4]
        mail = data[-3]
        url = data[2]
        created_at = parse(data[5]).replace(tzinfo=None)
        end = dt.datetime.now() 
        delta = end - created_at
        age = round(delta.total_seconds()/86400, 2)
        satdi = (repo, name, mail, url, age)

        satdi_names.add(name)
        if authors.get(name) == None:
            authors[name] = {'satdi': [satdi], 'satdc': []}
        else:
            authors[name]['satdi'].append(satdi)

print("satdi: " + str(len(satdi_names)))

satdc_names = set()

file_name = "datasets/selected/satdc_info_full.csv"
file_out_path = Path(__file__).parent / file_name
satdc_authors = {} #name: [(repo, name, mail), (rpeo, name, mail), ...]
with open(file_out_path, "r") as the_file:
    for line in the_file.readlines():
        data = line.replace("\n", "").split(";")

        if data[0] == 'repository': continue

        repo = data[0].split("/")[1]
        name = data[-2]
        mail = data[-1]
        file = data[1]
        init = data[2]
        end = data[3]
        hash = data[-3]
        created_at = parse(data[-5]).replace(tzinfo=None)
        end = dt.datetime.now() 
        delta = end - created_at
        age = round(delta.total_seconds()/86400, 2)
        satdc = (repo, name, mail, file, init, end, hash, age)

        satdc_names.add(name)
        if authors.get(name) != None:
            authors[name]['satdc'].append(satdc)
            

print("satdc: " + str(len(satdc_names)))
print("inter: " + str(len(satdi_names.intersection(satdc_names))))
print("diff c - i: " + str(len(satdc_names.difference(satdi_names))))
print("diff i - c: " + str(len(satdi_names.difference(satdc_names))))
