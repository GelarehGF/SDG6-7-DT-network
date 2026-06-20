"""
Step 1 - Corpus extraction.

Reads PDFs from data/corpus/ (local-only, not distributed), extracts section
text via the V7 positional/regex scheme, and writes df_documents_full.csv.

The corpus itself is NOT included in this repository because the source
articles are copyrighted. Place your own PDFs in data/corpus/ to reproduce.
"""
import os
import re
import warnings

import pandas as pd
import pdfplumber

from config import CORPUS_DIR, OUTPUTS

warnings.filterwarnings("ignore")

SECTION_PATTERNS = {
    "abstract":     re.compile(r"(?:^|\n)\s*abstract(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "introduction": re.compile(r"(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*)?(?:introduction(?:\s+and\s+literature\s+review)?|background)(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "methodology":  re.compile(r"(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*)?(?:research\s+)?(?:method(?:s|ology)?|materials?\s+and\s+methods?|research\s+design|research\s+methods?|methodological\s+approach)(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "results":      re.compile(r"(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*)?(?:results?(?:\s+and\s+discussion)?|findings?(?:\s+and\s+discussion)?|empirical\s+results?|research\s+findings?)(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "discussion":   re.compile(r"(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*)?(?:discussions?(?:\s+and\s+implications?)?|analysis|interpretation)(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "conclusion":   re.compile(r"(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*)?(?:conclusions?(?:\s+and\s+(?:recommendations?|implications?|suggestions?))?|concluding\s+remarks)(?:\s*[:\.]\s|\s*\n)", re.IGNORECASE),
    "references":   re.compile(r"(?:^|\n)\s*(?:references|bibliography|works\s+cited)\s*\n", re.IGNORECASE),
}
SECTION_KEYS = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"]


def extract_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def extract_sections_positional(text):
    """Positional section slicing with abstract-protection (V7)."""
    boundaries = []
    for name, pat in SECTION_PATTERNS.items():
        for m in pat.finditer(text):
            boundaries.append((m.start(), m.end(), name))
    boundaries.sort()

    intro_pos = next((s for s, e, n in boundaries if n == "introduction"), None)
    if intro_pos is not None:
        filtered, seen_abstract = [], False
        for start, end, name in boundaries:
            if name == "abstract":
                filtered.append((start, end, name)); seen_abstract = True
            elif start < intro_pos and seen_abstract:
                continue
            else:
                filtered.append((start, end, name))
        boundaries = filtered

    sections = {k: "" for k in SECTION_KEYS}
    for i, (start, end, name) in enumerate(boundaries):
        if name == "references":
            continue
        nxt = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        sections[name] = text[end:nxt].strip()
    return sections


def build_corpus(corpus_dir=CORPUS_DIR, out_dir=OUTPUTS):
    paths = []
    for root, _, files in os.walk(corpus_dir):
        paths += [os.path.join(root, f) for f in files if f.lower().endswith(".pdf")]
    if not paths:
        raise FileNotFoundError(f"No PDFs under {corpus_dir}. Add the corpus to reproduce.")

    records = []
    for path in paths:
        try:
            full = extract_pdf_text(path)
            if len(full.strip()) < 100:
                continue
            sec = extract_sections_positional(full)
            joined = " ".join(sec.values()).strip()
            if len(joined) < 300:
                sec = {k: "" for k in SECTION_KEYS}
                sec["abstract"] = full.strip()[:5000]
                joined = sec["abstract"]
            if len(joined) < 300:
                continue
            pid = re.sub(r"\.pdf$", "", os.path.basename(path), flags=re.IGNORECASE)
            records.append({"paper_id": pid, "text": joined, **sec})
        except Exception as e:  # noqa: BLE001
            print(f"  skip {path}: {str(e)[:80]}")

    df = pd.DataFrame(records, columns=["paper_id", "text", *SECTION_KEYS])
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(out_dir / "df_documents_full.csv", index=False)
    print(f"Extracted {len(df)} papers -> df_documents_full.csv")
    return df


if __name__ == "__main__":
    build_corpus()
