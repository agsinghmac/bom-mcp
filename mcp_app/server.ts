import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { registerAppTool, registerAppResource } from '@modelcontextprotocol/ext-apps/server';
import path from 'path';
import { fileURLToPath } from 'url';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Create MCP server
const server = new McpServer(
  { name: 'esp-bom-mcp-app', version: '1.0.0' },
  { capabilities: {} }
);

// Helper to forward tool calls to Python MCP server
async function callPythonTool(toolName: string, args: Record<string, unknown> = {}) {
  const params = new URLSearchParams(args as Record<string, string>).toString();
  const url = `http://localhost:3001/tool/${toolName}${params ? '?' + params : ''}`;
  const res = await fetch(url);
  return await res.json();
}

// Tool implementations
const listPartsHandler = async () => {
  const data = await callPythonTool('list_parts');
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getPartHandler = async (args: { part_number: string }) => {
  const data = await callPythonTool('get_part', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const searchPartsHandler = async (args: { query: string }) => {
  const data = await callPythonTool('search_parts', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getPartsByCategoryHandler = async (args: { category: string }) => {
  const data = await callPythonTool('get_parts_by_category', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getCriticalPartsHandler = async () => {
  const data = await callPythonTool('get_critical_parts');
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getPartAssembliesHandler = async (args: { part_number: string }) => {
  const data = await callPythonTool('get_part_assemblies', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getEspBomHandler = async (args: { esp_id: string }) => {
  const data = await callPythonTool('get_esp_bom', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getBomSummaryHandler = async (args: { esp_id: string }) => {
  const data = await callPythonTool('get_bom_summary', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

// ============ New View Tool Handlers ============

const getStatsHandler = async () => {
  const data = await callPythonTool('get_stats');
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const listESPsHandler = async () => {
  const data = await callPythonTool('list_esps');
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getESPsBySeriesHandler = async (args: { series: string }) => {
  const data = await callPythonTool('get_esps_by_series', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const createESPHandler = async (args: {
  esp_id: string;
  model_name: string;
  series: string;
  power_rating_kw: number;
  voltage_v: number;
  frequency_hz: number;
  flow_rate_m3d: number;
  stages: number;
  cable_length_m: number;
}) => {
  const data = await callPythonTool('create_esp', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const deleteESPHandler = async (args: { esp_id: string }) => {
  const data = await callPythonTool('delete_esp', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const createPartHandler = async (args: {
  part_number: string;
  name: string;
  category: string;
  material: string;
  weight_kg: number;
  is_critical: boolean;
}) => {
  const data = await callPythonTool('create_part', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const updatePartHandler = async (args: {
  part_number: string;
  name?: string;
  category?: string;
  material?: string;
  weight_kg?: number;
  is_critical?: boolean;
}) => {
  const data = await callPythonTool('update_part', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const deletePartHandler = async (args: { part_number: string; force?: boolean }) => {
  const data = await callPythonTool('delete_part', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const listAssembliesHandler = async () => {
  const data = await callPythonTool('list_assemblies');
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getAssemblyHandler = async (args: { assembly_code: string }) => {
  const data = await callPythonTool('get_assembly', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const getAssemblyESPsHandler = async (args: { assembly_code: string }) => {
  const data = await callPythonTool('get_assembly_esps', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const createAssemblyHandler = async (args: { assembly_code: string; name: string }) => {
  const data = await callPythonTool('create_assembly', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const deleteAssemblyHandler = async (args: { assembly_code: string; force?: boolean }) => {
  const data = await callPythonTool('delete_assembly', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const addPartToAssemblyHandler = async (args: { assembly_code: string; part_number: string }) => {
  const data = await callPythonTool('add_part_to_assembly', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const removePartFromAssemblyHandler = async (args: { assembly_code: string; part_number: string }) => {
  const data = await callPythonTool('remove_part_from_assembly', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

const updateAssemblyPartQuantityHandler = async (args: { assembly_code: string; part_number: string; quantity: number }) => {
  const data = await callPythonTool('update_assembly_part_quantity', args);
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
};

// Resources path
const resourcesPath = path.resolve(__dirname, 'resources');

// Register UI tools
registerAppTool(server, 'list_parts', {
  description: 'List all parts in the database',
  _meta: { ui: { resourceUri: 'parts-table.html', visibility: ['model', 'app'] } },
}, listPartsHandler);

registerAppTool(server, 'search_parts', {
  description: 'Search parts by name, category, or material',
  inputSchema: { properties: { query: { type: 'string' } }, required: ['query'], type: 'object' },
  _meta: { ui: { resourceUri: 'parts-table.html', visibility: ['model', 'app'] } },
}, searchPartsHandler);

registerAppTool(server, 'get_parts_by_category', {
  description: 'Get all parts in a given category',
  inputSchema: { properties: { category: { type: 'string' } }, required: ['category'], type: 'object' },
  _meta: { ui: { resourceUri: 'parts-table.html', visibility: ['model', 'app'] } },
}, getPartsByCategoryHandler);

registerAppTool(server, 'get_critical_parts', {
  description: 'List all critical parts',
  _meta: { ui: { resourceUri: 'parts-table.html', visibility: ['model', 'app'] } },
}, getCriticalPartsHandler);

registerAppTool(server, 'get_part', {
  description: 'Get a specific part by part number',
  inputSchema: { properties: { part_number: { type: 'string' } }, required: ['part_number'], type: 'object' },
  _meta: { ui: { resourceUri: 'part-detail.html', visibility: ['model', 'app'] } },
}, getPartHandler);

registerAppTool(server, 'get_esp_bom', {
  description: 'Get the Bill of Materials for an ESP',
  inputSchema: { properties: { esp_id: { type: 'string' } }, required: ['esp_id'], type: 'object' },
  _meta: { ui: { resourceUri: 'bom-table.html', visibility: ['model', 'app'] } },
}, getEspBomHandler);

registerAppTool(server, 'get_bom_summary', {
  description: 'Get BOM summary for an ESP',
  inputSchema: { properties: { esp_id: { type: 'string' } }, required: ['esp_id'], type: 'object' },
  _meta: { ui: { resourceUri: 'bom-summary.html', visibility: ['model', 'app'] } },
}, getBomSummaryHandler);

// ============ Register New View Tools ============

// Dashboard View
registerAppTool(server, 'view_dashboard', {
  description: 'Show ESP dashboard with stats, critical parts, and series overview',
  _meta: { ui: { resourceUri: 'view-dashboard.html', visibility: ['model', 'app'] } },
}, getStatsHandler);

// ESP Catalogue View
registerAppTool(server, 'view_esp_catalogue', {
  description: 'List all ESP pumps with filtering, create, and delete operations',
  _meta: { ui: { resourceUri: 'view-esp-catalogue.html', visibility: ['model', 'app'] } },
}, listESPsHandler);

registerAppTool(server, 'get_esps_by_series', {
  description: 'Get ESPs filtered by series',
  inputSchema: { properties: { series: { type: 'string' } }, required: ['series'], type: 'object' },
  _meta: { ui: { resourceUri: 'view-esp-catalogue.html', visibility: ['model', 'app'] } },
}, getESPsBySeriesHandler);

registerAppTool(server, 'create_esp', {
  description: 'Create a new ESP pump',
  inputSchema: {
    properties: {
      esp_id: { type: 'string' },
      model_name: { type: 'string' },
      series: { type: 'string' },
      power_rating_kw: { type: 'number' },
      voltage_v: { type: 'number' },
      frequency_hz: { type: 'number' },
      flow_rate_m3d: { type: 'number' },
      stages: { type: 'number' },
      cable_length_m: { type: 'number' },
    },
    required: ['esp_id', 'model_name', 'series', 'power_rating_kw', 'voltage_v', 'frequency_hz', 'flow_rate_m3d', 'stages', 'cable_length_m'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'view-esp-catalogue.html', visibility: ['model', 'app'] } },
}, createESPHandler);

registerAppTool(server, 'delete_esp', {
  description: 'Delete an ESP pump',
  inputSchema: { properties: { esp_id: { type: 'string' } }, required: ['esp_id'], type: 'object' },
  _meta: { ui: { resourceUri: 'view-esp-catalogue.html', visibility: ['model', 'app'] } },
}, deleteESPHandler);

// BOM Viewer View
registerAppTool(server, 'view_esp_bom', {
  description: 'View BOM for a specific ESP with parts table and export',
  inputSchema: { properties: { esp_id: { type: 'string' } }, required: ['esp_id'], type: 'object' },
  _meta: { ui: { resourceUri: 'view-esp-bom.html', visibility: ['model', 'app'] } },
}, getEspBomHandler);

// Parts Manager View
registerAppTool(server, 'manage_parts', {
  description: 'Manage parts with search, filters, create, edit, and delete',
  _meta: { ui: { resourceUri: 'manage-parts.html', visibility: ['model', 'app'] } },
}, listPartsHandler);

registerAppTool(server, 'create_part', {
  description: 'Create a new part',
  inputSchema: {
    properties: {
      part_number: { type: 'string' },
      name: { type: 'string' },
      category: { type: 'string' },
      material: { type: 'string' },
      weight_kg: { type: 'number' },
      is_critical: { type: 'boolean' },
    },
    required: ['part_number', 'name', 'category', 'material', 'weight_kg'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-parts.html', visibility: ['model', 'app'] } },
}, createPartHandler);

registerAppTool(server, 'update_part', {
  description: 'Update an existing part',
  inputSchema: {
    properties: {
      part_number: { type: 'string' },
      name: { type: 'string' },
      category: { type: 'string' },
      material: { type: 'string' },
      weight_kg: { type: 'number' },
      is_critical: { type: 'boolean' },
    },
    required: ['part_number'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-parts.html', visibility: ['model', 'app'] } },
}, updatePartHandler);

registerAppTool(server, 'delete_part', {
  description: 'Delete a part',
  inputSchema: {
    properties: {
      part_number: { type: 'string' },
      force: { type: 'boolean' },
    },
    required: ['part_number'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-parts.html', visibility: ['model', 'app'] } },
}, deletePartHandler);

// Assembly Manager View
registerAppTool(server, 'manage_assemblies', {
  description: 'Manage assemblies with parts, create, and delete operations',
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, listAssembliesHandler);

registerAppTool(server, 'get_assembly', {
  description: 'Get an assembly with its parts',
  inputSchema: { properties: { assembly_code: { type: 'string' } }, required: ['assembly_code'], type: 'object' },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, getAssemblyHandler);

registerAppTool(server, 'get_assembly_esps', {
  description: 'Get ESPs that use a specific assembly',
  inputSchema: { properties: { assembly_code: { type: 'string' } }, required: ['assembly_code'], type: 'object' },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, getAssemblyESPsHandler);

registerAppTool(server, 'create_assembly', {
  description: 'Create a new assembly',
  inputSchema: {
    properties: {
      assembly_code: { type: 'string' },
      name: { type: 'string' },
    },
    required: ['assembly_code', 'name'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, createAssemblyHandler);

registerAppTool(server, 'delete_assembly', {
  description: 'Delete an assembly',
  inputSchema: {
    properties: {
      assembly_code: { type: 'string' },
      force: { type: 'boolean' },
    },
    required: ['assembly_code'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, deleteAssemblyHandler);

registerAppTool(server, 'add_part_to_assembly', {
  description: 'Add a part to an assembly',
  inputSchema: {
    properties: {
      assembly_code: { type: 'string' },
      part_number: { type: 'string' },
    },
    required: ['assembly_code', 'part_number'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, addPartToAssemblyHandler);

registerAppTool(server, 'remove_part_from_assembly', {
  description: 'Remove a part from an assembly',
  inputSchema: {
    properties: {
      assembly_code: { type: 'string' },
      part_number: { type: 'string' },
    },
    required: ['assembly_code', 'part_number'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, removePartFromAssemblyHandler);

registerAppTool(server, 'update_assembly_part_quantity', {
  description: 'Update quantity of a part in an assembly',
  inputSchema: {
    properties: {
      assembly_code: { type: 'string' },
      part_number: { type: 'string' },
      quantity: { type: 'number' },
    },
    required: ['assembly_code', 'part_number', 'quantity'],
    type: 'object',
  },
  _meta: { ui: { resourceUri: 'manage-assemblies.html', visibility: ['model', 'app'] } },
}, updateAssemblyPartQuantityHandler);

// Also register the get_part_assemblies helper tool (no UI)
server.registerTool('get_part_assemblies', {
  description: 'Find all assemblies that contain a specific part',
  inputSchema: { properties: { part_number: { type: 'string' } }, required: ['part_number'], type: 'object' },
}, getPartAssembliesHandler);

// Register resources
registerAppResource(server, 'Parts Table', 'parts-table.html', {
  description: 'Interactive parts table with search and sorting',
}, async () => ({
  contents: [{
    uri: 'parts-table.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'parts-table.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'Part Detail', 'part-detail.html', {
  description: 'Part detail view with properties and assemblies',
}, async () => ({
  contents: [{
    uri: 'part-detail.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'part-detail.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'BOM Table', 'bom-table.html', {
  description: 'Bill of Materials table with stats and export',
}, async () => ({
  contents: [{
    uri: 'bom-table.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'bom-table.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'BOM Summary', 'bom-summary.html', {
  description: 'BOM summary dashboard with category breakdown',
}, async () => ({
  contents: [{
    uri: 'bom-summary.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'bom-summary.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'Shared Styles', 'shared.css', {
  description: 'Shared CSS styles for MCP App UI',
}, async () => ({
  contents: [{
    uri: 'shared.css',
    mimeType: 'text/css',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'shared.css'), 'utf-8')),
  }],
}));

// ============ Register New View Resources ============

registerAppResource(server, 'Dashboard View', 'view-dashboard.html', {
  description: 'ESP dashboard with stats, critical parts alert, search, and series summary',
}, async () => ({
  contents: [{
    uri: 'view-dashboard.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'view-dashboard.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'ESP Catalogue View', 'view-esp-catalogue.html', {
  description: 'ESP catalogue with cards, filtering, create and delete operations',
}, async () => ({
  contents: [{
    uri: 'view-esp-catalogue.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'view-esp-catalogue.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'BOM Viewer View', 'view-esp-bom.html', {
  description: 'BOM viewer with parts table, sorting, and CSV export',
}, async () => ({
  contents: [{
    uri: 'view-esp-bom.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'view-esp-bom.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'Parts Manager View', 'manage-parts.html', {
  description: 'Parts manager with search, filters, CRUD operations',
}, async () => ({
  contents: [{
    uri: 'manage-parts.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'manage-parts.html'), 'utf-8')),
  }],
}));

registerAppResource(server, 'Assembly Manager View', 'manage-assemblies.html', {
  description: 'Assembly manager with parts management, create and delete operations',
}, async () => ({
  contents: [{
    uri: 'manage-assemblies.html',
    mimeType: 'text/html;profile=mcp-app',
    text: await import('fs/promises').then(fs => fs.readFile(path.join(resourcesPath, 'manage-assemblies.html'), 'utf-8')),
  }],
}));

// Start server - use HTTP transport if PORT env var is set, otherwise stdio
const port = process.env.PORT ? parseInt(process.env.PORT) : undefined;
if (port) {
  const { StreamableHTTPServerTransport } = await import('@modelcontextprotocol/sdk/server/streamableHttp.js');
  const { createMcpExpressApp } = await import('@modelcontextprotocol/sdk/server/express.js');
  const express = await import('express');

  const app = createMcpExpressApp({ host: '127.0.0.1' });
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

  app.post('/mcp', async (req, res) => {
    try {
      await transport.handleRequest(req, res, { sessionIdGenerator: undefined });
    } catch (error) {
      console.error('Error handling MCP request:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  app.listen(port, () => {
    console.log(`MCP App server running on http://localhost:${port}/mcp`);
  });

  server.connect(transport);
} else {
  const transport = new StdioServerTransport();
  server.connect(transport).catch(console.error);
}