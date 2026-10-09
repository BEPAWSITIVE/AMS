import os

with open('app/api/analyze/route.ts', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('gemini-1.5-flash-latest', 'gemini-2.5-flash')

with open('app/api/analyze/route.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
