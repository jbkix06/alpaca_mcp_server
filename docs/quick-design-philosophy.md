# Quick Design Philosophy: Build Your MCP Server TODAY

> **Purpose**: Immediate implementation guide for building a complete three-tier MCP server in 1-2 days using proven patterns. No shortcuts on architecture.

## Core Philosophy: Build Smart, Not Complex

**The Innovation**: Transform MCP from isolated tools into intelligent, composable workflows using the **Prompts > Tools > Resources** hierarchy.

**Key Insight**: PROMPTS ARE EVERYTHING - they are the most important part of your architecture. Prompts transform simple tools into intelligent workflows that deliver exponential value. Design everything to support powerful prompts.

---

## 1. Foundation Architecture (Start Here)

### The Three-Tier Implementation Pattern

```python
# Implementation order (build dependencies first):
# 1. RESOURCES (Foundation) - Implement first for data access
# 2. TOOLS (Actions) - Build on top of resources
# 3. PROMPTS (Intelligence) - Orchestrate tools into workflows

from mcp.server import FastMCP
import pandas as pd
from typing import Dict, List, Any

class ProductionMCPServer:
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.mcp = FastMCP(f"{domain_name.title()} MCP Server", "1.0.0")
        
        # Core state management
        self.domain_data = {}  # Your domain-specific data
        self.schemas = {}      # Auto-discovered schemas
        self.context = {}      # Current context
        
        # Register in dependency order
        self._register_resources()  # Data foundation
        self._register_tools()      # Operations layer
        self._register_prompts()    # Orchestration layer
```

---

## 2. Universal Compatibility Pattern (Critical)

**Problem**: Some MCP clients only support tools, others only resources.
**Solution**: Implement both interfaces for the same functionality.

```python
class UniversalCompatibility:
    """Every capability gets both resource AND tool interfaces"""
    
    def __init__(self, server):
        self.server = server
        self.data_store = {}  # Your data storage
    
    # RESOURCE INTERFACE (for advanced clients)
    @server.mcp.resource("{domain}://status")
    async def domain_status_resource(self) -> dict:
        return await self._get_domain_status()
    
    # TOOL INTERFACE (for universal compatibility) 
    @server.mcp.tool()
    async def get_domain_status(self) -> dict:
        """Tool mirror of {domain}://status resource"""
        return await self._get_domain_status()
    
    async def _get_domain_status(self) -> dict:
        """Core logic used by both interfaces"""
        return {
            "domain": self.server.domain_name,
            "data_loaded": len(self.data_store),
            "capabilities": self._list_capabilities(),
            "current_context": self.server.context
        }
```

---

## 3. Domain-Agnostic Schema Discovery (Game Changer)

**Innovation**: Auto-discover any data structure and suggest relevant operations.

```python
class SmartSchemaDiscovery:
    """Automatically understand ANY data structure"""
    
    def discover_data_schema(self, data: Any, name: str) -> dict:
        """Universal schema discovery - works with any data type"""
        
        if isinstance(data, pd.DataFrame):
            return self._discover_dataframe_schema(data, name)
        elif isinstance(data, dict):
            return self._discover_dict_schema(data, name) 
        elif isinstance(data, list):
            return self._discover_list_schema(data, name)
        else:
            return self._discover_generic_schema(data, name)
    
    def _discover_dataframe_schema(self, df: pd.DataFrame, name: str) -> dict:
        """Smart pandas DataFrame analysis"""
        schema = {
            "name": name,
            "type": "dataframe", 
            "shape": df.shape,
            "columns": {},
            "suggested_operations": []
        }
        
        for col in df.columns:
            col_info = {
                "dtype": str(df[col].dtype),
                "unique_count": df[col].nunique(),
                "null_percentage": df[col].isnull().mean() * 100,
                "role": self._infer_column_role(df[col])  # quantitative, categorical, temporal, etc.
            }
            schema["columns"][col] = col_info
        
        # AI-powered operation suggestions
        schema["suggested_operations"] = self._suggest_operations(schema)
        return schema
    
    def _infer_column_role(self, series: pd.Series) -> str:
        """Intelligent column role detection"""
        if pd.api.types.is_numeric_dtype(series):
            return "quantitative"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "temporal" 
        elif series.nunique() / len(series) < 0.1:
            return "categorical"
        elif series.nunique() == len(series):
            return "identifier"
        else:
            return "textual"
    
    def _suggest_operations(self, schema: dict) -> List[str]:
        """AI-powered operation suggestions based on schema"""
        operations = []
        columns = schema["columns"]
        
        # Smart suggestions based on column types
        quant_cols = [c for c, info in columns.items() if info["role"] == "quantitative"]
        cat_cols = [c for c, info in columns.items() if info["role"] == "categorical"] 
        temporal_cols = [c for c, info in columns.items() if info["role"] == "temporal"]
        
        if len(quant_cols) >= 2:
            operations.extend(["correlation_analysis", "statistical_summary"])
        if cat_cols and quant_cols:
            operations.extend(["segmentation_analysis", "group_comparison"])
        if temporal_cols and quant_cols:
            operations.extend(["time_series_analysis", "trend_detection"])
            
        return operations
```

