#-*- coding: utf-8 -*-
from ..data import BoletoData, custom_property


class BoletoCaixa(BoletoData):
    '''
        Gera Dados necessários para criação de boleto para o banco Caixa
        Economica Federal

    '''

    conta_cedente = custom_property('conta_cedente', 11)

    '''
        Agencia do cedente sem DV
    '''
    agencia_cedente = custom_property('agencia_cedente', 4)

    def __init__(self):
        super(BoletoCaixa, self).__init__()

        self.codigo_banco = "104"
        self.local_pagamento = "Preferencialmente nas Casas Lotéricas e Agências da Caixa"
        self.logo_image = "logo_bancocaixa.jpg"
        self.inicio_nosso_numero = '24'

    '''
        Nosso Numero (sem DV) -> 17 digitos

        Este numero tem o inicio fixo
        Carteira SR: 80, 81 ou 82
        Carteira CR: 90 (Confirmar com gerente qual usar)

        Configurar: `self.inicio_nosso_numero`
    '''
    def _nosso_numero_get(self):
        return self._nosso_numero

    def _nosso_numero_set(self, val):
        try:
            self._nosso_numero = self.inicio_nosso_numero + str(self.formata_numero(val, 15))
        except AttributeError:
            pass

    nosso_numero = property(_nosso_numero_get, _nosso_numero_set)

    @property
    def dv_nosso_numero(self):
        resto2 = self.modulo11(self.nosso_numero.split('-')[0], 9, 1)
        digito = 11 - resto2
        if digito == 10 or digito == 11:
            dv = 0
        else:
            dv = digito
        return dv

    '''
        Chars para barcode de 44 digitos
    '''
    @property
    def barcode(self):
        num = "%3s%1s%1s%4s%10s%25s" % (
            self.codigo_banco,
            self.moeda,
            'X',
            self.fator_vencimento,
            self.formata_valor(self.valor_documento, 10),
            self.campo_livre
        )
        dv = self.calculate_dv_barcode(num.replace('X', '', 1))
        num = num.replace('X', str(dv), 1)
        return num

    @property
    def campo_livre(self):
        num = '%7s%3s%1s%3s%1s%9s' % (
            self.conta_cedente.replace('-', '')[-7:],
            self.nosso_numero[3:6],
            self.nosso_numero[0],
            self.nosso_numero[6:9],
            self.nosso_numero[1],
            self.nosso_numero[8:18]
        )
        num += str(self.modulo11(num))
        return num

    @property
    def linha_digitavel(self):
        linha = self.barcode
        if not linha:
            BoletoException("Boleto doesn't have a barcode")

        # campo1
        campo1 = linha[0:3] + linha[3] + linha[19:24]
        campo1 += str(self.modulo10(campo1))
        campo1 = '%s.%s' % (campo1[:5], campo1[5:])
        # campo2
        campo2 = linha[24:34]
        campo2 += str(self.modulo10(campo2))
        campo2 = '%s.%s' % (campo2[:5], campo2[5:])
        # campo3
        campo3 = linha[34:44]
        campo3 += str(self.modulo10(campo3))
        campo3 = '%s.%s' % (campo3[:5], campo3[5:])
        # campo4
        campo4 = linha[4]
        # campo5
        campo5 = linha[5:9] + linha[9:19]

        return "%s %s %s %s %s" % (campo1, campo2, campo3, campo4, campo5)

    def format_nosso_numero(self):
        return self._nosso_numero + '-' + str(self.dv_nosso_numero)

    @property
    def agencia_conta_cedente(self):
        v = self.conta_cedente.split('-')
        v[0] = v[0][-6:]
        return "%s/%s" % (self.agencia_cedente, '-'.join(v))
