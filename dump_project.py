import os

# To RUN:
# python dump_project.py > full_project_context.txt

# --- CONFIGURATION ---
# Folders to ignore (so we don't dump virtual environments or git history)
IGNORE_DIRS = {'.git', '.idea', '.vscode', 'venv', '.venv', '__pycache__', 'htmlcov', '.pytest_cache', 'crypto_env'}
# Files to ignore
IGNORE_FILES = {'.DS_Store', 'poetry.lock', 'package-lock.json'}
# Only read these extensions (add more if needed)
ALLOWED_EXTENSIONS = {'.py', '.yml', '.yaml', '.ini', '.toml', '.md', '.txt', '.csv'}


def print_tree(startpath):
    print(f"\n{'=' * 50}")
    print(f"PROJECT STRUCTURE: {startpath}")
    print(f"{'=' * 50}")
    for root, dirs, files in os.walk(startpath):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                print(f'{subindent}{f}')


def dump_files(startpath):
    print(f"\n{'=' * 50}")
    print("FILE CONTENTS")
    print(f"{'=' * 50}")

    for root, dirs, files in os.walk(startpath):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES:
                continue

            # Filter by extension
            _, ext = os.path.splitext(file)
            if ext not in ALLOWED_EXTENSIONS:
                continue

            filepath = os.path.join(root, file)

            print(f"\n\n--- START OF FILE: {filepath} ---")
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    print(f.read())
            except Exception as e:
                print(f"[Error reading file: {e}]")
            print(f"--- END OF FILE: {filepath} ---")


if __name__ == "__main__":
    current_dir = os.getcwd()
    print_tree(current_dir)
    dump_files(current_dir)