import pandas as pd

from src.hierarchy.tree import build_tree


def test_build_tree_returns_parent_child_rows():
    frame = pd.DataFrame([
        {"region": "CEE", "country": "HU", "channel": "Retail", "sku": "S1"},
        {"region": "CEE", "country": "HU", "channel": "Online", "sku": "S2"},
    ])

    out = build_tree(frame)

    assert {"parent", "child"}.issubset(out.columns)
    assert {"CEE", "CEE/HU", "CEE/HU/Retail", "CEE/HU/Online"}.issubset(set(out["parent"]))
    assert {"CEE/HU", "CEE/HU/Retail", "CEE/HU/Retail/S1", "CEE/HU/Online/S2"}.issubset(set(out["child"]))
