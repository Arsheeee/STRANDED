import uuid, os

meta_path = "Assets/Scripts/PixelArtFontManager.cs.meta"
if not os.path.exists(meta_path):
    guid = uuid.uuid4().hex
    meta_content = f"""fileFormatVersion: 2
guid: {guid}
MonoImporter:
  externalObjects: {{}}
  serializedVersion: 2
  defaultReferences: []
  executionOrder: 0
  icon: {{instanceID: 0}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""
    with open(meta_path, "w") as f:
        f.write(meta_content)
    print("Created", meta_path)

# Also check csproj
with open("Assembly-CSharp.csproj", "r", encoding="utf-8") as f:
    csproj = f.read()

target = '<Compile Include="Assets\\Scripts\\EscapeMenuUI.cs" />'
if target in csproj:
    print("Found EscapeMenuUI in csproj")
    new_entry = '<Compile Include="Assets\\Scripts\\PixelArtFontManager.cs" />\n    '
    if 'PixelArtFontManager.cs' not in csproj:
        csproj = csproj.replace(target, target + '\n    ' + '<Compile Include="Assets\\Scripts\\PixelArtFontManager.cs" />')
        with open("Assembly-CSharp.csproj", "w", encoding="utf-8") as f:
            f.write(csproj)
        print("Added PixelArtFontManager.cs to Assembly-CSharp.csproj")
else:
    print("Target not found exactly, searching...")
    idx = csproj.find("EscapeMenuUI.cs")
    print("EscapeMenuUI around:", csproj[idx-40:idx+40])
