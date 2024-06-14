# Relatório do projeto de RPCW

### Autores

* [Telmo Maciel PG54246](https://github.com/telmomaciel9)
* [Ricardo Araújo PG54190](https://github.com/ricardoaraujoo)


---

### Como correr a aplicação

##### Requisitos:

* Docker


##### Iniciar os servidores:

Para iniciar os servidores, tanto do graphdb como da nossa aplicação, basta ir à diretoria app/ e correr os comandos "docker-compose build" e "docker-compose up", por esta ordem. Após isso o graphdb fica disponível na porta 7200 e a nossa aplicação na porta 5001.

Os servidores ficam disponíveis nos seguintes links:
* [Graphdb](http://localhost:7200)
* [App](http://localhost:5001)


##### Colocar a ontologia no Graphdb:

Após iniciar os servidores é necessário colocar a ontologia no graphdb para podermos começar a disfrutar da nossa aplicação. Para tal, primeiro temos de ir à secção Setup -> Repositories e criar um novo repositório GraphDB com o nome "DRepublica". De seguida, ir à secção Import e dar import da ontologia a utilizar que, dependendo do tamanho do ficheiro, poderá ser dado de várias formas, no nosso caso damos import da nossa ontologia através de um ficheiro zip. 

Após a conclusão deste processo, a nossa aplicação está pronta a funcionar.


---
### Introdução

No âmbito da unidade curricular de Representação e Processamento de Conhecimento Web foi-nos pedido para desenvolver um projeto de forma a aprofundar todos os conhecimentos adquiridos ao longo do semestre. 

O nosso projeto consiste na criação de uma aplicação web capaz de recolher e adicionar informação a uma ontologia previamente desenvolvida. Esta ontologia é composta por dados (documentos) do site do Diário da Republica que se encontram no seguinte [link](https://epl.di.uminho.pt/~jcr/AULAS/RPCW2024/projeto/).


### Tarefas

As tarefas propostas para o nosso trabalho prático consistem no seguinte:

1. Especificação de uma ontologia para um determinado domínio;
2. Criação de uma App web que permita explorar e tirar partido da ontologia;
3. Deverá ser possível aumentar a ontologia a partir da aplicação Web.

### Análise do dataset fornecido

Após uma primeira análise do dataset fornecido encontramos vários campos desnecessário e que podiam ser retirados e, após uma discussão entre o grupo, foi decidido retirar as chaves 'dre_key', 'in_force', 'conditional', 'processing', 'plain_text', 'pdf_error' e 'timestamp'.

O dataset final consistiu apenas nos seguintes campos:

* claint
* doc_type
* number
* dr_number
* series
* emiting_body
* source
* date
* notes
* dre_pdf

Para tal ser possível, foi criado o ficheiro 'tratarDataset.py' que normaliza o texto em unicode e remove as colunas que o grupo decidiu retirar. O dataset final foi guardado como "DREdataset_clean.json".

### Ontologia desenvolvida

Nesta secção iremos falar de tudo que diz respeito à criação da nossa ontologia.

##### Estrutura da ontologia

Tendo em conta o ficheiro json resultante do preprocessamento dos dados, decidimos criar duas classes, Documento e Emissor, e as relações entre ambos, éEmitidoPor e Emitiu. Como data properties adicionamos a data, fonte, nomeEmissor, notas, numero, numeroDR, pdflink, series e tipo, sendo todos no formato string excepto o series que é um inteiro.

Um documento é composto pelo seguinte:
* id: número de identificação do documento (valor único)
* data: data que o documento foi emitido
* fonte: fonte do documento
* notas: informações sobre o documento
* numero: número de referência
* numeroDR: número no DR
* pdflink: link para o pdf do documento (que por vezes pode ser inválido ou não conter link)
* series: série
* tipo: tipo de documento

E o emissor é composto por nomeEmissor que representa o nome do mesmo.


##### Povoamento da ontologia

Para fazermos o povoamento de toda a ontologia tendo em conta o dataset que obtivemos, foi criado o ficheiro geraTTL.py que vai a cada documento presente no dataset e cria os atributos necessários para ser adicionado à ontologia. É aqui neste ficheiro que os dados são tratados de forma a não dar erros depois na importação, isto é, remoção de caracteres inválidos, remoção de espaços, quebras de linha, etc. O resulado será, então, guardado no ficheiro DR_output.ttl, que estará pronto a ser importado no graphdb.


### Desenvolvimento da aplicação

Nesta secção falaremos de todos os passos por detrás da criação da nossa aplicação web, envolvendo tanto o frontend como backend e as ferramentas/tecnologias utilizadas.

##### Ferramentas/tecnologias utilizadas

Para o desenvolvimento do nosso servidor backend foi utilizada a framework Flask do Python. Como base de dados recorremos, então, ao GraphDB, que é uma base de dados que permite o armazenamento em formato de grafo.

##### Backend

No desenvolvimento do backend foram criadas várias rotas que vão responder aos pedidos da nossa página e serão apresentadas já de seguida.

GET/: Retorna a página principal do nosso programa.

GET/tipos: Retorna todos os tipos de documentos disponíveis.

GET/documentos: Retorna todos os documentos num formato de tabela paginada.

GET/documentos/: Retorna uma página com todas as informações de um documento individual. Que recebe como parâmetros:
* id: identificador do documento

GET/documentos/tipo/: Retorna uma página com todos os documentos do tipo fornecido. Que recebe como parâmetros:
* tipo_documento: Tipo do documento

GET/emissor/: Retorna uma página com todos os documentos do autor fornecido. Que recebe como parâmetros:
* emissor_nome: Nome do emissor do documento

GET/autores: Retorna uma página com todos os emissores de documentos disponíveis.

GET/documentos/search: Retorna uma página com todos os documentos que dizem respeito ao critério de procura.

POST/addDocumento: Adiciona um novo documento à base de dados. Parâmetros do formulário:

* id
* emissor
* tipo 
* data
* notas 
* fonte 
* numero
* numeroDR 
* series 
* pdflink

POST/addEmissor: Adiciona um novo emissor à base de dados.

GET/documentos/edit/: Retorna uma página com todos os dados de um documento para posterior edição. Que recebe como parâmetros:
* id: identificador do documento

POST/documentos/update/: Guarda todas as alterações efetuadas na página de edição. Que recebe como parâmetro o id e como parâmetros do formulário:

* id
* emissor
* tipo 
* data
* notas 
* fonte 
* numero
* numeroDR 
* series 
* pdflink

POST/documentos/delete/: Retorna uma página de confirmação para eliminação de um documento da base de dados. Que recebe como parâmetros:
* id: identificador do documento

POST/confirm_delete/: Elimina um documento da base de dados. Que recebe como parâmetros:
* id: identificador do documento

##### Frontend

Nesta secção será referido todo o processo da construção do frontend e falar um pouco sobre a estrutura da nossa aplicação.

Para o desenvolvimento do frontend foi utilizado o html e o css nativo. 

Ao correr a nossa app o utilizador vai ter as seguintes funcionalidades:

1) Página principal (HomePage): É fornecida uma lista de opções para o utilizador selecionar, entre elas listar todos os documentos, listar todos os autores, listar todos os tipos de documentos, adicionar um novo documento e adicionar um novo emissor. É também possível pesquisar documentos por um critério à escolha através do input do utilizador numa barra de procura.

2) Página com os documentos listados: É apresentada uma tabela com todos os documentos existentes mostrando o id, tipo, emissor, fonte, data e notas. É possível efetuar uma procura dos documentos pelo termo que o utilizador quiser ou até ordenar os documentos pelo critério que assim desejar. É, ainda, possível eliminar ou editar um documento clicando num botão na linha correspondente ao documento que desejamos fazer alterações.

3) Página com os documentos filtrados: Funcionamento igual à página com os documentos todos mas apenas filtrando os documentos pelo termo de procura.

4) Mostrar as informações de um documento: É apresentada uma página com todas as informações de um documento, apresentando também uma pre-visualização do documento pdf. É possível aceder a esta página através do clique no campo 'id' em qualquer local do website.

5) Mostrar a lista de autores ou tipos: É apresentada uma página com todos os autores ou tipos de documentos disponíveis. Nesta página é possível clicar no autor/tipo e abrirá uma nova página que mostra os documentos desse mesmo autor ou tipo de documento. É possível aceder a esta página clicando no nome do autor ou tipo de documento em qualquer local do website.

