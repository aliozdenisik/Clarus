"""SSE Streaming API routes for real-time LLM responses."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user, check_rate_limit
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG


router = APIRouter()


async def generate_sse_events(data_generator) -> AsyncGenerator[str, None]:
    """Convert data generator to SSE format."""
    try:
        for chunk in data_generator:
            if chunk:
                # SSE format: data: {json}\n\n
                yield f"data: {json.dumps({'token': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.get("/search")
async def stream_search(
    q: str = Query(..., description="Arama sorgusu"),
    source: str = Query(default="quran", description="quran veya bible"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream search results with AI answer generation."""
    await check_rate_limit(current_user, db)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=q,
        search_type=f"stream_search_{source}"
    )
    db.add(history)
    await db.commit()
    
    async def generate():
        rag = UltimateRAG()
        
        # First, send search status
        yield f"data: {json.dumps({'status': 'searching', 'message': 'Aranıyor...'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Perform search
        if source == "quran":
            results = rag.search_quran(q, top_k=10)
        else:
            results = rag.search_bible(q, top_k=10)
        
        # Send results count
        yield f"data: {json.dumps({'status': 'found', 'count': len(results)})}\n\n"
        await asyncio.sleep(0.1)
        
        # Send "generating" status
        yield f"data: {json.dumps({'status': 'generating', 'message': 'Yanıt oluşturuluyor...'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Generate answer (simulated streaming - actual LLM may not stream)
        try:
            if source == "quran":
                answer = rag.ask_quran(q)
            else:
                answer = rag.ask_bible(q)
            
            # Stream the answer token by token
            answer_text = answer.get("answer", "")
            words = answer_text.split()
            
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # 30ms per word
            
            # Send citations
            yield f"data: {json.dumps({'citations': answer.get('citations', [])})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/compare")
async def stream_compare(
    topic: str = Query(..., description="Karşılaştırma konusu"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream comparative analysis with multi-agent output."""
    await check_rate_limit(current_user, db)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=topic,
        search_type="stream_compare"
    )
    db.add(history)
    await db.commit()
    
    async def generate():
        rag = ComparativeRAG()
        
        # Status updates
        yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Metinler analiz ediliyor...'})}\n\n"
        await asyncio.sleep(0.1)
        
        try:
            result = rag.compare_multi_agent(topic)
            analysis = result.get("analysis", "")
            
            # Stream section by section
            sections = analysis.split("##")
            
            for section in sections:
                if section.strip():
                    # Stream each word
                    words = section.split()
                    yield f"data: {json.dumps({'token': '## '})}\n\n"
                    
                    for word in words:
                        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                        await asyncio.sleep(0.02)
                    
                    yield f"data: {json.dumps({'token': '\\n\\n'})}\n\n"
            
            # Send metadata
            yield f"data: {json.dumps({'confidence': result.get('confidence', 0), 'latency': result.get('latency', 0)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
