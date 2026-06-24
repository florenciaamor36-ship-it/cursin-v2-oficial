import requests
import json
import datetime
import os

SUPABASE_URL = "https://ypzudkxowpxvdggvongz.supabase.co/rest/v1/cursos"
# Se recomienda usar variables de entorno para seguridad
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_KEY_HERE") 

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("discovery.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def get_existing_urls():
    try:
        res = requests.get(f"{SUPABASE_URL}?select=url", headers=HEADERS)
        if res.status_code == 200:
            return {item['url'] for item in res.json()}
    except: pass
    return set()

def discover_coursera():
    log("Iniciando descubrimiento en Coursera...")
    url = "https://api.coursera.org/api/courses.v1?q=search&query=UNAM&includes=partnerIds&fields=description,partnerIds,photoUrl"
    try:
        res = requests.get(url)
        data = res.json().get('elements', [])
        new_courses = []
        existing = get_existing_urls()
        
        for c in data:
            c_url = f"https://www.coursera.org/learn/{c['slug']}"
            if c_url not in existing:
                new_courses.append({
                    "titulo": c['name'],
                    "plataforma": "Coursera/UNAM",
                    "url": c_url,
                    "descripcion": c.get('description', '')[:500],
                    "imagen_url": c.get('photoUrl', ''),
                    "es_gratis": True,
                    "categoria_id": 2
                })
        
        if new_courses:
            log(f"Encontrados {len(new_courses)} nuevos cursos.")
            res_push = requests.post(SUPABASE_URL, headers=HEADERS, data=json.dumps(new_courses))
            log(f"Respuesta Supabase: {res_push.status_code}")
        else:
            log("No se encontraron cursos nuevos.")
            
    except Exception as e:
        log(f"Error: {str(e)}")

if __name__ == "__main__":
    discover_coursera()
