import os
import re

base_dir = r"d:\my downloads\myHospital-master"

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # replace ${{ with Ksh {{
            new_content = content.replace("${{", "Ksh {{")
            # replace ($) with (Ksh)
            new_content = new_content.replace("($)", "(Ksh)")
            
            if content != new_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {path}")
