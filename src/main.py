from fastapi import FastAPI, Request, Form
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
        return launch_error(400, "Something went wrong looking for the redirection entry")

def launch_error(code:int, details:str):
    html_code = Path('html/error.html').read_text()
    html_code = html_code.replace(f'%%_ERROR_CODE_%%', str(code))
    html_code = html_code.replace(f'%%_ERROR_DETAILS_%%', details)
    return HTMLResponse(content=html_code, status_code=code)

def add_redirect(domain: str, query_id: str, url: str):
    entry = search_url(domain, query_id)
    if type(entry) != Entry:
        entry_dict = {'query_id': query_id, "url": url, "domain": domain}
        db_client.redirections.insert_one(entry_dict)
        inserted_entry = search_url(domain, query_id)
        if type(inserted_entry) != Entry:
            print(type(inserted_entry))
            return launch_error(400, "Error creating the entry")
        else:
            return "Entry created succesfully"
    return launch_error(404, "Redirection already exists")

@app.get('/')
async def index():
    html_code = Path('html/index.html').read_text()
    return HTMLResponse(content=html_code, status_code=200)

@app.get('/{query_id}')
async def redirect(query_id: str, request: Request):
    base_url = str(request.base_url)
    domain = urlparse(base_url).netloc
    entry = search_url(domain, query_id)
    if type(entry) != Entry:
        return launch_error(404, "Redirection not found")
    html_code = Path('html/redirect.html').read_text()
    html_code = html_code.replace(f'%%_URL_%%', entry.url)
    return HTMLResponse(content=html_code, status_code=200)

@app.post('/json')
async def post_redirect(body: Entry):
    return add_redirect(domain=body.domain, query_id=body.query_id, url=body.url)

@app.post('/form')
async def post_redirect(domain:str = Form(...), query_id:str = Form(...), url:str = Form(...)):
    return add_redirect(domain=domain, query_id=query_id, url=url)
