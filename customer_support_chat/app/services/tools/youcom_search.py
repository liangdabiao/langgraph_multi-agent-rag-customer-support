# customer_support_chat/app/services/tools/youcom_search.py

import json
from typing import Any, Dict, List, Optional

import httpx
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from customer_support_chat.app.core.settings import get_settings

# Keyless You.com MCP endpoint (free profile). No API key is required.
# Setting YOUCOM_API_KEY / YDC_API_KEY switches to the authenticated endpoint
# with the full search toolset.
DEFAULT_YOUCOM_FREE_URL = "https://api.you.com/mcp?profile=free"
DEFAULT_YOUCOM_AUTH_URL = "https://api.you.com/mcp"

_MCP_PROTOCOL_VERSION = "2025-06-18"
_MCP_CLIENT_INFO = {"name": "customer-support-chat", "version": "0.1.0"}


def _parse_rpc_payload(response: httpx.Response) -> Dict[str, Any]:
    """Parse a You.com MCP JSON-RPC response.

    The server answers either with a plain JSON body or with an SSE stream
    (``text/event-stream``) whose ``data:`` lines each carry one JSON-RPC
    frame. Progress/notification frames do not carry a ``result``, so the
    first frame that does is the actual response.

    Frames are split on LF/CRLF only: ``str.splitlines()`` would also split
    on unicode line separators that can legally appear inside result payloads.
    """
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" not in content_type:
        return response.json()

    frames: List[Dict[str, Any]] = []
    for raw_line in response.text.split("\n"):
        line = raw_line.rstrip("\r")
        if not line.startswith("data:"):
            continue
        payload_text = line[len("data:"):].strip()
        if not payload_text:
            continue
        try:
            frame = json.loads(payload_text)
        except json.JSONDecodeError:
            continue
        if isinstance(frame, dict) and ("result" in frame or "error" in frame):
            frames.append(frame)

    if frames:
        return frames[0]
    raise Exception("You.com search: could not parse the MCP response.")


def _extract_web_results(payload: Any) -> List[Dict[str, Any]]:
    """Unwrap the you-search result payload into a list of web result dicts."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    results = payload.get("results")
    if isinstance(results, dict):
        web = results.get("web")
        if isinstance(web, list):
            return [item for item in web if isinstance(item, dict)]
    web = payload.get("web")
    if isinstance(web, list):
        return [item for item in web if isinstance(item, dict)]
    return []


def _snippet_of(item: Dict[str, Any]) -> str:
    """Best-effort snippet for a result, mirroring the DDG tool contract."""
    snippet = item.get("description") or ""
    if not snippet:
        candidates = [
            item.get("snippets"),
            (item.get("contents") or {}).get("highlights")
            if isinstance(item.get("contents"), dict)
            else None,
            item.get("highlights"),
        ]
        for values in candidates:
            if values:
                snippet = str(values[0])
                break
    return snippet


def youcom_mcp_search(
    query: str,
    count: int,
    url: str,
    api_key: str = "",
    timeout: int = 15,
) -> List[Dict[str, Any]]:
    """Run a web search through the You.com MCP server.

    Speaks the MCP streamable-HTTP JSON-RPC protocol over httpx:
    ``initialize`` -> ``notifications/initialized`` -> ``tools/call you-search``.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    with httpx.Client(timeout=timeout) as client:
        # 1) Initialize the MCP session.
        response = client.post(
            url,
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": _MCP_PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": _MCP_CLIENT_INFO,
                },
            },
        )
        response.raise_for_status()
        init_payload = _parse_rpc_payload(response)
        init_error = init_payload.get("error")
        if init_error:
            raise Exception(
                f"You.com search: MCP initialization failed: {init_error}"
            )
        session_id = response.headers.get("mcp-session-id")
        if session_id:
            headers["Mcp-Session-Id"] = session_id

        # 2) Notify the server that initialization is done (202 / empty body).
        client.post(
            url,
            headers=headers,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )

        # 3) Call the you-search tool.
        response = client.post(
            url,
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "you-search",
                    "arguments": {"query": query, "count": count},
                },
            },
        )
        response.raise_for_status()
        payload = _parse_rpc_payload(response)

    error = payload.get("error")
    if error:
        raise Exception(f"You.com search: MCP call failed: {error}")
    result = payload.get("result") or {}
    if result.get("isError"):
        raise Exception("You.com search: the you-search tool reported an error.")

    content = result.get("content") or []
    text = "".join(
        part.get("text", "") for part in content if isinstance(part, dict)
    )
    if not text:
        raise Exception("You.com search: empty response from the you-search tool.")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Exception(
            f"You.com search: could not parse search results: {exc}"
        ) from exc
    return _extract_web_results(data)


class YouComSearchResults(BaseTool):
    """Tool that queries You.com Search and gets back a string of results.

    Opt-in alternative to ``DuckDuckGoSearchResults`` for the primary
    assistant's web search (enabled via ``YOUCOM_SEARCH_ENABLED``). Keyless by
    default through the You.com MCP free profile (``YOUCOM_MCP_URL``), or
    authenticated with ``YOUCOM_API_KEY`` / ``YDC_API_KEY``. Results are
    formatted like the DuckDuckGo tool so the assistant consumes either one
    interchangeably.
    """

    name: str = "youcom_results_json"
    description: str = (
        "A wrapper around You.com Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. Output is a string of the query results"
    )
    max_results: int = 10
    timeout: int = 15
    results_separator: str = ", "

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        settings = get_settings()
        url = settings.YOUCOM_MCP_URL or DEFAULT_YOUCOM_FREE_URL
        if settings.YOUCOM_API_KEY and url == DEFAULT_YOUCOM_FREE_URL:
            # An API key was provided: use the authenticated endpoint unless
            # the MCP URL was explicitly overridden.
            url = DEFAULT_YOUCOM_AUTH_URL

        try:
            results = youcom_mcp_search(
                query=query,
                count=self.max_results,
                url=url,
                api_key=settings.YOUCOM_API_KEY,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise Exception(f"You.com search: request failed: {exc}") from exc

        if not results:
            return "No good You.com search result was found"

        res_strs = []
        for item in results:
            fields = []
            snippet = _snippet_of(item)
            if snippet:
                fields.append(f"snippet: {snippet}")
            if item.get("title"):
                fields.append(f"title: {item['title']}")
            if item.get("url"):
                fields.append(f"link: {item['url']}")
            if fields:
                res_strs.append(", ".join(fields))
        return self.results_separator.join(res_strs)