6) Edição de documento: É apresentada uma página com todas as informações de um documento, tal como referido em 4) mas, neste caso, é possível editar os campos do documento (que já se encontram pre-preenchidos) e, no final, guardar alterações ou voltar atrás.

7) Eliminação de documento: É apresentada uma página de confirmação da eliminação do documento que desejamos eliminar, tendo o utilizador de clicar em "eliminar" ou "cancelar".

8) Header da página: O header da página é composto pelo logo do Diário da República (sempre que o utilizador clica no mesmo é aberta a homepage) e opções de navegação como "Página inicial", "Documentos", "Autores" e "Tipos". Ao clicar em qualquer uma destas opções de navegação o website será redirecionado para a página em questão.


##### Docker

Por fim, o grupo recorreu ao docker para armazenar as várias camadas da nossa aplicação e permitir uma melhor e mais rápida execução da parte de quem vai testar ou correr a nossa aplicação web. Este passo também foi importante para reduzir os erros/conflitos na máquina de quem for executar o nosso projeto.

### Conclusão

Este projeto foi importante para consolidar os conhecimentos adquiridos ao longo do semestre na unidade curricular de RPCW. Durante o desenvolvimento, enfrentamos desafios significativos, especialmente na criação da ontologia e no tratamento do dataset, mas conseguimos superá-los com a colaboração dos vários membros do grupo.

No geral, estamos confiantes de que nosso trabalho atendeu aos requisitos estabelecidos pelo docente. Desenvolvemos uma aplicação web funcional que não só apresenta dados de forma eficaz através de uma ontologia, mas também permite a adição e remoção de dados. O grupo alcançou todos os objetivos propostos pelo professor, demonstrando um sólido entendimento dos conceitos abordados em sala de aula e aplicando-os de maneira eficaz num projeto final.

Estamos extremamente satisfeitos com o resultado final do projeto, e acreditamos que estabelecemos uma base sólida para o desenvolvimento futuro de uma plataforma com potencial aplicação no mundo real.