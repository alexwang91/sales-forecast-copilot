import pandas as pd


def build_tree(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grain = frame.loc[:, ["region", "country", "channel", "sku"]].drop_duplicates()
    for row in grain.itertuples(index=False):
        region = row.region
        country = f"{region}/{row.country}"
        channel = f"{country}/{row.channel}"
        sku = f"{channel}/{row.sku}"
        rows.extend([
            {"parent": region, "child": country},
            {"parent": country, "child": channel},
            {"parent": channel, "child": sku},
        ])
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)
