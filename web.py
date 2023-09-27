from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/subscription", response_class=HTMLResponse)
async def get_subscription_form(request: Request):
    return templates.TemplateResponse("subscription_form.html", {"request": request})
