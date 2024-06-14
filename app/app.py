from flask import Flask, render_template, request, jsonify, redirect
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import unquote
import re
import os

app = Flask(__name__)

#graphdb_endpoint = "http://localhost:7200/repositories/DRepublica"
graphdb_endpoint = "http://graphdb:7200/repositories/DRepublica"
#graphdb_endpoint = os.getenv('GRAPHDB_ENDPOINT', 'http://localhost:7200/repositories/DRepublica')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/tipos')
def mostrar_tipos():
    # Consulta SPARQL para recuperar todos os nomes de emissores únicos
    sparql_query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT DISTINCT ?tipo
    WHERE {
      ?documento rdf:type :Documento ;
                 :tipo ?tipo .
    }
    ORDER BY ?tipo

    """
    
    # Enviar a consulta SPARQL para o GraphDB
    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})
    
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        tipos = [tipo['tipo']['value'] for tipo in dados]
        return render_template('tipos.html', tipos=tipos)
    
    else:
        return render_template('error.html')

@app.route('/documentos')
def mostrar_documentos_paginados():
    sparql_query = """
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?id ?tipo (GROUP_CONCAT(?emissor_nome; SEPARATOR=", ") AS ?emissores) ?fonte ?data ?notas
WHERE {
  ?documento rdf:type :Documento ;
             :data ?data ;
             :tipo ?tipo ;
             :éEmitidoPor ?emissor ;
             :fonte ?fonte ;
             :notas ?notas .
  
  ?emissor :nomeEmissor ?emissor_nome .
  
  BIND(xsd:integer(STRAFTER(str(?documento), "#")) AS ?id)
}
GROUP BY ?id ?tipo ?fonte ?data ?notas
ORDER BY ?id
    """
    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    dados = resposta.json()['results']['bindings']

    return render_template('documentos.html', dados=dados)

@app.route('/documentos/<string:id>')
def detalhes_documento(id):
    sparql_query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?id ?data (GROUP_CONCAT(?emissor_nome; SEPARATOR=", ") AS ?emissores) ?fonte ?numero ?numeroDR ?pdflink ?series ?tipo ?notas
WHERE {{
  ?documento rdf:type :Documento ;
             :data ?data ;
             :éEmitidoPor ?emissor ;
             :fonte ?fonte ;
             :numero ?numero ;
             :notas ?notas ;
             :numeroDR ?numeroDR ;
             :pdflink ?pdflink ;
             :series ?series ;
             :tipo ?tipo .
  ?emissor :nomeEmissor ?emissor_nome .
  FILTER (STRAFTER(str(?documento), "#") = "{id}")
  BIND(STRAFTER(str(?documento), "#") AS ?id_s)  
  BIND(xsd:integer(?id_s) AS ?id) 
}}
GROUP BY ?id ?data ?fonte ?numero ?numeroDR ?pdflink ?series ?tipo ?notas

    """
    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    dados = resposta.json()['results']['bindings']
    return render_template('documentoID.html', dados=dados[0], documento_id=id)

@app.route('/documentos/tipo/<tipo_documento>')
def mostrar_documentos_por_tipo(tipo_documento):
    sparql_query = """
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?id ?tipo (GROUP_CONCAT(?emissor_nome; SEPARATOR=", ") AS ?emissores) ?fonte ?data ?notas
WHERE {
  ?documento rdf:type :Documento ;
             :data ?data ;
             :tipo ?tipo ;
             :éEmitidoPor ?emissor ;
             :fonte ?fonte ;
             :notas ?notas .
  
  ?emissor :nomeEmissor ?emissor_nome .
  
  BIND(STRAFTER(str(?documento), "#") AS ?id_s)  
  BIND(xsd:integer(?id_s) AS ?id)  

  FILTER (?tipo = "%s")
}
GROUP BY ?id ?tipo ?fonte ?data ?notas
ORDER BY ?id
""" % tipo_documento


    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    dados = resposta.json()['results']['bindings']

    return render_template('documentos_tipo.html', dados=dados)