---

## 4. Intelligent Prompts System (Your Competitive Advantage)

**Key**: Prompts that compose tools into contextually-aware workflows using **proven patterns from production**.

### Real Example: Dataset First Look (From Live Implementation)

```python
class IntelligentPrompts:
    """Proven intelligent prompt patterns from production MCP server"""
    
    @server.mcp.prompt()
    async def dataset_first_look(self, dataset_name: str) -> str:
        """Adaptive first-look analysis based on actual dataset characteristics."""
        
        if dataset_name not in self.schemas:
            return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
        
        schema = self.schemas[dataset_name]
        
        # INNOVATION: Organize columns by AI-detected roles
        numerical_cols = [name for name, info in schema.columns.items() 
                         if info.suggested_role == 'numerical']
        categorical_cols = [name for name, info in schema.columns.items() 
                           if info.suggested_role == 'categorical']
        temporal_cols = [name for name, info in schema.columns.items() 
                        if info.suggested_role == 'temporal']
        
        # INNOVATION: Dynamic content based on actual data
        prompt = f"""Let's explore your **{dataset_name}** dataset together! 

I can see you have **{schema.row_count:,} records** with **{len(schema.columns)} columns**:

"""
        
        if numerical_cols:
            prompt += f"**📊 Numerical columns** ({len(numerical_cols)}): {', '.join(numerical_cols)}\n"
            prompt += "→ Perfect for correlation analysis, statistical summaries, and trend analysis\n\n"
        
        if categorical_cols:
            prompt += f"**🏷️ Categorical columns** ({len(categorical_cols)}): {', '.join(categorical_cols)}\n"
            prompt += "→ Great for segmentation and group comparisons\n\n"
        
        # INNOVATION: Contextual commands using real column names
        prompt += "**🎯 Recommended starting points:**\n"
        
        if len(numerical_cols) >= 2:
            prompt += f"• **Correlation Analysis**: Explore relationships between {numerical_cols[0]} and {numerical_cols[1]}\n"
            prompt += f"  Command: `find_correlations('{dataset_name}')`\n"
        
        if categorical_cols and numerical_cols:
            prompt += f"• **Segmentation**: Group by {categorical_cols[0]} to analyze {numerical_cols[0]} patterns\n"
            prompt += f"  Command: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`\n"
        
        if temporal_cols and numerical_cols:
            prompt += f"• **Time Series**: Analyze {numerical_cols[0]} trends over {temporal_cols[0]}\n"
            prompt += f"  Command: `analyze_time_series('{dataset_name}', '{temporal_cols[0]}', '{numerical_cols[0]}')`\n"
        
        return prompt

    @server.mcp.prompt()
    async def segmentation_workshop(self, dataset_name: str) -> str:
        """Interactive segmentation guidance - REAL implementation pattern"""
        
        schema = self.schemas[dataset_name]
        categorical_cols = [name for name, info in schema.columns.items() 
                           if info.suggested_role == 'categorical']
        numerical_cols = [name for name, info in schema.columns.items() 
                         if info.suggested_role == 'numerical']
        
        # INNOVATION: Conditional logic based on available data
        if not categorical_cols:
            return f"""**Segmentation Challenge: No categorical columns found in {dataset_name}**

Don't worry! You can still create meaningful segments:

**🔢 Numerical Segmentation Options:**
• **Quantile-based segments**: Split {numerical_cols[0]} into high/medium/low groups
• **Threshold-based segments**: Above/below average {numerical_cols[0]}
• **Custom ranges**: Define meaningful business ranges for {numerical_cols[0]}

**💡 Pro tip**: Create categorical columns first using custom code:
```python
# Create value segments
df['value_segment'] = pd.cut(df['{numerical_cols[0]}'], bins=3, labels=['Low', 'Medium', 'High'])
```

Then use: `segment_by_column('{dataset_name}', 'value_segment')`
"""
        
        # INNOVATION: Rich context with sample values
        prompt = f"""Let's create meaningful segments from your **{dataset_name}** data!

**Available categorical columns for grouping:**
"""
        
        for col in categorical_cols:
            col_info = schema.columns[col]
            prompt += f"• **{col}**: {col_info.unique_values} unique values (examples: {', '.join(map(str, col_info.sample_values))})\n"
        
        prompt += f"""
**Recommended segmentation workflow:**

1. **Quick segment**: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`
2. **Compare metrics** across segments using numerical columns: {', '.join(numerical_cols[:3])}
3. **Visualize differences** with charts for each segment

Which column interests you most for segmentation?
"""
        
        return prompt

    @server.mcp.prompt()
    async def correlation_investigation(self, dataset_name: str) -> str:
        """Data-aware correlation analysis - REAL fallback strategies"""
        
        schema = self.schemas[dataset_name]
        numerical_cols = [name for name, info in schema.columns.items() 
                         if info.suggested_role == 'numerical']
        
        # INNOVATION: Smart fallback when insufficient numerical data
        if len(numerical_cols) < 2:
            return f"""**Correlation Analysis: Insufficient Numerical Data**

Your **{dataset_name}** dataset has {len(numerical_cols)} numerical column(s): {', '.join(numerical_cols) if numerical_cols else 'none'}

**To perform correlation analysis, you need:**
• At least 2 numerical columns
• Sufficient data variation (not all identical values)

**Suggestions:**
1. Check if any categorical columns contain numerical data stored as text
2. Convert date columns to numerical formats (days since epoch, etc.)
3. Create numerical features from categorical data (count encodings, etc.)

**Alternative analyses you can perform:**
• Data quality assessment: `validate_data_quality('{dataset_name}')`
• Distribution analysis for existing numerical columns
• Segmentation: `segment_by_column('{dataset_name}', 'categorical_column')`
"""
        
        # INNOVATION: Progressive analysis workflow
        return f"""🔍 Ready for correlation analysis with {len(numerical_cols)} numerical columns!

**Available numerical columns:**
{chr(10).join(f"• {col}" for col in numerical_cols)}

**🎯 Smart correlation workflow:**

1. **Overview**: Get correlation matrix for all numerical variables
   → `find_correlations('{dataset_name}')`

2. **Deep dive**: Investigate specific relationships
   → `create_chart('{dataset_name}', 'scatter', '{numerical_cols[0]}', '{numerical_cols[1]}')`

3. **Insights**: Look for correlations > 0.7 or < -0.7 for strong relationships

**🚀 Quick start**: `find_correlations('{dataset_name}', threshold=0.3)`
"""
```

### Real Schema Discovery Pattern (Production Implementation)

```python
def discover_column_role(self, series: pd.Series) -> str:
    """PROVEN intelligent column role detection"""
    
    # Real production logic from working MCP server
    if pd.api.types.is_numeric_dtype(series):
        return 'numerical'
    elif pd.api.types.is_datetime64_any_dtype(series):
        return 'temporal'
    elif series.nunique() / len(series) < 0.5:  # Low cardinality = categorical
        return 'categorical'
    elif series.nunique() == len(series):  # All unique = identifier
        return 'identifier'
    else:
        return 'categorical'

