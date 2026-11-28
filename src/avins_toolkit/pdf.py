import pymupdf
import logging

logger = logging.getLogger(__name__)


def extract(path: str, min_chars: int = 100) -> dict:
    try:
        doc = pymupdf.open(path)
    except Exception:
        logger.warning(f"{path}: PDF corrupted/inaccessable")
        return {"title": "", "text": ""}
    if doc.is_encrypted or doc.needs_pass:
        logger.warning(f"{path}: PDF requires authorization")
        doc.close()
        return {"title": "", "text": ""}
    txt = []
    for page in doc:
        txt.append(page.get_text().strip())
        if txt[-1] == "":
            txt.pop()
    if doc.metadata is not None and "title" in doc.metadata and doc.metadata["title"] is not None:
        title = doc.metadata["title"].strip()
    else:
        title = ""
    doc.close()
    txt = "\n".join(txt)
    if len(txt) < min_chars:
        txt = ""
        title = ""
        logger.info(f"{path} has less than minimum threshold content")
    return {"title": title, "text": txt}