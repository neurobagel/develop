"""Main app."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse

from .api import utility as util
from .api.routers import assessments, diagnoses, nodes, pipelines, query
from .api.security import check_client_id

logger = logging.getLogger("nb-f-API")
stdout_handler = logging.StreamHandler()

logger.setLevel(logging.INFO)
logger.addHandler(stdout_handler)

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
def root():
    """
    Display a welcome message and a link to the API documentation.
    """
    return """
    <html>
        <body>
            <h1>Welcome to the Neurobagel Federation API!</h1>
            <p>Please visit the <a href="/docs">documentation</a> to view available API endpoints.</p>
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
def overridden_swagger():
    """
    Overrides the Swagger UI HTML for the "/docs" endpoint.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Neurobagel Federation API",
        swagger_favicon_url=favicon_url,
    )


@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    """
    Overrides the Redoc HTML for the "/redoc" endpoint.
    """
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Neurobagel Federation API",
        redoc_favicon_url=favicon_url,
    )


app.include_router(query.router)
app.include_router(assessments.router)
app.include_router(diagnoses.router)
app.include_router(pipelines.router)
app.include_router(nodes.router)

# Automatically start uvicorn server on execution of main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8000, reload=True)
