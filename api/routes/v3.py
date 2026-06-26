"""v3 agentic and integration endpoints."""

from fastapi import APIRouter, HTTPException

from api.schemas.request import DigestGenerateRequest, FeedbackRequest, IntegrationSettingsRequest, MemoryRequest
from src.automation.scheduler import JobStore
from src.agents.digest_agent import DigestAgent
from src.integrations.store import IntegrationStore
from src.integrations.sync_engine import IntegrationSyncEngine
from src.storage.v3_store import DigestStore, EntityStore, FeedbackStore, InsightStore, MemoryStore

router = APIRouter(prefix="/v1", tags=["v3"])


@router.post("/digest/generate")
async def generate_digest(request: DigestGenerateRequest):
    return await DigestAgent().generate(request.type, request.period_start, request.period_end)


@router.get("/digest/{digest_type}/{date}")
def get_digest(digest_type: str, date: str):
    digest = DigestStore().get(digest_type, date)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@router.get("/insights")
def insights():
    return {"insights": InsightStore().pending()}


@router.post("/insights/{insight_id}/dismiss")
def dismiss_insight(insight_id: int):
    InsightStore().dismiss(insight_id)
    return {"status": "dismissed", "id": insight_id}


@router.get("/entities")
def entities():
    return {"entities": EntityStore().list()}


@router.get("/entities/{entity_id}")
def entity(entity_id: int):
    result = EntityStore().get(entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found")
    return result


@router.get("/memory")
def memory():
    return {"memories": MemoryStore().list()}


@router.post("/memory")
def add_memory(request: MemoryRequest):
    return MemoryStore().add(request.type, request.key, request.value, request.confidence, request.source)


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: int):
    MemoryStore().delete(memory_id)
    return {"status": "deleted", "id": memory_id}


@router.get("/feedback/stats")
def feedback_stats():
    return FeedbackStore().stats()


@router.post("/feedback")
def add_feedback(request: FeedbackRequest):
    return FeedbackStore().add(request.conversation_id, request.rating, request.comment)


@router.get("/integrations")
def integrations():
    return {"integrations": IntegrationStore().list()}


@router.post("/integrations/{connector_id}/connect")
def connect_integration(connector_id: str):
    store = IntegrationStore()
    if not store.get(connector_id):
        raise HTTPException(status_code=404, detail="Unknown integration")
    store.set_status(connector_id, "needs_configuration")
    return {"id": connector_id, "status": "needs_configuration"}


@router.post("/integrations/{connector_id}/disconnect")
def disconnect_integration(connector_id: str):
    IntegrationStore().set_status(connector_id, "disconnected")
    return {"id": connector_id, "status": "disconnected"}


@router.post("/integrations/{connector_id}/sync")
def sync_integration(connector_id: str):
    return IntegrationSyncEngine().sync(connector_id)


@router.get("/integrations/{connector_id}/status")
def integration_status(connector_id: str):
    store = IntegrationStore()
    integration = store.get(connector_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Unknown integration")
    return {"integration": integration, "sync_log": store.logs(connector_id)}


@router.put("/integrations/{connector_id}/settings")
def integration_settings(connector_id: str, request: IntegrationSettingsRequest):
    return IntegrationStore().update_settings(connector_id, request.settings)


@router.get("/timeline/{date}")
def timeline(date: str):
    return {
        "date": date,
        "summary": "Timeline reconstruction is ready for connected sources. Sync integrations, then query by date for full synthesis.",
        "sources": [],
    }


@router.get("/correlations")
def correlations():
    return {"correlations": [], "message": "At least 30 days of daily metrics are required before correlations are reported."}


@router.get("/jobs")
def jobs():
    return {"jobs": JobStore().list()}
