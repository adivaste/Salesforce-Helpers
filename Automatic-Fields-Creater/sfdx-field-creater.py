
#!/usr/bin/env python3
import os
import re
import xml.etree.ElementTree as ET
import inquirer  # pip install inquirer

def get_input(prompt, default=None):
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt)
    return value if value else default

def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for child in elem:
            indent(child, level+1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def generate_developer_name_from_label(label):
    """Convert a label (with spaces) to Salesforce-style developer name, preserving original casing."""
    return "_".join(word.strip() for word in label.split()) + "__c"

def generate_label_from_developer_name(dev_name):
    """Convert a Salesforce-style developer name into a human-readable label."""
    if dev_name.endswith("__c"):
        dev_name = dev_name[:-3]  # Remove "__c"
    # Replace underscores with spaces
    return " ".join(word for word in dev_name.split("_"))

def process_label_input(user_input):
    if " " in user_input:
        label = user_input
        dev_name = generate_developer_name_from_label(label)
    else:
        dev_name = user_input if user_input.endswith("__c") else user_input + "__c"
        label = generate_label_from_developer_name(dev_name)
    return label, dev_name

def create_text_field(label, dev_name):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Text"
    ET.SubElement(field, "length").text = "255"
    ET.SubElement(field, "required").text = "false"
    return field

def create_number_field(label, dev_name, precision, scale):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Number"
    ET.SubElement(field, "precision").text = precision
    ET.SubElement(field, "scale").text = scale
    ET.SubElement(field, "defaultValue").text = "0"
    ET.SubElement(field, "required").text = "false"
    return field

def create_currency_field(label, dev_name, precision, scale):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Currency"
    ET.SubElement(field, "precision").text = precision
    ET.SubElement(field, "scale").text = scale
    ET.SubElement(field, "defaultValue").text = "0"
    ET.SubElement(field, "required").text = "false"
    return field

def create_date_field(label, dev_name):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Date"
    ET.SubElement(field, "required").text = "false"
    return field

def create_datetime_field(label, dev_name):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "DateTime"
    ET.SubElement(field, "required").text = "false"
    return field

def create_boolean_field(label, dev_name):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Checkbox"
    ET.SubElement(field, "defaultValue").text = "false"
    ET.SubElement(field, "required").text = "false"
    return field

def create_lookup_field(label, dev_name, lookupObject):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Lookup"
    ET.SubElement(field, "referenceTo").text = lookupObject  # Hardcoded lookup object
    ET.SubElement(field, "required").text = "false"
    return field

def create_picklist_field(label, dev_name, global_vs, values):
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "type").text = "Picklist"
    ET.SubElement(field, "required").text = "false"

    valueSet = ET.SubElement(field, "valueSet")
    if global_vs:
        ET.SubElement(valueSet, "valueSetName").text = global_vs
    else:
        valueSetDef = ET.SubElement(valueSet, "valueSetDefinition")
        ET.SubElement(valueSet, "restricted").text = "true"

        for val in values.split(","):
            val = val.strip()
            if val:
                valueElem = ET.SubElement(valueSetDef, "value")
                ET.SubElement(valueElem, "fullName").text = val
                ET.SubElement(valueElem, "default").text = "false"
    return field

def main():
    print("=== Salesforce Custom Field XML Creator ===")
    while True:
        user_input = input("Enter field Label or Developer Name (or press Enter to quit): ")
        if not user_input:
            break

        label, dev_name = process_label_input(user_input)
        print(f"Using Label: '{label}' and Developer Name: '{dev_name}'")

        questions = [
            inquirer.List(
                "field_type",
                message="Choose field type",
                choices=["Text", "Number", "Currency", "Date", "DateTime", "Boolean", "Picklist", "Lookup"],
                carousel=True,
            )
        ]
        answers = inquirer.prompt(questions)
        field_type = answers.get("field_type", "Text")
        
        if field_type.lower() == "text":
            field_xml = create_text_field(label, dev_name)
        elif field_type.lower() == "number":
            precision = get_input("Enter precision", "0")
            scale = get_input("Enter scale", "0")
            field_xml = create_number_field(label, dev_name, precision, scale)
        elif field_type.lower() == "currency":
            precision = get_input("Enter precision", "18")
            scale = get_input("Enter scale", "2")
            field_xml = create_currency_field(label, dev_name, precision, scale)
        elif field_type.lower() == "date":
            field_xml = create_date_field(label, dev_name)
        elif field_type.lower() == "datetime":
            field_xml = create_datetime_field(label, dev_name)
        elif field_type.lower() in ("boolean", "checkbox"):
            field_xml = create_boolean_field(label, dev_name)
        elif field_type.lower() == "lookup":
            lookupObject = get_input("Enter Lookup Object Name", "Account")
            field_xml = create_lookup_field(label, dev_name,lookupObject);
        elif field_type.lower() == "picklist":
            global_vs = input("Enter Global Value Set name (if any, otherwise leave blank): ")
            values = ""
            if not global_vs:
                values = get_input("Enter comma-separated picklist values", "Option1, Option2")
            field_xml = create_picklist_field(label, dev_name, global_vs, values)
        else:
            print("Unknown field type. Defaulting to Text field.")
            field_xml = create_text_field(label, dev_name)
        
        indent(field_xml)
        filename = dev_name + ".field-meta.xml"
        tree = ET.ElementTree(field_xml)
        with open(filename, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        print(f"XML file '{filename}' created successfully.\n")

if __name__ == "__main__":
    main()


