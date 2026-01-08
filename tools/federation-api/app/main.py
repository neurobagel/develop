"""Main app."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse

from .api import utility as util
from .api.routers import (
    assessments,
    datasets,
    diagnoses,
    imaging_modalities,
    nodes,
    pipelines,
    query,
    subjects,
)
from .api.security import check_client_id

# Configure root logging once so all loggers (including the httpx logger and custom app logger)
# inherit same formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)

favicon_url = "https://raw.githubusercontent.com/neurobagel/documentation/main/docs/imgs/logo/neurobagel_favicon.png"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Collect and store locally defined and public node details for federation upon startup and clears the index upon shutdown.
    """
    check_client_id()
    await util.create_federation_node_index()
    yield
    util.FEDERATION_NODES.clear()


app = FastAPI(
    root_path=util.ROOT_PATH.value,
    default_response_class=ORJSONResponse,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """
    Display a welcome message and a link to the API documentation.
    """
    return f"""
 <html>
        <head>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f0f0f0;
                    font-family: Arial, sans-serif;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                }}
                .logo {{
                    animation: spin 5s linear infinite;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                h1 {{
                    color: #333;
                }}
                p {{
                    color: #666;
                }}
                a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://raw.githubusercontent.com/neurobagel/documentation/main/docs/imgs/logo/neurobagel_logo.png" alt="Neurobagel Logo" class="logo" width="144" height="144">
                <h1>Welcome to the Neurobagel Federation API!</h1>
                <p>Please visit the <a href="{request.scope.get('root_path', '')}/docs">API documentation</a> to view available API endpoints.</p>
            </div>
        </body>
    </html>
    """


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Overrides the default favicon with a custom one.
    """
    return RedirectResponse(url=favicon_url)


@app.get("/docs", include_in_schema=False)
def overridden_swagger(request: Request):
    """
    Overrides the Swagger UI HTML for the "/docs" endpoint.
    """
    return get_swagger_ui_html(
        openapi_url=f"{request.scope.get('root_path', '')}/openapi.json",
        title="Neurobagel Federation API",
        swagger_favicon_url=favicon_url,
    )


@app.get("/redoc", include_in_schema=False)
def overridden_redoc(request: Request):
    """
    Overrides the Redoc HTML for the "/redoc" endpoint.
    """
    return get_redoc_html(
        openapi_url=f"{request.scope.get('root_path', '')}/openapi.json",
        title="Neurobagel Federation API",
        redoc_favicon_url=favicon_url,
    )


app.include_router(query.router)
app.include_router(subjects.router)
app.include_router(datasets.router)
app.include_router(assessments.router)
app.include_router(diagnoses.router)
app.include_router(pipelines.router)
app.include_router(imaging_modalities.router)
app.include_router(nodes.router)

# Automatically start uvicorn server on execution of main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8000, reload=True)
