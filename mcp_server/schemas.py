from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EmptyArgs(BaseModel):
    pass


class TableCountsArgs(BaseModel):
    tables: list[str] = Field(default_factory=list)


class ReadonlyQueryArgs(BaseModel):
    sql: str
    params: list[Any] = Field(default_factory=list)
    limit: int = 100


class JobListArgs(BaseModel):
    job_key: str = ""
    status: str = ""
    unresolved_only: bool = True
    limit: int = 50


class WriteRequest(BaseModel):
    actor: str = ""
    reason: str = ""
    idempotency_key: str = ""
    dry_run: bool = True
    confirm: bool = False


class JobTriggerArgs(WriteRequest):
    job_key: str


class FunnelScoreAlignArgs(WriteRequest):
    score_date: str = ""
    max_candidates: int = 10000


class FunnelReviewRefreshArgs(WriteRequest):
    horizon_days: int = 5
    limit: int = 200


class DecisionSnapshotArgs(WriteRequest):
    job_key: str = "decision_daily_snapshot"


class ReconcilePositionsArgs(WriteRequest):
    limit: int = 500


class PortfolioOrderReviewsArgs(WriteRequest):
    horizon_days: int = 5
    limit: int = 200
    order_status: str = "executed"


class AgentStartRunArgs(BaseModel):
    agent_key: str = "funnel_progress_agent"
    mode: str = "auto"
    trigger_source: str = "mcp"
    actor: str = "mcp"
    goal: dict[str, Any] = Field(default_factory=dict)
    schedule_key: str = ""
    dedupe: bool = True


class AgentGetRunArgs(BaseModel):
    run_id: str


class AgentListRunsArgs(BaseModel):
    agent_key: str = ""
    status: str = ""
    limit: int = 50


class AgentCancelRunArgs(BaseModel):
    run_id: str
    actor: str = "mcp"
    reason: str = "mcp cancel"


class AgentApprovalArgs(BaseModel):
    run_id: str
    actor: str = "mcp"
    reason: str = ""
    idempotency_key: str = ""
