from bs4 import BeautifulSoup


def html_cleaner(
    url,
    r,
    min_len,
    noise_tags=(
        "script",
        "noscript",
        "style",
        "svg",
        "canvas",
        "template",
        "iframe",
        "embed",
        "form",
        "button",
        "input",
        "select",
        "textarea",
        "label",
        "nav",
        "header",
        "footer",
        "aside",
    ),
):
    soup = BeautifulSoup(r, "html.parser")
    if soup.body is not None:
        for tags in noise_tags:
            for snippet in soup.body.find_all(tags):
                snippet.decompose()
    if soup.title is not None and soup.body is not None:
        d = {
            "url": url,
            "title": soup.title.get_text(strip=True, separator=" "),
            "text": soup.body.get_text(strip=True, separator="\n"),
        }
        " ".join(d["text"].split())
    elif soup.title is None and soup.body is not None:
        d = {"url": url, "title": "", "text": soup.body.get_text(strip=True, separator=" ")}
        " ".join(d["text"].split())
    else:
        d = {"url": url, "title": "", "text": ""}
    if len(d["text"]) <= min_len:
        d["text"] = ""
    return d
