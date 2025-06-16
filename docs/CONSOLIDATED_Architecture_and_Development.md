# CONSOLIDATED Architecture and Development Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [Development Environment](#development-environment)
4. [MCP Development Guidelines](#mcp-development-guidelines)
5. [FastMCP Implementation](#fastmcp-implementation)
6. [Production Deployment](#production-deployment)
7. [Performance Optimization](#performance-optimization)
8. [Resource Management](#resource-management)
9. [Advanced Features](#advanced-features)

---

## Project Overview

### 🚀 Professional Alpaca MCP Server

A sophisticated **Model Context Protocol (MCP) server** that transforms Alpaca's Trading API into an intelligent trading assistant for LLMs. Built with advanced prompt engineering, modular architecture, and institutional-grade market analysis capabilities.

### 🧠 Design Philosophy: Intelligence Over Integration

Instead of simple API passthrough, we built an **intelligent trading assistant** that:
- **Interprets market conditions** using advanced prompts
- **Combines multiple data sources** for comprehensive analysis
- **Provides actionable insights** rather than raw data
- **Scales to institutional requirements** with professional-grade tools

### Core Development Principles

- **Do not simplify the tools or pretend to solve the problems - actually solve the problems. Never mock - engineer.**
- **I don't want hype, propaganda, or mock functionality - only real engineering solutions**
- **Use the MCP tools, not direct Alpaca API methods. If the tools do not exist in the MCP server, we will create them.**
- **You can use the get_stock_bars_intraday MCP tool to fetch historical intraday bar data for MULTIPLE STOCK SYMBOLS at one time - this is more efficient than individual stock symbol tool use.**

---

## Architecture Deep Dive

### 🏗️ Enterprise Architecture Hierarchy

```
Enterprise Architecture = Prompts + Tools + Resources + Configuration
```

#### **Intelligence Hierarchy (Highest to Lowest Leverage)**

🥇 **PROMPTS** (Highest Leverage - "Intelligent Orchestration")
├── Intelligent workflows that guide users through complete strategies
├── Compose multiple tools and resources automatically
├── Transform raw data into actionable trading intelligence
└── Examples: account_analysis(), position_management(), market_analysis()

🥈 **TOOLS** (Action Execution)
├── Single-purpose functions that execute specific operations
├── Account, Position, Order, Market Data operations
├── Building blocks orchestrated by prompts
└── Examples: place_stock_order(), get_stock_quote(), stream_data()

🥉 **RESOURCES** (Data Context - Lowest Leverage)
├── Real-time data and state information providers
├── account://status - Live account metrics
├── positions://current - Real-time P&L data
└── market://conditions - Market status and momentum

### 📊 Layer Architecture (Correct Priority Order)

```
Enterprise Architecture = Prompts > Tools > Resources + Configuration
```

```
alpaca_mcp_server/
├── prompts/           # 🥇 HIGHEST: Intelligent orchestration
├── tools/            # 🥈 MIDDLE: Action execution (40+ tools)
├── resources/        # 🥉 LOWEST: Data context providers
├── config/           # Configuration management
└── models/           # Type-safe data structures
```

#### 1. **Prompt Engineering Layer** (`prompts/`)
**Purpose**: Transform raw API data into intelligent trading insights

```python
prompts/
├── account_analysis_prompt.py     # Portfolio health & risk assessment
├── position_management_prompt.py  # Intelligent position analysis
├── market_analysis_prompt.py      # Market condition interpretation
├── risk_management_prompt.py      # Multi-factor risk scoring
├── options_strategy_prompt.py     # Options trading strategies
├── portfolio_review_prompt.py     # Performance attribution
├── pro_technical_workflow.py      # Professional technical analysis
├── startup_prompt.py              # Day trading startup checks
└── list_trading_capabilities.py   # Capabilities discovery
```

**Key Features:**
- **Multi-source data fusion**: Combines account, position, and market data
- **Contextual analysis**: Interprets performance relative to market conditions
- **Actionable recommendations**: Specific next steps, not just status
- **Professional formatting**: Institutional-quality reporting

#### 2. **Tools Layer** (`tools/`) - Action Execution
**Purpose**: Specialized functions that execute specific trading operations

```python
tools/
├── account/           # Account & portfolio management
│   ├── account_info.py      # Account details & balances
│   ├── positions.py         # Position management
│   └── portfolio_history.py # Performance tracking
├── market_data/       # Advanced market data
│   ├── stocks.py           # Enhanced stock data (10K bars)
│   ├── options.py          # Options chains & Greeks
│   ├── snapshots.py        # Comprehensive market snapshots
│   ├── streaming.py        # Real-time data feeds
│   └── advanced_plotting_tool.py  # Professional plotting
├── orders/            # Professional order management
│   ├── stock_orders.py     # All stock order types
│   ├── option_orders.py    # Multi-leg options strategies
│   └── order_management.py # Order lifecycle management
├── assets/            # Asset discovery & analysis
└── watchlist/         # Portfolio tracking
```

**Advanced Tool Features:**
- **Enhanced data limits**: 10,000 intraday bars (vs typical 100)
- **Professional timeframes**: 1-minute default for institutional analysis
- **Multi-asset support**: Stocks, options, ETFs unified interface
- **Error handling**: Graceful degradation with actionable error messages

#### 3. **Resources Layer** (`resources/`) - Data Context
**Purpose**: Real-time analysis engines for institutional-grade insights

```python
resources/
├── market_momentum.py       # Technical analysis engine
├── data_quality.py         # Feed quality monitoring
├── intraday_pnl.py         # Performance analytics
├── streaming_resources.py  # Real-time data management
├── api_monitor.py          # Connection health monitoring
└── server_health.py        # System status tracking
```

**Resource Capabilities:**
- **Configurable parameters**: Customize analysis to trading style
- **Real-time computation**: Live market analysis during trading hours
- **Quality monitoring**: Latency, spread, and data freshness tracking
- **Professional metrics**: Institutional-grade performance analytics
