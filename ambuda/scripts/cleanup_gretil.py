import re
from collections import OrderedDict

from xml.etree import ElementTree as ET
from ambuda.seed.texts.gretil import remove_namespace, NS

INPUT_FILE = "/home/ubuntu/environment/sanskrit/gretil/1_sanskr/tei/sa_kauTilya-arthazAstra.xml"
OUTPUT_FILE = "/home/ubuntu/environment/sanskrit/gretil/1_sanskr/tei/sa_kauTilya-arthazAstra.xml"

def main():
    tree = ET.parse(INPUT_FILE)
    xml = tree.getroot()
    namespaces = {"tei": NS["tei"]}
    ET.register_namespace('', NS["tei"])
    body = xml.find("./tei:text/tei:body", namespaces)
    sections = OrderedDict()
    for text in body.itertext():
        m = re.match('KAZ(\d*)?\.(\d*?)\.(\d*?)/ (.*)', text)
        if not m: continue
        book, chapter, verse, remaining = m.groups()
        section = f"{int(book)}.{int(chapter)}"
        if section not in sections:
            sections[section] = ET.Element("div", n=section)
        el = ET.SubElement(sections[section], "p")
        el.text = remaining
    for child in [c for c in body]:
        body.remove(child)
    for section in sections:
        body.append(sections[section])
    ET.indent(body, "  ", 1)
    with open(OUTPUT_FILE, "wb+") as out:
        ET.ElementTree(xml).write(out, encoding="UTF-8", xml_declaration=True)

if __name__ == '__main__':
    main()


# python -m ambuda.scripts.cleanup_gretil