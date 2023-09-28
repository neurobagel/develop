"""Main app."""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .api.routers import query

app = FastAPI(default_response_class=ORJSONResponse)

# TODO: bring this back when we spin up the query tool
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=util.parse_origins_as_list(util.ALLOWED_ORIGINS.val),
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.on_event("startup")
# async def allowed_origins_check():
#     """Raises warning if allowed origins environment variable has not been set or is an empty string."""
#     if os.environ.get(util.ALLOWED_ORIGINS.name, "") == "":
#         warnings.warn(
#             f"The API was launched without providing any values for the {util.ALLOWED_ORIGINS.name} environment variable. "
#             "This means that the API will only be accessible from the same origin it is hosted from: https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy. "
#             f"If you want to access the API from tools hosted at other origins such as the Neurobagel query tool, explicitly set the value of {util.ALLOWED_ORIGINS.name} to the origin(s) of these tools (e.g. http://localhost:3000). "
#             "Multiple allowed origins should be separated with spaces in a single string enclosed in quotes. "
#         )


app.include_router(query.router)

# Automatically start uvicorn server on execution of main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8000, reload=True)
