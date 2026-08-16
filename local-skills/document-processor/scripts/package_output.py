#!/usr/bin/env python3
"""
Packages refined Markdown text and image assets into a structured EPUB or a clean TXT file,
utilizing standard library zipfile for EPUB generation (no ebooklib or markdown dependencies required).
"""
import os
import re
import sys
import json
import argparse
import zipfile
import html

def markdown_to_html_fallback(text):
    """Fallback Markdown parser to convert basic elements."""
    lines = text.split('\n')
    html_lines = []
    
    img_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # 1. Headings
        if stripped.startswith('#'):
            level = min(len(stripped) - len(stripped.lstrip('#')), 6)
            title = stripped.lstrip('#').strip()
            html_lines.append(f"<h{level}>{title}</h{level}>")
            continue
            
        # 2. Image
        match = img_pattern.search(stripped)
        if match:
            alt = match.group(1)
            src = match.group(2)
            img_filename = src.split('/')[-1]
            html_lines.append(f'<div class="illustration"><img src="images/{img_filename}" alt="{alt}" /></div>')
            continue
            
        # 3. List Item
        if stripped.startswith(('* ', '- ', '• ')):
            item_text = stripped[2:].strip()
            html_lines.append(f"<ul><li>{item_text}</li></ul>")
            continue
            
        # 4. Standard Paragraph
        escaped = html.escape(stripped)
        escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
        escaped = re.sub(r'\*(.*?)\*', r'<em>\1</em>', escaped)
        html_lines.append(f"<p>{escaped}</p>")
        
    return '\n'.join(html_lines)


