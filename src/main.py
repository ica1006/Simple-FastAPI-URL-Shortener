from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from urllib.parse import urlparse
from db_client import db_client
from pathlib import Path
from entry_model import Entry

app = FastAPI()

def search_url(domain, query_id):
    try:
        entry = db_client.redirections.find_one({'domain': domain, 'query_id': query_id})
        return Entry(**entry)
    except:
        raise HTTPException(status_code=400, detail='Something went wrong looking for the redirection entry')

@app.get('/')
async def hello_world():
    return 'Hello World!'

@app.get('/{query_id}')
async def redirect(query_id: str, request: Request):
    base_url = str(request.base_url)
    domain = urlparse(base_url).netloc
    entry = search_url(domain, query_id)
    if type(entry) != Entry:
        raise HTTPException(status_code=404, detail="Redirection not found")
    html_code = Path('index.html').read_text()
    html_code = html_code.replace(f'%%_URL_%%', entry.url)
    return HTMLResponse(content=html_code, status_code=200)

@app.post('/')
async def add_redirect(body: Entry):
    entry = search_url(body.domain, body.query_id)
    if type(entry) != Entry:
        db_client.redirections.insert_one(dict(body))
        inserted_entry = search_url(body.domain, body.query_id)
        if type(inserted_entry) != Entry:
            print(type(inserted_entry))
            raise HTTPException(status_code=400, detail="Error creating the entry")
        else:
            return "Entry created succesfully"
    raise HTTPException(status_code=404, detail="Redirection already exists")
