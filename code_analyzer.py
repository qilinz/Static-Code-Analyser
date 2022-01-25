import re
import os
import argparse
import ast

error_dict = {
    "S001": "Too long",
    "S002": "Indentation is not a multiple of four",
    "S003": "Unnecessary semicolon after a statement",
    "S004": "Less than two spaces before inline comments",
    "S005": "TODO found",
    "S006": "More than two blank lines preceding a code line"
}


def get_issue(path, line_index, error_code) -> tuple:
    """Get the error message tuple by line and error code. """
    line_count = line_index + 1
    error_message = error_dict[error_code]
    code_issue = f"{error_code} {error_message}"
    return path, line_count, code_issue


def space_counter(string) -> int:
    """Return the count of spaces in the beginning of a string. """
    count = 0
    for char in string:
        if char == " ":
            count += 1
        else:   # break if no more space
            break
    return count


def issue_S001(line_string):
    """Return True if the length of the line > 79. """
    code_len = len(line_string)
    if code_len > 79:
        return True

    return False


def issue_S002(line_string):
    """Return True if the indentation does not meet the requirements. """
    # count how many spaces before any code
    space_count = space_counter(line_string)

    # check the indentation
    if space_count % 4 != 0:
        return True

    return False


def issue_S003(line_string):
    """Return True if there's unnecessary semicolon. """
    if ";" not in line_string:
        return False

    # remove quotations
    string_to_check = re.sub(r'".*"', "", line_string)
    string_to_check = re.sub(r"'.*'", "", string_to_check)

    # remove the comments
    if "#" in string_to_check:
        string_to_check = string_to_check.split("#")[0]

    if ";" in string_to_check:
        return True

    return False


def issue_S004(line_string):
    """ Return True if there's less than two spaces before inline comments. """
    if "#" in line_string:
        string_to_check = line_string.split("#")[0]

        # rule out comments that start from the first character
        if string_to_check == "":
            return False

        # count how many spaces before "#"
        space_count = space_counter(reversed(string_to_check))
        if space_count < 2:
            return True

    return False


def issue_S005(line_string):
    """Return True if there's to-do in comments. """
    if "#" in line_string:
        comment_index = line_string.index("#")
        string_to_check = line_string[comment_index:]  # only check comments
        string_lower = string_to_check.lower()
        if "todo" in string_lower:
            return True

    return False


def issue_S007(line_string):
    """Return code issue if too many spaces after def or class"""
    string_to_check = line_string.strip()
    if string_to_check[:5] == "class":
        space_count = space_counter(string_to_check[5:])
        if space_count > 1:
            return "S007 Too many spaces after 'class'"

    if string_to_check[:3] == "def":
        space_count = space_counter(string_to_check[3:])
        if space_count > 1:
            return "S007 Too many spaces after 'def'"


def issue_S008(node):
    """Return code issue if name of class is not CamelCase. """
    if isinstance(node, ast.ClassDef):
        class_name = node.name
        if "_" in class_name:
            return node.lineno, f"S008 Class name '{class_name}' should be written in CamelCase"

        if re.match(r"[A-Z][a-z]", class_name) is None:
            return node.lineno, f"S008 Class name '{class_name}' should be written in CamelCase"

    return None, None


def issue_S009(node):
    """Return code issue if name of function is not snake_case. """
    if isinstance(node, ast.FunctionDef):
        function_name = node.name
        if function_name == "__init__":
            return None, None
        if function_name != function_name.lower():
            return node.lineno, f"S009 Function name '{function_name}' should be written in snake_case"

    return None, None


def issue_S010(node):
    """Return code issue if argument name is not snake_case. """
    if isinstance(node, ast.FunctionDef):
        arg_list = node.args.args
        for arg in arg_list:
            arg_name = arg.arg
            if arg_name != arg_name.lower():
                return node.lineno, f"S010 Argument name '{arg_name}' should be written in snake_case"

    return None, None


def issue_S011(node):
    """Return code issue if variable name in functions is not snake_case. """
    if isinstance(node, ast.FunctionDef):
        for body_node in node.body:
            if isinstance(body_node, ast.Assign):
                targets = body_node.targets
                for target_node in targets:
                    if isinstance(target_node, ast.Name):
                        var_name = target_node.id
                        if var_name != var_name.lower():
                            return target_node.lineno, f"S011 Variable '{var_name}' should be written in snake_case"

    return None, None


def issue_S012(node):
    """Return issue of the given code if The default argument value is mutable. """
    if isinstance(node, ast.FunctionDef):
        default_list = node.args.defaults
        for default in default_list:
            if isinstance(default, ast.List) or isinstance(default, ast.Dict) or isinstance(default, ast.Set):
                return default.lineno, "S012 The default argument value is mutable"

    return None, None


def get_files(dir_path) -> list:
    """Return a list of all files in the given directory path. """
    file_list = []
    for root, dirs, files in os.walk(dir_path, topdown=True):
        for name in files:
            if name.endswith(".py"):  # only check .py file
                full_path = os.path.join(root, name)
                file_list.append(full_path)
    return file_list


# -------------------------main function------------------------------ #
def main():
    # create ab ArgumentParser
    parser = argparse.ArgumentParser(description="This program check the code style of python file.")
    parser.add_argument("path", help="You need to enter the path of a directory or file to check.")

    # read the args
    args = parser.parse_args()
    path_to_check = args.path

    # list all files to check
    file_to_check = []

    # check if the input path is file or dir
    if os.path.isfile(path_to_check):  # file
        if path_to_check.endswith(".py"):  # only check .py file
            file_to_check.append(path_to_check)

    else:  # dir
        file_to_check = get_files(path_to_check)
        # file_to_check.sort()

    issue_list = []  # add all issues to this list

    function_dict_1 = {
        "S001": issue_S001,
        "S002": issue_S002,
        "S003": issue_S003,
        "S004": issue_S004,
        "S005": issue_S005,
    }

    function_dict_2 = {
        "S008": issue_S008,
        "S009": issue_S009,
        "S010": issue_S010,
        "S011": issue_S011,
        "S012": issue_S012,
    }

    # loop through all files to check
    for file_path in file_to_check:
        with open(file_path) as file:
            data = file.read()
            data_list = data.splitlines()

            # check errors line by line S001 - S006
            for index, line in enumerate(data_list):

                # check errors within a line S001 - S005
                for code, func in function_dict_1.items():
                    if func(line):  # if issue exists
                        issue = get_issue(file_path, index, code)
                        issue_list.append(issue)

                # check errors across lines S006
                if (index > 2) and (line != ""):
                    if data_list[index - 1] == "" and data_list[index - 2] == "" and data_list[index - 3] == "":
                        issue = get_issue(file_path, index, "S006")
                        issue_list.append(issue)

                # check error within a line S007
                code_issue = issue_S007(line)
                if code_issue:
                    issue = (file_path, index + 1, code_issue)
                    issue_list.append(issue)

            # check errors by nodes S008 - S012
            tree = ast.parse(data)
            for node in ast.walk(tree):
                for code, func in function_dict_2.items():
                    line_no, code_issue = func(node)
                    if line_no:   # if issue exists
                        issue = (file_path, line_no, code_issue)
                        if issue not in issue_list:
                            issue_list.append(issue)

    for path, line, error in sorted(issue_list):
        print(f"{path}: Line {line}: {error}")


if __name__ == "__main__":
    main()
