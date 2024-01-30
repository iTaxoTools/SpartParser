from lxml import etree
import sys
import os

def validate_xmlSpart(xml_path):
    xsd_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'XMLSpart.xsd')
    with open(
        xsd_file_path, 'rb') as schema_file:
        xsd_content = schema_file.read()
        schema_root = etree.XML(xsd_content)

    schema = etree.XMLSchema(schema_root)

    parser = etree.XMLParser(schema=schema)

    try:
        with open(xml_path, 'rb') as xml_file:
            etree.fromstring(xml_file.read(), parser)
        print("XML file is valid!")
    except etree.XMLSyntaxError as e:
        print(f"XML file is not valid: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python yourscript.py <path_to_xml>")
        sys.exit(1)

    xml_file = sys.argv[1]
        
    validate_xmlSpart(xml_file)