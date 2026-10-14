import uuid, os

meta_path = 'Assets/Scripts/GameStartMenuUI.cs.meta'
if not os.path.exists(meta_path):
    guid = uuid.uuid4().hex
    content = f'''fileFormatVersion: 2
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
'''
    with open(meta_path, 'w') as f:
        f.write(content)
    print('Created', meta_path)

with open('Assembly-CSharp.csproj', 'r', encoding='utf-8') as f:
    csproj = f.read()

target = '<Compile Include="Assets\\Scripts\\EscapeMenuUI.cs" />'
new_entry = '<Compile Include="Assets\\Scripts\\GameStartMenuUI.cs" />'
if new_entry not in csproj and target in csproj:
    csproj = csproj.replace(target, target + '\n    ' + new_entry)
    with open('Assembly-CSharp.csproj', 'w', encoding='utf-8') as f:
        f.write(csproj)
    print('Added GameStartMenuUI.cs to Assembly-CSharp.csproj')
