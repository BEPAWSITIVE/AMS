import os

with open('app/api/analyze/route.ts', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace v1beta and gemini-1.5-flash with v1 and gemini-1.5-flash
code = code.replace('v1beta/models/gemini-1.5-flash:generateContent', 'v1beta/models/gemini-1.5-flash-latest:generateContent')

with open('app/api/analyze/route.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
