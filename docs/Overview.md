# MCP Server Engineering Documentation

## Engineering Objective

Build production-grade MCP servers using proven architecture patterns. Documentation provides implementation guidance, not conceptual frameworks.

## Core Architecture: Prompt -> Tool -> Resource

### Value Hierarchy vs Implementation Order (Critical)

**Design Hierarchy** (most to least important):
```
1. PROMPT - Intelligent workflows (HIGHEST IMPORTANCE)
2. TOOL - Atomic operations (supporting prompts)
3. RESOURCE - Data context (supporting foundation)
```

**Implementation Order** (dependencies first):
```
1. RESOURCE - Data foundation (build first)
2. TOOL - Operations layer (build second)
3. PROMPT - Orchestration (build last, delivers most value)
```

**Critical Insight**: Prompts are the MOST IMPORTANT - they transform simple tools into intelligent workflows. Design everything to support powerful prompts. We build Resources→Tools→Prompts due to dependencies, but Prompts drive the entire design.

### Architecture Rationale

**Prompt Layer (MOST IMPORTANT)**
- Transforms tools into intelligent workflows
- Provides contextual guidance and expertise
- Delivers exponential value through orchestration
- Where the true intelligence lives
- Implementation: @mcp.prompt() decorators

**Tool Layer (SUPPORTING PROMPTS)**
- Atomic operations that prompts compose
- Building blocks designed for prompt orchestration
- Can be used directly but designed for workflows
- Implementation: @mcp.tool() decorators

**Resource Layer (FOUNDATION)**
- Provides data and context to tools
- Enables dynamic, real-time operations
- Foundation that enables tool flexibility
- Implementation: @mcp.resource() decorators

## Implementation Framework

### Technical Stack
- FastMCP framework v1.0+ (required)
- Python 3.11+ 
- Pandas 2.0+ for data operations
- Async/await patterns throughout
- Additional dependencies as needed for domain

### Development Timeline: 2 Weeks Maximum

**Week 1: Core Implementation**
- Day 1-2: Server framework, basic prompts
- Day 3-4: Tool implementation, error handling
- Day 5-7: Resource layer, integration testing

**Week 2: Production Hardening**
- Day 8-10: Performance optimization, security
- Day 11-12: Deployment configuration
- Day 13-14: Production validation, documentation

### Quality Gates

**Week 1 Exit Criteria:**
- Functional MCP server with prompt/tool/resource layers
- Sub-second response times for basic operations
- Comprehensive error handling
- Unit test coverage >80%

**Week 2 Exit Criteria:**
- Production deployment configuration
- Performance benchmarks met
- Security validation complete
- Operation procedures documented

## Document Structure

### Primary Implementation Documents
1. **Architecture_and_Development.md** - Core patterns, FastMCP implementation
2. **Trading_Operations.md** - Domain-specific example implementation
3. **Data_Analytics_Framework.md** - Generic data processing patterns
4. **Core_Principles.md** - Engineering standards, quality practices

### Supporting Documents
5. **Integration_and_Operations.md** - Production deployment, monitoring
6. **Implementation_Templates.md** - Ready-to-use code templates

## Technical Standards

### Code Quality Requirements
- Type hints for all function signatures
- Comprehensive error handling with specific error types
- Async/await for all I/O operations
- Logging at appropriate levels (INFO, WARNING, ERROR)
- Input validation for all external data

### Performance Requirements
- Response time: <500ms for 95th percentile, <1000ms for 99th percentile
- Memory usage: <1GB per server instance
- Error rate: <1% under normal load
- Uptime target: 99.9% availability
- Graceful degradation under load
- Connection pooling for external resources

### Security Requirements
- Input sanitization for all user data
- Authentication for production deployments
- Audit logging for all operations
- Rate limiting on public endpoints

## Implementation Anti-Patterns

**Avoid These Common Mistakes:**
- Building resources before understanding prompt requirements
- Implementing complex features before basic functionality works
- Over-engineering initial implementation
- Ignoring error handling until integration phase
- Skipping performance testing until production

## Validation Strategy

### Testing Approach
- Unit tests for individual components
- Integration tests for prompt workflows
- Load testing for performance validation
- Security testing for production readiness

### Success Metrics
- Functional completeness: All specified operations work
- Performance: Meet defined response time targets
- Reliability: <1% error rate under normal load
- Maintainability: Code review passes, documentation complete

## Engineering Philosophy

Focus on working implementations. Deliver functional systems within timeline constraints. Optimize for maintainability and debuggability. Plan for production operation from initial design.

Build proven solutions using established patterns. Test with real data. Measure actual performance.
