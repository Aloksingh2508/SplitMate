# SplitMate – Smart Group Expense & Money Management
live link- https://aloksingh2508.github.io/SplitMate/
## Status
Milestone 1 (done): calculation engine + FastAPI calc endpoints + tests.
- Equal / exact / percentage / shares splits, paise-accurate (no rounding drift)
- Validation (negative amounts, bad percentages, mismatched exact totals)
- Net balance = paid − share; balances always sum to 0
- Settlement optimisation (≤ n−1 payments)

## Run
    cd backend && pip install -r requirements.txt
    uvicorn app.main:app --reload     # docs at /docs
    pytest

## Next milestones
2. PostgreSQL + SQLAlchemy models + Alembic (User, Group, GroupMember, Expense, ExpenseSplit, Settlement, RecurringExpense)
3. JWT auth, groups/members/expenses/settlement CRUD with group-membership authorization
4. React + TS + Tailwind + shadcn/ui frontend (dashboard, add expense, settle up, dark mode, mobile nav)
5. Analytics (Recharts), notifications, recurring expenses, CSV/PDF export, SplitMate AI
