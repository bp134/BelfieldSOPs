import json
import os

# Files are right here in the current folder
files_to_merge = [
    "profile_and_rp.json",
    "dispensing_sops.json",
    "advanced_and_appendices.json",
]

all_sops = []

print("Extracting SOPs from current folder...")

for file_name in files_to_merge:
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                content = json.load(f)
                
                if isinstance(content, list):
                    all_sops.extend(content)
                elif isinstance(content, dict):
                    if "sops" in content and isinstance(content["sops"], list):
                        all_sops.extend(content["sops"])
                    else:
                        all_sops.append(content)
                        
            print(f"✅ Successfully read: {file_name}")
        except json.JSONDecodeError as e:
            print(f"❌ Error reading {file_name}: {e}")
    else:
        print(f"⚠️ Missing file: {file_name}")

# Wrap them up for app.py
master_data = {
    "pharmacy_profile": {
        "name": "Belfield Pharmacy",
        "location": "Rochdale"
    },
    "sops": all_sops
}

# Save directly into this folder
output_path = "fixed_sop_data.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Success! Rebuilt master file with {len(all_sops)} SOPs inside.")
print(f"Saved to: {os.path.abspath(output_path)}")
