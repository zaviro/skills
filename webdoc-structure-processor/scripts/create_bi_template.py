import re
import sys

def create_template(filepath, output_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = ""
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        frontmatter = content[:fm_match.end()]
        content = content[fm_match.end():]

    lines = content.split('\n')
    output_lines = []
    if frontmatter:
        output_lines.append(frontmatter.strip())
        output_lines.append("")

    current_block = []
    in_code = False

    for line in lines:
        if line.strip().startswith('```'):
            if in_code:
                # End of code block
                current_block.append(line)
                output_lines.extend(current_block)
                output_lines.append("")
                current_block = []
                in_code = False
            else:
                # Start of code block
                if current_block:
                    txt = "\n".join(current_block).strip()
                    if txt:
                        output_lines.append(":::block")
                        output_lines.append("[en]")
                        output_lines.append(txt)
                        output_lines.append("[zh]")
                        output_lines.append(txt)
                        output_lines.append(":::")
                        output_lines.append("")
                    current_block = []
                in_code = True
                current_block.append(line)
        elif in_code:
            current_block.append(line)
        else:
            # Check headers
            if re.match(r'^#+ ', line):
                if current_block:
                    txt = "\n".join(current_block).strip()
                    if txt:
                        output_lines.append(":::block")
                        output_lines.append("[en]")
                        output_lines.append(txt)
                        output_lines.append("[zh]")
                        output_lines.append(txt)
                        output_lines.append(":::")
                        output_lines.append("")
                    current_block = []
                output_lines.append(":::block")
                output_lines.append("[en]")
                output_lines.append(line.strip())
                output_lines.append("[zh]")
                output_lines.append(line.strip())
                output_lines.append(":::")
                output_lines.append("")
            elif line.strip() == "":
                if current_block:
                    txt = "\n".join(current_block).strip()
                    if txt:
                        output_lines.append(":::block")
                        output_lines.append("[en]")
                        output_lines.append(txt)
                        output_lines.append("[zh]")
                        output_lines.append(txt)
                        output_lines.append(":::")
                        output_lines.append("")
                    current_block = []
            else:
                current_block.append(line)

    if current_block:
        txt = "\n".join(current_block).strip()
        if txt:
            output_lines.append(":::block")
            output_lines.append("[en]")
            output_lines.append(txt)
            output_lines.append("[zh]")
            output_lines.append(txt)
            output_lines.append(":::")
            output_lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))
    print(f"Created template at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_bi_template.py <input.md> <output.bi.md>")
        sys.exit(1)
    create_template(sys.argv[1], sys.argv[2])
