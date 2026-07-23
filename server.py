"""Simple MCP Server — weather, time, and calculation tools.

Built as a learning project to understand the MCP (Model Context Protocol)
tool/resource/response model. Works with Claude Desktop, Claude Code,
and any other MCP-compatible client.

启动方式:
    python server.py
    或在 Claude Code 中: claude mcp add demo -- python server.py
"""

import json
import time
import math
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================
# Tool implementations
# ============================================================

def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """返回当前 UTC 时间戳 + 指定时区的可读时间。"""
    now_utc = datetime.utcnow()
    timestamp = int(time.time())
    return json.dumps({
        "utc": now_utc.isoformat() + "Z",
        "timestamp": timestamp,
        "timezone": timezone,
        "note": "This is UTC time. Add +8h for Beijing time."
    }, ensure_ascii=False, indent=2)


def get_weather(city: str) -> str:
    """模拟天气查询。实际使用时替换为真实 API。"""
    templates = {
        "南京": {"temp": 32, "condition": "多云", "humidity": 65},
        "苏州": {"temp": 31, "condition": "晴", "humidity": 60},
        "北京": {"temp": 28, "condition": "阴", "humidity": 55},
        "上海": {"temp": 33, "condition": "雷阵雨", "humidity": 75},
    }
    data = templates.get(city, {"temp": 25, "condition": "未知", "humidity": 50})
    data["city"] = city
    data["source"] = "mock — 替换为和风天气 / OpenWeatherMap API"
    return json.dumps(data, ensure_ascii=False, indent=2)


def calculate(expression: str) -> str:
    """安全计算数学表达式。"""
    allowed = set("0123456789+-*/().%^ eEπpi")
    cleaned = expression.replace("π", str(math.pi)).replace("pi", str(math.pi))
    if not all(c in allowed for c in cleaned.replace(" ", "")):
        return json.dumps({"error": "表达式包含不允许的字符"}, ensure_ascii=False)
    try:
        result = eval(cleaned, {"__builtins__": {}}, {"e": math.e, "pi": math.pi})
        return json.dumps({"expression": expression, "result": result}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ============================================================
# MCP protocol handler (stdio transport)
# ============================================================

TOOLS = [
    {
        "name": "get_current_time",
        "description": "获取当前时间（UTC + 指定时区）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "时区，如 Asia/Shanghai"}
            }
        }
    },
    {
        "name": "get_weather",
        "description": "查询指定城市的天气信息",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称，如 南京"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "安全计算数学表达式",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，如 (3+5)*2"}
            },
            "required": ["expression"]
        }
    }
]

RESOURCES = [
    {"uri": "server://status", "name": "Server Status", "mimeType": "application/json"},
    {"uri": "server://config", "name": "Server Configuration", "mimeType": "application/json"},
]

TOOL_MAP = {
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "calculate": calculate,
}

RESOURCE_MAP = {
    "server://status": lambda: json.dumps({"status": "running", "tools": len(TOOLS), "version": "0.1.0"}, ensure_ascii=False, indent=2),
    "server://config": lambda: json.dumps({"transport": "stdio", "protocol": "mcp/2024-11-05"}, ensure_ascii=False, indent=2),
}


def handle_request(request: dict) -> dict:
    """Process a single JSON-RPC style MCP request."""
    method = request.get("method", "")
    req_id = request.get("id", 0)

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "demo-mcp-server", "version": "0.1.0"}
            }
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = request["params"]["name"]
        tool_args = request["params"].get("arguments", {})
        fn = TOOL_MAP.get(tool_name)
        if not fn:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
        result_text = fn(**tool_args) if tool_args else fn()
        return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": result_text}]}}

    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": RESOURCES}}

    if method == "resources/read":
        uri = request["params"]["uri"]
        fn = RESOURCE_MAP.get(uri)
        if not fn:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Resource not found: {uri}"}}
        return {"jsonrpc": "2.0", "id": req_id, "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": fn()}]}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Read JSON-RPC requests line-by-line from stdin, write responses to stdout."""
    print("MCP Demo Server v0.1.0 — stdio transport", file=__import__('sys').stderr)
    for line in __import__('sys').stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response, ensure_ascii=False), flush=True)
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
