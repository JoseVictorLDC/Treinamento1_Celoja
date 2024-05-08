## Como rodar o projeto?

Para facilitar a execução dos códigos de extração, vamos utilizar o virtualenv, que é uma ferramenta que cria ambientes isolados de Python.

Dessa forma, podemos instalar somente as dependências necessárias sem termos que nos preocupar com o resto.

É necessário ter o pip instalado, caso não tenha, instale-o primeiro.
  
Para criar o ambiente isolado primeiro é necessário instalar o virtualenv.

Aqui tem um [tutorial de instalação](https://virtualenv.pypa.io/en/latest/installation.html).

Uma vez que temos o virtualenv instalado, vamos criar o ambiente, para isso rode os seguintes comandos.

`virtualenv .venv`

Agora temos o ambiente nomeado como *.venv*, para ativá-lo rode o seguinte comando no terminal.

Se for Windows:
`.venv\Scripts\activate`

Se for Linux:
`source .venv/bin/activate`

Agora temos o ambiente ativado, para instalar as dependências do projeto rode o seguinte comando.
`pip install -r requirements.txt`

**Pronto!** Agora você já possui o ambiente adequado para rodar o projeto.