@app.route('/emissor/<emissor_nome>')
def mostrar_documentos_por_emissor(emissor_nome):

    emissor_nome = unquote(emissor_nome)
    sparql_query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?id ?tipo ?emissor_nome ?fonte ?data ?notas
    WHERE {
      ?documento rdf:type :Documento ;
                 :data ?data ;
                 :tipo ?tipo ;
                 :éEmitidoPor ?emissor ;
                 :fonte ?fonte ;
                 :notas ?notas .
      
      ?emissor :nomeEmissor ?emissor_nome .
      FILTER (?emissor_nome = "%s")
      
      BIND(STRAFTER(str(?documento), "#") AS ?id_s)  
      BIND(xsd:integer(?id_s) AS ?id)  
    }
    ORDER BY ?id
    """ % emissor_nome

    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})
    
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        print(dados)
        return render_template('documentos_por_emissor.html', dados=dados, emissor_nome=emissor_nome)
    else:
        return render_template('error.html')

@app.route('/autores')
def mostrar_autores():
    # Consulta SPARQL para recuperar todos os nomes de emissores únicos
    sparql_query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT DISTINCT ?emissor_nome
    WHERE {
      ?emissor :nomeEmissor ?emissor_nome .
    }
    ORDER BY ?emissor_nome
    """
    
    # Enviar a consulta SPARQL para o GraphDB
    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})
    
    if resposta.status_code == 200:
        dados = resposta.json()['results']['bindings']
        emissores = [emissor['emissor_nome']['value'] for emissor in dados]
        return render_template('autores.html', emissores=emissores)
    else:
        return render_template('error.html')

@app.route('/addDocumento', methods=['POST', 'GET'])
def add_documento():
    tipos = []  # Inicializa a lista de tipos
    emissores = []  # Inicializa a lista de emissores

    if request.method == 'POST':
        id = request.form['id']
        emissor = request.form['emissor']
        tipo = request.form['tipo']
        data = request.form['data']
        notas = request.form['notas']
        fonte = request.form['fonte']
        numero = request.form['numero']
        numeroDR = request.form['numeroDR']
        series = request.form['series']
        pdflink = request.form['pdflink']

        if series == "":
            series = 1
        emissor = re.sub(r'\s+', '_', emissor)
        emissor = re.sub(r'[\n\r]+', '', emissor)
        emissor = emissor.replace(',','').replace('.','').replace('"', '').replace('(','').replace(')','').replace('º','').replace('ª','').replace('«','').replace('»','').replace("'","").replace('/','_').replace('–','').replace('%', 'Porcento').replace('_¿', '').replace('-_','').replace('°', '').replace('!', '').replace('?', '').replace('+', 'Mais').replace('[', '').replace(']', '').replace('_', '').replace('@', '_arroba_').replace('=', '_igual_a_').replace('´', '_').replace('&', 'E')

        query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT DATA {{
<http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}> rdf:type owl:NamedIndividual ,
                                                           :Documento ;
			  :éEmitidoPor :{emissor} ;
              :tipo "{tipo}" ;
              :data "{data}" ;
              :notas "{notas}" ;
              :fonte "{fonte}" ;
              :numero "{numero}" ;
              :numeroDR "{numeroDR}" ;
              :series {series} ;
              :pdflink "{pdflink}" .
}}
"""
        try:
            print(query)
            sparql = SPARQLWrapper(graphdb_endpoint + "/statements")
            sparql.setMethod('POST')
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.query().convert()
            return render_template('confirmacaoDoc.html')
        except Exception as e:
            return render_template('error.html')


    # Consulta SPARQL para recuperar todos os tipos
    sparql_query_tipos = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?tipo
    WHERE {
      ?documento rdf:type :Documento ;
                 :tipo ?tipo .
    }
    """

    # Consulta SPARQL para recuperar todos os emissores
    sparql_query_emissores = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?emissor_nome
    WHERE {
      ?emissor :nomeEmissor ?emissor_nome .
    }
    ORDER BY ?emissor_nome
    """

    sparql_query_maxid = """
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (MAX(?id) as ?max_id)
WHERE {
  ?documento rdf:type :Documento .
  BIND(xsd:integer(STRAFTER(str(?documento), "#")) AS ?id)
}

    """

    try:
        # Enviar consulta SPARQL para obter o id
        resposta_tipos = requests.get(graphdb_endpoint, params={'query': sparql_query_maxid}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_tipos.status_code == 200:
            id = int(resposta_tipos.json()['results']['bindings'][0]['max_id']['value']) + 1
        else:
            return "Erro ao obter o id."
        
        # Enviar consulta SPARQL para obter tipos
        resposta_tipos = requests.get(graphdb_endpoint, params={'query': sparql_query_tipos}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_tipos.status_code == 200:
            tipos = [tipo['tipo']['value'] for tipo in resposta_tipos.json()['results']['bindings']]
        else:
            return "Erro ao obter os tipos."

        # Enviar consulta SPARQL para obter emissores
        resposta_emissores = requests.get(graphdb_endpoint, params={'query': sparql_query_emissores}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_emissores.status_code == 200:
            emissores = [emissor['emissor_nome']['value'] for emissor in resposta_emissores.json()['results']['bindings']]
        else:
            return "Erro ao obter os emissores."
    except Exception as e:
        return f"Erro: {e}"

    return render_template('addDocumento.html', tipos=tipos, emissores=emissores, id=id)

@app.route('/addEmissor', methods=['POST', 'GET'])
def add_emissor():

    if request.method == 'POST':
        emissor = request.form['emissor']

        emissor2 = emissor
        emissor = re.sub(r'\s+', '_', emissor)
        emissor =  re.sub(r'[\n\r]+', '', emissor)
        emissor = emissor.replace(',','').replace('.','').replace('"', '').replace('(','').replace(')','').replace('º','').replace('ª','').replace('«','').replace('»','').replace("'","").replace('/','_').replace('–','').replace('%', 'Porcento').replace('_¿', '').replace('-_','').replace('°', '').replace('!', '').replace('?', '').replace('+', 'Mais').replace('[', '').replace(']', '').replace('_', '').replace('@', '_arroba_').replace('=', '_igual_a_').replace('´', '_').replace('&', 'E')

        query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT DATA {{
:{emissor} rdf:type owl:NamedIndividual ,
                                :Emissor ;
                 :nomeEmissor "{emissor2.replace('"', '')}" .
}}

"""
        try:
            print(query)
            sparql = SPARQLWrapper(graphdb_endpoint + "/statements")
            sparql.setMethod('POST')
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.query().convert()
            return render_template('confirmacaoEmissor.html')
        except Exception as e:
            return render_template('error.html')


    return render_template('addEmissor.html')


