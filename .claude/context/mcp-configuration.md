# MCP Server Configuration

## Installed MCP Servers

**✅ Core Servers (Production Ready & Connected):**
- **Context7**: Library documentation and API references → `https://mcp.context7.com/mcp`
- **Sentry**: Error monitoring, issue analysis, performance tracking → `https://mcp.sentry.dev/mcp`
- **Exa**: Advanced web search and research capabilities → `npx -y exa-mcp-server`
- **Filesystem**: Enhanced file operations and directory management → `npx @modelcontextprotocol/server-filesystem`

**✅ Browser & Automation (Connected):**
- **Playwright**: Browser automation, console access, web testing → `npx @playwright/mcp@latest`
  - ✅ **CONFIRMED**: Perfect for reading browser console messages and returns
  - ✅ **Accessibility Tree**: Structured data representation of web pages  
  - ✅ **Network Monitoring**: API calls and responses tracking
  - ✅ **Real-time Debugging**: Interactive browser sessions for testing HydroML frontend
  - ✅ **Screenshot Capture**: Visual debugging and documentation

**✅ Development Tools (Connected):**
- **GitHub Official**: Advanced repository management beyond gh CLI → `ghcr.io/github/github-mcp-server`
  - Status: ✅ **CONNECTED** - Docker-based with token authentication
  - Features: Issues, PRs, repos, actions, code security, discussions, gists

**⚠️ Database & Infrastructure (Configuration Required):**
- **PostgreSQL**: Database operations and query optimization → `npx @modelcontextprotocol/server-postgres`
  - Status: ⚠️ Configured but connection issues (Docker services required)
  - Features: Direct SQL operations, query optimization, schema analysis

**🔄 New Installations (In Configuration):**
- **Redis Official**: Cache & session management → `uvx redis/mcp-redis`
  - Status: 🔄 Recently installed, requires environment configuration
  - Features: Natural language Redis operations, cache management, session storage
- **Django MCP Server**: Django app integration → `uvx django-mcp-server`  
  - Status: 🔄 Recently installed, requires Django project configuration
  - Features: AI interaction with Django models, API generation, admin operations

## MCP Server Implementation Roadmap

**🥇 Tier 1: CRÍTICO - Completed ✅**
1. ✅ **Playwright MCP** - Browser context & console debugging (CONNECTED)
2. ✅ **GitHub Official MCP** - Advanced repository management (CONNECTED)  
3. ✅ **Filesystem MCP** - Enhanced file operations (CONNECTED)
4. ✅ **Context7, Sentry, Exa** - Documentation, monitoring, research (CONNECTED)

**🥈 Tier 2: ALTO IMPACTO - In Progress 🔄**
1. 🔄 **Redis Official MCP** - Cache & session management (INSTALLED, needs config)
2. 🔄 **Django MCP Server** - Django app integration (INSTALLED, needs config)
3. ⚠️ **PostgreSQL MCP** - Database operations (INSTALLED, connection issues)

**🥉 Tier 3: ESPECIALIZADO - Planning 📋**
1. 🔍 **Docker MCP Toolkit** - Container management (requires Docker Desktop)
2. 🔍 **MLflow MCP** - ML experiment tracking (research needed)
3. 🔍 **Apache Airflow MCP** - Workflow orchestration (future consideration)

## Browser Console & Playwright Integration

**⚡ Protocolo de Debugging Optimizado:**

**Flujo de Debugging Jerarquico (Token-Optimizado):**
1. **🥇 Django Logs**: `docker compose logs web --tail=20` (SIEMPRE PRIMERO - 0 tokens)
   - ✅ Detecta: Errores Python, template issues, missing dependencies, server status
   - ✅ **Comando**: `docker compose logs web --tail=20`

2. **🥈 Browser Console Only**: `browser_console_messages` (MEDIO - tokens optimizados)  
   - ✅ Detecta: JavaScript errors, network failures, client-side issues
   - ✅ **Comando**: `mcp__playwright__browser_console_messages`
   - ✅ **Ventaja**: Solo console logs, sin DOM snapshot completo

3. **🥉 Visual Debug**: Playwright full snapshot (ÚLTIMO RECURSO - alto token usage)
   - ✅ Propósito: Confirmación visual, complex UI interactions
   - ✅ **Comando**: `mcp__playwright__browser_snapshot`

## GitHub MCP Setup

**Configuration:**
```json
{
  "command": "docker",
  "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "gho_****"
  }
}
```

**Features Available:**
- ✅ **Repository Management**: Browse code, analyze commits, manage branches
- ✅ **Issues & PRs**: Create, update, comment, assign, merge pull requests  
- ✅ **GitHub Actions**: Monitor workflows, analyze build failures, manage CI/CD
- ✅ **Code Security**: Code scanning alerts, Dependabot, secret scanning
- ✅ **Team Collaboration**: Discussions, notifications, team management
- ✅ **Advanced Search**: Code search, repository search, user search

## MCP Server Status Summary

**✅ FULLY OPERATIONAL (6 servers):**
- Context7, Sentry, Exa, Filesystem, Playwright, GitHub Official

**🔄 INSTALLED - CONFIGURATION NEEDED (3 servers):**
- Redis Official (requires environment vars)
- Django MCP Server (requires Django project integration)  
- PostgreSQL (requires connection troubleshooting)

**🔍 PLANNED - FUTURE IMPLEMENTATION:**
- Docker MCP Toolkit (Docker Desktop integration)
- MLflow MCP (research & custom implementation)
- Apache Airflow MCP (workflow orchestration)

**🎯 NEXT PRIORITY ACTIONS:**
1. Configure Redis MCP with HydroML Docker environment
2. Integrate Django MCP Server with HydroML models
3. Resolve PostgreSQL MCP connection issues
4. Explore Docker Desktop MCP Toolkit integration