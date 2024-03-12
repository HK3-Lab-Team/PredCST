import polars as pl
import math

def create_dataset(df, ds_size, target_node, node_list):
    df = df.with_columns(
        pl.when(df[target_node].gt(0))
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("target_node_exists")
    )
    fifty_percent = ds_size/2
    
    target_rows = df.filter(pl.col("target_node_exists")==True)
    if target_rows.shape[0] >fifty_percent:
        target_rows = target_rows.sample(fifty_percent)

    other = df.filter(pl.col("target_node_exists")==False)

    node_list = node_list.filter(pl.col("column") != target_node)
    k_other = node_list.select(pl.col("column")).unique()
    k = len(k_other)
    per_sample = math.floor(fifty_percent/k)

    without = []
    for o_node in k_other['column'].to_list():
        temp = other.with_columns(
                pl.when(other[o_node].gt(0))
                .then(pl.lit(True))
                .otherwise(pl.lit(False))
                .alias("other_node_exists")
            ).filter(pl.col("other_node_exists")==True).drop("other_node_exists")
        try:
            temp = temp.sample(per_sample)
            without.append(temp)
        except:
            without.append(temp)
            continue
    train = pl.concat([target_rows] + without)
    test = df.join(train, on="code", how="anti")
    return train, test

