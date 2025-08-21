"""
Suna AI Backend Main Application

This is the main entry point for the Suna AI backend server.
It sets up the FastAPI application with all necessary routes and middleware.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routers
from api import router as main_router
from agent.api import router as agent_router
from sandbox.api import router as sandbox_router
from flags.api import router as flags_router
from knowledge_base.api import router as kb_router
from mcp_local.api import router as mcp_router
from scheduling.api import router as scheduling_router
from webhooks.api import router as webhooks_router
from workflows.api import router as workflows_router
from services.email_api import router as email_router

# Initialize FastAPI app
app = FastAPI(
    title="Suna AI Backend",
    description="Advanced AI Assistant Backend with Enhanced Capabilities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(main_router, prefix="/api")
app.include_router(agent_router, prefix="/api/agent")
app.include_router(sandbox_router, prefix="/api/sandbox")
app.include_router(flags_router, prefix="/api/flags")
app.include_router(kb_router, prefix="/api/knowledge-base")
app.include_router(mcp_router, prefix="/api/mcp")
app.include_router(scheduling_router, prefix="/api/scheduling")
app.include_router(webhooks_router, prefix="/api/webhooks")
app.include_router(workflows_router, prefix="/api/workflows")
app.include_router(email_router, prefix="/api/email")

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Suna AI Backend - Advanced AI Assistant",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Advanced Cognitive Capabilities",
            "Specialized Intelligence",
            "Natural Interaction",
            "Multi-modal Processing",
            "Professional Expertise",
            "Creative Problem Solving",
            "Adaptive Learning",
            "Ethical AI Framework"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "suna-ai-backend"}

@app.get("/api/capabilities")
async def get_capabilities():
    """Get information about available AI capabilities."""
    return {
        "cognitive_capabilities": [
            "advanced_reasoning",
            "memory_management", 
            "adaptive_learning",
            "knowledge_integration",
            "meta_cognitive_analysis"
        ],
        "specialized_intelligence": [
            "creative_problem_solving",
            "advanced_decision_making",
            "professional_expertise",
            "quality_control_analysis",
            "systems_thinking_analysis"
        ],
        "interaction_features": [
            "natural_conversation",
            "advanced_task_management",
            "user_adaptation_learning",
            "multi_modal_communication"
        ],
        "enhancement_tools": [
            "sentiment_analysis",
            "entity_extraction",
            "trend_prediction",
            "image_analysis"
        ],
        "data_processing": [
            "advanced_analytics",
            "machine_learning",
            "statistical_analysis",
            "data_visualization"
        ],
        "integration": [
            "api_connectivity",
            "database_operations",
            "cloud_services",
            "workflow_automation"
        ],
        "security": [
            "data_encryption",
            "access_control",
            "audit_logging",
            "compliance_monitoring"
        ],
        "monitoring": [
            "system_health",
            "performance_analytics",
            "maintenance_scheduling",
            "alert_management"
        ]
    }

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Suna AI Backend Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🧠 Advanced AI Capabilities: ENABLED")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
