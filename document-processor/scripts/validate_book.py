#!/usr/bin/env python3
"""
General quality validator for output EPUB or TXT books, optimized for Markdown flow.
Verifies structure, paragraph health, integrity, and remaining spam.
"""
import os
import re
import sys
import zipfile


class ValidationReport:
    def __init__(self, filename):
        self.filename = filename
        self.checks = []  # [(name, status, detail), ...]

    def add(self, name, status, detail=""):
        self.checks.append((name, status, detail))

    def print_summary(self):
        passed = sum(1 for _, s, _ in self.checks if s == "PASS")
        warned = sum(1 for _, s, _ in self.checks if s == "WARN")
        failed = sum(1 for _, s, _ in self.checks if s == "FAIL")
        total = len(self.checks)
        
        print("\n" + "=" * 60)
        print(f"Validation Report: {os.path.basename(self.filename)}")
        print("=" * 60)
        print(f"Total: {total}  |  Passed: {passed}  |  Warnings: {warned}  |  Failed: {failed}")
        print("-" * 60)
        
        for name, status, detail in self.checks:
            icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}[status]
            line = f"  {icon} {name:<25}"
            if detail:
                line += f"  -  {detail}"
            print(line)
            
        print("=" * 60)


def validate_epub(filepath, extracted_dir=None):
    report = ValidationReport(filepath)
    
    if not os.path.exists(filepath):
        report.add("File existence", "FAIL", f"File '{filepath}' not found.")
        return report

    file_size = os.path.getsize(filepath)
    report.add("File size", "PASS", f"{file_size/1024:.1f} KB")

    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            names = z.namelist()
            
            # Check necessary EPUB files
            required_files = ["mimetype", "META-INF/container.xml"]
            for req in required_files:
                if req in names:
                    report.add(f"Required file: {req}", "PASS")
                else:
                    report.add(f"Required file: {req}", "FAIL", "Missing")
                    
            # Check for content document pages
            xhtml_files = [n for n in names if n.endswith(('.xhtml', '.html'))]
            if xhtml_files:
                report.add("XHTML content pages", "PASS", f"Found {len(xhtml_files)} pages")
            else:
                report.add("XHTML content pages", "FAIL", "No XHTML content pages found")

            # Extract text from XHTML pages to check quality
            full_html = ""
            illustrations_found = []
            
            for page in xhtml_files:
                content = z.read(page).decode('utf-8', errors='ignore')
                full_html += content
                
                # Check for referenced images in HTML
                img_srcs = re.findall(r'<img[^>]+src=["\']images/(.*?)["\'][^>]*>', content)
                illustrations_found.extend(img_srcs)
            
            # Extract text from full_html by stripping tags
            full_text = re.sub(r'<[^>]+>', ' ', full_html)
            
            # Check paragraph health (broken paragraphs ending without punctuation)
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', full_html, re.DOTALL)
            END_PUNCT = set("。！？；：\"\"''」』】》）]}”’!?.）)")
            
            broken_paras = 0
            empty_paras = 0
            total_paras = 0
            total_chars = 0
            
            for p in paragraphs:
                clean = re.sub(r'<[^>]+>', '', p).strip()
                if not clean:
                    empty_paras += 1
                    continue
                total_paras += 1
                total_chars += len(clean)
                if clean[-1] not in END_PUNCT:
                    broken_paras += 1
                    
            report.add("Total clean characters", "PASS", f"{total_chars:,} characters")
            
            if total_paras > 0:
                broken_rate = broken_paras / total_paras
                status = "PASS" if broken_rate < 0.06 else ("WARN" if broken_rate < 0.15 else "FAIL")
                report.add("Paragraph split rate", status, f"{broken_rate:.1%} ({broken_paras}/{total_paras} broken)")
                
                avg_para_len = total_chars / total_paras
                status = "PASS" if avg_para_len > 25 else "WARN"
                report.add("Average paragraph length", status, f"{avg_para_len:.1f} characters")
            else:
                report.add("Paragraph statistics", "FAIL", "No paragraphs found in XHTML files")

            # Validate images reference completeness
            missing_images = []
            for img in illustrations_found:
                # EPUB internally maps images in images/img_xxx.png
                if f"images/{img}" not in names:
                    missing_images.append(img)
            
            if missing_images:
                report.add("Illustration assets", "FAIL", f"Missing referenced images: {missing_images}")
            else:
                report.add("Illustration assets", "PASS", f"{len(illustrations_found)} references mapped correctly")

    except zipfile.BadZipFile:
        report.add("ZIP format validation", "FAIL", "Invalid ZIP/EPUB format")

    # Content integrity check against extracted dir if provided
    if extracted_dir and os.path.isdir(extracted_dir):
        raw_text_path = os.path.join(extracted_dir, "raw_text.txt")
        if os.path.exists(raw_text_path):
            with open(raw_text_path, "r", encoding="utf-8") as f:
                orig_text = f.read()
                
            orig_len = len(orig_text.replace(" ", "").replace("\n", ""))
            ref_len = len(full_text.replace(" ", "").replace("\n", ""))
            
            if orig_len > 0:
                ratio = ref_len / orig_len
                status = "PASS" if 0.85 <= ratio <= 1.05 else ("WARN" if 0.70 <= ratio <= 1.15 else "FAIL")
                report.add("Text retention ratio", status, f"Retained {ratio:.1%} of original text volume")

    return report


