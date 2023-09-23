from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Documento
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
documento_tag = Tag(name="Documento", description="Adição, visualização e remoção de documentos à base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/documento', tags=[documento_tag],
          responses={"200": DocumentoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_documento(form: DocumentoSchema):
    """Adiciona um novo Documento à base de dados

    Retorna uma representação dos documentos
    """
    documento = Documento(
        tipo_documento=form.tipo_documento,
        nr_documento=form.nr_documento,
        razao_social=form.razao_social,
        valor=form.valor,
        data_vencimento=form.data_vencimento,
        status=form.status)
    logger.debug(f"Adicionando o documento de numero: '{documento.nr_documento}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(documento)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado o documento de numero: '{documento.nr_documento}'")
        return apresenta_documento(documento), 200

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar o documento '{documento.nr_documento}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/documentos', tags=[documento_tag],
         responses={"200": ListagemDocumentosSchema, "404": ErrorSchema})
def get_documentos():
    """Faz a busca por todos os Documentos cadastrados

    Retorna uma representação da listagem de documentos.
    """
    logger.debug(f"Coletando Documentos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    documentos = session.query(Documento).all()

    if not documentos:
        # se não há produtos cadastrados
        return {"documentos": []}, 200
    else:
        logger.debug(f"%d rodutos econtrados" % len(documentos))
        # retorna a representação de produto
        print(documentos)
        return apresenta_documentos(documentos), 200


@app.get('/documento', tags=[documento_tag],
         responses={"200": DocumentoViewSchema, "404": ErrorSchema})
def get_documento(query: DocumentoBuscaSchema):
    """Faz a busca por um Documento a partir do id do documento

    Retorna uma representação dos documento.
    """
    nr_documento = request.args.get("NR_DOCUMENTO")
    razao_social = request.args.get("RAZAO_SOCIAL")
    logger.debug(f"Coletando dados sobre documento com NR_DOCUMENTO '{nr_documento}' e RAZAO_SOCIAL '{razao_social}'")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    query = session.query(Documento)
    if nr_documento:
        query = query.filter(Documento.nr_documento == nr_documento)
    if razao_social:
        query = query.filter(Documento.razao_social == razao_social)

    if not documento:
        # se o documento não foi encontrado
        error_msg = "Documento não encontrado na base :/"
        logger.warning(f"Erro ao buscar documento '{nr_documento}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Documento econtrado: '{documento.nr_documento}'")
        # retorna a representação de documento
        return apresenta_documento(documento), 200


@app.delete('/documento', tags=[documento_tag],
            responses={"200": DocumentoDelSchema, "404": ErrorSchema})
def del_documento(query: DocumentoBuscaSchema):
    """Deleta um Documento a partir do numero do documento (nr_documento) informado

    Retorna uma mensagem de confirmação da remoção.
    """
    nr_documento = query.nr_documento
    razao_social = query.razao_social

    print(nr_documento)
    logger.debug(f"Deletando dados sobre produto #{nr_documento}")
    # criando conexão com a base    
    session = Session()
    # fazendo a remoção
    count = session.query(Documento).filter(Documento.nr_documento == nr_documento, Documento.razao_social == razao_social).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado o documento numero #{nr_documento}")
        return {"mesage": "Documento removido", "nr_documento": nr_documento}
    else:
        # se o documento não foi encontrado
        error_msg = "Documento não encontrado na base :/"
        logger.warning(f"Erro ao deletar documento #'{nr_documento}', {error_msg}")
        return {"mesage": error_msg}, 404
