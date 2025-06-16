# CONSOLIDATED Data Analytics Framework

## Table of Contents
1. [Generic Data Analytics Vision](#generic-data-analytics-vision)
2. [Dataset-Agnostic Architecture](#dataset-agnostic-architecture)
3. [Custom Analytics Code Execution](#custom-analytics-code-execution)
4. [In-Memory Dataset Management](#in-memory-dataset-management)
5. [Schema Discovery & Adaptation](#schema-discovery--adaptation)
6. [Advanced Analytics Patterns](#advanced-analytics-patterns)
7. [Visualization & Export Capabilities](#visualization--export-capabilities)
8. [Multi-Dataset Operations](#multi-dataset-operations)
9. [AI-Guided Data Exploration](#ai-guided-data-exploration)
10. [Resource Workaround Strategy](#resource-workaround-strategy)

---

## Generic Data Analytics Vision

### Problem Statement

Teams have data in JSON/CSV files but lack an easy, AI-assisted way to explore, analyze, and generate insights from ANY dataset. Current solutions require custom coding for each data source, making analysis slow and inaccessible to non-technical users.

### Solution Vision

Build a **dataset-agnostic** MCP server that automatically adapts to any structured data (JSON/CSV), discovers schemas dynamically, and provides intelligent analytics capabilities. The AI can analyze customer data, sales records, survey responses, inventory data, or any business dataset through the same interface.

### Core Design Principles

#### 1. Dataset Agnostic
- Works with any structured data without hardcoded schemas
- Automatically discovers column types, relationships, and constraints
- Adapts analysis techniques to data characteristics

#### 2. Schema Discovery
- Dynamic column detection and type inference
- Automatic identification of categorical vs numerical vs temporal data
- Intelligent suggestions for analysis based on data patterns

#### 3. Adaptive Analytics
- Generic segmentation that works on any categorical columns
- Correlation analysis that adapts to available numerical data
- Time series analysis when temporal columns are detected

#### 4. Conversational Guidance
- AI prompts that guide users through data exploration
- Context-aware suggestions based on current dataset
- Interactive tutorials for complex analytics operations

### Test Data Flexibility

#### Example Dataset A: E-commerce Orders
```json
[
  {
    "order_id": "ord_001",
    "customer_id": "cust_123", 
    "product_category": "electronics",
    "order_value": 299.99,
    "order_date": "2024-11-15",
    "region": "west_coast",
    "payment_method": "credit_card",
    "customer_segment": "premium"
  }
]
```

#### Example Dataset B: Employee Survey
```csv
employee_id,department,satisfaction_score,tenure_years,remote_work,salary_band
emp_001,engineering,8.5,3.2,yes,senior
emp_002,sales,6.2,1.8,no,mid
emp_003,marketing,9.1,5.5,hybrid,senior
```

#### Example Dataset C: Product Performance
```csv
product_id,category,monthly_sales,inventory_level,supplier,launch_date,rating
prod_001,widgets,1250,45,supplier_a,2024-01-15,4.2
prod_002,gadgets,890,12,supplier_b,2023-08-22,3.8
```

---

## Dataset-Agnostic Architecture

### Generic MCP Architecture

#### Tools (Dataset-Agnostic Actions)

##### Data Discovery & Loading
- `load_dataset(file_path, format)` - Load any JSON/CSV with automatic schema detection
- `analyze_schema(dataset_name)` - Discover column types, distributions, missing values
- `suggest_analysis(dataset_name)` - AI recommendations based on data characteristics
- `validate_data_quality(dataset_name)` - Generic data quality assessment

##### Flexible Analytics
- `segment_by_column(dataset_name, column_name, method)` - Generic segmentation on any categorical column
- `find_correlations(dataset_name, columns)` - Correlation analysis on any numerical columns
- `analyze_distributions(dataset_name, column_name)` - Distribution analysis for any column
- `detect_outliers(dataset_name, columns)` - Outlier detection using configurable methods
- `time_series_analysis(dataset_name, date_column, value_column)` - Temporal analysis when dates detected

##### Adaptive Visualization
- `create_chart(dataset_name, chart_type, x_column, y_column, groupby)` - Generic chart creation
- `generate_dashboard(dataset_name, chart_configs)` - Multi-chart dashboards from any data
- `export_insights(dataset_name, format)` - Export analysis in multiple formats

##### Cross-Dataset Operations
- `compare_datasets(dataset_a, dataset_b, common_columns)` - Compare multiple datasets
- `merge_datasets(dataset_configs, join_strategy)` - Join datasets on common keys

### Resources (Dynamic Data Context)

#### Dataset Metadata
- `datasets://loaded` - List of all currently loaded datasets with basic info
- `datasets://{name}/schema` - Dynamic schema for any loaded dataset
- `datasets://{name}/summary` - Statistical summary (pandas.describe() equivalent)
- `datasets://{name}/sample` - Sample rows for data preview

#### Analysis Context
- `analytics://current_dataset` - Currently active dataset name and basic stats
- `analytics://available_analyses` - List of applicable analysis types for current data
- `analytics://column_types` - Column classification (categorical, numerical, temporal, text)
- `analytics://suggested_insights` - AI-generated analysis recommendations

#### Results & History
- `results://recent_analyses` - Recently performed analyses and their outputs
- `results://generated_charts` - Available visualizations with metadata
- `results://export_ready` - Datasets/analyses ready for export

### Prompts (Adaptive Conversation Starters)

#### Data Exploration
- `dataset_first_look(dataset_name)` - Guide initial exploration of any new dataset
- `column_deep_dive(dataset_name, column_name)` - Detailed analysis of specific columns
- `data_quality_review(dataset_name)` - Systematic data quality assessment

#### Analysis Strategy
- `segmentation_planning(dataset_name)` - Plan segmentation strategy based on available columns
- `correlation_investigation(dataset_name)` - Guide correlation analysis workflow
- `pattern_discovery_session(dataset_name)` - Open-ended pattern mining conversation

#### Business Intelligence
- `insight_generation_workshop(dataset_name, business_context)` - Generate business insights
- `dashboard_design_consultation(dataset_name, audience)` - Plan dashboards for specific audiences
- `export_strategy_planning(dataset_name, use_case)` - Plan data export and sharing strategy

---

## Custom Analytics Code Execution

### Problem Statement

Current analytics tools provide predefined operations (correlations, segmentation, charts), but AI agents often need to perform **custom analysis** that goes beyond these fixed patterns. Agents should be able to write and execute their own Python code against loaded datasets for:

- **Novel analysis patterns** not covered by existing tools
- **Custom calculations** (financial metrics, scientific formulas, etc.)
- **Complex data transformations** requiring multi-step operations
- **Domain-specific analysis** tailored to specific business needs
- **Experimental algorithms** for pattern detection and insights

### Solution Overview

Implement an **`execute_custom_analytics_code()`** tool that:
- Accepts dataset name and Python code as parameters
- Executes code in a **subprocess** with access to the specified dataset
- Returns **stdout/stderr output** as a string for agent iteration
- Provides **basic error capture** so agents can debug and fix code
- Uses **subprocess isolation** for safety

### Architecture Design

#### Simplified Flow

```
┌─────────────────────────────────────────────┐
│           MCP Server (Main Process)         │
├─────────────────────────────────────────────┤
│  execute_custom_analytics_code()            │
│       │                                     │
│       ▼                                     │
│  1. Get dataset from DatasetManager         │
│  2. Serialize to JSON                       │
│  3. Wrap code in execution template         │
│  4. Launch subprocess with uv run           │
│  5. Capture stdout/stderr                   │
│  6. Return output string                    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│        Python Subprocess (Isolated)         │
├─────────────────────────────────────────────┤
│  - pandas, numpy, plotly imported           │
│  - Dataset loaded as 'df' DataFrame         │
│  - User code executed with try/catch        │
│  - All output printed to stdout             │
│  - 30 second timeout enforced              │
└─────────────────────────────────────────────┘
```

#### Data Flow

1. **Agent Request**: `execute_custom_analytics_code(dataset_name, python_code)`
2. **Dataset Access**: Get DataFrame from loaded datasets
3. **Serialization**: Convert dataset to JSON for subprocess
4. **Code Wrapping**: Embed user code in safe execution template
5. **Subprocess Launch**: `uv run --with pandas python -c "..."`
6. **Output Capture**: Collect all stdout/stderr output
7. **Return Result**: Simple string with all output for agent parsing

### API Specification

#### Tool Definition

```python
@mcp.tool()
async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset and return the output.
    
    IMPORTANT FOR AGENTS:
    - The dataset will be available as 'df' (pandas DataFrame) in your code
    - Libraries pre-imported: pandas as pd, numpy as np, plotly.express as px
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    USAGE EXAMPLES:
    
    Basic analysis:
    ```python
    print("Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("Summary stats:")
    print(df.describe())
    ```
    
    Custom calculations:
    ```python
    # Calculate customer metrics
    customer_stats = df.groupby('customer_id').agg({
        'order_value': ['sum', 'mean', 'count']
    }).round(2)
    print("Top 5 customers by total value:")
    print(customer_stats.sort_values(('order_value', 'sum'), ascending=False).head())
    ```
    
    Data analysis:
    ```python
    # Find correlations
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()
    print("Correlation matrix:")
    print(correlations)
    
    # Custom insights
    if 'sales' in df.columns and 'date' in df.columns:
        monthly_sales = df.groupby(pd.to_datetime(df['date']).dt.to_period('M'))['sales'].sum()
        print("Monthly sales trend:")
        print(monthly_sales)
    ```
    
    Args:
        dataset_name: Name of the loaded dataset to analyze
        python_code: Python code to execute (must print() results to see output)
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
```

#### Execution Template

The tool automatically wraps user code in a safe execution environment:

```python
# Agent provides this:
user_code = """
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

# Calculate customer lifetime value
customer_ltv = df.groupby('customer_id')['order_value'].sum()
print("Top 5 customers by total value:")
print(customer_ltv.sort_values(ascending=False).head())

# Basic statistics
print("Average order value:", df['order_value'].mean())
print("Total customers:", df['customer_id'].nunique())
"""

# Tool wraps it in execution template:
execution_template = f"""
import pandas as pd
import numpy as np
import plotly.express as px

# Load dataset
try:
    # Dataset serialized as JSON from DatasetManager
    dataset_data = {serialized_dataset}
    df = pd.DataFrame(dataset_data)
    
    # Execute user code
    {user_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
"""
```

#### Response Format

Simple string return with stdout/stderr combined:

```python
# Success case:
"Dataset shape: (1000, 5)
Columns: ['customer_id', 'order_value', 'date', 'category', 'region']
Top 5 customers by total value:
customer_id
C001    5670.50
C043    4320.75
C012    3890.25
C087    3456.80
C234    3201.40
Average order value: 125.45
Total customers: 250"

# Error case:
"ERROR: KeyError: 'invalid_column'
Traceback:
  File \"<string>\", line 8, in <module>
    result = df['invalid_column'].sum()
KeyError: 'invalid_column'"

# Timeout case:
"TIMEOUT: Code execution exceeded 30 second limit"
```

### Security Model

#### Subprocess Isolation

- **Process isolation**: Code runs in separate Python process via `uv run`
- **30 second timeout**: Prevents infinite loops and resource exhaustion
- **No file system access**: Subprocess cannot access host files
- **Limited imports**: Only safe libraries (pandas, numpy, plotly) available
- **Read-only dataset access**: Dataset copied as JSON, not referenced

#### Basic Safety Measures

```python
# Execute in isolated subprocess
process = await asyncio.create_subprocess_exec(
    'uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
    'python', '-c', execution_code,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.STDOUT,
    timeout=30  # Hard timeout limit
)
```

### Implementation Plan

#### Core Implementation

Add to `analytics_tools.py`:

```python
import asyncio
import json
import subprocess
from typing import Dict, Any
from pathlib import Path

async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset.
    
    Implementation steps:
    1. Get dataset from DatasetManager
    2. Serialize dataset to JSON for subprocess
    3. Wrap user code in execution template
    4. Execute via subprocess with uv run python -c
    5. Capture and return stdout/stderr
    """
    try:
        # Step 1: Get dataset
        df = DatasetManager.get_dataset(dataset_name)
        
        # Step 2: Serialize dataset
        dataset_json = df.to_json(orient='records')
        
        # Step 3: Create execution template
        execution_code = f'''
import pandas as pd
import numpy as np
import plotly.express as px
import json

try:
    # Load dataset
    dataset_data = {dataset_json}
    df = pd.DataFrame(dataset_data)
    
    # Execute user code
    {python_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
'''
        
        # Step 4: Execute subprocess
        process = await asyncio.create_subprocess_exec(
            'uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
            'python', '-c', execution_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            timeout=30
        )
        
        # Step 5: Get output
        stdout, _ = await process.communicate()
        return stdout.decode('utf-8')
        
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Code execution exceeded 30 second limit"
    except Exception as e:
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"
```

#### Integration with Server

Add to `server.py`:

```python
@mcp.tool()
async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset and return the output.
    
    IMPORTANT FOR AGENTS:
    - The dataset will be available as 'df' (pandas DataFrame) in your code
    - Libraries pre-imported: pandas as pd, numpy as np, plotly.express as px
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    Args:
        dataset_name: Name of the loaded dataset to analyze
        python_code: Python code to execute (must print() results to see output)
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    return await analytics_tools.execute_custom_analytics_code(dataset_name, python_code)
```

### Usage Examples

#### Basic Data Analysis

```python
output = await execute_custom_analytics_code(
    dataset_name="sales_data",
    python_code="""
print("Dataset Info:")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Basic statistics
print("\\nBasic Statistics:")
print(f"Total sales: ${df['order_value'].sum():,.2f}")
print(f"Average order: ${df['order_value'].mean():.2f}")
print(f"Unique customers: {df['customer_id'].nunique()}")

# Top customers
top_customers = df.groupby('customer_id')['order_value'].sum().sort_values(ascending=False).head()
print("\\nTop 5 Customers:")
for customer, total in top_customers.items():
    print(f"{customer}: ${total:.2f}")
"""
)

# Output:
# Dataset Info:
# Shape: (1500, 5) 
# Columns: ['customer_id', 'order_value', 'order_date', 'category', 'region']
# 
# Basic Statistics:
# Total sales: $125,430.50
# Average order: $83.62
# Unique customers: 250
# 
# Top 5 Customers:
# C001: $5,670.50
# C043: $4,320.75
# ...
```

#### Custom Calculations

```python
output = await execute_custom_analytics_code(
    dataset_name="employee_survey",
    python_code="""
# Employee satisfaction analysis
satisfaction_cols = ['work_life_balance', 'compensation', 'career_growth']

print("Satisfaction Metrics:")
for col in satisfaction_cols:
    avg_score = df[col].mean()
    print(f"{col.replace('_', ' ').title()}: {avg_score:.2f}/5")

# Department comparison
dept_satisfaction = df.groupby('department')[satisfaction_cols].mean()
print("\\nDepartment Satisfaction Averages:")
print(dept_satisfaction.round(2))

# Find correlation
if len(satisfaction_cols) >= 2:
    correlation = df[satisfaction_cols].corr()
    print("\\nCorrelation Matrix:")
    print(correlation.round(3))
"""
)
```

#### Error Handling Example

```python
# Agent tries invalid code
output = await execute_custom_analytics_code(
    dataset_name="sales_data", 
    python_code="""
# This will cause an error
result = df['nonexistent_column'].sum()
print(f"Result: {result}")
"""
)

# Output:
# ERROR: KeyError: 'nonexistent_column'
# Traceback:
#   File "<string>", line 9, in <module>
#     result = df['nonexistent_column'].sum()
# KeyError: 'nonexistent_column'

# Agent can then fix the code
output = await execute_custom_analytics_code(
    dataset_name="sales_data",
    python_code="""
# Check available columns first
print("Available columns:", df.columns.tolist())

# Use correct column name
result = df['order_value'].sum()
print(f"Total sales: ${result:.2f}")
"""
)
```

---

## In-Memory Dataset Management

### Implementation Architecture

#### In-Memory Dataset Storage (Simple & Fast)

```python
# Global in-memory storage - simple and effective
loaded_datasets: Dict[str, pd.DataFrame] = {}
dataset_schemas: Dict[str, DatasetSchema] = {}

class DatasetManager:
    """Simple in-memory dataset management"""
    
    @staticmethod
    def load_dataset(file_path: str, dataset_name: str) -> dict:
        """Load dataset into memory with automatic schema discovery"""
        
        # Load based on file extension
        if file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Store in global memory
        loaded_datasets[dataset_name] = df
        
        # Discover and cache schema
        schema = DatasetSchema.from_dataframe(df, dataset_name)
        dataset_schemas[dataset_name] = schema
        
        return {
            "status": "loaded",
            "dataset_name": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"
        }
    
    @staticmethod
    def get_dataset(dataset_name: str) -> pd.DataFrame:
        """Retrieve dataset from memory"""
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")
        return loaded_datasets[dataset_name]
    
    @staticmethod
    def list_datasets() -> List[str]:
        """Get names of all loaded datasets"""
        return list(loaded_datasets.keys())
    
    @staticmethod
    def get_dataset_info(dataset_name: str) -> dict:
        """Get basic info about loaded dataset"""
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded")
            
        df = loaded_datasets[dataset_name]
        schema = dataset_schemas[dataset_name]
        
        return {
            "name": dataset_name,
            "shape": df.shape,
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "schema": schema.model_dump()
        }
```

### Storage Benefits

**✅ Zero Complexity**: No file management, caching, or persistence logic
**✅ Immediate Access**: Instant dataset operations without I/O overhead  
**✅ Perfect for Demos**: Load sample data and start analyzing immediately
**✅ Memory Efficient**: Pandas DataFrames are already optimized for memory usage
**✅ Session-Based**: Clean slate on each restart - perfect for experimentation

### Memory Considerations

**Typical Dataset Sizes**:
- 1K rows × 10 columns = ~1MB memory
- 10K rows × 20 columns = ~10MB memory  
- 100K rows × 50 columns = ~100MB memory

**Best Practices**:
- Sample large datasets before loading (`df.sample(10000)`)
- Provide memory usage feedback to users
- Clear datasets when no longer needed (`del loaded_datasets[name]`)

---

## Schema Discovery & Adaptation

### DatasetSchema Class

```python
class DatasetSchema:
    """Dynamically discovered dataset schema"""
    name: str
    columns: Dict[str, ColumnInfo]
    row_count: int
    suggested_analyses: List[str]
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str) -> 'DatasetSchema':
        """Auto-discover schema from pandas DataFrame"""
        columns = {}
        for col in df.columns:
            columns[col] = ColumnInfo.from_series(df[col], col)
        
        # Generate analysis suggestions based on column types
        suggestions = []
        numerical_cols = [col for col, info in columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [col for col, info in columns.items() if info.suggested_role == 'categorical']
        temporal_cols = [col for col, info in columns.items() if info.suggested_role == 'temporal']
        
        if len(numerical_cols) >= 2:
            suggestions.append("correlation_analysis")
        if categorical_cols:
            suggestions.append("segmentation_analysis")
        if temporal_cols:
            suggestions.append("time_series_analysis")
            
        return cls(
            name=name,
            columns=columns,
            row_count=len(df),
            suggested_analyses=suggestions
        )
    
class ColumnInfo:
    """Column metadata and characteristics"""
    name: str
    dtype: str
    unique_values: int
    null_percentage: float
    sample_values: List[Any]
    suggested_role: str  # 'categorical', 'numerical', 'temporal', 'identifier'
    
    @classmethod
    def from_series(cls, series: pd.Series, name: str) -> 'ColumnInfo':
        """Auto-discover column characteristics from pandas Series"""
        
        # Determine suggested role
        if pd.api.types.is_numeric_dtype(series):
            role = 'numerical'
        elif pd.api.types.is_datetime64_any_dtype(series):
            role = 'temporal'
        elif series.nunique() / len(series) < 0.5:  # High cardinality = categorical
            role = 'categorical'
        elif series.nunique() == len(series):  # Unique values = identifier
            role = 'identifier'
        else:
            role = 'categorical'
            
        return cls(
            name=name,
            dtype=str(series.dtype),
            unique_values=series.nunique(),
            null_percentage=series.isnull().mean() * 100,
            sample_values=series.dropna().head(3).tolist(),
            suggested_role=role
        )
```

---

## Advanced Analytics Patterns

### Generic Tool Implementation Examples

```python
@mcp.tool()
async def load_dataset(file_path: str, dataset_name: str) -> dict:
    """Load any JSON/CSV dataset into memory"""
    return DatasetManager.load_dataset(file_path, dataset_name)

@mcp.tool()
async def list_loaded_datasets() -> dict:
    """Show all datasets currently in memory"""
    datasets = []
    for name in DatasetManager.list_datasets():
        info = DatasetManager.get_dataset_info(name)
        datasets.append(info)
    
    return {
        "loaded_datasets": datasets,
        "total_memory_mb": sum(d["memory_usage_mb"] for d in datasets)
    }

@mcp.tool()
async def segment_by_column(
    dataset_name: str, 
    column_name: str, 
    method: str = "auto"
) -> dict:
    """Generic segmentation that works on any categorical column"""
    df = DatasetManager.get_dataset(dataset_name)
    
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found in dataset '{dataset_name}'"}
    
    # Auto-select aggregation based on available numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    agg_dict = {}
    for col in numerical_cols:
        if col != column_name:  # Don't aggregate the groupby column
            agg_dict[col] = ['count', 'mean', 'sum']
    
    if not agg_dict:
        # No numerical columns - just count
        segments = df.groupby(column_name).size().to_frame('count')
    else:
        segments = df.groupby(column_name).agg(agg_dict)
    
    return {
        "dataset": dataset_name,
        "segmented_by": column_name,
        "segment_count": len(segments),
        "segments": segments.to_dict(),
        "total_rows": len(df)
    }

@mcp.tool()
async def find_correlations(dataset_name: str, columns: List[str] = None) -> dict:
    """Find correlations between numerical columns"""
    df = DatasetManager.get_dataset(dataset_name)
    
    # Auto-select numerical columns if none specified
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(columns) < 2:
        return {"error": "Need at least 2 numerical columns for correlation analysis"}
    
    # Calculate correlation matrix
    corr_matrix = df[columns].corr()
    
    # Find strongest correlations (excluding self-correlations)
    strong_correlations = []
    for i in range(len(columns)):
        for j in range(i+1, len(columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > 0.3:  # Threshold for "interesting" correlation
                strong_correlations.append({
                    "column_1": columns[i],
                    "column_2": columns[j],
                    "correlation": round(corr_value, 3),
                    "strength": "strong" if abs(corr_value) > 0.7 else "moderate"
                })
    
    return {
        "dataset": dataset_name,
        "correlation_matrix": corr_matrix.to_dict(),
        "strong_correlations": strong_correlations,
        "columns_analyzed": columns
    }

@mcp.tool()
async def create_chart(
    dataset_name: str,
    chart_type: str,
    x_column: str,
    y_column: str = None,
    groupby_column: str = None
) -> dict:
    """Create generic charts that adapt to any dataset"""
    df = DatasetManager.get_dataset(dataset_name)
    
    # Validate columns exist
    required_cols = [x_column]
    if y_column:
        required_cols.append(y_column)
    if groupby_column:
        required_cols.append(groupby_column)
        
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {"error": f"Columns not found: {missing_cols}"}
    
    # Generate chart based on type
    if chart_type == "bar":
        if groupby_column:
            chart_data = df.groupby([x_column, groupby_column])[y_column].mean().unstack()
        else:
            chart_data = df.groupby(x_column)[y_column].mean()
    elif chart_type == "histogram":
        chart_data = df[x_column].value_counts()
    else:
        return {"error": f"Unsupported chart type: {chart_type}"}
    
    # In a real implementation, this would generate plotly charts
    return {
        "dataset": dataset_name,
        "chart_type": chart_type,
        "chart_data": chart_data.to_dict(),
        "chart_config": {
            "x_column": x_column,
            "y_column": y_column,
            "groupby_column": groupby_column
        }
    }
```

---

## Visualization & Export Capabilities

### Adaptive Resource System
```python
@mcp.resource("datasets://loaded")
async def get_loaded_datasets() -> dict:
    """List all datasets currently in memory"""
    datasets = []
    for name in DatasetManager.list_datasets():
        info = DatasetManager.get_dataset_info(name)
        datasets.append({
            "name": name,
            "rows": info["shape"][0],
            "columns": info["shape"][1],
            "memory_mb": round(info["memory_usage_mb"], 1)
        })
    
    return {
        "datasets": datasets,
        "total_datasets": len(datasets),
        "total_memory_mb": sum(d["memory_mb"] for d in datasets)
    }

@mcp.resource("datasets://{dataset_name}/schema")
async def get_dataset_schema(dataset_name: str) -> dict:
    """Get dynamic schema for any loaded dataset"""
    if dataset_name not in dataset_schemas:
        return {"error": f"Dataset '{dataset_name}' not loaded"}
    
    schema = dataset_schemas[dataset_name]
    
    # Organize columns by type
    columns_by_type = {
        "numerical": [],
        "categorical": [], 
        "temporal": [],
        "identifier": []
    }
    
    for col_name, col_info in schema.columns.items():
        columns_by_type[col_info.suggested_role].append({
            "name": col_name,
            "dtype": col_info.dtype,
            "unique_values": col_info.unique_values,
            "null_percentage": round(col_info.null_percentage, 1),
            "sample_values": col_info.sample_values
        })
    
    return {
        "dataset_name": dataset_name,
        "total_rows": schema.row_count,
        "total_columns": len(schema.columns),
        "columns_by_type": columns_by_type,
        "suggested_analyses": schema.suggested_analyses
    }

@mcp.resource("datasets://{dataset_name}/analysis_suggestions")
async def get_analysis_suggestions(dataset_name: str) -> dict:
    """AI-powered analysis recommendations based on dataset characteristics"""
    if dataset_name not in dataset_schemas:
        return {"error": f"Dataset '{dataset_name}' not loaded"}
        
    schema = dataset_schemas[dataset_name]
    
    # Get columns by type
    numerical_cols = [name for name, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    categorical_cols = [name for name, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    temporal_cols = [name for name, info in schema.columns.items() 
                    if info.suggested_role == 'temporal']
    
    suggestions = []
    
    # Numerical columns → correlation analysis
    if len(numerical_cols) >= 2:
        suggestions.append({
            "type": "correlation_analysis",
            "description": f"Find relationships between {len(numerical_cols)} numerical variables",
            "columns": numerical_cols,
            "tool": "find_correlations",
            "priority": "high"
        })
    
    # Categorical columns → segmentation
    if categorical_cols and numerical_cols:
        suggestions.append({
            "type": "segmentation",
            "description": f"Group data by {len(categorical_cols)} categorical variables",
            "columns": categorical_cols,
            "tool": "segment_by_column", 
            "priority": "high"
        })
    
    # Date columns → time series
    if temporal_cols and numerical_cols:
        suggestions.append({
            "type": "time_series",
            "description": f"Analyze trends over time using {len(temporal_cols)} date columns",
            "columns": temporal_cols,
            "tool": "time_series_analysis",
            "priority": "medium"
        })
    
    # Data quality checks
    high_null_cols = [name for name, info in schema.columns.items() 
                     if info.null_percentage > 10]
    if high_null_cols:
        suggestions.append({
            "type": "data_quality",
            "description": f"Review data quality - {len(high_null_cols)} columns have >10% missing values",
            "columns": high_null_cols,
            "tool": "validate_data_quality",
            "priority": "medium"
        })
    
    return {
        "dataset_name": dataset_name,
        "suggestions": suggestions,
        "dataset_summary": {
            "numerical_columns": len(numerical_cols),
            "categorical_columns": len(categorical_cols),
            "temporal_columns": len(temporal_cols)
        }
    }

@mcp.resource("analytics://memory_usage")
async def get_memory_usage() -> dict:
    """Monitor memory usage of loaded datasets"""
    usage = []
    total_memory = 0
    
    for name in DatasetManager.list_datasets():
        info = DatasetManager.get_dataset_info(name)
        memory_mb = info["memory_usage_mb"]
        total_memory += memory_mb
        
        usage.append({
            "dataset": name,
            "memory_mb": round(memory_mb, 1),
            "rows": info["shape"][0],
            "columns": info["shape"][1]
        })
    
    # Sort by memory usage
    usage.sort(key=lambda x: x["memory_mb"], reverse=True)
    
    return {
        "datasets": usage,
        "total_memory_mb": round(total_memory, 1),
        "dataset_count": len(usage)
    }
```

---

## Multi-Dataset Operations

### Cross-Dataset Analysis Tools

```python
@mcp.tool()
async def compare_datasets(dataset_a: str, dataset_b: str, common_columns: List[str] = None) -> dict:
    """Compare two datasets on common dimensions"""
    df_a = DatasetManager.get_dataset(dataset_a)
    df_b = DatasetManager.get_dataset(dataset_b)
    
    # Find common columns if not specified
    if common_columns is None:
        common_columns = list(set(df_a.columns) & set(df_b.columns))
    
    if not common_columns:
        return {"error": "No common columns found between datasets"}
    
    comparison = {
        "datasets": [dataset_a, dataset_b],
        "common_columns": common_columns,
        "shape_comparison": {
            dataset_a: df_a.shape,
            dataset_b: df_b.shape
        },
        "column_analysis": {}
    }
    
    # Compare each common column
    for col in common_columns:
        if col in df_a.columns and col in df_b.columns:
            comparison["column_analysis"][col] = {
                "type_a": str(df_a[col].dtype),
                "type_b": str(df_b[col].dtype),
                "unique_values_a": df_a[col].nunique(),
                "unique_values_b": df_b[col].nunique(),
                "null_pct_a": round(df_a[col].isnull().mean() * 100, 2),
                "null_pct_b": round(df_b[col].isnull().mean() * 100, 2)
            }
            
            # For numerical columns, add statistical comparison
            if pd.api.types.is_numeric_dtype(df_a[col]) and pd.api.types.is_numeric_dtype(df_b[col]):
                comparison["column_analysis"][col].update({
                    "mean_a": round(df_a[col].mean(), 2),
                    "mean_b": round(df_b[col].mean(), 2),
                    "std_a": round(df_a[col].std(), 2),
                    "std_b": round(df_b[col].std(), 2)
                })
    
    return comparison

@mcp.tool()
async def merge_datasets(dataset_configs: List[dict], join_strategy: str = "inner") -> dict:
    """Join datasets on common keys"""
    if len(dataset_configs) < 2:
        return {"error": "Need at least 2 datasets to merge"}
    
    # Get first dataset as base
    base_config = dataset_configs[0]
    result_df = DatasetManager.get_dataset(base_config["dataset_name"])
    
    merge_log = [{
        "step": 1,
        "action": "base_dataset",
        "dataset": base_config["dataset_name"],
        "shape": result_df.shape
    }]
    
    # Merge each additional dataset
    for i, config in enumerate(dataset_configs[1:], 2):
        merge_df = DatasetManager.get_dataset(config["dataset_name"])
        join_keys = config.get("join_keys", [])
        
        if not join_keys:
            # Auto-detect common columns
            join_keys = list(set(result_df.columns) & set(merge_df.columns))
        
        if not join_keys:
            return {"error": f"No join keys found for dataset {config['dataset_name']}"}
        
        # Perform merge
        result_df = pd.merge(
            result_df, 
            merge_df, 
            on=join_keys, 
            how=join_strategy,
            suffixes=('', f'_{config["dataset_name"]}')
        )
        
        merge_log.append({
            "step": i,
            "action": "merge",
            "dataset": config["dataset_name"],
            "join_keys": join_keys,
            "join_strategy": join_strategy,
            "result_shape": result_df.shape
        })
    
    # Store merged dataset
    merged_name = f"merged_{'_'.join([c['dataset_name'] for c in dataset_configs])}"
    loaded_datasets[merged_name] = result_df
    
    return {
        "merged_dataset_name": merged_name,
        "final_shape": result_df.shape,
        "merge_log": merge_log,
        "columns": list(result_df.columns)
    }
```

---

## AI-Guided Data Exploration

### Intelligent Prompt System
```python
@mcp.prompt()
async def dataset_first_look(dataset_name: str) -> str:
    """Adaptive first-look analysis based on dataset characteristics"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    
    # Organize columns by type for display
    numerical_cols = [name for name, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    categorical_cols = [name for name, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    temporal_cols = [name for name, info in schema.columns.items() 
                    if info.suggested_role == 'temporal']
    
    prompt = f"""Let's explore your **{dataset_name}** dataset together! 

I can see you have **{schema.row_count:,} records** with **{len(schema.columns)} columns**:

"""
    
    if numerical_cols:
        prompt += f"**📊 Numerical columns** ({len(numerical_cols)}): {', '.join(numerical_cols)}\n"
        prompt += "→ Perfect for correlation analysis, statistical summaries, and trend analysis\n\n"
    
    if categorical_cols:
        prompt += f"**🏷️ Categorical columns** ({len(categorical_cols)}): {', '.join(categorical_cols)}\n"  
        prompt += "→ Great for segmentation, group comparisons, and distribution analysis\n\n"
    
    if temporal_cols:
        prompt += f"**📅 Date/Time columns** ({len(temporal_cols)}): {', '.join(temporal_cols)}\n"
        prompt += "→ Ideal for time series analysis and trend identification\n\n"
    
    # Add specific recommendations based on data
    prompt += "**🎯 Recommended starting points:**\n"
    
    if len(numerical_cols) >= 2:
        prompt += f"• **Correlation Analysis**: Explore relationships between {numerical_cols[0]} and {numerical_cols[1]}\n"
    
    if categorical_cols and numerical_cols:
        prompt += f"• **Segmentation**: Group by {categorical_cols[0]} to analyze {numerical_cols[0]} patterns\n"
    
    if temporal_cols and numerical_cols:
        prompt += f"• **Time Trends**: Track {numerical_cols[0]} changes over {temporal_cols[0]}\n"
    
    # Data quality insights
    high_null_cols = [name for name, info in schema.columns.items() 
                     if info.null_percentage > 10]
    if high_null_cols:
        prompt += f"• **Data Quality Review**: {len(high_null_cols)} columns have missing values to investigate\n"
    
    prompt += f"\n**Available tools**: `segment_by_column`, `find_correlations`, `create_chart`, `validate_data_quality`\n"
    prompt += f"\nWhat aspect of your {dataset_name} data would you like to explore first?"
    
    return prompt

@mcp.prompt()
async def segmentation_workshop(dataset_name: str) -> str:
    """Interactive segmentation guidance based on actual dataset"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    
    # Find categorical columns suitable for segmentation
    categorical_cols = [name for name, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    numerical_cols = [name for name, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    
    if not categorical_cols:
        return f"No categorical columns found in {dataset_name} for segmentation. Consider creating segments from numerical columns using ranges."
    
    prompt = f"""Let's create meaningful segments from your **{dataset_name}** data!

**Available categorical columns for grouping:**
"""
    
    for col in categorical_cols:
        col_info = schema.columns[col]
        prompt += f"• **{col}**: {col_info.unique_values} unique values (examples: {', '.join(map(str, col_info.sample_values))})\n"
    
    if numerical_cols:
        prompt += f"\n**Numerical columns to analyze by segment:**\n"
        for col in numerical_cols:
            col_info = schema.columns[col]
            prompt += f"• **{col}**: {col_info.dtype} (sample values: {', '.join(map(str, col_info.sample_values))})\n"
    
    prompt += f"""
**Segmentation strategies:**

1. **Simple segmentation**: Group by one categorical column
   Example: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`

2. **Cross-segmentation**: Combine multiple categories (manual analysis)
   Example: Group by {categorical_cols[0]}, then analyze patterns within each group

3. **Value-based segments**: Focus on high/low values of numerical columns
   Example: Top 20% vs bottom 20% by {numerical_cols[0] if numerical_cols else 'value'}

Which segmentation approach interests you most? I can guide you through the specific pandas operations."""
    
    return prompt

@mcp.prompt()
async def data_quality_assessment(dataset_name: str) -> str:
    """Guide systematic data quality review"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    df = DatasetManager.get_dataset(dataset_name)
    
    prompt = f"""Let's systematically review the quality of your **{dataset_name}** dataset.

**Dataset Overview:**
• **{schema.row_count:,} rows** × **{len(schema.columns)} columns**
• **Memory usage**: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB

**Data Quality Indicators:**
"""
    
    # Missing values analysis
    missing_data = []
    for col_name, col_info in schema.columns.items():
        if col_info.null_percentage > 0:
            missing_data.append((col_name, col_info.null_percentage))
    
    if missing_data:
        missing_data.sort(key=lambda x: x[1], reverse=True)
        prompt += f"\n**📋 Missing Values** ({len(missing_data)} columns affected):\n"
        for col, pct in missing_data[:5]:  # Show top 5
            prompt += f"• **{col}**: {pct:.1f}% missing\n"
        if len(missing_data) > 5:
            prompt += f"• ... and {len(missing_data) - 5} more columns\n"
    else:
        prompt += f"\n**✅ Missing Values**: No missing values detected!\n"
    
    # Duplicates check (simple heuristic)
    potential_id_cols = [name for name, info in schema.columns.items() 
                        if info.suggested_role == 'identifier']
    
    if potential_id_cols:
        prompt += f"\n**🔍 Potential Duplicates**: Check uniqueness of {', '.join(potential_id_cols)}\n"
    
    # Data type consistency
    mixed_type_cols = [name for name, info in schema.columns.items() 
                      if info.dtype == 'object' and info.suggested_role not in ['categorical', 'identifier']]
    
    if mixed_type_cols:
        prompt += f"\n**⚠️ Mixed Data Types**: {', '.join(mixed_type_cols)} may need type conversion\n"
    
    prompt += f"""
**Recommended quality checks:**

1. **Run validation**: `validate_data_quality('{dataset_name}')` for comprehensive analysis
2. **Examine distributions**: `create_chart('{dataset_name}', 'histogram', 'column_name')` for outliers
3. **Check relationships**: `find_correlations('{dataset_name}')` for unexpected patterns

What data quality aspect would you like to investigate first?"""
    
    return prompt
```

---

## Resource Workaround Strategy

### Problem Statement

Some MCP clients may not fully support the **Resource** protocol, which limits their ability to access the rich contextual data our analytics server provides through 12 dynamic resources. This creates a compatibility gap where tool-only clients cannot access dataset schemas, memory usage, analysis suggestions, and other critical read-only information.

### Solution Overview

Implement **Resource Mirror Tools** - a parallel set of tools with `resource_*` prefixes that provide identical functionality to our existing resources. This approach ensures 100% compatibility with tool-only clients while maintaining our existing resource architecture for clients that support it.

### Dual Access Pattern
```
Resource-Enabled Clients:           Tool-Only Clients:
├── @mcp.resource()                ├── @mcp.tool() 
├── datasets://loaded              ├── resource_datasets_loaded()
├── analytics://memory_usage       ├── resource_analytics_memory_usage()
└── datasets://{name}/schema       └── resource_datasets_schema(name)
```

### Benefits
- ✅ **Universal Compatibility** - Works with any MCP client regardless of resource support
- ✅ **Identical Data Access** - Same information available through both patterns  
- ✅ **Zero Breaking Changes** - Existing resource-enabled clients continue working unchanged
- ✅ **Consistent API** - Resource tools use same parameters and return formats
- ✅ **Easy Migration** - Tool-only clients can switch to resources when support is added

### Resource Mapping Strategy

#### Dataset Context Resources → Tools

| Resource URI | Tool Function | Parameters | Description |
|--------------|---------------|------------|-------------|
| `datasets://loaded` | `resource_datasets_loaded()` | None | List all loaded datasets |
| `datasets://{name}/schema` | `resource_datasets_schema(name)` | `dataset_name: str` | Dynamic schema info |
| `datasets://{name}/summary` | `resource_datasets_summary(name)` | `dataset_name: str` | Statistical summary |
| `datasets://{name}/sample` | `resource_datasets_sample(name)` | `dataset_name: str` | Sample rows |

#### Analytics Intelligence Resources → Tools

| Resource URI | Tool Function | Parameters | Description |
|--------------|---------------|------------|-------------|
| `analytics://current_dataset` | `resource_analytics_current_dataset()` | None | Active dataset context |
| `analytics://available_analyses` | `resource_analytics_available_analyses()` | None | Applicable analysis types |
| `analytics://column_types` | `resource_analytics_column_types()` | None | Column classifications |
| `analytics://suggested_insights` | `resource_analytics_suggested_insights()` | None | AI recommendations |
| `analytics://memory_usage` | `resource_analytics_memory_usage()` | None | Memory monitoring |

#### System Resources → Tools

| Resource URI | Tool Function | Parameters | Description |
|--------------|---------------|------------|-------------|
| `config://server` | `resource_config_server()` | None | Server configuration |
| `users://{user_id}/profile` | `resource_users_profile(user_id)` | `user_id: str` | User profile by ID |
| `system://status` | `resource_system_status()` | None | System health info |

### Implementation Example

```python
# Add to server.py

@mcp.tool()
async def resource_datasets_loaded() -> dict:
    """Tool mirror of datasets://loaded resource."""
    from .resources.data_resources import get_loaded_datasets
    return await get_loaded_datasets()

@mcp.tool()
async def resource_datasets_schema(dataset_name: str) -> dict:
    """Tool mirror of datasets://{name}/schema resource."""
    from .resources.data_resources import get_dataset_schema
    return await get_dataset_schema(dataset_name)

@mcp.tool()
async def resource_analytics_memory_usage() -> dict:
    """Tool mirror of analytics://memory_usage resource."""
    from .resources.data_resources import get_memory_usage
    return await get_memory_usage()
```

---

## Architecture Benefits

### True Reusability
- **One Server, Any Data**: Works with customer data, sales records, surveys, inventory, etc.
- **No Hardcoding**: Zero dataset-specific assumptions in tools or prompts
- **Instant Adaptation**: Load new dataset and immediately get relevant analysis options

### Modular Excellence
- **Data Layer Abstraction**: Pandas operations work identically across any structured data
- **Analysis Portability**: Same correlation/segmentation tools work on any applicable columns
- **Visualization Flexibility**: Charts adapt to data types and characteristics

### AI-Guided Discovery
- **Smart Recommendations**: AI suggests analyses based on actual data characteristics
- **Interactive Exploration**: Conversational guidance through complex analytics workflows
- **Context-Aware Prompts**: Prompts that reference actual column names and data patterns

### Business Value
- **Immediate Utility**: Drop in ANY business dataset and start analyzing immediately
- **Non-Technical Friendly**: AI guides users through analytics without requiring pandas knowledge
- **Scalable Insights**: Same server grows from 100-row CSV to 100K-row enterprise data

## Extension Pathways

### Advanced Analytics Integration
- **ML Pipeline**: Automatic feature engineering and model suggestion based on data
- **Statistical Testing**: A/B testing, significance testing, hypothesis validation
- **Forecasting**: Time series forecasting when temporal patterns detected

### Enterprise Features
- **Multi-Dataset Workflows**: Join and compare multiple datasets intelligently
- **Automated Reporting**: Generate business reports with insights and recommendations
- **Real-Time Updates**: Stream new data and update analyses automatically

### Collaboration Tools
- **Insight Sharing**: Export findings in business-friendly formats
- **Analysis Templates**: Save and reuse analysis workflows across datasets
- **Team Dashboards**: Collaborative analytics with role-based access

This generic approach transforms our MCP server from a user analytics tool into a **universal data analysis platform** that demonstrates the true power of modular architecture - building once and adapting to infinite use cases.

---

*This analytics framework provides comprehensive capabilities for building intelligent, dataset-agnostic analysis tools that scale from simple CSV files to enterprise data warehouses while maintaining the highest standards of usability and flexibility.*
