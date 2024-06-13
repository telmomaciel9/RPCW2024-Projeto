import json
import re

ttl = """
@prefix : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://rpcw.di.uminho.pt/2024/DiarioRepublica/> .

<http://rpcw.di.uminho.pt/2024/DiarioRepublica> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/emitiu
:emitiu rdf:type owl:ObjectProperty ;
       rdfs:domain :Emissor ;
       rdfs:range :Documento .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/éEmitidoPor
:éEmitidoPor rdf:type owl:ObjectProperty ;
             rdfs:domain :Documento ;
             rdfs:range :Emissor .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/data
:data rdf:type owl:DatatypeProperty ;
      rdfs:domain :Documento ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/fonte
:fonte rdf:type owl:DatatypeProperty ;
       rdfs:domain :Documento ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/nome
:nomeEmissor rdf:type owl:DatatypeProperty ;
      rdfs:domain :Emissor ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/notas
:notas rdf:type owl:DatatypeProperty ;
       rdfs:domain :Documento ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/numero
:numero rdf:type owl:DatatypeProperty ;
        rdfs:domain :Documento ;
        rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/numeroDR
:numeroDR rdf:type owl:DatatypeProperty ;
          rdfs:domain :Documento ;
          rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/pdflink
:pdflink rdf:type owl:DatatypeProperty ;
         rdfs:domain :Documento ;
         rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/series
:series rdf:type owl:DatatypeProperty ;
        rdfs:domain :Documento ;
        rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/tipo
:tipo rdf:type owl:DatatypeProperty ;
      rdfs:domain :Documento ;
      rdfs:range xsd:string .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/Documento
:Documento rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2024/DiarioRepublica/Emissor
:Emissor rdf:type owl:Class .


#################################################################
#    Individuals
#################################################################
"""

# Open the output file
output = open("DR_output.ttl", "w", encoding='utf-8')

# Write the prefixes and ontology definitions to the output file
output.write(ttl)

idx=0

with open("DREdataset_clean.json", 'r', encoding='utf-8') as f:
#with open(f"exemplo.json", 'r', encoding='utf-8') as f:
    bd = json.load(f)

for doc in bd:
        idx += 1
        emissores = []
        notas2 = re.sub(r'[\n\r]+', '', doc['notes'])
        notas = re.sub(r'\\$', '', notas2)
        notas = notas.replace('\\', '')
        rdf2 = ""
        rdf = f"""
###  http://rpcw.di.uminho.pt/2024/DiarioRepublica#{idx}
<http://rpcw.di.uminho.pt/2024/DiarioRepublica#{idx}> rdf:type owl:NamedIndividual ,
                                :Documento ;
                 :data "{doc['date'].replace('"', '')}" ;
                 :fonte "{doc['source'].replace('"', '')}" ;
                 :notas "{notas.replace('"', '')}" ;
                 :numero "{doc['number'].replace('"', '')}" ;
                 :numeroDR "{doc['dr_number'].replace('"', '')}" ;
                 :pdflink "{doc['dre_pdf'].replace('"', '')}" ;
                 :series {doc['series']} ;
                 :tipo "{doc['doc_type'].replace('"', '')}" ;
"""

        for emissor in doc['emiting_body']:
            emissor =  re.sub(r'[\n\r]+', '', emissor)
            emissor = emissor.replace('_', '').replace(' ', '')
            emissor_filtred = re.sub(r'\s+', '_', emissor)
            emissor_filtred =  re.sub(r'[\n\r]+', '', emissor_filtred)
            emissor_filtred = emissor_filtred.replace(',','').replace('.','').replace('"', '').replace('(','').replace(')','').replace('º','').replace('ª','').replace('«','').replace('»','').replace("'","").replace('/','_').replace('–','').replace('%', 'Porcento').replace('_¿', '').replace('-_','').replace('°', '').replace('!', '').replace('?', '').replace('+', 'Mais').replace('[', '').replace(']', '').replace('_', '').replace('@', '_arroba_').replace('=', '_igual_a_').replace('´', '_').replace('&', 'E')
            emissores.append(emissor_filtred)
            rdf2 += f"""
###  http://rpcw.di.uminho.pt/2024/DiarioReplublica#{emissor_filtred}
:{emissor_filtred} rdf:type owl:NamedIndividual ,
                                :Emissor ;
                 :nomeEmissor "{emissor.replace('"', '')}" ;
                 :emitiu <http://rpcw.di.uminho.pt/2024/DiarioReplublica#{idx}> .
"""
    
        for i, emissor in enumerate(emissores):
            if i == len(emissores) - 1:  # Verifica se é o último emissor
                rdf += f"""
                 :éEmitidoPor :{emissor} .
"""
            else:
                rdf += f"""
                 :éEmitidoPor :{emissor} ;
"""

        rdf += rdf2

        output.write(rdf)
    
output.close()

    