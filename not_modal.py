from cynde.functional.distributed_cv import train_nested_cv_from_np_modal, cv_stub
import cynde.functional as cf
import os
import polars as pl
from typing import List
import time

def main():
    def booleanize_nodes(df: pl.DataFrame, node_columns : List[str]) -> pl.DataFrame:
        expression= [pl.col(col) > 0 for col in node_columns]
        return df.with_columns(expression)

    def remove_empty_nodes(df: pl.DataFrame, node_columns: List[str]) -> pl.DataFrame:
        zero_cols = [col for col in node_columns if df[col].sum() == 0]
        return df.drop(zero_cols), zero_cols
    # Get the directory above the current directory
    # data_url = r"C:\Users\Tommaso\Documents\Dev\PredCST\python_3_12_1_standard_lib_all_with_counts.parquet"
    data_url = "/Users/tommasofurlanello/Documents/Dev/PredCST/python_3_12_1_standard_lib_all_with_counts.parquet"
    # dataset_path = os.path.join(cache_dir, dataset_name)
    start_time = time.time()
    cynde_dir = os.getenv('CYNDE_DIR')
    mount_dir = os.getenv('MODAL_MOUNT')
    df = pl.read_parquet(data_url)
    df = df.with_row_index()
    print(f"Time to read the dataset: {time.time() - start_time} seconds")
    start_time = time.time()
    node_cols = df.columns[13:]
    df_f = df.filter(pl.col("type") == "function")

    df_fb = booleanize_nodes(df_f, node_cols)
    df_f_ne, empty_cols = remove_empty_nodes(df_fb, node_cols)

    print(f"Time to preprocess the dataset: {time.time() - start_time} seconds")

    models_dict = {"RandomForest": [{"n_estimators": 50, "max_depth": 10}]}
    inputs =[{"numerical":["code_text-embedding-3-small_embedding"]},
            {"numerical":["code_text-embedding-3-large_embedding"]}]

    # Call the train_nested_cv_from_np function with the required arguments
    df_f_ne = cf.check_add_cv_index(df_f_ne)
    target = "If"
    print(f"df_f_ne shape: {df_f_ne.shape}, starting training")
    # results,pred=train_nested_cv_from_np_modal(df = df_f_ne,
    #                  cv_type=("stratified","stratified"),
    #                  mount_dir=mount_dir,
    #                  inputs=inputs,
    #                  models=models_dict,
    #                  group_outer=[target],
    #                  k_outer = 5,
    #                  group_inner=[target],
    #                  k_inner = 5,
    #                  r_outer=1,
    #                  r_inner=1,
    #                  skip_class=False,
    #                  target_column = target)# 

    results = pl.DataFrame(schema=cf.RESULTS_SCHEMA)
    print("Training completed successfully!")
    summary = cf.results_summary(results)
    print(summary)
    cf.save_results(df=df_f_ne,results_df=results,pred_df=pred,save_name="test",base_path=cynde_dir)



if __name__ == "__main__":
    main()
    