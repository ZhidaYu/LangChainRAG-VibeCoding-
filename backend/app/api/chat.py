"""Chat API: SSE streaming Q&A endpoint."""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatQueryRequest
from app.services.conversation_service import ConversationService
from app.services.rag_service import RagService
from app.utils.cache import query_cache

router = APIRouter()


@router.post("/query")
async def chat_query(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a question and receive a streaming RAG answer via SSE."""
    conv_svc = ConversationService(db)
    rag_svc = RagService()

    # Check cache
    cached = query_cache.get(req.question)
    if cached:
        async def cache_stream():
            yield f"data: {json.dumps({'type': 'sources', 'sources': cached['sources']}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'content': cached['answer']}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return StreamingResponse(cache_stream(), media_type="text/event-stream")

    # Resolve conversation
    conv_id = req.conversation_id
    if not conv_id:
        conv = await conv_svc.create_conversation(current_user.id)
        conv_id = conv.id
    else:
        conv = await conv_svc.get_conversation(conv_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="对话不存在")

    # Save user message
    await conv_svc.save_message(conv_id, "user", req.question)

    # Load history
    history = await conv_svc.get_messages(conv_id)

    # Collect full answer and sources for persistence
    full_answer = ""
    sources_meta = []

    async def event_stream():
        nonlocal full_answer, sources_meta
        try:
            async for event in rag_svc.query_stream(req.question, history):
                # Extract sources when they arrive
                if '"type": "sources"' in event:
                    data_str = event.replace("data: ", "").strip()
                    data = json.loads(data_str)
                    sources_meta = data.get("sources", [])
                # Track answer tokens
                elif '"type": "token"' in event:
                    data_str = event.replace("data: ", "").strip()
                    data = json.loads(data_str)
                    full_answer += data.get("content", "")
                elif '"type": "done"' in event:
                    # Save assistant message before sending done
                    cited = rag_svc.extract_citations(full_answer, sources_meta)
                    await conv_svc.save_message(
                        conv_id, "assistant", full_answer,
                        sources=json.dumps(cited, ensure_ascii=False),
                    )
                    # Update conversation title if first exchange
                    if len(history) <= 2:
                        await conv_svc.update_conversation_title(
                            conv_id, req.question[:20]
                        )
                    # Cache result
                    query_cache.set(req.question, {
                        "answer": full_answer,
                        "sources": sources_meta,
                    })
                yield event
        except Exception as e:
            error_event = json.dumps(
                {"type": "error", "detail": str(e)}, ensure_ascii=False
            )
            yield f"data: {error_event}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
