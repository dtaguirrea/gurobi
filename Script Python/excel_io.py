"""Excel tabular (.xlsx) con biblioteca estándar, sin openpyxl/xlsxwriter.

Soporta texto compartido o inline, números y booleanos. Rechaza fórmulas:
exporte los parámetros como valores para evitar cachés de Excel obsoletas.
No pretende ser un editor general de libros de Excel.
"""
import math
import posixpath
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CONTENT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def column_name(index):
    name = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def read_xlsx(path):
    result = {}
    with ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            shared = [''.join(t.text or '' for t in si.iter(f'{{{NS}}}t'))
                      for si in root]
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in relationships}
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in workbook.find(f'{{{NS}}}sheets'):
            target = targets[sheet.attrib[f'{{{REL}}}id']]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            root = ET.fromstring(archive.read(member))
            rows = []
            for row in root.findall(f'.//{{{NS}}}sheetData/{{{NS}}}row'):
                values = []
                for cell in row.findall(f'{{{NS}}}c'):
                    ref = cell.attrib['r']
                    if cell.find(f'{{{NS}}}f') is not None:
                        raise ValueError(f'{sheet.attrib["name"]}!{ref}: use valores, no fórmulas.')
                    letters = re.match(r'[A-Z]+', ref).group()
                    index = 0
                    for letter in letters:
                        index = index * 26 + ord(letter) - 64
                    while len(values) < index:
                        values.append(None)
                    kind, node = cell.attrib.get('t'), cell.find(f'{{{NS}}}v')
                    raw = node.text if node is not None else None
                    if kind == 'inlineStr':
                        value = ''.join(t.text or '' for t in cell.iter(f'{{{NS}}}t'))
                    elif kind == 's':
                        value = shared[int(raw)]
                    elif kind == 'e':
                        raise ValueError(f'{sheet.attrib["name"]}!{ref}: error de Excel {raw}.')
                    elif raw is None:
                        value = None
                    elif kind == 'b':
                        value = raw == '1'
                    elif kind in ('str', 'd'):
                        value = raw
                    else:
                        value = float(raw)
                    values[index - 1] = value
                while values and values[-1] is None:
                    values.pop()
                rows.append(values)
            result[sheet.attrib['name']] = rows
    return result


def write_xlsx(path, tables):
    """Escribe tablas de valores con cabeceras, anchos y filtros en XLSX real."""
    def xml(element):
        return ET.tostring(element, encoding='utf-8', xml_declaration=True)

    workbook = ET.Element('workbook', xmlns=NS)
    sheets = ET.SubElement(workbook, 'sheets')
    relationships = ET.Element('Relationships', xmlns=PKG)
    types = ET.Element('Types', xmlns=CONTENT)
    for ext, mime in [('rels', 'application/vnd.openxmlformats-package.relationships+xml'),
                      ('xml', 'application/xml')]:
        ET.SubElement(types, 'Default', Extension=ext, ContentType=mime)
    ET.SubElement(types, 'Override', PartName='/xl/workbook.xml',
                  ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml')
    root_rels = ET.Element('Relationships', xmlns=PKG)
    ET.SubElement(root_rels, 'Relationship', Id='rId1', Type=REL + '/officeDocument', Target='xl/workbook.xml')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        for index, (name, rows) in enumerate(tables.items(), 1):
            if not name or len(name) > 31 or re.search(r'[\[\]:*?/\\]', name):
                raise ValueError(f'Nombre de hoja inválido: {name!r}.')
            ET.SubElement(sheets, 'sheet', name=name, sheetId=str(index),
                          attrib={f'{{{REL}}}id': f'rId{index}'})
            ET.SubElement(relationships, 'Relationship', Id=f'rId{index}',
                          Type=REL + '/worksheet', Target=f'worksheets/sheet{index}.xml')
            ET.SubElement(types, 'Override', PartName=f'/xl/worksheets/sheet{index}.xml',
                          ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
            sheet = ET.Element('worksheet', xmlns=NS)
            views = ET.SubElement(sheet, 'sheetViews')
            ET.SubElement(views, 'sheetView', workbookViewId='0', showGridLines='0')
            cols = ET.SubElement(sheet, 'cols')
            width = max((len(row) for row in rows), default=1)
            for col in range(width):
                size = max((len(str(row[col])) for row in rows if col < len(row)), default=10)
                ET.SubElement(cols, 'col', min=str(col+1), max=str(col+1),
                              width=str(min(65, max(16, size+2))), customWidth='1')
            data = ET.SubElement(sheet, 'sheetData')
            for ri, row in enumerate(rows, 1):
                node = ET.SubElement(data, 'row', r=str(ri))
                for ci, value in enumerate(row, 1):
                    if value is None:
                        continue
                    cell = ET.SubElement(node, 'c', r=f'{column_name(ci)}{ri}')
                    if isinstance(value, bool):
                        cell.set('t', 'b')
                        ET.SubElement(cell, 'v').text = str(int(value))
                    elif isinstance(value, (int, float)) and math.isfinite(value):
                        ET.SubElement(cell, 'v').text = str(value)
                    else:
                        cell.set('t', 'inlineStr')
                        ET.SubElement(ET.SubElement(cell, 'is'), 't').text = str(value)
            if rows:
                ET.SubElement(sheet, 'autoFilter', ref=f'A1:{column_name(width)}{len(rows)}')
            archive.writestr(f'xl/worksheets/sheet{index}.xml', xml(sheet))
        archive.writestr('[Content_Types].xml', xml(types))
        archive.writestr('_rels/.rels', xml(root_rels))
        archive.writestr('xl/workbook.xml', xml(workbook))
        archive.writestr('xl/_rels/workbook.xml.rels', xml(relationships))
