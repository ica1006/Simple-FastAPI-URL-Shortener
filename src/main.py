from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from db_client import db_client
from pathlib import Path
from entry_model import Entry

app = FastAPI()

def search_url(query_id):
    try:
        entry = db_client.redirections.find_one({'query_id': query_id})
        return entry
    except:
        None

@app.get('/')
async def hello_world():
    return 'Hello World!'

@app.get('/{query_id}')
async def redirect(query_id: str):
    entry = search_url(query_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Query parameter not found")
    url = entry['url']
    html_code = Path('index.html').read_text()
    html_code = html_code.replace(f'%%_URL_%%', url)
    return HTMLResponse(content=html_code, status_code=200)

@app.post('/{query_id}')
async def add_redirect(query_id: str, body: dict):
    entry = search_url(query_id)
    if not entry:
        db_client.redirections.insert_one(body)
        inserted_entry = search_url(query_id)
        if not inserted_entry:
            raise HTTPException(status_code=400, detail="Error creating the entry")
        else:
            return "Entry created succesfully"
    raise HTTPException(status_code=404, detail="Query id already exists")
