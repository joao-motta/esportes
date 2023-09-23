from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from model import Base

class Documento(Base):
    __tablename__ = 'documento'

    id = Column("id", Integer, primary_key=True)
    tipo_documento = Column(String(50))
    nr_documento = Column(Integer)
    razao_social = Column(String(140))
    valor = Column(Float)
    data_vencimento = Column(String(50))
    status = Column(String(50))

    def __init__(self, tipo_documento: str, nr_documento: int, razao_social: str, valor: float, data_vencimento: str, status: str):
        """
        Cria um Documento

        Arguments:
            tipo_documento: AP ou AR (Sendo AP = Contas a Pagar e AR = Contas a Receber)
            nr_documento: Numero do documento
            razao_social: Nome completo do cliente ou fornecedor
            valor: valor do documento
            data_vencimento: data quando o documento irá vencer
        """
        self.tipo_documento = tipo_documento
        self.nr_documento = nr_documento
        self.razao_social = razao_social
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.status = status