# Nanodegree Desenvolvedor Web Full-Stack Udacity
## Projeto: Catalogo de Itens

Esse projeto ter por objetivo gerar uma lista de itens em várias categorias e um sistema de registro e autenticação
de usuarios. Aqueles registrados poderão postar, editar e excluir apenas os seus próprios itens.

### Instalação

Este projeto requer **Python 2.7** que pode ser baixado e instalado 
através desse link: [Python 2.7](https://www.python.org/download/releases/2.7/)

Para rodar será necessário instalar O [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) 
e o [Vagrant](https://www.vagrantup.com/downloads.html)

Após isso, é necessário clonar a Virtual Machine [fullstack-nanodegree-vm] (https://github.com/udacity/fullstack-nanodegree-vm)
Para executar, dentro da pasta vagrant, via terminal, rode **vagrant up** e depois, para acessar, execute **vagrant ssh**

### Banco de Dados

O Banco de dados será criado automaticando quando rodar o comando:
**python database_setup.py**

Ele ficará fisicamente armazenado no arquivo **catalogo.db**
No projeto já tem uma versão dele populado com dados de teste.
Mas ele pode ser exluído e recriado que a aplicação se comportará normalmente.

O banco de dados possui duas tabelas:
**Categoria** Relação das categorias
**Item** Relação dos itens

Ambas possuem um campo **user** para guardar o usuário que fez o cadastro.

### Execução

Para executar utilize no terminal: **$ python application.py**

O sistema abrirá uma tela que permitirá visualizar Caegorias e itens mesmo sem estar logado.
Para poder cadastrar, alterar e excluir tanto categorias, quanto itens, é precisa fazer a autenticação
no serviço **oauth** do Google.

Para configurar essa autenticação, existe um arquivo chamado **client_secrets.json** que armazena uma
chave secreta da aplicação Udacity Catalog criada no serviço Google APIs.

Após autenticar, o usuário poderá cadastrar itens e categorias e editar e excluir apenas as categorias
e itens cadastros previamente por ele.

### Endpoint JSON

Existem 2 endpoints disponiveis para o usuário:
http://localhost:8000/jsonCategorias - que permite visualizar o JSON com todas as categorias existentes.
http://localhost:8000/jsonItens - que permite visualizar o JSON com todas os itens existentes.
http://localhost:8000/jsonItem/(item_id) - que permite visualizar o JSON referente aqule item que o id foi fornecido.

### Outras considerações 

A interface gráfica usa a biblioteca [Bootstrap] (https://getbootstrap.com/) e tem alguma customizações
especificas dentro da pasta **/static/css/** no arquivo style.css

Os templates html estão na pasta **/templates/**, para facilitar a leitura, foi criado um arquivo de nome 
**base.html** que possui todo o código que é comum para todas as páginas.