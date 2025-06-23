import os, json

def get_manifest():
    files = []
    for root, _, filenames in os.walk("src"):
        for f in filenames:
            if f.endswith((".py", ".twhile")): 
                files.append("transpiler/" + os.path.join(root, f).replace("\\", "/"))

    files.append("transpiler/config.py")
    return files

with open("manifest.json", "w") as out:
    json.dump(get_manifest(), out)