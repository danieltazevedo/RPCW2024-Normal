import json
import csv

ttl = f"""
@prefix : <http://www.example.org/disease-ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .

:Ontology a owl:Ontology .

# Classes
:Disease a owl:Class .
:Symptom a owl:Class .
:Treatment a owl:Class .
:Patient a owl:Class .

# Properties
:hasSymptom a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Symptom .

:hasTreatment a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Treatment .

:exhibitsSymptom a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Symptom .

:hasDisease a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Disease .

:receivesTreatment a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Treatment .

:description a owl:DatatypeProperty ;
    rdfs:domain :Disease ;
    rdfs:range xsd:string .
"""
tratamento_lista = []
tratamento_dic = {}
csvfile3 = open('Disease_Treatment.csv', newline='')
reader = csv.reader(csvfile3)
next(reader)
for row in reader: 
    doenca = row[0].replace(" ","").replace(".","").replace("(","").replace(")","")
    tratamentos = [tratamento for tratamento in row[1:] if tratamento]
    tratamentos = [t.replace(' ', '').replace("(","").replace(")","") for t in tratamentos]
    tratamentos_formatados = ', '.join(f':{tratamento}' for tratamento in tratamentos)
    tratamento_dic[doenca] = tratamentos_formatados
    for tratamento in tratamentos:
        if tratamento not in tratamento_lista:
            tratamento_lista.append(tratamento)
            Treatment = f""":{tratamento} a :Treatment ."""
            ttl += Treatment    


desc_dic = {}
csvfile2 = open('Disease_Description.csv', newline='')
reader = csv.reader(csvfile2)
next(reader)
for row in reader: 
    doenca = row[0].replace(" ","").replace("(","").replace(")","")
    description = row[1].replace("\"","")
    desc_dic[doenca] = description

csvfile = open('Disease_Syntoms.csv', newline='')
sintomas_lista = []

reader = csv.reader(csvfile)
next(reader)
for row in reader: 
    sintomas = [sintoma for sintoma in row[1:] if sintoma]
    sintomas = [s.replace(' ', '').replace("(","").replace(")","") for s in sintomas]
    sintomas_formatados = ', '.join(f':{sintoma}' for sintoma in sintomas)
    doenca = row[0].replace(" ","").replace("(","").replace(")","")
    disease = f"""
    :{doenca} a :Disease ;
    :hasSymptom {sintomas_formatados}
    """
    if doenca in desc_dic:
        desc = f""";
        :description "{desc_dic[doenca]}"  """
        disease += desc 

    if doenca in tratamento_dic:
        trat = f""";
        :hasTreatment {tratamento_dic[doenca]}.\n"""
        disease += trat
    else:
        disease += "."
    ttl += disease
    for sintoma in sintomas:
        if sintoma not in sintomas_lista:
            sintomas_lista.append(sintoma)
            Symptom = f""":{sintoma} a :Symptom ."""
            ttl += Symptom    

f = open("pg50311.json")
bd = json.load(f)
f.close

id = 0
for doente in bd:
    sint = doente["sintomas"]
    resultado = ""
    for sintoma in sint:
        sintoma = sintoma.replace(' ', '').replace("(","").replace(")","")
        resultado += f":exhibitsSymptom :{sintoma} ;\n"
    resultado = resultado[:-2]
    resultado += ".\n"
    Patient = f"""
    :{id} a :Patient ;
    :name "{doente["nome"]}" ;
    {resultado}
    """
    id += 1
    ttl += Patient

output = open("med_doentes.ttl", "w")
output.write(ttl)
    

