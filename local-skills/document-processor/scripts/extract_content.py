#!/usr/bin/env python3
"""
Extracts text and image assets from EPUB or TXT documents.
Outputs clean Markdown files and a manifest file.

Dependencies: Python 3.6+ standard library only.
"""
import os
import re
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


def sanitize_text(text):
    """Remove control characters and normalize whitespace per line."""
    text = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', ' ', text)
    lines = []
    for line in text.splitlines():
        clean = re.sub(r'\s+', ' ', line).strip()
        if clean:
            lines.append(clean)
    return '\n'.join(lines)


def _resolve_path(base, relative):
    """Resolve a relative path against a base path within a zip archive."""
    if relative.startswith('/'):
        return relative.lstrip('/')
    result = os.path.normpath(os.path.join(os.path.dirname(base), relative))
    result = result.replace('\\', '/')
    while result.startswith('../'):
        result = result[3:]
    while result.startswith('./'):
        result = result[2:]
    return result


class _XHTMLExtractor(HTMLParser):
    """Extracts headings, paragraphs, and image references from XHTML as Markdown."""

    _HEADINGS = frozenset({'h1', 'h2', 'h3', 'h4', 'h5', 'h6'})
    _BLOCKS = frozenset({'p', 'div'})
    _SKIP = frozenset({'script', 'style'})

    def __init__(self, img_map, base_href=''):
        super().__init__()
        self.img_map = img_map
        self.base_href = base_href
        self.parts = []
        self._stack = []        # [(tag, [text_pieces])]
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self._SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in self._HEADINGS or tag in self._BLOCKS:
            self._stack.append((tag, []))
        elif tag == 'img':
            self._add_image(dict(attrs).get('src', ''))
        elif tag == 'image':
            ad = dict(attrs)
            self._add_image(ad.get('xlink:href', ad.get('href', '')))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self._SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if (tag in self._HEADINGS or tag in self._BLOCKS) and self._stack:
            st, pieces = self._stack.pop()
            if st == tag:
                text = ''.join(pieces).strip()
                if text:
                    if st in self._HEADINGS:
                        self.parts.append(f"{'#' * int(st[1])} {text}")
                    else:
                        self.parts.append(text)

    def handle_data(self, data):
        if self._skip_depth:
            return
        if self._stack:
            self._stack[-1][1].append(data)

    def _add_image(self, src):
        if not src:
            return
        resolved = _resolve_path(self.base_href, src)
        name = self.img_map.get(resolved)
        if name:
            self.parts.append(f"![Illustration {name}](images/{name})")

    def get_markdown(self):
        return '\n\n'.join(self.parts)


def extract_epub(epub_path, output_dir, manifest):
    pages_dir = os.path.join(output_dir, 'pages')
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    print(f"Loading EPUB: {epub_path}")

    with zipfile.ZipFile(epub_path, 'r') as z:
        # --- Locate OPF via container.xml ---
        opf_path = None
        try:
            container = ET.fromstring(z.read('META-INF/container.xml'))
            for el in container.iter():
                el.tag = re.sub(r'\{[^}]*\}', '', el.tag)
            rf = container.find('.//rootfile')
            if rf is not None:
                opf_path = rf.get('full-path')
        except Exception:
            pass

        if not opf_path or opf_path not in z.namelist():
            candidates = [n for n in z.namelist() if n.lower().endswith('.opf')]
            opf_path = candidates[0] if candidates else None
        if not opf_path:
            print("Error: OPF file not found in EPUB.")
            sys.exit(1)

        print(f"Reading OPF: {opf_path}")
        opf_raw = z.read(opf_path).decode('utf-8', errors='ignore')
        opf_clean = re.sub(r'\sxmlns="[^"]*"', '', opf_raw, count=1)
        opf = ET.fromstring(opf_clean)

        # --- Manifest items ---
        items = {}
        for it in opf.findall('.//manifest/item'):
            iid, href, mt = it.get('id'), it.get('href'), it.get('media-type', '')
            if iid and href:
                items[iid] = {'href': _resolve_path(opf_path, href), 'media_type': mt}

        # --- Spine order ---
        spine = []
        for ref in opf.findall('.//spine/itemref'):
            idref = ref.get('idref')
            if idref in items:
                spine.append(idref)

        # --- Extract images ---
        images_list = []
        img_counter = 1
        img_map = {}
        for info in items.values():
            mt, href = info['media_type'], info['href']
            if 'image/' in mt or href.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                if href in z.namelist():
                    ext = os.path.splitext(href)[1].lower() or '.png'
                    new_name = f"img_{img_counter:03d}{ext}"
                    try:
                        with open(os.path.join(images_dir, new_name), 'wb') as f:
                            f.write(z.read(href))
                        img_map[href] = new_name
                        images_list.append({'name': new_name, 'original_path': href})
                        img_counter += 1
                    except Exception as e:
                        print(f"Warning: image {href}: {e}")

        # --- Extract text per spine item ---
        text_parts = []
        page_counter = 1
        for idref in spine:
            href = items[idref]['href']
            if href not in z.namelist():
                continue
            try:
                raw = z.read(href).decode('utf-8', errors='ignore')
                parser = _XHTMLExtractor(img_map, base_href=href)
                parser.feed(raw)
                md = sanitize_text(parser.get_markdown())
                if md.strip():
                    path = os.path.join(pages_dir, f"page_{page_counter:04d}.txt")
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(md)
                    text_parts.append(md)
                    page_counter += 1
            except Exception as e:
                print(f"Warning: {href}: {e}")

    with open(os.path.join(output_dir, 'raw_text.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(text_parts))

    manifest['total_pages'] = len(text_parts)
    manifest['images'] = images_list
    manifest['extracted_text_file'] = 'raw_text.txt'


def extract_txt(txt_path, output_dir, manifest):
    pages_dir = os.path.join(output_dir, 'pages')
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)

    for enc in ('utf-8', 'gbk', 'utf-16'):
        try:
            with open(txt_path, 'r', encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        print("Error: Could not decode file.")
        sys.exit(1)

    chunk_size = 5000
    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
    for idx, chunk in enumerate(chunks, 1):
        with open(os.path.join(pages_dir, f"page_{idx:04d}.txt"), 'w', encoding='utf-8') as f:
            f.write(sanitize_text(chunk))

    with open(os.path.join(output_dir, 'raw_text.txt'), 'w', encoding='utf-8') as f:
        f.write(content)

    manifest['total_pages'] = len(chunks)
    manifest['images'] = []
    manifest['extracted_text_file'] = 'raw_text.txt'


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_content.py <input_file> <output_dir>")
        sys.exit(1)

    input_file, output_dir = sys.argv[1], sys.argv[2]
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    manifest = {
        'source_file': os.path.abspath(input_file),
        'source_format': os.path.splitext(input_file)[1].lower().lstrip('.'),
        'total_pages': 0, 'images': [], 'extracted_text_file': ''
    }

    fmt = manifest['source_format']
    if fmt == 'epub':
        extract_epub(input_file, output_dir, manifest)
    elif fmt in ('txt', 'html', 'htm'):
        extract_txt(input_file, output_dir, manifest)
    else:
        print(f"Unsupported: {fmt}. Treating as plain text.")
        extract_txt(input_file, output_dir, manifest)

    with open(os.path.join(output_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    print(f"Done. Output: {output_dir}")


if __name__ == '__main__':
    main()
