import json
with open('package.json', 'r') as f:
    data = json.load(f)
data['dependencies']['dexie'] = '^4.0.4'
data['dependencies']['dexie-react-hooks'] = '^1.1.7'
with open('package.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Done")
