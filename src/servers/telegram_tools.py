"""
Telegram tool parsing and execution for parity with the HTML client.
Used only by the proxy Telegram chat endpoint; does not modify the web client.
"""

import ast
import asyncio
import json
import re
from typing import Any, Dict, List, Optional

# Maximum length for calculate expression to avoid abuse
CALC_EXPR_MAX_LEN = 200
# Allowed characters for safe calculate (numbers, spaces, + - * / ( ) .)
CALC_ALLOWED_RE = re.compile(r"^[\d\s+\-*/().]+$")


def parse_telegram_tool_response(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse assistant content for a single tool call in the same format as the web client.
    Looks for <tool>name</tool><parameters>{...}</parameters> at top-level (no leading/trailing text).
    Strips fenced code blocks before matching so example snippets are not executed.
    Optionally supports JSON-style and contentPrompt fallbacks.
    Returns a dict with keys 'name' and 'arguments' (JSON string), or None if no valid tool call.
    """
    if not content or not isinstance(content, str):
        return None
    # Strip fenced code blocks to avoid executing examples
    content_without_code = re.sub(r"```[\s\S]*?```", "", content)
    # XML format: top-level only
    tool_match = re.search(r"<tool>(.*?)</tool>", content_without_code)
    params_match = re.search(r"<parameters>([\s\S]*?)</parameters>", content_without_code)
    if tool_match and params_match:
        try:
            leading = content_without_code[: tool_match.start()].strip()
            trailing = content_without_code[params_match.end() :].strip()
            if leading or trailing:
                return None
            tool_name = tool_match.group(1).strip()
            params_str = params_match.group(1).strip()
            params = json.loads(params_str)
            return {"name": tool_name, "arguments": json.dumps(params) if isinstance(params, dict) else params_str}
        except (json.JSONDecodeError, ValueError):
            pass
    # JSON-style: content is JSON object
    trimmed = content.strip()
    if trimmed.startswith("{") or trimmed.startswith("["):
        try:
            obj = json.loads(trimmed)
            if isinstance(obj, dict):
                if obj.get("action") and obj.get("contentPrompt") is not None:
                    return {
                        "name": obj.get("action", "runWorkflow"),
                        "arguments": json.dumps({"contentPrompt": obj["contentPrompt"]}),
                    }
                if obj.get("name") and "arguments" in obj:
                    args = obj["arguments"]
                    return {
                        "name": obj["name"],
                        "arguments": args if isinstance(args, str) else json.dumps(args),
                    }
        except json.JSONDecodeError:
            pass
    if "contentPrompt" in trimmed and trimmed.strip():
        return {"name": "runWorkflow", "arguments": trimmed}
    return None


def _safe_calculate(expression: str) -> Optional[float]:
    """
    Evaluate a simple math expression safely. Only allows numbers and + - * / ( ).
    Returns None on invalid or unsafe input.
    """
    if not expression or len(expression) > CALC_EXPR_MAX_LEN:
        return None
    expr = expression.strip()
    if not CALC_ALLOWED_RE.match(expr):
        return None
    try:
        tree = ast.parse(expr, mode="eval")
        if not isinstance(tree.body, (ast.BinOp, ast.UnaryOp, ast.Constant)):
            return None
        # Only allow Constant (numbers) and BinOp/UnaryOp
        def allowed(node):
            if isinstance(node, ast.Constant):
                return isinstance(node.value, (int, float))
            if isinstance(node, ast.BinOp):
                return isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)) and allowed(node.left) and allowed(node.right)
            if isinstance(node, ast.UnaryOp):
                return isinstance(node.op, (ast.UAdd, ast.USub)) and allowed(node.operand)
            return False
        if not allowed(tree.body):
            return None
        return eval(compile(tree, "<calc>", "eval"))
    except Exception:
        return None


async def execute_telegram_tool(
    name: str,
    arguments: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Execute a single tool by name with the given arguments.
    context must include: conversation_id, and optionally:
    - todo_store: Dict[str, list], memory_cache_store: Dict[str, list]
    - do_search, do_fetch, do_news, do_autogen, do_browser_agent, do_deep_research (async callables)
    - read_file_internal, write_file_internal, list_files_internal (callables)
    - upload_drive_internal (callable), memory_manager (object with store/search/list/delete)
    Returns a dict with success (bool), message (str), and optional data.
    """
    cid = context.get("conversation_id") or "default"
    todo_store = context.get("todo_store") or {}
    memory_cache_store = context.get("memory_cache_store") or {}

    def todo_list() -> List[str]:
        return todo_store.setdefault(cid, [])

    def mem_cache() -> List[str]:
        return memory_cache_store.setdefault(cid, [])

    # --- manageTodoList ---
    if name == "manageTodoList":
        action = (arguments.get("action") or "").strip().lower()
        task_id = arguments.get("taskId")
        task_description = (arguments.get("taskDescription") or "").strip()
        tasks = todo_list()
        if action == "list":
            if not tasks:
                return {"success": True, "message": "Your todo list is empty."}
            lines = [f"{i + 1}. {t}" for i, t in enumerate(tasks)]
            return {"success": True, "message": "Here are your current tasks:\n" + "\n".join(lines)}
        if action == "add":
            if not task_description:
                return {"success": False, "message": "Task description is required."}
            tasks.append(task_description)
            return {"success": True, "message": f"Added task: {task_description}"}
        if action == "update":
            if task_id is None or not task_description:
                return {"success": False, "message": "Both task ID and new description are required."}
            idx = int(task_id) if isinstance(task_id, (int, float)) else None
            if idx is None or idx < 1 or idx > len(tasks):
                return {"success": False, "message": "Invalid task ID."}
            old = tasks[idx - 1]
            tasks[idx - 1] = task_description
            return {"success": True, "message": f'Updated task {idx} from "{old}" to "{task_description}"'}
        if action == "delete":
            if task_id is None:
                return {"success": False, "message": "Task ID is required."}
            idx = int(task_id) if isinstance(task_id, (int, float)) else None
            if idx is None or idx < 1 or idx > len(tasks):
                return {"success": False, "message": "Invalid task ID."}
            deleted = tasks.pop(idx - 1)
            return {"success": True, "message": f"Deleted task: {deleted}"}
        if action == "clear":
            tasks.clear()
            return {"success": True, "message": "Todo list has been cleared."}
        return {"success": False, "message": "Invalid action."}

    # --- manageMemoryCache ---
    if name == "manageMemoryCache":
        action = (arguments.get("action") or "").strip().lower()
        mem_id = arguments.get("memId")
        mem_description = (arguments.get("memDescription") or "").strip()
        items = mem_cache()
        if action == "list":
            if not items:
                return {"success": True, "message": "Memory cache is empty."}
            lines = [f"{i + 1}. {m}" for i, m in enumerate(items)]
            return {"success": True, "message": "Memory cache:\n" + "\n".join(lines)}
        if action == "add":
            if not mem_description:
                return {"success": False, "message": "Memory description is required."}
            items.append(mem_description)
            return {"success": True, "message": f"Added to memory cache: {mem_description}"}
        if action == "update":
            if mem_id is None or not mem_description:
                return {"success": False, "message": "Both memId and memDescription are required."}
            idx = int(mem_id) if isinstance(mem_id, (int, float)) else None
            if idx is None or idx < 1 or idx > len(items):
                return {"success": False, "message": "Invalid memId."}
            items[idx - 1] = mem_description
            return {"success": True, "message": "Updated memory cache entry."}
        if action == "delete":
            if mem_id is None:
                return {"success": False, "message": "memId is required."}
            idx = int(mem_id) if isinstance(mem_id, (int, float)) else None
            if idx is None or idx < 1 or idx > len(items):
                return {"success": False, "message": "Invalid memId."}
            items.pop(idx - 1)
            return {"success": True, "message": "Deleted from memory cache."}
        if action == "clear":
            items.clear()
            return {"success": True, "message": "Memory cache has been cleared."}
        return {"success": False, "message": "Invalid action."}

    # --- navigateToUrl / openChatToUser ---
    if name in ("navigateToUrl", "openChatToUser"):
        url = (arguments.get("url") or "").strip()
        if not url:
            return {"success": False, "message": "URL is required."}
        return {
            "success": True,
            "message": f"Here's the link: {url}. In Telegram I can't open it; open it in your browser.",
        }

    # --- calculate ---
    if name == "calculate":
        expr = (arguments.get("expression") or "").strip()
        result = _safe_calculate(expr)
        if result is None:
            return {"success": False, "message": "Invalid or unsafe expression."}
        return {"success": True, "message": str(result), "data": {"result": result}}

    # --- runWorkflow ---
    if name == "runWorkflow":
        do_autogen = context.get("do_autogen")
        if not do_autogen:
            return {"success": False, "message": "Workflow (AutoGen) is not available."}
        prompt = (arguments.get("contentPrompt") or "").strip()
        if not prompt:
            return {"success": False, "message": "contentPrompt is required."}
        result = await do_autogen(prompt)
        msg = result.get("output") or result.get("response") or result.get("detail", str(result))
        return {"success": True, "message": msg, "data": result}

    # --- scrapeWebsite ---
    if name == "scrapeWebsite":
        do_fetch = context.get("do_fetch")
        if not do_fetch:
            return {"success": False, "message": "Web fetch is not available."}
        url = (arguments.get("url") or "").strip()
        if not url:
            return {"success": False, "message": "URL is required."}
        out = await do_fetch(url)
        content = (out.get("content") or "")[:4000]
        return {"success": True, "message": f"Fetched content (snippet):\n{content}", "data": out}

    # --- webSearch ---
    if name == "webSearch":
        do_search = context.get("do_search")
        if not do_search:
            return {"success": False, "message": "Web search is not available."}
        query = (arguments.get("query") or "").strip()
        if not query:
            return {"success": False, "message": "Query is required."}
        data = await do_search(query)
        results = data.get("results") or []
        lines = [f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results[:5]]
        return {"success": True, "message": "Search results:\n" + "\n".join(lines) if lines else "No results.", "data": data}

    # --- fetchNews ---
    if name == "fetchNews":
        do_news = context.get("do_news")
        write_internal = context.get("write_file_internal")
        if not do_news or not write_internal:
            return {"success": False, "message": "News or file write is not available."}
        search_term = (arguments.get("searchTerm") or arguments.get("query") or "").strip()
        filename = (arguments.get("filename") or "news.csv").strip() or "news.csv"
        if not search_term:
            return {"success": False, "message": "searchTerm is required."}
        data = await do_news(search_term)
        articles = data.get("articles") or []
        if not articles:
            return {"success": True, "message": f"No articles found for \"{search_term}\"."}
        csv_lines = ["Title,URL"]
        for a in articles:
            title = (a.get("title") or "").replace(",", " ")
            url = a.get("url") or ""
            csv_lines.append(f'"{title}","{url}"')
        csv_content = "\n".join(csv_lines)
        wr = await write_internal(filename, csv_content, "txt")
        if isinstance(wr, dict) and not wr.get("success"):
            return {"success": False, "message": wr.get("message", "Failed to write file.")}
        return {"success": True, "message": f"Saved {len(articles)} news articles to {filename}."}

    # --- readFile ---
    if name == "readFile":
        read_internal = context.get("read_file_internal")
        if not read_internal:
            return {"success": False, "message": "File read is not available."}
        filename = (arguments.get("filename") or "").strip()
        if not filename:
            return {"success": False, "message": "filename is required."}
        out = await read_internal(filename)
        if isinstance(out, dict) and not out.get("success"):
            return {"success": False, "message": out.get("message", "Read failed.")}
        data = out.get("data") or {}
        content = data.get("content", "")
        return {"success": True, "message": out.get("message", "Read OK"), "data": {"content": content}}

    # --- writeFile ---
    if name == "writeFile":
        write_internal = context.get("write_file_internal")
        if not write_internal:
            return {"success": False, "message": "File write is not available."}
        filename = (arguments.get("filename") or "").strip()
        content = arguments.get("content", "")
        fmt = (arguments.get("format") or "txt").strip().lower() or "txt"
        if not filename:
            return {"success": False, "message": "filename is required."}
        out = await write_internal(filename, str(content), fmt)
        if isinstance(out, dict) and not out.get("success"):
            return {"success": False, "message": out.get("message", "Write failed.")}
        return {"success": True, "message": out.get("message", "Write OK.")}

    # --- listFiles ---
    if name == "listFiles":
        list_internal = context.get("list_files_internal")
        if not list_internal:
            return {"success": False, "message": "File list is not available."}
        out = await list_internal()
        if isinstance(out, dict) and not out.get("success"):
            return {"success": False, "message": out.get("message", "List failed.")}
        files = out.get("files") or []
        lines = [f"- {f.get('name', '')}" for f in files]
        return {"success": True, "message": "Files:\n" + "\n".join(lines) if lines else "No files.", "data": out}

    # --- saveToFile (map to writeFile) ---
    if name == "saveToFile":
        return await execute_telegram_tool(
            "writeFile",
            {"filename": arguments.get("filename", "saved.txt"), "content": arguments.get("content", ""), "format": "txt"},
            context,
        )

    # --- storeMemory ---
    if name == "storeMemory":
        mm = context.get("memory_manager")
        if not mm:
            return {"success": False, "message": "Memory system is not available."}
        text = (arguments.get("text") or arguments.get("content") or "").strip()
        if not text:
            return {"success": False, "message": "text is required."}
        mid = await mm.store_memory(text=text, source="telegram")
        return {"success": True, "message": "Memory stored.", "data": {"memory_id": mid}}

    # --- searchMemories ---
    if name == "searchMemories":
        mm = context.get("memory_manager")
        if not mm:
            return {"success": False, "message": "Memory system is not available."}
        query = (arguments.get("query") or "").strip()
        if not query:
            return {"success": False, "message": "query is required."}
        results = await mm.search_memories(query=query, limit=arguments.get("limit", 5))
        items = results or []
        lines = [f"- {m.get('text', '')}" for m in items]
        return {"success": True, "message": "Memories:\n" + "\n".join(lines) if lines else "No matches.", "data": {"memories": items}}

    # --- listMemories ---
    if name == "listMemories":
        mm = context.get("memory_manager")
        if not mm:
            return {"success": False, "message": "Memory system is not available."}
        try:
            mems = mm.list_memories(limit=arguments.get("limit", 20))
        except Exception:
            mems = []
        lines = [f"- {m.get('text', '')}" for m in (mems or [])]
        return {"success": True, "message": "Memories:\n" + "\n".join(lines) if lines else "No memories.", "data": {"memories": mems}}

    # --- deleteMemory ---
    if name == "deleteMemory":
        mm = context.get("memory_manager")
        if not mm:
            return {"success": False, "message": "Memory system is not available."}
        mid = (arguments.get("memory_id") or arguments.get("id") or "").strip()
        if not mid:
            return {"success": False, "message": "memory_id is required."}
        if asyncio.iscoroutinefunction(getattr(mm, "delete_memory", None)):
            await mm.delete_memory(mid)
        else:
            mm.delete_memory(mid)
        return {"success": True, "message": "Memory deleted."}

    # --- runBrowserAgent ---
    if name == "runBrowserAgent":
        do_browser = context.get("do_browser_agent")
        if not do_browser:
            return {"success": False, "message": "Browser agent is not available."}
        out = await do_browser(arguments)
        msg = out.get("message") or out.get("output") or str(out)[:500]
        return {"success": True, "message": msg, "data": out}

    # --- runDeepResearch ---
    if name == "runDeepResearch":
        do_research = context.get("do_deep_research")
        if not do_research:
            return {"success": False, "message": "Deep research is not available."}
        out = await do_research(arguments)
        msg = out.get("message") or out.get("output") or str(out)[:500]
        return {"success": True, "message": msg, "data": out}

    # --- pdfToPowerPoint ---
    if name == "pdfToPowerPoint":
        return {"success": True, "message": "PDF to PowerPoint is only available in the CATBot web interface. Please use the web app for this feature."}

    # --- uploadToGoogleDrive ---
    if name == "uploadToGoogleDrive":
        upload_internal = context.get("upload_drive_internal")
        if not upload_internal:
            return {"success": False, "message": "Google Drive upload is not available."}
        file_path = (arguments.get("filePath") or arguments.get("filename") or "").strip()
        file_name = (arguments.get("fileName") or "").strip() or None
        if not file_path:
            return {"success": False, "message": "filePath is required."}
        out = await upload_internal(file_path, file_name)
        if isinstance(out, dict) and not out.get("success", True):
            return {"success": False, "message": out.get("message", "Upload failed.")}
        return {"success": True, "message": out.get("message", "Uploaded to Google Drive.")}

    # --- llmQuery ---
    if name == "llmQuery":
        llm_internal = context.get("llm_query_internal")
        if not llm_internal:
            return {"success": True, "message": "Custom LLM queries are available in the CATBot web interface."}
        prompt = (arguments.get("contentPrompt") or arguments.get("query") or arguments.get("message") or "").strip()
        if not prompt:
            return {"success": False, "message": "query or contentPrompt is required."}
        out = await llm_internal(prompt)
        return {"success": True, "message": out.get("content", str(out)), "data": out}

    return {"success": False, "message": f"Unknown tool: {name}"}
