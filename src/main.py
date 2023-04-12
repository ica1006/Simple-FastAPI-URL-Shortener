from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from urllib.parse import urlparse
from pathlib import Path
from entry_model import Entry
from pymongo import MongoClient
from json import load

with open("config.json", encoding='UTF-8') as json_file:
            config = load(json_file)
ADMIN_KEY = config['admin_key']
CONNECTION_STRING = config['mongodb_connection_string']

app = FastAPI()
db_client = MongoClient(CONNECTION_STRING).url_shortener

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

@app.post('/')
async def post_redirect(body: Entry):
    entry = search_url(body.domain, body.query_id)
    if type(entry) != Entry:
        if body.admin_key == ADMIN_KEY:
            entry_dict = {'query_id': body.query_id, "url": body.url, "domain": body.domain}
            db_client.redirections.insert_one(entry_dict)
            inserted_entry = search_url(body.domain, body.query_id)
            if type(inserted_entry) != Entry:
                return launch_error(400, "Error creating the entry")
            else:
                return "Entry created succesfully"
        else:
             return launch_error(400, "Not valid admin_key")
    return launch_error(404, "Redirection already exists")

@app.delete('/{domain}/{query_id}')
async def delete_redirect(domain: str, query_id: str, admin_key: str):
    entry = search_url(domain, query_id)
    if type(entry) == Entry:
        if admin_key == ADMIN_KEY:
            db_client.redirections.find_one_and_delete({"domain": domain, "query_id": query_id})
            return "Entry deleted succesfully"
        else:
             return launch_error(400, "Not valid admin_key")
    else:
         return launch_error(404, "Redirection not found")

@app.put('/')
async def put_redirect(body: Entry):
    entry = search_url(body.domain, body.query_id)
    if type(entry) == Entry:
        if body.admin_key == ADMIN_KEY:
            entry_dict = {'query_id': body.query_id, "url": body.url, "domain": body.domain}
            db_client.redirections.find_one_and_replace({"domain": body.domain, "query_id": body.query_id}, entry_dict)
            edited_entry = search_url(body.domain, body.query_id)
            if edited_entry.url != body.url:
                return launch_error(400, "Error modifying the entry")
            else:
                return "Entry modified succesfully"
        else:
             return launch_error(400, "Not valid admin_key")
    return launch_error(404, "Redirection not found")