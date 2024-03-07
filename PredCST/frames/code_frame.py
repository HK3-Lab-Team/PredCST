import os
from typing import List, Optional

import libcst as cst
import polars as pl
from tqdm import tqdm

from PredCST.processors.parsers.python_parser import (
    extract_values_python,
)
from PredCST.processors.parsers.visitors.node_type_counters import *
from PredCST.processors.parsers.visitors.operator_counters import *


class CodeFrame:
    def __init__(
        self,
        df: pl.DataFrame,
        value_column: str = "code",
        name: str = "code_frame",
        save_path: Optional[str] = "./storage",
        resolution: str = "module"
    ):

        self.df = df
        self.value_column = value_column
        self.name = name
        self.save_path = save_path
        self.save_dir = f"{self.save_path}/{self.name}"
        self.resolution = resolution
        if self.resolution == "all":
            self.code_triage()

    def __getattr__(self, name: str):
        if "df" in self.__dict__:
            return getattr(self.df.lazy(), name)
        raise AttributeError(
            f"{self.__class__.__name__} object has no attribute {name}"
        )
    def code_triage(self):
        self.modules = self.df.filter(pl.col("type") == 'module')
        self.functions = self.df.filter(pl.col("type") == 'function')
        self.classes = self.df.filter(pl.col("type") == 'class')


    def save(self):
        # create dir in storage if not exists
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.full_save_path = f"{self.save_path}/{self.name}/{self.name}.parquet"
        self.df.write_parquet(self.full_save_path)

    @classmethod
    def load(cls, frame_path: str, name: str):
        ## ReWrite
        df = pl.read_parquet(f"{frame_path}/{name}.parquet")
        return cls(
            df=df,
            name=name,
            save_path=f"{frame_path}/{name}.parquet",
        )

    def apply_visitor_to_column(
        self,
        column_name: str,
        visitor_class: type,
        df:pl.DataFrame,
        new_column_prefix: Optional[str] = None
         
    ):
        # Ensure the visitor_class is a subclass of PythonCodeVisitor
        if not issubclass(visitor_class, cst.CSTVisitor):
            raise TypeError("visitor_class must be a subclass of PythonCodeVisitor")

        # Iterate over the specified column
        new_values = []
        for code in tqdm(df[column_name], desc="Processing codes"):
            # Create a visitor and apply it to the code
            visitor = visitor_class(code)
            new_value = visitor.collect()
            new_values.append(new_value)
        # Generate new column
        new_column_name = f"{column_name}_{new_column_prefix}"
        new_series = pl.Series(new_column_name, new_values)
        df = df.with_columns(new_series)

        return self

    def count_node_types(self, column_name: str, new_column_prefix: str = "node_count", resolution:str="all"):
        match resolution:
            case "all":
                df_used = self.df
            case "modules":
                df_used = self.modules
            case "functions":
                df_used = self.functions
            case "classes":
                df_used = self.classes
            case _:
                raise ValueError(f"Unknown resolution: {resolution}")

        self.apply_visitor_to_column(
            column_name, NodeTypeCounter, new_column_prefix
        )
        new_column_name = f"{column_name}_{new_column_prefix}"
        df_used = df_used.unnest(new_column_name)
        return df_used

    def count_operators(
        self, column_name: str, new_column_prefix: str = "operator_count", resolution:str="all"
    ):
        match resolution:
            case "all":
                df_used = self.df
            case "modules":
                df_used = self.modules
            case "functions":
                df_used = self.functions
            case "classes":
                df_used = self.classes
            case _:
                raise ValueError(f"Unknown resolution: {resolution}")

        self.apply_visitor_to_column(
            column_name, UnifiedOperatorCounter, new_column_prefix
        )
        new_column_name = f"{column_name}_{new_column_prefix}"
        df_used = df_used.unnest(new_column_name)
        return df_used


    @classmethod
    def from_python(
        cls,
        directory_path: str,
        value_column: str,
        remove_docstrings: bool = False,
        lint_code: bool = False,
        resolution: str = "module",

        name: str = "code_frame",
        save_path: Optional[str] = "./storage",
    ) -> "CodeFrame":
        values = extract_values_python(
            directory_path, remove_docstrings, lint_code, resolution
        )
        # convert retrieved data to polars dataframe
        df = pl.DataFrame({value_column: values}).unnest(value_column)
        kwargs = {
            "value_column": value_column,
            "name": name,
            "save_path": save_path,
            "resolution": resolution
        }
        return cls(df, **kwargs)
