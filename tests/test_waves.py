import pytest
from waves import plan_waves


def test_simple_chain():
    deps = {"web": ["api"], "api": ["db"], "db": []}
    assert plan_waves(deps) == [["db"], ["api"], ["web"]]


def test_parallel_apps_share_a_wave():
    deps = {"a": ["db"], "b": ["db"], "db": []}
    assert plan_waves(deps) == [["db"], ["a", "b"]]


def test_undeclared_dependency_is_included():
    assert plan_waves({"web": ["api"]}) == [["api"], ["web"]]


def test_cycle_raises():
    with pytest.raises(ValueError):
        plan_waves({"a": ["b"], "b": ["a"]})