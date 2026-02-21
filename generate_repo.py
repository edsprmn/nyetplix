import os
import hashlib
import zipfile
import shutil
import xml.etree.ElementTree as ET

def get_addon_info(addon_xml_path):
    tree = ET.parse(addon_xml_path)
    root = tree.getroot()
    return root.get('id'), root.get('version')

def create_zip(addon_folder, addon_id, addon_version, output_path):
    zip_filename = f"{addon_id}-{addon_version}.zip"
    zip_path = os.path.join(output_path, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Create the path inside the zip (must start with the addon id folder)
                arcname = os.path.join(addon_id, os.path.relpath(file_path, addon_folder))
                zipf.write(file_path, arcname)
    return zip_filename

def generate():
    zips_path = "zips"
    if not os.path.exists(zips_path):
        os.makedirs(zips_path)
    
    xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
    
    addon_folders = [d for d in os.listdir(".") if os.path.isdir(d) and os.path.exists(os.path.join(d, "addon.xml")) and d != zips_path and not d.startswith(".")]
    
    for folder in addon_folders:
        addon_xml_path = os.path.join(folder, "addon.xml")
        addon_id, addon_version = get_addon_info(addon_xml_path)
        
        # Create folder for this addon in zips
        addon_zip_dir = os.path.join(zips_path, addon_id)
        if not os.path.exists(addon_zip_dir):
            os.makedirs(addon_zip_dir)
            
        print(f"Packaging {addon_id} v{addon_version}...")
        
        # Create the zip file
        create_zip(folder, addon_id, addon_version, addon_zip_dir)
        
        # Copy addon.xml to the zip dir (Kodi sometimes needs this for icons)
        shutil.copy(addon_xml_path, os.path.join(addon_zip_dir, "addon.xml"))
        
        # Add to master xml content
        with open(addon_xml_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines[0].startswith("<?xml"):
                xml_content += "".join(lines[1:])
            else:
                xml_content += "".join(lines)
        xml_content += "\n"
        
    xml_content += "</addons>\n"
    
    xml_output_path = os.path.join(zips_path, "addons.xml")
    with open(xml_output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    md5 = hashlib.md5(xml_content.encode("utf-8")).hexdigest()
    with open(xml_output_path + ".md5", "w") as f:
        f.write(md5)
        
    print(f"\nSukses! Generated {xml_output_path} and packed {len(addon_folders)} addons.")

if __name__ == "__main__":
    generate()
