from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Minimal server is running"}

@app.post("/api/agent/initiate")
async def test_agent_initiate():
    return {"status": "success", "message": "Sandbox bypass working", "sandbox_id": "bypass-mode"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)