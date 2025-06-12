# How to Access Alpaca MCP Tools - User Guide

There are now **multiple ways** to discover and use the available tools in the Alpaca MCP Server:

## 📋 **Complete Tools Reference**

### **Full Documentation: `MCP_TOOLS_REFERENCE.md`**
- Comprehensive reference with 45+ tools
- Detailed parameters and examples
- Organized by trading categories
- Complete usage patterns and workflows

## 🚀 **Quick Access Methods**

### **1. Slash Commands (Recommended)**

Type these commands directly in Claude Code:

- **`/tools`** - List all available tools with descriptions
- **`/trading`** - Day trading tools quick reference  
- **`/analysis`** - Technical analysis tools and parameters

**How it works:** Slash commands are stored in `.claude/commands/` folder and become available in Claude Code when you type `/`

---

### **2. MCP Prompt**

Use the MCP prompt function:

```
list_all_tools()
```

**What it does:** Returns a formatted reference of all available tools organized by category with examples

---

### **3. Direct Tool Categories**

**Account & Portfolio:**
- `get_account_info()`, `get_positions()`, `close_position()`

**Market Data:**
- `get_stock_quote()`, `get_stock_snapshots()`, `get_stock_bars_intraday()`

**🔥 Technical Analysis:**
- `get_stock_peak_trough_analysis()` - **NEW** Peak/trough analysis tool

**Order Management:**
- `place_stock_order()`, `get_orders()`, `cancel_all_orders()`

**Streaming Data:**
- `start_global_stock_stream()`, `get_stock_stream_data()`

---

## 🎯 **Recommended Usage**

### **For New Users:**
1. Start with `/tools` slash command for overview
2. Use `list_all_tools()` MCP prompt for detailed reference
3. Check `MCP_TOOLS_REFERENCE.md` for complete documentation

### **For Day Trading:**
1. Use `/trading` slash command for essential workflow
2. Focus on `get_stock_peak_trough_analysis()` for entry points
3. Use streaming tools for real-time monitoring

### **For Technical Analysis:**
1. Use `/analysis` slash command for analysis tools
2. Experiment with different parameters for `get_stock_peak_trough_analysis()`
3. Combine with streaming data for live signals

---

## 📚 **Documentation Hierarchy**

1. **Quick Access:** Slash commands (`/tools`, `/trading`, `/analysis`)
2. **Interactive:** MCP prompt (`list_all_tools()`)
3. **Complete Reference:** `MCP_TOOLS_REFERENCE.md` file
4. **Specific Tool:** `PEAK_TROUGH_ANALYSIS_TOOL.md` for detailed technical analysis

---

## 🛠 **Implementation Details**

### **Slash Commands Location:**
```
.claude/commands/
├── tools.md          # Complete tools listing
├── trading.md        # Day trading workflow
└── analysis.md       # Technical analysis tools
```

### **MCP Server Registration:**
- **Tools:** Registered with `@mcp.tool()` decorator
- **Prompts:** Registered with `@mcp.prompt()` decorator
- **Access:** Available through Claude Desktop, Cursor, VSCode

### **Tool Naming Convention:**
All stock-related tools follow the pattern:
- `get_stock_*` - Data retrieval tools
- `place_stock_*` - Order placement tools  
- `start_*_stock_*` - Streaming tools

---

## 🎉 **New Features Highlighted**

### **Peak/Trough Analysis Tool**
- **Function:** `get_stock_peak_trough_analysis()`
- **Purpose:** Zero-phase Hanning filtering + peak detection
- **Trading Integration:** Perfect for "SCAN LONGER before entry" lesson
- **Returns:** BUY/LONG and SELL/SHORT signals with precise price levels

### **Multiple Access Methods**
- **Slash Commands:** Quick workflow references
- **MCP Prompts:** Interactive tool listing
- **Complete Docs:** Comprehensive reference guide

---

## 💡 **Pro Tips**

1. **Bookmark** `/tools` for quick reference during trading
2. **Use** `get_stock_peak_trough_analysis()` before entering positions
3. **Combine** multiple tools for complete trading workflows
4. **Check** `health_check()` before starting trading sessions
5. **Always use** limit orders with `place_stock_order()`

This multi-layered approach ensures users can quickly find the right tools for their trading needs, whether they want a quick reference or complete documentation.