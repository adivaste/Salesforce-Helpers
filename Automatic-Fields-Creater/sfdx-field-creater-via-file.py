
#!/usr/bin/env python3
import os
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

# ========= Utility Functions =========

def get_pretty_xml(element):
    """Return a pretty-printed XML string for the Element."""
    raw_xml = ET.tostring(element, encoding="utf-8")
    return parseString(raw_xml).toprettyxml(indent="  ")



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
    """
    Process the input string.
    If it contains a space then treat it as a label,
    otherwise treat it as a developer name.
    Returns a tuple: (label, developer_name)
    """
    if " " in user_input:
        label = user_input
        dev_name = generate_developer_name_from_label(label)
    else:
        dev_name = user_input if user_input.endswith("__c") else user_input + "__c"
        label = generate_label_from_developer_name(dev_name)
    return label, dev_name

# ========= XML Field Creation Functions =========

def create_field_xml(label_input, field_type, details):
    """Generate a pretty-printed XML string for the given field."""
    label, dev_name = process_label_input(label_input)
    field = ET.Element("CustomField", xmlns="http://soap.sforce.com/2006/04/metadata")
    ET.SubElement(field, "fullName").text = dev_name
    ET.SubElement(field, "label").text = label
    ET.SubElement(field, "required").text = "false"

    field_type_lower = field_type.strip().lower()
    if field_type_lower == "text":
        ET.SubElement(field, "type").text = "Text"
        ET.SubElement(field, "length").text = "255"
    elif field_type_lower == "number":
        ET.SubElement(field, "type").text = "Number"
        precision, scale = details.split(",") if "," in details else ("0", "0")
        ET.SubElement(field, "precision").text = precision.strip()
        ET.SubElement(field, "scale").text = scale.strip()
    elif field_type_lower == "currency":
        ET.SubElement(field, "type").text = "Currency"
        precision, scale = details.split(",") if "," in details else ("0", "0")
        ET.SubElement(field, "precision").text = precision.strip()
        ET.SubElement(field, "scale").text = scale.strip()
    elif field_type_lower == "date":
        ET.SubElement(field, "type").text = "Date"
    elif field_type_lower in ("datetime", "date time"):
        ET.SubElement(field, "type").text = "DateTime"
    elif field_type_lower in ("checkbox", "boolean"):
        ET.SubElement(field, "type").text = "Checkbox"
        ET.SubElement(field, "defaultValue").text = "false"
    elif field_type_lower == "lookup":
        ET.SubElement(field, "type").text = "Lookup"
        lookup_object = details.strip() if details else "Account"
        ET.SubElement(field, "referenceTo").text = lookup_object
    elif field_type_lower == "picklist":
        ET.SubElement(field, "type").text = "Picklist"
        valueSet = ET.SubElement(field, "valueSet")
        if details.lower().startswith("global:"):
            global_vs = details[len("global:"):].strip()
            ET.SubElement(valueSet, "valueSetName").text = global_vs
            ET.SubElement(valueSet, "restricted").text = "true"
        else:
            valueSetDef = ET.SubElement(valueSet, "valueSetDefinition")
            ET.SubElement(valueSetDef, "sorted").text = "false"
            ET.SubElement(valueSet, "restricted").text = "true"
            for val in details.split(";"):
                if val.strip():
                    valueElem = ET.SubElement(valueSetDef, "value")
                    ET.SubElement(valueElem, "fullName").text = val.strip()
                    ET.SubElement(valueElem, "default").text = "false"
                    ET.SubElement(valueElem, "label").text = val.strip()
    else:
        ET.SubElement(field, "type").text = "Text"
        ET.SubElement(field, "length").text = "255"

    return get_pretty_xml(field)

# ========= File Processing Functions =========

def create_sample_file(file_path):
    """Create a sample input file with examples of all field types."""
    sample_content = """\
Customer Name,Text,
Order Amount,Number,10,2
Price,Currency,8,2
Start Date,Date,
Created Date,DateTime,
Is Active,Checkbox,
Account Reference,Lookup,Contact
Status,Picklist,New;In Progress;Closed
Category,Picklist,global:MyGlobalValueSet
"""
    with open(file_path, "w") as sample_file:
        sample_file.write(sample_content)
    print(f"Sample file created: {file_path}")

def process_input_file(file_path):
    """Process an input file and generate XML files for each field."""
    output_dir = "output_xml"
    os.makedirs(output_dir, exist_ok=True)
    with open(file_path, 'r') as infile:
        for lineno, line in enumerate(infile, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 2)
            if len(parts) < 2:
                print(f"Line {lineno} has an invalid format: {line}")
                continue
            field_id = parts[0].strip()
            field_type = parts[1].strip()
            details = parts[2].strip() if len(parts) > 2 else ""
            xml_str = create_field_xml(field_id, field_type, details)
            _, dev_name = process_label_input(field_id)
            filename = os.path.join(output_dir, f"{dev_name}.field-meta.xml")
            with open(filename, "w", encoding="utf-8") as outfile:
                outfile.write(xml_str)
            print(f"Generated XML for: {field_id} -> {filename}")

# ========= Main Entry Point =========

def main():
    input_file = "fields.txt"
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found!")
        create_sample_file(input_file)
        print("A sample input file has been created with examples of all field types.")
        print("Please review and edit the file, then re-run the script.")
        if input("Do you want to delete the sample file? (yes/no): ").strip().lower() == "yes":
            os.remove(input_file)
            print("Sample file deleted.")
        return

    process_input_file(input_file)

if __name__ == "__main__":
    main()