@app.route('/documentos/search')
def mostrar_criterio_procura():
    criterio_procura = request.args.get('term', '').strip()
    if not criterio_procura:
        return "Erro: Nenhum critério de busca fornecido.", 400

    criterio_procura = unquote(criterio_procura)
    sparql_query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?id ?tipo (GROUP_CONCAT(?emissor_nome; SEPARATOR=", ") AS ?emissores) ?fonte ?data ?notas
WHERE {{
  ?documento rdf:type :Documento ;
             :data ?data ;
             :tipo ?tipo ;
             :éEmitidoPor ?emissor ;
             :fonte ?fonte ;
             :notas ?notas .
  
  ?emissor :nomeEmissor ?emissor_nome .

  FILTER(
    CONTAINS(LCASE(STR(?tipo)), LCASE("{criterio_procura}")) || 
    CONTAINS(LCASE(STR(?emissor_nome)), LCASE("{criterio_procura}")) || 
    CONTAINS(LCASE(STR(?fonte)), LCASE("{criterio_procura}")) || 
    CONTAINS(LCASE(STR(?data)), LCASE("{criterio_procura}")) || 
    CONTAINS(LCASE(STR(?notas)), LCASE("{criterio_procura}"))
  )

  BIND(xsd:integer(STRAFTER(str(?documento), "#")) AS ?id)
}}
GROUP BY ?id ?tipo ?fonte ?data ?notas
ORDER BY ?id

    """

    resposta = requests.get(graphdb_endpoint, params={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    dados = resposta.json()['results']['bindings']

    return render_template('filtered_documents.html', dados=dados, criterio_procura=criterio_procura)


@app.route('/documentos/edit/<id>', methods=['GET'])
def edit_documento(id):
    # Consultas SPARQL para obter o documento, emissores e tipos
    sparql_query_documento = f"""
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?id ?tipo ?emissores ?fonte ?data ?notas ?numero ?numeroDR ?series ?pdflink
    WHERE {{
        ?documento rdf:type :Documento ;
                   :éEmitidoPor ?emissores ;
                   :tipo ?tipo ;
                   :data ?data ;
                   :notas ?notas ;
                   :fonte ?fonte ;
                   :numero ?numero ;
                   :numeroDR ?numeroDR ;
                   :series ?series ;
                   :pdflink ?pdflink ;
                   FILTER(STR(?documento) = "http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}")
                   
        BIND(xsd:integer(STRAFTER(str(?documento), "#")) AS ?id)
    }}
    """
    
    # Obter emissores e tipos como nas outras rotas
    sparql_query_emissores = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?emissor_nome
    WHERE {
      ?emissor :nomeEmissor ?emissor_nome .
    }
    ORDER BY ?emissor_nome
    """
    
    sparql_query_tipos = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?tipo
    WHERE {
      ?documento rdf:type :Documento ;
                 :tipo ?tipo .
    }
    """
    
    try:
        # Obter documento
        resposta_documento = requests.get(graphdb_endpoint, params={'query': sparql_query_documento}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_documento.status_code == 200:
            item = resposta_documento.json()['results']['bindings'][0]
        else:
            return "Erro ao obter o documento."

        # Obter emissores
        resposta_emissores = requests.get(graphdb_endpoint, params={'query': sparql_query_emissores}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_emissores.status_code == 200:
            emissores = [emissor['emissor_nome']['value'] for emissor in resposta_emissores.json()['results']['bindings']]
        else:
            return "Erro ao obter os emissores."

        # Obter tipos
        resposta_tipos = requests.get(graphdb_endpoint, params={'query': sparql_query_tipos}, headers={'Accept': 'application/sparql-results+json'})
        if resposta_tipos.status_code == 200:
            tipos = [tipo['tipo']['value'] for tipo in resposta_tipos.json()['results']['bindings']]
        else:
            return "Erro ao obter os tipos."
        
    except Exception as e:
        return f"Erro: {e}"

    return render_template('editar_documento.html', item=item, emissores=emissores, tipos=tipos)

@app.route('/documentos/update/<id>', methods=['POST'])
def update_documento(id):
    emissor = request.form['emissor']
    tipo = request.form['tipo']
    data = request.form['data']
    notas = request.form['notas']
    fonte = request.form['fonte']
    numero = request.form['numero']
    numeroDR = request.form['numeroDR']
    series = request.form['series']
    pdflink = request.form['pdflink']

    if series == "":
        series = 1
    emissor = re.sub(r'\s+', '_', emissor)
    emissor = re.sub(r'[\n\r]+', '', emissor)
    emissor = emissor.replace(',','').replace('.','').replace('"', '').replace('(','').replace(')','').replace('º','').replace('ª','').replace('«','').replace('»','').replace("'","").replace('/','_').replace('–','').replace('%', 'Porcento').replace('_¿', '').replace('-_','').replace('°', '').replace('!', '').replace('?', '').replace('+', 'Mais').replace('[', '').replace(']', '').replace('_', '').replace('@', '_arroba_').replace('=', '_igual_a_').replace('´', '_').replace('&', 'E')

    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {{
<http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}> ?p ?o .
}}
INSERT {{
<http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}> rdf:type owl:NamedIndividual ,
                                                        :Documento ;
                                                      :éEmitidoPor :{emissor} ;
                                                      :tipo "{tipo}" ;
                                                      :data "{data}" ;
                                                      :notas "{notas}" ;
                                                      :fonte "{fonte}" ;
                                                      :numero "{numero}" ;
                                                      :numeroDR "{numeroDR}" ;
                                                      :series {series} ;
                                                      :pdflink "{pdflink}" .
}}
WHERE {{
    <http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}> ?p ?o .
}}
"""
    try:
        sparql = SPARQLWrapper(graphdb_endpoint + "/statements")
        sparql.setMethod('POST')
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.query().convert()
        return redirect('/documentos')  # Redireciona para a página de documentos após atualização
    except Exception as e:
        return render_template('error.html', error=str(e))
    


@app.route('/documentos/delete/<id>', methods=['POST'])
def delete_documento(id):
    # Renderizar a página de confirmação
    documento = {"id": {"value": id}}  # Aqui, você pode buscar mais detalhes se necessário
    return render_template('confirmar_delete.html', item=documento)

@app.route('/confirm_delete/<id>', methods=['POST'])
def confirm_delete_documento(id):
    query = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/DiarioRepublica/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE WHERE {{
    <http://rpcw.di.uminho.pt/2024/DiarioRepublica#{id}> ?p ?o .
}}
"""
    try:
        sparql = SPARQLWrapper(graphdb_endpoint + "/statements")
        sparql.setMethod('POST')
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.query().convert()
        return redirect('/documentos')  # Redireciona para a página de documentos após eliminação
    except Exception as e:
        return render_template('error.html', error=str(e))






if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)