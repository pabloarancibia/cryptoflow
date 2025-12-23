import os

# Configuration: Directories and files to ignore
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'site', 'node_modules'}
IGNORE_FILES = {'.DS_Store', 'poetry.lock', 'package-lock.json'}

# Extensions to read (to avoid reading binaries or images)
INCLUDE_EXTENSIONS = {'.py', '.md', '.yml', '.yaml', '.toml', '.Dockerfile', '.txt'}

def print_tree(startpath):
    structure = "PROJECT STRUCTURE:\n"
    for root, dirs, files in os.walk(startpath):
        # Filter ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                structure += '{}{}\n'.format(subindent, f)
    return structure

def get_file_contents(startpath):
    contents = "\nFILE CONTENTS:\n"
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for f in files:
            if f in IGNORE_FILES:
                continue
            
            # Only include files with allowed extensions
            _, ext = os.path.splitext(f)
            if ext not in INCLUDE_EXTENSIONS:
                continue

            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, startpath)
            
            contents += f"\n{'='*20}\nFILE: {relpath}\n{'='*20}\n"
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file_obj:
                    contents += file_obj.read()
            except Exception as e:
                contents += f"<Error reading file: {e}>"
    return contents

if __name__ == "__main__":
    base_path = "."  # Current directory
    
    # 1. Generate Tree
    full_context = print_tree(base_path)
    
    # 2. Generate Content
    full_context += get_file_contents(base_path)
    
    # 3. Save to a temporary file or print
    # Option A: Print to console for copying
    # print(full_context)
    
    # Option B: Save to 'context_dump.txt' to open and copy (RECOMMENDED)
    output_filename = "context_dump.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(full_context)
    
    print(f"✅ Context generated in '{output_filename}'. Copy its content and paste it into Gemini.")