def validate_txt(filepath, extracted_dir=None):
    report = ValidationReport(filepath)
    
    if not os.path.exists(filepath):
        report.add("File existence", "FAIL", f"File '{filepath}' not found.")
        return report

    file_size = os.path.getsize(filepath)
    report.add("File size", "PASS", f"{file_size/1024:.1f} KB")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        report.add("Encoding check", "FAIL", "File is not UTF-8 encoded")
        return report

    report.add("Encoding check", "PASS", "UTF-8 encoded")
    
    char_count = len(text.strip())
    report.add("Text length", "PASS", f"{char_count:,} characters")

    # Scan for common advertisement keywords
    ad_keywords = ["V信", "Free书", "下载更多", "微信号", "更多免费书"]
    ads_found = []
    for kw in ad_keywords:
        if kw in text:
            ads_found.append(kw)
            
    if ads_found:
        report.add("Residual Spam Check", "WARN", f"Found residual spam keywords: {ads_found}")
    else:
        report.add("Residual Spam Check", "PASS", "No common ad keywords found")

    # Compare with original text
    if extracted_dir and os.path.isdir(extracted_dir):
        raw_text_path = os.path.join(extracted_dir, "raw_text.txt")
        if os.path.exists(raw_text_path):
            with open(raw_text_path, "r", encoding="utf-8") as f:
                orig_text = f.read()
            orig_len = len(orig_text.replace(" ", "").replace("\n", ""))
            ref_len = len(text.replace(" ", "").replace("\n", ""))
            
            if orig_len > 0:
                ratio = ref_len / orig_len
                status = "PASS" if 0.85 <= ratio <= 1.05 else ("WARN" if 0.70 <= ratio <= 1.15 else "FAIL")
                report.add("Text retention ratio", status, f"Retained {ratio:.1%} of original text volume")

    return report


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: validate_book.py <book_file_path> [--extracted-dir <dir>]")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help") else 1)

    filepath = sys.argv[1]
    
    extracted_dir = None
    if "--extracted-dir" in sys.argv:
        try:
            idx = sys.argv.index("--extracted-dir")
            extracted_dir = sys.argv[idx + 1]
        except IndexError:
            pass

    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".epub":
        report = validate_epub(filepath, extracted_dir)
    elif ext == ".txt":
        report = validate_txt(filepath, extracted_dir)
    else:
        print(f"Unsupported file format for validation: {ext}")
        sys.exit(1)

    report.print_summary()
    
    failed_checks = sum(1 for _, s, _ in report.checks if s == "FAIL")
    sys.exit(1 if failed_checks > 0 else 0)


if __name__ == "__main__":
    main()