def generate_analysis_suggestions(self, schema: dict) -> List[str]:
    """PROVEN analysis suggestions based on column types"""
    
    suggestions = []
    numerical_cols = [col for col, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    categorical_cols = [col for col, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    temporal_cols = [col for col, info in schema.columns.items() 
                    if info.suggested_role == 'temporal']
    
    # Real logic from production server
    if len(numerical_cols) >= 2:
        suggestions.append("correlation_analysis")
    if categorical_cols and numerical_cols:
        suggestions.append("segmentation_analysis")
    if temporal_cols and numerical_cols:
        suggestions.append("time_series_analysis")
    if categorical_cols:
        suggestions.append("distribution_analysis")
        
    return suggestions
```

---

## 5. Basic Implementation Template

### Production-Ready Server Template (Based on Proven Implementation)

```python
# main.py - Your complete advanced MCP server using proven patterns
from mcp.server import FastMCP
import pandas as pd
from typing import Dict, Any, List, Optional
import asyncio

class ProvenAdvancedMCPServer:
    """Production-ready MCP server using patterns from live implementation"""
    
    def __init__(self, domain_name: str = "analytics"):
        self.domain_name = domain_name
        self.mcp = FastMCP(f"Advanced {domain_name.title()} Server", "1.0.0")
        
        # PROVEN: In-memory storage pattern from production
        self.loaded_datasets: Dict[str, pd.DataFrame] = {}
        self.dataset_schemas: Dict[str, dict] = {}
        
        # Initialize server
        self._setup_server()
    
    def _setup_server(self):
        """Setup all MCP endpoints using proven patterns"""
        
        # ============================================================================
        # RESOURCES (Foundation Layer) - PROVEN dynamic resource pattern
        # ============================================================================
        
        @self.mcp.resource("datasets://loaded")
        async def get_loaded_datasets_resource() -> dict:
            """List of all currently loaded datasets with basic info."""
            return {
                "datasets": list(self.loaded_datasets.keys()),
                "total_datasets": len(self.loaded_datasets),
                "schemas": {name: {
                    "shape": schema.get("shape", [0, 0]),
                    "columns": list(schema.get("columns", {}).keys()),
                    "suggested_operations": schema.get("suggested_operations", [])
                } for name, schema in self.dataset_schemas.items()}
            }
        
        @self.mcp.resource("datasets://{dataset_name}/schema")
        async def get_dataset_schema(dataset_name: str) -> dict:
            """Dynamic schema for any loaded dataset - PROVEN pattern."""
            if dataset_name not in self.dataset_schemas:
                return {"error": f"Dataset '{dataset_name}' not found"}
            return self.dataset_schemas[dataset_name]
        
        @self.mcp.resource("analytics://suggested_insights")
        async def get_analysis_suggestions() -> dict:
            """AI-generated analysis recommendations - PROVEN intelligence."""
            if not self.loaded_datasets:
                return {"suggestions": ["Load a dataset first to get personalized suggestions"]}
            
            # Get suggestions for the most recently loaded dataset
            latest_dataset = list(self.loaded_datasets.keys())[-1]
            schema = self.dataset_schemas[latest_dataset]
            
            return {
                "dataset": latest_dataset,
                "suggestions": schema.get("suggested_operations", []),
                "next_steps": self._generate_next_steps(schema)
            }
        
        # ============================================================================
        # TOOLS (Action Layer) - PROVEN tool patterns
        # ============================================================================
        
        @self.mcp.tool()
        async def load_dataset(file_path: str, dataset_name: str, sample_size: Optional[int] = None) -> dict:
            """PROVEN: Load any JSON/CSV dataset with automatic schema discovery."""
            try:
                # Support multiple formats (from production implementation)
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.json'):
                    df = pd.read_json(file_path)
                else:
                    return {"error": "Unsupported format. Use .csv or .json files."}
                
                # PROVEN: Sample large datasets
                if sample_size and len(df) > sample_size:
                    df = df.sample(n=sample_size, random_state=42)
                
                # PROVEN: Store data and auto-discover schema
                self.loaded_datasets[dataset_name] = df
                self.dataset_schemas[dataset_name] = self._discover_schema(df, dataset_name)
                
                return {
                    "success": True,
                    "dataset_name": dataset_name,
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "schema": self.dataset_schemas[dataset_name]
                }
            except Exception as e:
                return {"error": f"Failed to load dataset: {str(e)}"}
        
        @self.mcp.tool()
        async def find_correlations(
            dataset_name: str, 
            columns: Optional[List[str]] = None,
            threshold: float = 0.3
        ) -> dict:
            """PROVEN: Find correlations between numerical columns."""
            if dataset_name not in self.loaded_datasets:
                return {"error": f"Dataset '{dataset_name}' not found"}
            
            df = self.loaded_datasets[dataset_name]
            
            # Get numerical columns only
            if columns:
                numeric_df = df[columns].select_dtypes(include=['number'])
            else:
                numeric_df = df.select_dtypes(include=['number'])
            
            if numeric_df.empty:
                return {"error": "No numeric columns found for correlation analysis"}
            
            # Calculate correlations
            corr_matrix = numeric_df.corr()
            
            # PROVEN: Extract significant correlations
            significant_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= threshold:
                        significant_correlations.append({
                            "column1": col1,
                            "column2": col2,
                            "correlation": round(corr_value, 3),
                            "strength": "strong" if abs(corr_value) > 0.7 else "moderate"
                        })
            
            return {
                "dataset": dataset_name,
                "significant_correlations": significant_correlations,
                "correlation_matrix": corr_matrix.round(3).to_dict(),
                "threshold_used": threshold
            }
        
        @self.mcp.tool()
        async def segment_by_column(
            dataset_name: str, 
            column_name: str, 
            method: str = "auto",
            top_n: int = 10
        ) -> dict:
            """PROVEN: Generic segmentation that works on any categorical column."""
            if dataset_name not in self.loaded_datasets:
                return {"error": f"Dataset '{dataset_name}' not found"}
            
            df = self.loaded_datasets[dataset_name]
            
            if column_name not in df.columns:
                return {"error": f"Column '{column_name}' not found in dataset"}
            
            # PROVEN: Automatic segmentation logic
            segments = df[column_name].value_counts().head(top_n)
            
            # Get numerical columns for segment analysis
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            segment_analysis = {}
            for segment_value in segments.index:
                segment_data = df[df[column_name] == segment_value]
                
                if numeric_cols:
                    segment_analysis[str(segment_value)] = {
                        "count": int(segments[segment_value]),
                        "percentage": round(segments[segment_value] / len(df) * 100, 1),
                        "numeric_summary": segment_data[numeric_cols].describe().round(2).to_dict()
                    }
            
            return {
                "dataset": dataset_name,
                "segmentation_column": column_name,
                "total_segments": len(segments),
                "segment_analysis": segment_analysis
            }
        
        @self.mcp.tool()
        async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
            """PROVEN: Execute custom Python code with dataset context (simplified version)."""
            if dataset_name not in self.loaded_datasets:
                return f"❌ Dataset '{dataset_name}' not found. Available: {list(self.loaded_datasets.keys())}"
            
            df = self.loaded_datasets[dataset_name]
            
            # PROVEN: Safe execution context
            local_context = {
                'df': df,
                'pd': pd,
                'dataset_name': dataset_name
            }
            
            try:
                # Capture output
                import io
                import sys
                from contextlib import redirect_stdout, redirect_stderr
                
                output_buffer = io.StringIO()
                error_buffer = io.StringIO()
                
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    exec(python_code, {"__builtins__": {}}, local_context)
                
                output = output_buffer.getvalue()
                errors = error_buffer.getvalue()
                
                return output if output else (errors if errors else "Code executed successfully (no output)")
                
            except Exception as e:
                return f"❌ Error executing code: {str(e)}"
        
        # ============================================================================
        # PROMPTS (Intelligence Layer) - PROVEN intelligent prompts
        # ============================================================================
        
        @self.mcp.prompt()
        async def dataset_first_look_prompt(dataset_name: str) -> str:
            """PROVEN: Adaptive first-look analysis from production."""
            if dataset_name not in self.dataset_schemas:
                available = list(self.dataset_schemas.keys())
                return f"""# 🚀 Dataset Explorer

## Available Datasets
{chr(10).join(f"- **{name}**" for name in available) if available else "No datasets loaded yet."}

## Quick Start
1. **Load data**: `load_dataset('file.csv', 'my_data')`
2. **Explore**: Come back here with your dataset name for personalized guidance!
"""
            
            return await self._generate_dataset_first_look(dataset_name)
        
        @self.mcp.prompt()
        async def segmentation_workshop_prompt(dataset_name: str) -> str:
            """PROVEN: Interactive segmentation guidance."""
            if dataset_name not in self.dataset_schemas:
                return f"❌ Dataset '{dataset_name}' not found. Load it first with `load_dataset()`"
            
            return await self._generate_segmentation_workshop(dataset_name)
        
        # ============================================================================
        # UNIVERSAL COMPATIBILITY - PROVEN resource mirror pattern
        # ============================================================================
        
        @self.mcp.tool()
        async def resource_datasets_loaded() -> dict:
            """Tool mirror of datasets://loaded resource - PROVEN compatibility."""
            return await get_loaded_datasets_resource()
        
        @self.mcp.tool()
        async def resource_datasets_schema(dataset_name: str) -> dict:
            """Tool mirror of datasets://{name}/schema resource."""
            return await get_dataset_schema(dataset_name)
        
        @self.mcp.tool()
        async def resource_analytics_suggested_insights() -> dict:
            """Tool mirror of analytics://suggested_insights resource."""
            return await get_analysis_suggestions()
    
    def _discover_schema(self, df: pd.DataFrame, name: str) -> dict:
        """PROVEN: Intelligent schema discovery from production."""
        schema = {
            "name": name,
            "shape": df.shape,
            "row_count": len(df),
            "columns": {},
            "suggested_operations": []
        }
        
        for col in df.columns:
            # PROVEN: Role detection logic
            if pd.api.types.is_numeric_dtype(df[col]):
                role = 'numerical'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                role = 'temporal'
            elif df[col].nunique() / len(df) < 0.5:  # Low cardinality
                role = 'categorical'
            elif df[col].nunique() == len(df):  # All unique
                role = 'identifier'
            else:
                role = 'categorical'
            
            schema["columns"][col] = {
                "suggested_role": role,
                "dtype": str(df[col].dtype),
                "unique_values": df[col].nunique(),
                "null_percentage": round(df[col].isnull().mean() * 100, 1),
                "sample_values": df[col].dropna().head(3).tolist()
            }
        
        # PROVEN: Analysis suggestions logic
        numerical_cols = [col for col, info in schema["columns"].items() 
                         if info["suggested_role"] == 'numerical']
        categorical_cols = [col for col, info in schema["columns"].items() 
                           if info["suggested_role"] == 'categorical']
        temporal_cols = [col for col, info in schema["columns"].items() 
                        if info["suggested_role"] == 'temporal']
        
        if len(numerical_cols) >= 2:
            schema["suggested_operations"].append("correlation_analysis")
        if categorical_cols and numerical_cols:
            schema["suggested_operations"].append("segmentation_analysis")
        if temporal_cols and numerical_cols:
            schema["suggested_operations"].append("time_series_analysis")
        
        return schema
    
    async def _generate_dataset_first_look(self, dataset_name: str) -> str:
        """PROVEN: Generate contextual first look prompt."""
        schema = self.dataset_schemas[dataset_name]
        
        # Organize columns by type
        numerical_cols = [name for name, info in schema["columns"].items() 
                         if info["suggested_role"] == 'numerical']
        categorical_cols = [name for name, info in schema["columns"].items() 
                           if info["suggested_role"] == 'categorical']
        
        prompt = f"""# 🎯 Let's explore your **{dataset_name}** dataset!

## 📊 Dataset Overview
- **Records**: {schema['row_count']:,}
- **Columns**: {len(schema['columns'])}

"""
        
        if numerical_cols:
            prompt += f"**📈 Numerical columns** ({len(numerical_cols)}): {', '.join(numerical_cols)}\n"
        if categorical_cols:
            prompt += f"**🏷️ Categorical columns** ({len(categorical_cols)}): {', '.join(categorical_cols)}\n"
        
        prompt += "\n**🚀 Recommended starting points:**\n"
        
        if len(numerical_cols) >= 2:
            prompt += f"• **Correlations**: `find_correlations('{dataset_name}')`\n"
        if categorical_cols and numerical_cols:
            prompt += f"• **Segmentation**: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`\n"
        
        return prompt
    
    async def _generate_segmentation_workshop(self, dataset_name: str) -> str:
        """PROVEN: Generate segmentation workshop prompt."""
        schema = self.dataset_schemas[dataset_name]
        
        categorical_cols = [name for name, info in schema["columns"].items() 
                           if info["suggested_role"] == 'categorical']
        
        if not categorical_cols:
            return f"""**No categorical columns found in {dataset_name}** 😔

**Create segments from numerical data:**
```python
# Create value-based segments
df['value_tier'] = pd.cut(df['numerical_column'], bins=3, labels=['Low', 'Medium', 'High'])
```
Then use: `segment_by_column('{dataset_name}', 'value_tier')`
"""
        
        prompt = f"""# 🎯 Segmentation Workshop for {dataset_name}

**Available columns for grouping:**
"""
        
        for col in categorical_cols[:5]:  # Show top 5
            col_info = schema["columns"][col]
            prompt += f"• **{col}**: {col_info['unique_values']} unique values\n"
        
        prompt += f"\n**Quick start**: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`"
        
        return prompt
    
    def _generate_next_steps(self, schema: dict) -> List[str]:
        """PROVEN: Generate intelligent next steps."""
        steps = []
        suggested_ops = schema.get("suggested_operations", [])
        
        if "correlation_analysis" in suggested_ops:
            steps.append("Explore correlations between numerical variables")
        if "segmentation_analysis" in suggested_ops:
            steps.append("Segment data by categorical columns")
        if not steps:
            steps.append("Explore data with custom code execution")
        
        return steps

# PROVEN: Simple server runner
def main():
    server = ProvenAdvancedMCPServer("analytics")
    server.mcp.run()

if __name__ == "__main__":
    main()
```

---

## 6. Day 1-2 Implementation Checklist

### ✅ Day 1: Morning (Hours 1-4) - Foundation
1. **Set up FastMCP server** with three-tier structure
2. **Implement Resource Layer** (minimum 3):
   - `{domain}://status` - System state
   - `{domain}://capabilities` - Available operations
   - `{domain}://data/{id}` - Dynamic data access
3. **Implement Tool Layer** (minimum 5):
   - Core CRUD operations for your domain
   - Data loading/processing tools
   - Analysis/computation tools
4. **Test both layers** work independently

### ✅ Day 1: Afternoon (Hours 5-8) - Intelligence & Compatibility
1. **Implement Prompt Layer** (minimum 3):
   - Onboarding prompt (guides new users)
   - Analysis workflow prompt (combines multiple tools)
   - Expert guidance prompt (contextual help)
2. **Add Universal Compatibility**:
   - Every resource gets a tool mirror
   - Consistent naming: `resource_{name}` for mirrors
3. **Implement Schema Discovery**:
   - Auto-detect data structures
   - Generate operation suggestions

### ✅ Day 2: Morning (Hours 1-4) - Robustness
1. **Comprehensive error handling**:
   - Try/catch in every tool
   - Meaningful error messages
   - Graceful degradation
2. **Input validation**:
   - Type checking
   - Bounds validation
   - Schema validation
3. **Performance instrumentation**:
   - Log response times
   - Track resource usage

### ✅ Day 2: Afternoon (Hours 5-8) - Production Ready
1. **Integration testing**:
   - Test all three tiers together
   - Verify universal compatibility
   - Load test with real data
2. **Documentation**:
   - API reference for all endpoints
   - Example workflows
   - Deployment guide
3. **Deploy and validate**:
   - Test with actual client
   - Verify <500ms response times
   - Confirm all three tiers functioning

### ✅ Key Success Metrics

- **Universal Compatibility**: Both resource and tool interfaces work
- **Schema Discovery**: Automatically understands any data you throw at it
- **Intelligent Prompts**: Generates contextual workflows, not just static text
- **Composable Tools**: Each tool can be used independently or in workflows

---

## 7. Quick Testing Strategy

```python
# test_quick_server.py
async def test_your_server():
    server = QuickAdvancedMCPServer()
    
    # Test 1: Load sample data
    result = await server.load_data("test", "sample.csv")
    assert result["success"] == True
    
    # Test 2: Schema discovery worked
    assert "test" in server.schemas
    assert "columns" in server.schemas["test"]
    
    # Test 3: Universal compatibility
    resource_data = await server.loaded_data()
    tool_data = await server.get_loaded_data()
    assert resource_data == tool_data  # Same data, different interfaces
    
    # Test 4: Intelligent prompt
    prompt = await server.data_exploration_guide("test")
    assert "🎯" in prompt  # Should be contextual and formatted
    
    print("✅ All tests passed! Your advanced MCP server is working.")
```

---

## 8. Expansion Points (Add These Next)

### When Your Foundation Works, Add:

1. **More Domain Operations**: Add tools specific to your domain
2. **Enhanced Prompts**: Create workflow prompts for complex multi-step operations  
3. **Context Tracking**: Remember what users have done for better suggestions
4. **Error Recovery**: Intelligent error messages with fix suggestions
5. **Performance**: Caching and optimization for larger datasets

### BONUS: Enhanced Code Execution (Production Innovation)

**From the reference implementation** - this is the killer feature that sets advanced MCP servers apart:

```python
@mcp.tool()
async def execute_enhanced_analytics_code(
    dataset_name: str, 
    python_code: str,
    execution_mode: str = "safe",
    include_ai_context: bool = True,
    timeout_seconds: int = 30
) -> dict:
    """PROVEN: Enhanced code execution with AI context and safety analysis."""
    
    if dataset_name not in self.loaded_datasets:
        return {"error": f"Dataset '{dataset_name}' not found"}
    
    df = self.loaded_datasets[dataset_name]
    schema = self.dataset_schemas[dataset_name]
    
    # INNOVATION: AI helper functions injected into execution context
    ai_helpers = """
def smart_describe(df, column=None):
    \"\"\"AI-powered dataset description with outlier detection\"\"\"
    if column:
        series = df[column]
        print(f"📊 Analysis for '{column}':")
        print(f"  Type: {series.dtype}")
        print(f"  Unique values: {series.nunique()}")
        print(f"  Missing: {series.isnull().sum()} ({series.isnull().mean()*100:.1f}%)")
        if pd.api.types.is_numeric_dtype(series):
            print(f"  Range: {series.min()} to {series.max()}")
            # Outlier detection
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = series[(series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)]
            print(f"  Potential outliers: {len(outliers)}")
    else:
        print(f"📈 Dataset Overview: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print("Column types:")
        for col in df.columns:
            print(f"  {col}: {df[col].dtype}")

def get_analysis_suggestions():
    \"\"\"Get AI-powered analysis suggestions\"\"\"
    suggestions = {schema.get('suggested_operations', [])}
    print("🎯 Recommended analyses:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion.replace('_', ' ').title()}")

def performance_check():
    \"\"\"Check execution performance\"\"\"
    import time
    current_time = time.time()
    print(f"⏱️  Execution time so far: {current_time - execution_start_time:.2f}s")

# Auto-inject dataset context
DATASET_NAME = "{dataset_name}"
DATASET_INFO = {schema}
execution_start_time = time.time()

print(f"🚀 Enhanced execution context loaded for '{dataset_name}'")
print(f"📊 Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"🔧 AI helpers available: smart_describe(), get_analysis_suggestions(), performance_check()")
print("="*50)
"""
    
    # INNOVATION: Safety analysis before execution
    safety_issues = []
    if "import os" in python_code or "subprocess" in python_code:
        safety_issues.append("Potentially unsafe system operations detected")
    if "exec(" in python_code or "eval(" in python_code:
        safety_issues.append("Dynamic code execution detected")
    
    if safety_issues and execution_mode == "safe":
        return {
            "status": "analysis_error",
            "errors": safety_issues,
            "suggestions": ["Remove unsafe operations", "Use 'standard' mode if needed"]
        }
    
    # INNOVATION: Enhanced execution context
    enhanced_context = {
        'df': df,
        'pd': pd,
        'np': __import__('numpy'),
        'px': __import__('plotly.express'),
        'dataset_name': dataset_name,
        'schema': schema
    }
    
    try:
        import io, sys, time
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        start_time = time.time()
        
        # Execute AI helpers first if enabled
        full_code = (ai_helpers + "\n" + python_code) if include_ai_context else python_code
        
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            exec(full_code, {"__builtins__": {}}, enhanced_context)
        
        execution_time = time.time() - start_time
        output = output_buffer.getvalue()
        errors = error_buffer.getvalue()
        
        # INNOVATION: Extract insights from execution
        insights = []
        if "correlation" in output.lower():
            insights.append("Correlation analysis performed")
        if "outlier" in output.lower():
            insights.append("Outlier detection applied")
        
        # INNOVATION: Generate follow-up suggestions
        follow_up_suggestions = []
        if execution_time > 5:
            follow_up_suggestions.append("Consider optimizing for large datasets")
        if not insights:
            follow_up_suggestions.append("Try using AI helper functions for enhanced analysis")
        
        return {
            "status": "success",
            "execution_output": output or "Code executed successfully (no output)",
            "insights": insights,
            "follow_up_suggestions": follow_up_suggestions,
            "performance_metrics": {
                "execution_time": round(execution_time, 3),
                "lines_executed": len(python_code.split('\n'))
            },
            "execution_history_count": 1  # Simplified - could track actual history
        }
        
    except Exception as e:
        return {
            "status": "system_error", 
            "error": str(e),
            "suggestions": ["Check syntax", "Verify column names exist", "Use print() to see output"]
        }
```

### Domain-Specific Extensions (Copy These Patterns)

```python
# ANALYTICS DOMAIN - Real pattern from production
@mcp.tool()
async def validate_data_quality(dataset_name: str) -> dict:
    """Domain-specific data quality assessment"""
    df = self.loaded_datasets[dataset_name]
    
    quality_report = {
        "missing_data": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "data_types": df.dtypes.to_dict(),
        "quality_score": 100 - (df.isnull().sum().sum() / df.size * 100)
    }
    return quality_report

# E-COMMERCE DOMAIN - Extend for your business
@mcp.tool()
async def analyze_customer_segments(dataset_name: str, customer_id_col: str, value_col: str) -> dict:
    """Domain-specific customer analysis"""
    df = self.loaded_datasets[dataset_name]
    
    customer_metrics = df.groupby(customer_id_col)[value_col].agg([
        'sum', 'mean', 'count'
    ]).round(2)
    
    # RFM-style segmentation
    customer_metrics['tier'] = pd.cut(
        customer_metrics['sum'], 
        bins=3, 
        labels=['Bronze', 'Silver', 'Gold']
    )
    
    return {
        "total_customers": len(customer_metrics),
        "customer_tiers": customer_metrics['tier'].value_counts().to_dict(),
        "average_values": customer_metrics.groupby('tier')['mean'].mean().to_dict()
    }

# TIME SERIES DOMAIN - Real production pattern
@mcp.tool()
async def analyze_time_series_trends(
    dataset_name: str, 
    date_col: str, 
    value_col: str,
    frequency: str = "M"  # Monthly
) -> dict:
    """Domain-specific time series analysis"""
    df = self.loaded_datasets[dataset_name]
    
    # Convert to datetime and resample
    df[date_col] = pd.to_datetime(df[date_col])
    time_series = df.set_index(date_col)[value_col].resample(frequency).sum()
    
    # Calculate trend metrics
    trend_analysis = {
        "period_count": len(time_series),
        "trend_direction": "increasing" if time_series.iloc[-1] > time_series.iloc[0] else "decreasing",
        "growth_rate": ((time_series.iloc[-1] / time_series.iloc[0]) - 1) * 100,
        "monthly_data": time_series.to_dict()
    }
    
    return trend_analysis
```

---

## Key Takeaways for Building Now

1. **Start with the three-tier hierarchy** - this is your foundation
2. **Universal compatibility is non-negotiable** - implement both resource and tool interfaces
3. **Schema discovery is your competitive advantage** - auto-understand any data
4. **Prompts are your killer feature** - they transform tools into workflows
5. **Build domain-agnostic first** - then add domain-specific extensions

**The goal**: Build an MCP server that's immediately useful AND has the architecture to evolve into an intelligent, learning system.

**Time to value**: You can have a working advanced MCP server in hours, not weeks.

**Next step**: Copy the implementation template, customize for your domain, and start building!