import json
from typing import List, Dict, Optional

import httpx
from bs4 import BeautifulSoup


def fetch_url_content(url: str, timeout: float = 10.0) -> Dict:
    """
    Fetch a single URL and extract its title and full text content.

    Args:
        url: The page URL to fetch.
        timeout: Seconds to wait before giving up.

    Returns:
        A dict with keys:
          - url: original URL
          - status_code: HTTP status
          - title: <title> text (or None)
          - content: all page text (newlines collapsed)
          - error: error message if fetch/parsing failed
    """
    result = {"url": url, "status_code": None, "title": None, "content": None, "error": None}
    try:
        resp = httpx.get(url, timeout=timeout)
        result["status_code"] = resp.status_code
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        if soup.title and soup.title.string:
            result["title"] = soup.title.string.strip()

        # Extract visible text
        text = soup.get_text(separator="\n", strip=True)
        # Optionally collapse multiple blank lines:
        lines = [line for line in text.splitlines() if line.strip()]
        result["content"] = "\n".join(lines)

    except Exception as e:
        result["error"] = str(e)

    return result


def get_content_json(
    urls: List[str],
    output_file: Optional[str] = None,
    timeout: float = 10.0
) -> List[Dict]:
    """
    Fetch multiple URLs and return (and optionally save) a JSON array of their contents.

    Args:
        urls: List of page URLs.
        output_file: If given, path to write the JSON file.
        timeout: Per-request timeout in seconds.

    Returns:
        A list of dicts as produced by `fetch_url_content`.
    """
    all_data = []
    for url in urls:
        data = fetch_url_content(url, timeout=timeout)
        all_data.append(data)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)

    return all_data


# Example usage:
if __name__ == "__main__":
    urls = [
        "https://www.materiom.org/",
        "https://infoguides.rit.edu/packaging/databases",
        "https://search.library.wisc.edu/catalog/9914150907202121",
        # … add more …
    ]
    data = get_content_json(urls, output_file="packaging_resources.json")
    print(json.dumps(data, indent=2, ensure_ascii=False))