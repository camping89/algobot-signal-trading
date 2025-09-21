import ast
import re
import os
from pathlib import Path
from typing import List

def remove_comments_and_docstrings(source_code: str) -> str:
    lines = source_code.split('\n')
    cleaned_lines = []
    in_multiline_string = False
    multiline_delimiter = None
    multiline_indent = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line

        if not in_multiline_string:
            stripped = line.lstrip()

            if stripped.startswith('"""') or stripped.startswith("'''"):
                delimiter = '"""' if stripped.startswith('"""') else "'''"

                if stripped.count(delimiter) >= 2:
                    if stripped.startswith(delimiter) and stripped.rstrip().endswith(delimiter) and len(stripped.strip()) > len(delimiter):
                        i += 1
                        continue

                if stripped.count(delimiter) == 1:
                    in_multiline_string = True
                    multiline_delimiter = delimiter
                    multiline_indent = len(line) - len(line.lstrip())
                    i += 1
                    continue

            if '#' in line:
                in_string = False
                in_single_quote = False
                in_double_quote = False
                escape_next = False

                for j, char in enumerate(line):
                    if escape_next:
                        escape_next = False
                        continue

                    if char == '\\':
                        escape_next = True
                        continue

                    if char == '"' and not in_single_quote:
                        in_double_quote = not in_double_quote
                        in_string = in_double_quote or in_single_quote
                    elif char == "'" and not in_double_quote:
                        in_single_quote = not in_single_quote
                        in_string = in_double_quote or in_single_quote
                    elif char == '#' and not in_string:
                        line = line[:j].rstrip()
                        break

            if line.strip():
                cleaned_lines.append(line)
            elif not original_line.strip():
                cleaned_lines.append('')
        else:
            if multiline_delimiter in line:
                in_multiline_string = False
                multiline_delimiter = None
                multiline_indent = 0
                i += 1
                continue

        i += 1

    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    return '\n'.join(cleaned_lines)

def process_python_file(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        cleaned_content = remove_comments_and_docstrings(original_content)

        try:
            ast.parse(cleaned_content)
        except SyntaxError as e:
            print(f"Syntax error in cleaned version of {file_path}: {e}")
            return False

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        print(f"Processed: {file_path}")
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    base_path = Path("/Users/admin/workspace/trading/algobot-signal-trading")

    python_files = []
    for root, dirs, files in os.walk(base_path):
        if '.venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    print(f"Found {len(python_files)} Python files to process")

    processed = 0
    failed = 0

    for file_path in python_files:
        if process_python_file(file_path):
            processed += 1
        else:
            failed += 1

    print(f"\nProcessing complete:")
    print(f"Successfully processed: {processed} files")
    print(f"Failed: {failed} files")

if __name__ == "__main__":
    main()