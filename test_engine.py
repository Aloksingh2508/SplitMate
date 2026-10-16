import pytest
from app.engine import *

def test_equal_exact_sum():
    s = compute_split(100, "equal", {"a": None, "b": None, "c": None})
    assert sum(s.values()) == 10000 and sorted(s.values()) == [3333, 3333, 3334]

def test_methods():
    assert compute_split(2000, "exact", {"a": 800, "b": 500, "c": 400, "d": 300})["a"] == 80000
    assert compute_split(2000, "percentage", {"a": 40, "b": 20, "c": 20, "d": 20})["a"] == 80000
    assert compute_split(400, "shares", {"a": 2, "b": 1, "c": 1})["a"] == 20000

def test_validation():
    with pytest.raises(SplitError): compute_split(100, "exact", {"a": 50, "b": 40})
    with pytest.raises(SplitError): compute_split(100, "percentage", {"a": 50, "b": 40})
    with pytest.raises(SplitError): compute_split(-5, "equal", {"a": None})

def test_rent_example():
    sp = compute_split(4000, "equal", {u: None for u in ["Alok", "Rahul", "Aman", "Rohit"]})
    net = net_balances([{"paid_by": "Alok", "amount": 400000, "splits": sp}])
    assert net["Alok"] == 300000 and net["Rahul"] == -100000
    assert len(optimize_settlements(net)) == 3

def test_optimization():
    net = {"B": 800, "C": 200, "A": -500, "D": -500}
    assert sum(s["amount"] for s in optimize_settlements(net)) == 1000
    assert len(optimize_settlements({"A": -1000, "B": 800, "C": 200})) == 2
