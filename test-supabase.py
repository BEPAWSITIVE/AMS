import urllib.request
import json
import ssl

url = "https://rcsjwdtatnqodekwqpur.supabase.co/rest/v1/employees?select=*"
headers = {
    "apikey": "sb_publishable_oczVf9MN6xKzfYNcIy37uQ_4V0Y4mE0",
    "Authorization": "Bearer sb_publishable_oczVf9MN6xKzfYNcIy37uQ_4V0Y4mE0"
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print("Status:", response.status)
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.reason)
    print(e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
