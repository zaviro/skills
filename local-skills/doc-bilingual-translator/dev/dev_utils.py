import os
import re

def split_bi_markdown(filepath, max_blocks=50):
    """
    Splits a .bi.md file into chunks, each containing up to max_blocks :::block elements.
    Code blocks are kept inline and not split inside.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = ""
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        frontmatter = content[:fm_match.end()]
        content = content[fm_match.end():]

    # Split by :::block or code blocks
    # We want to identify top-level elements: :::block ... ::: AND code blocks ``` ... ```
    pattern = re.compile(r'(:::block\n.*?\n:::|```.*?\n```)', re.DOTALL)
    parts = pattern.split(content)

    chunks = []
    current_chunk = []
    block_count = 0

    for part in parts:
        part_strip = part.strip()
        if not part_strip:
            continue
        
        current_chunk.append(part)
        if part_strip.startswith(':::block'):
            block_count += 1
            
        if block_count >= max_blocks:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            block_count = 0

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # Save chunks
    base_dir = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    chunk_paths = []
    for idx, chunk_content in enumerate(chunks, 1):
        chunk_file = os.path.join(base_dir, f"{name}_part{idx}{ext}")
        with open(chunk_file, 'w', encoding='utf-8') as f:
            if frontmatter:
                f.write(frontmatter + "\n")
            f.write(chunk_content)
        chunk_paths.append(chunk_file)
        print(f"Created chunk: {chunk_file}")
        
    return chunk_paths

def merge_bi_markdown(chunk_paths, output_path):
    """
    Merges multiple .bi.md chunks back into a single file.
    Only the frontmatter from the first chunk is preserved.
    """
    merged_content = []
    frontmatter = ""
    
    for idx, path in enumerate(chunk_paths):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            if idx == 0:
                frontmatter = content[:fm_match.end()]
            content = content[fm_match.end():]
            
        merged_content.append(content.strip())
        
    with open(output_path, 'w', encoding='utf-8') as f:
        if frontmatter:
            f.write(frontmatter + "\n")
        f.write("\n\n".join(merged_content))
        
    print(f"Merged chunks into: {output_path}")
