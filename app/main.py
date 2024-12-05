import webbrowser

import uvicorn
from fastapi import FastAPI

from app.api.query_router import router as query_router
from app.api.websocket_router import router as websocket_router
from app.api.prompt_manager_router import router as prompt_manager_router

app = FastAPI(title="LLM API", docs_url="/api/docs", redoc_url="/api/redoc", )

app.include_router(query_router)
app.include_router(prompt_manager_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="localhost", port=5201, reload=True, log_level="info")
    webbrowser.open("http://localhost:5201/api/docs")
