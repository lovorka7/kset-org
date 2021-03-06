#coding: utf-8

import os
from datetime import date
from decimal import *
from copy import copy

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle


font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'assets', 'fonts', 'nimbus_sans_becker_lcon.ttf')
pdfmetrics.registerFont(TTFont('NimbusSans', font_path))


class InvoiceTemplate():
    """
    Invoice document class.
    Defines seller, buyer, info (no, date, etc) and items.
    """

    # public members

    seller = {'name':        'Savez studenata Fakulteta elektrotehnike i računarstva',
              'address':     'Unska 3, 10000 Zagreb',
              'phone':       '01/6129-758',
              'email':       'info@kset.org',
              'taxnum':      '14504100762',
              'bankaccount': '2402006-1100582760'}

    buyer = {'name':    'N.N.',
             'address': '',
             'taxnum':  ''}

    info = {'num':         'YYYY-RB',
            'date':        date.today().strftime('%d.%m.%Y.'),
            'items':       [],
            'taxnote':     'Porez na dodanu vrijednost nije zaračunat na temelju čl. 22. Zakona o PDV-u.'}

    # private members

    # document flow
    __flow = []

    __pSeller = "<font size=13>{name}</font> <br />{address} <br />Tel: {phone}, E-mail: {email} <br />OIB: {taxnum} <br />ž.r: {bankaccount}"

    __pBuyer = "<font size=13>{name}</font> <br />{address} <br />Šifra: {taxnum}"

    __pInfo = "<font size=16>Račun br. {num}</font> <br /><font size=13>Datum: {date}</font>"

    __pSignature = "Odgovorna osoba &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br /><br /><br /><br /><br />MP &nbsp;&nbsp; ____________________________________ &nbsp;&nbsp;&nbsp;&nbsp;"

    __margins = {'top': 1.5*cm,
                 'right': 1.5*cm,
                 'bottom': 1.5*cm,
                 'left': 1.5*cm}

    __tStyle = [('FONT', (0, 0), (-1, -1), 'NimbusSans'),
                ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('LINEABOVE', (0, 2), (-1, -2), 0.25, colors.black),
                ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                ('SPAN', (0, -1), (-2, -1))]

    def __init__(self, filename):
        """Constructor, sets styles and creates blank document."""

        # set paragraph styles
        self.__set_styles()

        # creat document from template
        self.doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1.0*cm, rightMargin=1.0*cm, bottomMargin=1.0*cm, leftMargin=1.0*cm, title='', author='')

    def __set_styles(self):
        """Prepares document styles."""

        self.__styles = {}
        self.__styles['Normal'] = ParagraphStyle('Normal')
        self.__styles['Normal'].fontName = 'NimbusSans'

        self.__styles['NormalCenter'] = copy(self.__styles['Normal'])
        self.__styles['NormalCenter'].alignment = 1

        self.__styles['NormalRight'] = copy(self.__styles['Normal'])
        self.__styles['NormalRight'].alignment = 2

    def hr(self):
        """Inserts horizontal rule into document flow."""

        style = [("LINEBELOW", (0, 0), (0, 0), 1, colors.black)]

        self.__flow.append(Spacer(1, 1*cm))
        self.__flow.append(Table([''], colWidths=19*cm, style=TableStyle(style)))
        self.__flow.append(Spacer(1, 1*cm))

    def newPage(self):
        """Jumps to a new page, aka pageBreak."""

        self.__flow.append(PageBreak())

    def populate(self):
        """Populates document flow.

           Elements:
             - header:  seller, buyer
             - content: items, prices, tax, final sum
             - footer:  none

        """

        # header
        self.__flow.append(Paragraph(self.__pSeller.format(name=self.seller['name'],
                                                           address=self.seller['address'],
                                                           phone=self.seller['phone'],
                                                           email=self.seller['email'],
                                                           taxnum=self.seller['taxnum'],
                                                           bankaccount=self.seller['bankaccount']), self.__styles['Normal']))

        self.__flow.append(Spacer(1, 1*cm))

        self.__flow.append(Paragraph(self.__pBuyer.format(name=self.buyer['name'],
                                                          address=self.buyer['address'],
                                                          taxnum=self.buyer['taxnum']), self.__styles['NormalRight']))

        self.__flow.append(Spacer(1, 2*cm))

        # info
        self.__flow.append(Paragraph(self.__pInfo.format(num=self.info['num'], date=self.info['date']), self.__styles['NormalCenter']))
        self.__flow.append(Spacer(1, 3*cm))

        # items
        data = [['', 'Stavka', 'Iznos']]

        summarum = 0.0
        n = 0
        for item in self.info['items']:
            n += 1
            summarum += item[1]
            data.append([str(n), item[0], '%.2f kn' % item[1]])

        data.append(['Ukupno:', '', '%.2f kn' % summarum])

        self.__flow.append(Table(data, colWidths=(1*cm, 14*cm, 3*cm), style=TableStyle(self.__tStyle)))
        self.__flow.append(Spacer(1, 1*cm))

        self.__flow.append(Paragraph(self.info['taxnote'], self.__styles['NormalRight']))

        self.__flow.append(Spacer(1, 7*cm))

        self.__flow.append(Paragraph(self.__pSignature, self.__styles['NormalRight']))

    def create(self):
        """Finally build document."""

        self.doc.build(self.__flow)
