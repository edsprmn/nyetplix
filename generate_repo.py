import os
import hashlib

def generate():
    # Go to the zips directory
    zips_path = "zips"
    if not os.path.exists(zips_path):
        os.makedirs(zips_path)
    
    # Header for addons.xml
    xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
    
    # Find all addon folders (including the repository itself)
    # For this simplified repo, we assume addon folders are in the root
    addon_folders = [d for d in os.listdir(".") if os.path.isdir(d) and os.path.exists(os.path.join(d, "addon.xml"))]
    
    for folder in addon_folders:
        addon_xml_path = os.path.join(folder, "addon.xml")
        with open(addon_xml_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Skip the first line if it's the xml declaration
            if lines[0].startswith("<?xml"):
                xml_content += "".join(lines[1:])
            else:
                xml_content += "".join(lines)
        xml_content += "\n"
        
    xml_content += "</addons>\n"
    
    # Write addons.xml to zips folder
    xml_output_path = os.path.join(zips_path, "addons.xml")
    with open(xml_output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    # Generate MD5
    md5 = hashlib.md5(xml_content.encode("utf-8")).hexdigest()
    with open(xml_output_path + ".md5", "w") as f:
        f.write(md5)
        
    print(f"Generated {xml_output_path} and its MD5.")

if __name__ == "__main__":
    generate()
