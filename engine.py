"""SplitMate calculation engine. All money is handled in integer paise (no float drift)."""
from decimal import Decimal, ROUND_HALF_UP

class SplitError(ValueError):
    pass

def to_paise(x) -> int:
    return int((Decimal(str(x)) * 100).to_integral_value(ROUND_HALF_UP))

def _distribute(total: int, weights: list[int]) -> list[int]:
    """Split total proportionally; leftover paise go to largest remainders so the sum is exact."""
    tw = sum(weights)
    if tw <= 0:
        raise SplitError("Total weight must be positive")
    base = [total * w // tw for w in weights]
    order = sorted(range(len(weights)), key=lambda i: -((total * weights[i]) % tw))
    for i in order[: total - sum(base)]:
        base[i] += 1
    return base

def compute_split(amount, method: str, values: dict[str, float | None]) -> dict[str, int]:
    """values: user -> (ignored for equal | exact amount | percentage | share count)."""
    total = to_paise(amount)
    if total <= 0:
        raise SplitError("Amount must be positive")
    if not values:
        raise SplitError("At least one participant is required")
    users = list(values)
    if method == "equal":
        parts = _distribute(total, [1] * len(users))
    elif method == "shares":
        w = [int(values[u] or 0) for u in users]
        if any(x <= 0 for x in w):
            raise SplitError("Shares must be positive integers")
        parts = _distribute(total, w)
    elif method == "percentage":
        p = [to_paise(values[u] or 0) for u in users]  # percent in hundredths
        if any(x < 0 for x in p) or sum(p) != 10000:
            raise SplitError("Percentages must be non-negative and total 100")
        parts = _distribute(total, p)
    elif method == "exact":
        parts = [to_paise(values[u] or 0) for u in users]
        if any(x < 0 for x in parts):
            raise SplitError("Amounts cannot be negative")
        if sum(parts) != total:
            raise SplitError(f"Split total {sum(parts)/100:.2f} does not match expense {total/100:.2f}")
    else:
        raise SplitError(f"Unknown split method: {method}")
    return dict(zip(users, parts))

def net_balances(expenses: list[dict]) -> dict[str, int]:
    """expenses: [{paid_by, amount (paise), splits: {user: paise}}]. Net = paid - share. Sums to 0."""
    net: dict[str, int] = {}
    for e in expenses:
        net[e["paid_by"]] = net.get(e["paid_by"], 0) + e["amount"]
        for u, s in e["splits"].items():
            net[u] = net.get(u, 0) - s
    assert sum(net.values()) == 0, "Balances must sum to zero"
    return net

def optimize_settlements(net: dict[str, int]) -> list[dict]:
    """Greedy min-cash-flow: match biggest debtor with biggest creditor. Gives at most n-1 payments."""
    cred = sorted([[u, b] for u, b in net.items() if b > 0], key=lambda x: -x[1])
    debt = sorted([[u, -b] for u, b in net.items() if b < 0], key=lambda x: -x[1])
    out, i, j = [], 0, 0
    while i < len(debt) and j < len(cred):
        pay = min(debt[i][1], cred[j][1])
        out.append({"from": debt[i][0], "to": cred[j][0], "amount": pay})
        debt[i][1] -= pay
        cred[j][1] -= pay
        if debt[i][1] == 0: i += 1
        if cred[j][1] == 0: j += 1
        debt.sort(key=lambda x: -x[1]) if False else None
    return out
