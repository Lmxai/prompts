import logging
from asyncio import sleep

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status
from app.models.query_model import QueryRequest, QueryAgentResponse
from app.services.chain_service import ChainService
from app.utils.web_socket_connection_manager import ConnectionManager

router = APIRouter(tags=["Agent Service"])
manager = ConnectionManager()  # WebSocket bağlantı yöneticisi


@router.post(path="/llm/query_agent",
             response_model=QueryAgentResponse,
             summary="Query Agent to LLM model",
             description="Query to LLM model with ChainServiceV3")
async def handle_query_v3(query: QueryRequest):
    """
    Query Router:
    - Başlatılan sorgu sırasında WebSocket bağlantısı açılır.
    - Mesaj gönderilmez, bu ToolExecution tarafından yapılır.
    """
    try:
        # WebSocket bağlantısının hazır olduğundan emin olun
        if not manager.active_connections:
            await manager.connect_websocket()
            logging.info("WebSocket connections initialized.")

        chain_service = ChainService()
        results, errors = await chain_service.execute_workflow(query=query)

        if errors:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(errors))

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(results))
        await sleep(5)
        await manager.close_connections()


    except ValidationError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"details": e.errors()})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})
