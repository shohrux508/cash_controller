"""REST API v1: Transaction endpoints for future WebApp."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.deps import get_session
from app.services.transaction_service import TransactionService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/transactions", tags=["transactions"])

tx_service = TransactionService()


class TransactionCreate(BaseModel):
    """Request body for creating a transaction."""

    user_id: int
    amount: int
    type: str  # "income" | "expense"
    description: str = ""
    category_id: int | None = None


class TransactionOut(BaseModel):
    """Response schema for a transaction."""

    id: int
    user_id: int
    category_id: int | None
    amount: int
    type: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryOut(BaseModel):
    """Response schema for period summary."""

    income: int
    expense: int
    balance: int
    by_category: list[dict[str, object]]


@router.get("/", response_model=list[TransactionOut])
async def list_transactions(
    user_id: int = Query(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionOut]:
    """Get list of transactions for a user."""
    transactions = await tx_service.get_transactions(session, user_id, limit=limit, offset=offset)
    return [TransactionOut.model_validate(tx) for tx in transactions]


@router.post("/", response_model=TransactionOut, status_code=201)
async def create_transaction(
    body: TransactionCreate,
    session: AsyncSession = Depends(get_session),
) -> TransactionOut:
    """Create a new transaction."""
    tx = await tx_service.create_transaction(
        session=session,
        user_id=body.user_id,
        amount=body.amount,
        tx_type=body.type,
        description=body.description,
        category_id=body.category_id,
    )
    return TransactionOut.model_validate(tx)


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: int,
    user_id: int = Query(..., description="User ID for ownership check"),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a transaction."""
    deleted = await tx_service.delete_transaction(session, transaction_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.get("/summary", response_model=SummaryOut)
async def get_summary(
    user_id: int = Query(..., description="User ID"),
    start_date: datetime = Query(..., description="Period start"),
    end_date: datetime = Query(..., description="Period end"),
    session: AsyncSession = Depends(get_session),
) -> SummaryOut:
    """Get financial summary for a period."""
    summary = await tx_service.get_period_summary(session, user_id, start_date, end_date)
    return SummaryOut(**summary)
