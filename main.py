from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .engine import SplitError, compute_split, net_balances, optimize_settlements, to_paise

app = FastAPI(title="SplitMate API", version="0.1.0")

class SplitReq(BaseModel):
    amount: float = Field(gt=0)
    method: str
    values: dict[str, float | None]

class ExpenseIn(BaseModel):
    title: str
    amount: float = Field(gt=0)
    paid_by: str
    method: str = "equal"
    values: dict[str, float | None]

@app.post("/calc/split")
def split(r: SplitReq):
    try:
        return {u: v / 100 for u, v in compute_split(r.amount, r.method, r.values).items()}
    except SplitError as e:
        raise HTTPException(422, str(e))

@app.post("/calc/settle")
def settle(expenses: list[ExpenseIn]):
    try:
        rows = [{"paid_by": e.paid_by, "amount": to_paise(e.amount),
                 "splits": compute_split(e.amount, e.method, e.values)} for e in expenses]
    except SplitError as e:
        raise HTTPException(422, str(e))
    net = net_balances(rows)
    return {
        "balances": {u: b / 100 for u, b in net.items()},
        "status": {u: ("receive" if b > 0 else "owe" if b < 0 else "settled") for u, b in net.items()},
        "settlements": [{**s, "amount": s["amount"] / 100} for s in optimize_settlements(net)],
    }

@app.get("/health")
def health():
    return {"ok": True}

from pathlib import Path
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "static", html=True), name="static")
