# MCP Demo Server

A simple Model Context Protocol (MCP) server with weather, time, and calculation tools — built as a learning project to understand the MCP tool/resource model.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that lets AI assistants like Claude securely access external tools and data sources. This server implements the protocol from scratch using stdio transport, without relying on the official SDK — to understand the underlying JSON-RPC message flow.

## Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_current_time` | Get UTC timestamp + timezone info | `timezone` (optional) |
| `get_weather` | Query weather for a city (mock) | `city` (required) |
| `calculate` | Safely evaluate math expressions | `expression` (required) |

## Resources

| URI | Content |
|-----|---------|
| `server://status` | Server runtime status (JSON) |
| `server://config` | Server configuration (JSON) |

## Quick Start

```bash
# No dependencies required — pure Python stdlib
python server.py
```

### Connect to Claude Code

```bash
claude mcp add demo -- python d:/mcp-demo-server/server.py
```

Then ask Claude:
- "What time is it?" → triggers `get_current_time`
- "What's the weather in Nanjing?" → triggers `get_weather`
- "Calculate (3+5)*2 for me" → triggers `calculate`
- "Show me the server status" → triggers `resources/read`

## Why This Exists

Built to understand:
1. The MCP JSON-RPC message format (initialize → tools/list → tools/call)
2. The difference between tools (actions) and resources (data)
3. How stdio transport works vs HTTP
4. How Claude Code discovers and invokes MCP servers

## License

MIT

## License

MIT
