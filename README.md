# Static Code Analyzer
This program aims to check code style of python files according to PEP 8.

## How to use
- run the [file](https://github.com/qilinz/Static-Code-Analyser/blob/main/code_analyzer.py) with argument of which folder or which file to check. e.g. `python handler.py root_folder` or `python handler.py path/main.py`
- The program will list all the code issue in the given folder or the given file.
- Attention: only `.py` file will be checked.

## Code issues covered:
- S001: Too long
- S002: Indentation is not a multiple of four 
- S003: Unnecessary semicolon after a statement
- S004: Less than two spaces before inline comments
- S005: TODO found
- S006: More than two blank lines preceding a code line
- S007: Too many spaces after construction_name (def or class)
- S008: Class name class_name should be written in CamelCase
- S009: Function name function_name should be written in snake_case
- S010: Argument name arg_name should be written in snake_case
- S011: Variable var_name should be written in snake_case
- S012: The default argument value is mutable.

## Theory
Above issues are checked through two modes:
1. Read the file as a string, check it line by line using regex.
2. Parse the file as a tree, check it node by node using ast module.

## Example
An example python file:
```
CONSTANT = 10
names = ['John', 'Lora', 'Paul']


def fun1(S=5, test=[]):  # default argument value is mutable
    VARIABLE = 10
    string = 'string'
    print(VARIABLE)
```
The expected output for this code is:
```
/path/to/file/script.py: Line 5: S010 Argument name 'S' should be snake_case
/path/to/file/script.py: Line 5: S012 Default argument value is mutable
/path/to/file/script.py: Line 6: S011 Variable 'VARIABLE' in function should be snake_case
```

Disclaimer: The original project idea is from [JetBrains Academy](https://hyperskill.org/projects/112). All codes were written by myself.