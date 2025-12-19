"""FastAPI backend for AI Research Assistant."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import config
from backend.agent.research_agent import ResearchAgent

# Validate configuration on startup
try:
    config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please set required environment variables in .env file")

app = FastAPI(
    title="AI Research Assistant API",
    description="Autonomous research agent with tool use and report generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = ResearchAgent()


class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    query: str
    generate_pdf: Optional[bool] = False
    use_cache: Optional[bool] = True


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Research Assistant API"
    }


@app.post("/agent/research")
async def research(request: ResearchRequest):
    """Main research endpoint with streaming support.
    
    Args:
        request: Research request with query
        
    Returns:
        Streaming JSON response with research results
    """
    try:
        # Create generator for streaming responses
        def generate():
            for update in agent.research_streaming(
                query=request.query,
                use_cache=request.use_cache
            ):
                yield f"data: {json.dumps(update)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/research/sync")
async def research_sync(request: ResearchRequest):
    """Synchronous research endpoint (non-streaming).
    
    Args:
        request: Research request with query
        
    Returns:
        Complete research results as JSON
    """
    try:
        import asyncio
        # Run research in executor with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(
                    agent.research,
                    request.query,
                    request.use_cache,
                    request.generate_pdf
                ),
                timeout=540.0  # 9 minutes timeout
            )
            return JSONResponse(content=results)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Research request timed out. The query is too complex or the system is overloaded."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

