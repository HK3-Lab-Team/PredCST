import os
from typing import List, Optional

import libcst as cst
import polars as pl


from PredCST.utils.pythonparser import (
    extract_values_python,

)
from PredCST.processors.parsers.visitors.node_type_counters import *
from PredCST.processors.parsers.visitors.operator_counters import *


class CodeFrame():
    def __init__(
        self,
        df: pl.DataFrame,
        context_columns: Optional[List[str]] = None,
        name: str = "code_frame",
        save_path: Optional[str] = "./storage",
    ):

        self.df = df
        self.context_columns = context_columns
        self.name = name
        self.save_path = save_path
        self.save_dir = f"{self.save_path}/{self.name}"


    def __getattr__(self, name: str):
        if "df" in self.__dict__:
            return getattr(self.df.lazy(), name)
        raise AttributeError(
            f"{self.__class__.__name__} object has no attribute {name}"
        )

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
        new_column_prefix: Optional[str] = None,
    ):
        # Ensure the visitor_class is a subclass of PythonCodeVisitor
        if not issubclass(visitor_class, cst.CSTVisitor):
            raise TypeError("visitor_class must be a subclass of PythonCodeVisitor")

        # Iterate over the specified column
        new_values = []
        for code in self.df[column_name]:
            # Create a visitor and apply it to the code
            visitor = visitor_class(code)
            new_value = visitor.collect()
            new_values.append(new_value)
        # Generate new column
        new_column_name = f"{column_name}_{new_column_prefix}|{visitor_class.__name__}"
        new_series = pl.Series(new_column_name, new_values)
        self.df = self.df.with_columns(new_series)

        return self

    def count_node_types(self, column_name: str, new_column_prefix: str = "node_count"):
        for node_type_counter in NODETYPE_COUNTERS:
            self.apply_visitor_to_column(
                column_name, globals()[node_type_counter], new_column_prefix
            )
        return self

    def count_operators(
        self, column_name: str, new_column_prefix: str = "operator_count"
    ):
        for operator_counter in OPERATOR_COUNTERS:
            self.apply_visitor_to_column(
                column_name, globals()[operator_counter], new_column_prefix
            )
        return self

    @classmethod
    def from_python(
        cls,
        directory_path: str,
        value_column: str,
        remove_docstrings: bool = False,
        resolution: str = "both",
        context_columns: Optional[List[str]] = None,
        name: str = "code_frame",
        save_path: Optional[str] = "./storage",

    ) -> "CodeFrame":
        values, context = extract_values_python(
            directory_path,remove_docstrings, resolution
        )
        # convert retrieved data to polars dataframe
        df = pl.DataFrame({value_column: values})
        context_df = pl.DataFrame(context)
        # merge context columns with dataframe
        df = pl.concat([df, context_df], how="horizontal")
        kwargs = {
            "context_columns": context_columns,
            "name": name,
            "save_path": save_path,
        }
        return cls(df, **kwargs)


