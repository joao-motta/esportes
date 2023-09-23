from pydantic import BaseModel
from typing import Optional, List
from model.documento import Documento
#from datetime import datetime


class DocumentoSchema(BaseModel):
    """ Define como um novo documento a ser inserido deve ser representado
    """
    tipo_documento: str = "AP"
    nr_documento: int = 123
    razao_social: str = "Ze Das Couves"
    valor: float = 500.20
    data_vencimento: str = "01/01/2023"
    status: str = "Pago"

class DocumentoBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome do produto.
    """
    nr_documento: int = 123
    razao_social: str = "Ze Das Couves"


class ListagemDocumentosSchema(BaseModel):
    """ Define como uma listagem de documentos será retornada.
    """
    documentos:List[DocumentoSchema]


def apresenta_documentos(documentos: List[Documento]):
    """ Retorna uma representação do documento seguindo o schema definido em
        DocumentoViewSchema.
    """
    result = []
    for documento in documentos:
        result.append({
            "tipo_documento": documento.tipo_documento,
            "nr_documento": documento.nr_documento,
            "razao_social": documento.razao_social,
            "valor": documento.valor,
            "data_vencimento": documento.data_vencimento,
            "status": documento.status
        })

    return {"documentos": result}


class DocumentoViewSchema(BaseModel):
    """ Define como um documento será retornado
    """
    id: int = 1
    tipo_documento: str = "AP"
    nr_documento: int = 123
    razao_social: str = "Ze Das Couves"
    valor: float = 500.20
    data_vencimento: str = "01/01/2023"
    status: str = "Pago"


class DocumentoDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nr_documento: int
    razao_social: str

def apresenta_documento(documento: Documento):
    """ Retorna uma representação do documento seguindo o schema definido em
        DocumentoViewSchema.
    """
    return {
        "id": documento.id,
        "tipo_documento": documento.tipo_documento,
        "nr_documento": documento.nr_documento,
        "razao_social": documento.razao_social,
        "valor": documento.valor,
        "data_vencimento": documento.data_vencimento,
        "status": documento.status
    }
