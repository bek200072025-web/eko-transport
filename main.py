from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.router import api

USERNAME = 'admin'
PASSWORD = 'banana'
security = HTTPBasic()

app = FastAPI(
    title='Eko-Transport API',
    contact={
        'name': "ASILBEK",
        'url': 'https://t.me/murojaat13_bot',
    },
    description="Boss username: ekorentuz@email.com, "
                "Boss password: ekorent: "
                "Admin username: bek200072025@gmail.com, "
                "Admin password: bek2004",
    docs_url=None,
    redoc_url=None,
)
from fastapi.staticfiles import StaticFiles
# deploy uchun
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/redoc", include_in_schema=False)
def custom_redoc(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="ReDoc Documentation"
    )

if not os.path.exists("files"):
    os.makedirs("files")

app.include_router(api)

app.mount(
    "/files/",
    StaticFiles(directory=os.path.join(os.getcwd(), "files")),
    name="files"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
