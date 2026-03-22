from crewai.tools import BaseTool
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


class MySearchTool(BaseTool):
    name: str = "MySearchTool"
    description: str = "Searches Arxiv for academic papers related to a given topic."

    def _run(self, query: str) -> str:

        # ─────────────────────────────────────────
        # BUILD ARXIV API URL
        # ─────────────────────────────────────────
        base_url = "http://export.arxiv.org/api/query?"
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 10,
            "sortBy": "relevance",
            "sortOrder": "descending"
        })
        url = base_url + params

        # ─────────────────────────────────────────
        # FETCH RESULTS
        # ─────────────────────────────────────────
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode("utf-8")

        # ─────────────────────────────────────────
        # PARSE XML RESPONSE
        # ─────────────────────────────────────────
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_data)
        entries = root.findall("atom:entry", namespace)

        if not entries:
            return f"No results found on Arxiv for: {query}"

        # ─────────────────────────────────────────
        # FORMAT RESULTS
        # ─────────────────────────────────────────
        results = []
        for i, entry in enumerate(entries, 1):
            title     = entry.find("atom:title", namespace).text.strip()
            summary   = entry.find("atom:summary", namespace).text.strip()
            published = entry.find("atom:published", namespace).text.strip()
            arxiv_id  = entry.find("atom:id", namespace).text.strip()
            authors   = [
                a.find("atom:name", namespace).text
                for a in entry.findall("atom:author", namespace)
            ]

            results.append(
                f"[{i}] Title     : {title}\n"
                f"    Authors   : {', '.join(authors)}\n"
                f"    Published : {published[:10]}\n"
                f"    Arxiv ID  : {arxiv_id}\n"
                f"    Summary   : {summary[:300]}...\n"
            )

        return "\n".join(results)