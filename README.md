# Yuta

## Arquitetura do Projeto

O projeto Yuta é uma aplicação web desenvolvida com Flask, seguindo o padrão MVC (Model-View-Controller). A aplicação está configurada para rodar em um ambiente Docker com um banco de dados MongoDB.

### Estrutura de Diretórios

- `app/`: Contém o código fonte da aplicação, incluindo modelos, visualizações, controladores e configurações.
- `app/templates/`: Armazena os templates HTML usados pela aplicação.
- `app/static/`: Contém arquivos estáticos como CSS e JavaScript.
- `docker-compose.yml`: Define os serviços do Docker, como o banco de dados MongoDB e o Mongo Express para gerenciamento do banco.

## Adicionando Endpoints

Para adicionar novos endpoints à aplicação:

1. **Defina o Controlador**: Crie um novo controlador em `app/controllers/`. Use APIBlueprint para definir rotas.

```python
from flask_openapi3 import APIBlueprint

new_controller = APIBlueprint("new", __name__, url_prefix="/api/new")

@new_controller.get("/")
def new_function():
    return {"message": "New endpoint"}
```

2. Registre o Endpoint: Adicione o controlador ao método register_endpoints em app/register_endpoints.py.

```python
from app.controllers.new_controller import new_controller

def register_endpoints(app: Flask):
    app.register_api(new_controller)
    # Adicione outros endpoints aqui
```


## Documentação com Swagger

A documentação é gerada automaticamente pelo Flask-OpenAPI3. Para adicionar descrições e especificações ao Swagger:
1. Adicione Tags e Respostas: No controlador, defina tags e respostas esperadas para cada rota.

```python
from flask_openapi3 import Tag

new_tag = Tag(name="New Feature")

@new_controller.get("/", tags=[new_tag])
def new_function():
    return {"message": "New endpoint"}
```

## Rodando o Projeto

1. Instale as dependências do projeto com o Poetry.

```
$ poetry install
```

2. Execute o projeto com as dependencias instaladas:

```
$ poetry run dev
```

## Usando Docker Compose

Para subir o projeto com todos os serviços necessários:

1. Suba os containers:

```
$ docker-compose up -d
````

2. Acesse o Mongo Express para gerenciar o banco de dados em http://localhost:8081.

## Validação de Esquema com Pydantic

A validação de esquema no projeto é realizada utilizando a biblioteca Pydantic. Pydantic é uma biblioteca de análise de dados e validação de dados usando anotações de tipo Python. Ela permite a definição de modelos de dados que automaticamente realizam a validação de tipos, conversão e documentação.

### Definição de Modelos com PyMongo

Os modelos de dados são definidos utilizando o PyMongo, que é uma biblioteca Python para trabalhar com o MongoDB. Os modelos são definidos como classes Python, e o Pydantic é usado para garantir que os dados recebidos e armazenados estejam de acordo com o esquema definido.

Exemplo de um modelo de dispositivo:

```python
class Device(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    type: Literal["lamp", "fan", "door", "motion-sensor"]
    pin: int
```

## Schema de validação com OpenAPI

O projeto utiliza o Flask-OpenAPI3 para gerar o schema de validação com OpenAPI. O schema é gerado automaticamente a partir das anotaçes de tipo do Pydantic. Para adicionar uma nova validação, basta adicionar o modelo ao controlador e definir a tag do endpoint.


```python
@devices_controller.get("/", tags=[devices_tag], responses={200: DevicesResponse})
def devices_list():
    """List devices for the authenticated user"""
    repository = DevicesRepository(database=database)
    devices = list(repository.find_by({}))

    print(devices)

    response = DevicesResponse(devices=devices).json()
    return Response(
        status=200,
        response=response,
        content_type="application/json",
    )
```

## Ferramentas de Desenvolvimento e Formatação de Código

### Ruff

O Ruff é um linter de código para Python que garante que o código esteja em conformidade com um estilo consistente. Para formatar o código do projeto, execute o seguinte comando:

```bash
$ poetry run ruff check . --fix
```
