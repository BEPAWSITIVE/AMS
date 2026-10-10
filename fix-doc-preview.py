import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'(\{documentFile \? \(\s*<>\s*<svg className="w-8 h-8 mb-1 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth=\{2\} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" \/><\/svg>\s*<span className="text-green-600">Photo Ready!<\/span>\s*<span className="text-xs text-gray-500 mt-1 max-w-full truncate px-4">\{documentFile\.name\}<\/span>\s*<\/>)'

replacement = """{documentFile ? (
                          <div className="flex flex-col items-center justify-center space-y-2">
                            <img src={URL.createObjectURL(documentFile)} alt="Preview" className="w-full max-h-32 object-contain rounded-lg border-2 border-green-400 shadow-sm" />
                            <div className="flex items-center text-green-600">
                              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                              <span>Photo Ready!</span>
                            </div>
                            <span className="text-xs text-gray-500 max-w-full truncate px-4">{documentFile.name}</span>
                          </div>"""

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
    print("Success")
else:
    print("Pattern not found")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