def package_epub(refined_dir, output_path):
    manifest_path = os.path.join(refined_dir, "refined_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"Error: Refined manifest file '{manifest_path}' not found.")
        sys.exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Resolve metadata
    title = "Refined Book"
    author = "Unknown"
    language = "zh-CN"
    
    src_manifest_path = manifest.get("source_manifest")
    if src_manifest_path and os.path.exists(src_manifest_path):
        try:
            with open(src_manifest_path, "r", encoding="utf-8") as f:
                src_manifest = json.load(f)
                filename = os.path.basename(src_manifest.get("source_file", ""))
                title = os.path.splitext(filename)[0]
                if " - " in title:
                    author, title = title.split(" - ", 1)
        except Exception:
            pass

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. mimetype (MUST be first and uncompressed)
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        z.writestr("META-INF/container.xml", container_xml)

        # 3. style.css
        css = """body {
    font-family: "Noto Sans CJK SC", "WenQuanYi Micro Hei", "PingFang SC", "Microsoft YaHei", sans-serif;
    line-height: 1.8;
    text-align: justify;
    margin: 1em;
    padding: 0;
    color: #222;
}
h1 {
    text-align: center;
    font-size: 2em;
    margin: 2em 0 1em 0;
    color: #111;
}
h2 {
    text-align: center;
    font-size: 1.5em;
    margin: 2em 0 1em 0;
    color: #111;
    page-break-before: always;
}
h3 {
    font-size: 1.2em;
    margin: 1.5em 0 0.5em 0;
    color: #222;
}
p {
    text-indent: 2em;
    margin: 0.5em 0;
}
ul, ol {
    margin: 0.5em 0;
    padding-left: 2em;
}
li {
    margin: 0.2em 0;
}
.illustration {
    text-align: center;
    margin: 1.5em 0;
    page-break-inside: avoid;
}
.illustration img {
    max-width: 95%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}"""
        z.writestr("style.css", css)

        # 4. Images
        images_dir = os.path.join(refined_dir, "images")
        manifest_images = []
        if os.path.isdir(images_dir):
            for img_name in sorted(os.listdir(images_dir)):
                img_path = os.path.join(images_dir, img_name)
                if os.path.isfile(img_path) and img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    ext = os.path.splitext(img_name)[1].lower().replace('.', '')
                    media_type = f'image/{ext}'
                    if ext == 'jpg':
                        media_type = 'image/jpeg'
                    
                    with open(img_path, 'rb') as img_f:
                        z.writestr(f"images/{img_name}", img_f.read())
                    
                    manifest_images.append({
                        "id": f"img_{len(manifest_images) + 1}",
                        "href": f"images/{img_name}",
                        "media_type": media_type
                    })

        # 5. XHTML Chapters
        manifest_pages = []
        
        # Cover Page
        cover_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Cover</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <div style="text-align:center; margin-top:30%;">
    <h1>{title}</h1>
    <p style="text-indent:0; margin-top:2em; font-weight:bold;">{author}</p>
    <p style="text-indent:0; color:#555; margin-top:4em; font-size:0.9em;">LLM-Refined Edition</p>
  </div>
</body>
</html>"""
        z.writestr("cover.xhtml", cover_html)
        manifest_pages.append({
            "id": "cover",
            "href": "cover.xhtml",
            "title": "Cover"
        })

        for chap_info in manifest["chapters"]:
            title_text = chap_info["title"]
            file_name = chap_info["file"]
            idx = chap_info["index"]
            
            filepath = os.path.join(refined_dir, file_name)
            if not os.path.exists(filepath):
                print(f"Warning: Refined file '{filepath}' missing. Skipping.")
                continue
                
            with open(filepath, "r", encoding="utf-8") as f:
                raw_markdown = f.read()

            html_body = markdown_to_html_fallback(raw_markdown)
            
            if not re.search(r'<h[1-6]>', html_body, re.IGNORECASE):
                html_body = f"<h2>{title_text}</h2>\n" + html_body
            
            xhtml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{title_text}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{html_body}
</body>
</html>"""
            
            page_href = f"chap_{idx:03d}.xhtml"
            z.writestr(page_href, xhtml_content)
            
            manifest_pages.append({
                "id": f"chap_{idx}",
                "href": page_href,
                "title": title_text
            })

        # 6. toc.ncx
        ncx_points = []
        for i, page in enumerate(manifest_pages):
            if page["id"] == "cover":
                continue
            ncx_points.append(f"""    <navPoint id="{page['id']}" playOrder="{i}">
      <navLabel><text>{page['title']}</text></navLabel>
      <content src="{page['href']}"/>
    </navPoint>""")
        
        ncx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:baccano-refined"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
{chr(10).join(ncx_points)}
  </navMap>
</ncx>"""
        z.writestr("toc.ncx", ncx_content)

        # 7. content.opf
        manifest_items_xml = [
            '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
            '    <item id="css" href="style.css" media-type="text/css"/>'
        ]
        for page in manifest_pages:
            manifest_items_xml.append(f'    <item id="{page["id"]}" href="{page["href"]}" media-type="application/xhtml+xml"/>')
        for img in manifest_images:
            manifest_items_xml.append(f'    <item id="{img["id"]}" href="{img["href"]}" media-type="{img["media_type"]}"/>')
            
        spine_items_xml = []
        for page in manifest_pages:
            spine_items_xml.append(f'    <itemref idref="{page["id"]}"/>')

        opf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:identifier id="bookid">urn:uuid:baccano-refined</dc:identifier>
    <dc:language>{language}</dc:language>
  </metadata>
  <manifest>
{chr(10).join(manifest_items_xml)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine_items_xml)}
  </spine>
</package>"""
        z.writestr("content.opf", opf_content)

    print(f"EPUB packaging complete! Output file: {output_path}")


def package_txt(refined_dir, output_path, include_placeholders):
    manifest_path = os.path.join(refined_dir, "refined_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"Error: manifest file '{manifest_path}' not found.")
        sys.exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"Assembling TXT file in {output_path}...")
    
    img_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

    with open(output_path, "w", encoding="utf-8") as out:
        for idx, chap_info in enumerate(manifest["chapters"]):
            title_text = chap_info["title"]
            file_name = chap_info["file"]
            
            filepath = os.path.join(refined_dir, file_name)
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            out.write(f"\n\n========================================\n")
            out.write(f"{title_text}\n")
            out.write(f"========================================\n\n")
            
            lines = content.split('\n')
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                match = img_pattern.search(stripped)
                if match:
                    if include_placeholders:
                        img_filename = match.group(2).split('/')[-1]
                        out.write(f"\n【插图位置：{img_filename}】\n")
                elif stripped.startswith('#'):
                    heading_text = stripped.lstrip('#').strip()
                    out.write(f"\n{heading_text}\n")
                else:
                    out.write(f"    {stripped}\n")

    print("TXT assembly complete!")


def main():
    parser = argparse.ArgumentParser(description="Markdown Clean Book Packager")
    parser.add_argument("--refined-dir", required=True, help="Directory containing refined Markdown files")
    parser.add_argument("--format", choices=["epub", "txt"], required=True, help="Target export format")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--no-illustrations", action="store_true", help="Remove illustration markers in TXT export")
    args = parser.parse_args()

    if args.format == "epub":
        package_epub(args.refined_dir, args.output)
    elif args.format == "txt":
        include_placeholders = not args.no_illustrations
        package_txt(args.refined_dir, args.output, include_placeholders)


if __name__ == "__main__":
    main()
