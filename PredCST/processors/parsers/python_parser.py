import subprocess
from typing import List, Dict, Any
import libcst as cst
from PredCST.processors.os_processor import OsProcessor
class FunctionAndClassVisitor(cst.CSTVisitor):
    def __init__(self):
        self.function_source_codes = []
        self.function_nodes = []
        self.function_count = 0
        self.class_source_codes = []
        self.class_nodes = []
        self.class_count = 0
        self.filename_map = []
        self.full_source_list = []
        self.full_node_list = []

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """This method is called for every FunctionDef node in the tree.
        and it does the following:
        1. Gets the source code for the node
        2. Adds the node to the list of function nodes
        3. Adds the source code to the list of function source codes
        4. Increments the function count
        """
        function_source_code = cst.Module([]).code_for_node(node)
        self.function_nodes.append(node)
        self.function_source_codes.append(function_source_code)
        self.full_node_list.append(node)
        self.full_source_list.append(function_source_code)
        self.function_count += 1

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """This method is called for every ClassDef node in the tree.
        and it does the following:
        1. Gets the source code for the node
        2. Adds the node to the list of class nodes
        3. Adds the source code to the list of class source codes
        4. Increments the class count
        """
        class_source_code = cst.Module([]).code_for_node(node)
        self.class_nodes.append(node)
        self.class_source_codes.append(class_source_code)
        self.full_node_list.append(node)
        self.full_source_list.append(class_source_code)
        self.class_count += 1

class PythonDocstringExtractor:
    @staticmethod
    def extract_docstring(function_def: cst.FunctionDef) -> str:
        docstring = None

        for stmt in function_def.body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for expr in stmt.body:
                    if isinstance(expr, cst.Expr) and isinstance(
                        expr.value, cst.SimpleString
                    ):
                        docstring = expr.value.value.strip('"').strip("'")
                        break
            if docstring is not None:
                break

        if docstring is not None:
            return docstring.strip()
        else:
            function_name = function_def.name.value
            return f"No docstring provided for function '{function_name}'."

class PythonParser(OsProcessor):
    def __init__(
        self,
        directory_path: str,
        remove_docstrings: bool = False,
        lint_code: bool = False
    ):
        super().__init__(directory_path)
        self.remove_docstrings = remove_docstrings
        self.lint_code = lint_code

    def remove_docstring(self, tree: cst.Module) -> cst.Module:
        class DocstringRemover(cst.CSTTransformer):
            def leave_FunctionDef(
                self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
            ) -> cst.FunctionDef:
                docstring = PythonDocstringExtractor.extract_docstring(original_node)
                if docstring.startswith("No docstring"):
                    return updated_node

                return updated_node.with_changes(
                    body=updated_node.body.with_changes(
                        body=[
                            stmt
                            for stmt in updated_node.body.body
                            if not (
                                isinstance(stmt, cst.SimpleStatementLine)
                                and any(
                                    isinstance(expr, cst.Expr)
                                    and isinstance(expr.value, cst.SimpleString)
                                    for expr in stmt.body
                                )
                            )
                        ]
                    )
                )

        return tree.visit(DocstringRemover())

    def process_directory(self) -> List[Dict[str, Any]]:
        python_files = self.get_files_with_extension(".py")
        results = []

        for file_path in python_files:
            if file_path.split('/')[-1] in ["__init__.py"]:
                continue
            if self.lint_code:
                self.normalize_file(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    source_code = file.read()

                tree = cst.parse_module(source_code)
                if self.remove_docstrings:
                    tree = self.remove_docstring(tree)

                results.append({
                    'code': tree.code,
                    'cst_tree': tree,
                    'file_name': file_path
                })

            except Exception as e:  # Catch exceptions related to file reading or CST parsing
                print(f"Error processing {file_path}: {e}")
        return results

    def normalize_file(self, file_path: str):
        subprocess.run(["black", file_path], capture_output=True)

def extract_values_python(
    directory_path: str,
    remove_docstrings: bool = False,
    lint_code: bool = False,
    resolution: str = "module",
) -> List[Dict[str, Any]]:
    parser = PythonParser(
        directory_path=directory_path,
        remove_docstrings=remove_docstrings,
        lint_code=lint_code
    )
    processed_files = parser.process_directory()

    results = []
    for item in processed_files:
        match resolution:
            case "module":
                # Directly append the processed file data for 'module' resolution
                results.append({
                    'code': item['code'],
                    'cst_tree': str(item['cst_tree']),
                    'file_name': item['file_name']
                })
            case "function" | "class":
                # Logic to extract specific nodes ('function' or 'class') from 'cst_tree' if needed
                visitor = FunctionAndClassVisitor()
                cst_tree = item['cst_tree']
                cst_tree.visit(visitor)
                if resolution == "function":
                    for function_node in visitor.function_nodes:
                        function_source_code = cst.Module([]).code_for_node(function_node)
                        results.append({
                            'code': function_source_code,
                            'cst_tree': str(function_node),
                            'file_name': item['file_name']
                        })
                elif resolution == "class":
                    for class_node in visitor.class_nodes:
                        class_source_code = cst.Module([]).code_for_node(class_node)
                        results.append({
                            'code': class_source_code,
                            'cst_tree': str(class_node),
                            'file_name': item['file_name']
                        })
    return results
