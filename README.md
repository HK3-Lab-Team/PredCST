# PredCST: Learning Predictive Models of Concrete Syntax Tree from Text

## Introduction
PredCST is a tool designed to learn predictive models of concrete syntax trees from text. It is built on two main packages: frames and processors. The frames package includes the code frame, which is used to load and save parquet files of Python packages. It also utilizes the Python Parser and the OS processor. The processors package is responsible for scraping Python code from directories, either from Pip packages or GitHub repositories. It can parse the Python code and break it down into its component parts, such as functions, methods, classes, and modules. This is done using LibCST, which converts Python code into concrete syntax trees. These trees are comprised of different types of nodes, such as if statements, for loops, and operator types like plus, minus, and bit invert.

## Usage
PredCST uses several types of visitors to process the CST tree. Some are used to break them up into classes and functions, while others count the different types of nodes and operators used. All of this is done through the code frame and the frames package.

## Initial anaysis
In the initial anaysis, PredCST was used to analyze the Python Standard Library. The code frame was used to parse the library, breaking it down into modules, functions, and classes. Each of these was then analyzed to determine the number of tokens in each row of the polars df. PredCST also has the ability to map the licenses of the code to the specific files of the polar's data frame. The first anaysis involved plotting histograms of the token counts in all three of the different data frames: modules, functions, and classes. The percentage of rows in each of the three data frames that fit within the embedding context length was also calculated.

## Further Information
More details about the initial experiment can be found in the slides here: [Google Slides](https://docs.google.com/presentation/d/1YyTfzS9lA0SfWUzGDala4u9vkA2w8-uwmyjGlAvaR2M/edit?usp=sharing). The cost of embedding each of the data frames for both the open AI embedding models small and large is also discussed.

## Conclusion
PredCST is a powerful tool for analyzing and learning from Python code. It can be used to break down code into its component parts and analyze the structure and complexity of the code. It is a valuable tool for anyone working with Python code and looking to gain insights from it.



