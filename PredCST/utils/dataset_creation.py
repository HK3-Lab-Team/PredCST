import polars as pl
import math

def create_dataset(df: pl.DataFrame, ds_size, target_node, node_list):
    
    df_ = df.drop(['type', 'code', 'type',
        'cst_tree',
        'file_name',
        'modules',
        'version',
        'license',
        'code_token_len',
        'cst_tree_token_len',
        'code_text-embedding-3-small_embedding',
        'code_text-embedding-3-large_embedding',
        'cst_tree_text-embedding-3-small_embedding'])
    for column in df_.columns:
        if isinstance(df_[column].dtype,pl.Int64) and column != 'index':
            df_ = df_.with_columns((pl.col(column) > 0).alias(column))

    fifty_percent = ds_size/2
    
    target_rows = df_.filter(pl.col(target_node)==True)
    if target_rows.shape[0] >fifty_percent:
        target_rows = target_rows.sample(fifty_percent)

    other = df_.filter(pl.col(target_node)==False)

    node_list = node_list.filter(pl.col("column") != target_node)
    k_other = node_list.select(pl.col("column")).unique()
    k = len(k_other)
    per_sample = math.floor(fifty_percent/k)

    without = []
    for o_node in k_other['column'].to_list():
        temp = other.filter(pl.col(o_node)==True)
        try:
            temp = temp.sample(per_sample)
            without.append(temp)
        except:
            without.append(temp)
            continue
    train = pl.concat([target_rows] + without)
    test = df_.join(train, on="index", how="anti")
    train_indexes = train['index'].to_list()
    test_indexes = test['index'].to_list()
    train = df.filter(pl.col("index").is_in(train_indexes))
    test = df.filter(pl.col("index").is_in(test_indexes))

    return train, test

