from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import init_db
from app.api import uploads, reconciliation, exceptions, rules, reports, qa, health, costs

app = FastAPI(
    title="Agentic AI Finance Controller",
    description="Finance operations platform for multi-source reconciliation, profit engine, unknown pattern detection, and human governance.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database schema on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(uploads.router, prefix="/api", tags=["Batches & Uploads"])
app.include_router(reconciliation.router, prefix="/api", tags=["Reconciliation"])
app.include_router(exceptions.router, prefix="/api", tags=["Exceptions Queue"])
app.include_router(rules.router, prefix="/api", tags=["Rule Registry"])
app.include_router(costs.router, prefix="/api", tags=["SKU Unit Costs"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(qa.router, prefix="/api", tags=["Finance Q&A"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
