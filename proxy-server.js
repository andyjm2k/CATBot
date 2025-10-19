const express = require('express');
const cors = require('cors');
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const app = express();

// Parse JSON and URL-encoded request bodies
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Enable CORS for your local development server
app.use(cors({
    origin: 'http://localhost:8000'
}));

// Proxy endpoint for fetching web content
app.get('/v1/proxy/fetch', async (req, res) => {
    try {
        const { url } = req.query;
        
        if (!url) {
            return res.status(400).json({ error: 'URL parameter is required' });
        }

        // Add common browser headers to avoid being blocked
        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout: 10000 // 10 second timeout
        });

        res.json({ content: response.data });
    } catch (error) {
        console.error('Proxy error:', error.message);
        res.status(500).json({ 
            error: 'Failed to fetch content',
            details: error.message 
        });
    }
});

// Add helper functions for text cleaning
function cleanText(text) {
    return text
        // Remove HTML tags
        .replace(/<\/?[^>]+(>|$)/g, '')
        // Decode HTML entities
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'")
        .replace(/&rsquo;/g, "'")
        .replace(/&lsquo;/g, "'")
        .replace(/&rdquo;/g, '"')
        .replace(/&ldquo;/g, '"')
        .replace(/&ndash;/g, '–')
        .replace(/&mdash;/g, '—')
        // Remove extra whitespace
        .replace(/\s+/g, ' ')
        .trim();
}

// Add these helper functions at the top of the file
function parseDate(dateStr) {
    if (!dateStr) return null;
    try {
        return new Date(dateStr).getTime();
    } catch (e) {
        return null;
    }
}

// New endpoint for web search
app.get('/v1/proxy/search', async (req, res) => {
    try {
        const { query } = req.query;
        
        if (!query) {
            return res.status(400).json({ error: 'Search query is required' });
        }

        try {
            // Try Brave Search with date sorting
            const braveResponse = await axios.get('https://api.search.brave.com/res/v1/web/search', {
                headers: {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip',
                    'X-Subscription-Token': process.env.BRAVE_API_KEY || 'BSAu30gzJMxRgMIyw8HEO5CYU5bP_0R'
                },
                params: {
                    q: query,
                    count: 10, // Increased count to get more results for better date filtering
                    search_lang: 'en',
                    safesearch: 'moderate',
                    freshness: 'past_month' // Add freshness parameter to prioritize recent results
                }
            });

            if (braveResponse.data && braveResponse.data.web && braveResponse.data.web.results) {
                // Process and sort results by date
                const results = braveResponse.data.web.results
                    .map(result => ({
                        url: result.url,
                        title: cleanText(result.title),
                        snippet: cleanText(result.description),
                        date: result.age || result.published || null
                    }))
                    .filter(result => result.title && result.snippet) // Filter out invalid results
                    .sort((a, b) => {
                        // Sort by date if available, newest first
                        const dateA = parseDate(a.date);
                        const dateB = parseDate(b.date);
                        if (dateA && dateB) return dateB - dateA;
                        if (dateA) return -1;
                        if (dateB) return 1;
                        return 0;
                    })
                    .slice(0, 5); // Take top 5 results

                return res.json({ results });
            }
        } catch (braveError) {
            console.log('Brave Search failed, falling back to DuckDuckGo:', braveError.message);
        }

        // Fallback to DuckDuckGo if Brave Search fails
        const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
        
        const response = await axios.get(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            },
            timeout: 10000
        });

        const results = [];
        const html = response.data;
        
        // Try multiple regex patterns to match different HTML structures
        const patterns = [
            /<div class="links_main links_deep result__body">.*?<a class="result__a" href="([^"]+)".*?>(.*?)<\/a>.*?<a class="result__snippet".*?>(.*?)<\/a>/gs,
            /<div class="result__body">.*?<a class="result__url" href="([^"]+)".*?>(.*?)<\/a>.*?<div class="result__snippet">(.*?)<\/div>/gs,
            /<div class="result__body">.*?<a class="result__a" href="([^"]+)".*?>(.*?)<\/a>.*?<div class="result__snippet">(.*?)<\/div>/gs
        ];

        for (const pattern of patterns) {
            let match;
            while ((match = pattern.exec(html)) !== null && results.length < 5) {
                const [_, url, title, snippet] = match;
                const decodedUrl = decodeURIComponent(url.replace(/&amp;/g, '&'));
                
                if (!decodedUrl.includes('duckduckgo.com')) {
                    results.push({
                        url: decodedUrl,
                        title: cleanText(title),
                        snippet: cleanText(snippet)
                    });
                }
            }
            
            if (results.length > 0) break;
        }

        res.json({ results });
    } catch (error) {
        console.error('Search error:', error.message);
        res.status(500).json({ 
            error: 'Failed to perform search',
            details: error.message 
        });
    }
});

// MCP server management
const mcpClients = new Map();
const mcpServers = new Map();
const SERVERS_FILE = path.join(__dirname, 'mcp_servers.json');

// Load servers from disk
async function loadServers() {
    try {
        const data = await fs.readFile(SERVERS_FILE, 'utf8');
        const servers = JSON.parse(data);
        servers.forEach(server => {
            mcpServers.set(server.id, server);
        });
        console.log(`Loaded ${servers.length} MCP servers from disk`);
    } catch (error) {
        console.log('No existing servers file found, starting with empty state');
    }
}

// Save servers to disk
async function saveServers() {
    try {
        const servers = Array.from(mcpServers.values());
        await fs.writeFile(SERVERS_FILE, JSON.stringify(servers, null, 2));
        console.log(`Saved ${servers.length} MCP servers to disk`);
    } catch (error) {
        console.error('Error saving servers to disk:', error);
    }
}

// Load servers on startup
loadServers();

// Helper function to create MCP client
async function createMcpClient(serverConfig) {
    try {
        const commandParts = serverConfig.command.trim().split(' ');
        if (commandParts.length === 0) {
            throw new Error('Invalid command format');
        }

        console.log(`🔧 Creating MCP client with command: ${commandParts[0]} and args:`, commandParts.slice(1));

        // Prepare environment variables
        const env = {};

        // Add API keys from server config if available
        if (serverConfig.apiKey) {
            // Determine which API key to use based on the model or default to Gemini
            if (serverConfig.model && serverConfig.model.includes('gemini')) {
                env.GEMINI_API_KEY = serverConfig.apiKey;
            } else if (serverConfig.model && serverConfig.model.includes('claude')) {
                env.ANTHROPIC_API_KEY = serverConfig.apiKey;
            } else {
                env.OPENAI_API_KEY = serverConfig.apiKey;
            }
        }

        // Add model configuration
        if (serverConfig.model) {
            env.BROWSER_USE_MODEL = serverConfig.model;
        }

        console.log('🔐 Environment variables for MCP server:', Object.keys(env));

        const transport = new StdioClientTransport({
            command: commandParts[0],
            args: commandParts.slice(1),
            env: env
        });

        const client = new Client(
            { name: 'ai-assistant-proxy', version: '1.0.0' },
            { capabilities: { tools: {} } }
        );

        // 🎯 ADD DETAILED DEBUGGING LOGGING
        console.log('🔍 Setting up MCP transport debugging...');

        // Note: StdioClientTransport doesn't expose onmessage/send methods for event listeners
        // The MCP SDK handles the underlying communication internally

        // Note: MCP SDK Client doesn't have event listeners like client.on()
        // Event handling is done through the transport layer

        console.log('✅ MCP client debugging setup complete');

        await client.connect(transport);
        console.log('🔗 MCP client connected successfully');
        return client;
    } catch (error) {
        console.error('Error creating MCP client:', error);
        throw new Error(`Failed to connect to MCP server: ${error.message}`);
    }
}

// MCP server management endpoints
app.post('/v1/mcp/servers', async (req, res) => {
    try {
        const serverConfig = req.body;

        console.log('Received server config:', JSON.stringify(serverConfig, null, 2));

        if (!serverConfig) {
            return res.status(400).json({ error: 'Request body is required' });
        }

        // Handle clear action
        if (serverConfig.action === 'clear') {
            // Disconnect all connected servers
            for (const [serverId, client] of mcpClients.entries()) {
                try {
                    await client.close();
                } catch (error) {
                    console.error(`Error closing client ${serverId}:`, error);
                }
            }

            // Clear all servers and clients
            mcpServers.clear();
            mcpClients.clear();

            console.log('Cleared all MCP servers and clients');

            // Save to disk
            await saveServers();

            return res.json({ message: 'All MCP servers cleared successfully' });
        }

        if (!serverConfig.id || !serverConfig.name) {
            return res.status(400).json({ error: 'Missing required fields: id, name' });
        }

        // Update existing server or add new one
        const existingServer = mcpServers.get(serverConfig.id);
        if (existingServer) {
            // Update existing server
            mcpServers.set(serverConfig.id, {
                ...serverConfig,
                status: existingServer.status // Preserve connection status
            });
            console.log(`Updated MCP server: ${serverConfig.name} (${serverConfig.id})`);
        } else {
            // Add new server
            mcpServers.set(serverConfig.id, {
                ...serverConfig,
                status: 'disconnected'
            });
            console.log(`Added MCP server: ${serverConfig.name} (${serverConfig.id})`);
        }

        res.json({ message: 'Server saved successfully' });

        // Save to disk
        await saveServers();
    } catch (error) {
        console.error('Error saving MCP server:', error);
        res.status(500).json({ error: 'Failed to save MCP server', details: error.message });
    }
});

app.get('/v1/mcp/servers', async (req, res) => {
    try {
        const servers = Array.from(mcpServers.values());
        res.json({ servers });
    } catch (error) {
        console.error('Error getting MCP servers:', error);
        res.status(500).json({ error: 'Failed to get MCP servers' });
    }
});

app.post('/v1/mcp/servers/:serverId/connect', async (req, res) => {
    try {
        const serverId = req.params.serverId;
        console.log(`Attempting to connect to server: ${serverId}`);

        const server = mcpServers.get(serverId);

        if (!server) {
            console.log(`Server not found: ${serverId}`);
            return res.status(404).json({ error: 'Server not found' });
        }

        console.log(`Found server: ${server.name} (${serverId})`);

        if (mcpClients.has(serverId)) {
            console.log(`Server already connected: ${serverId}`);
            return res.status(409).json({ error: 'Server is already connected' });
        }

        console.log(`Creating MCP client for server: ${server.name}`);
        const client = await createMcpClient(server);
        mcpClients.set(serverId, client);

        server.status = 'connected';
        mcpServers.set(serverId, server);

        console.log(`Successfully connected to MCP server: ${server.name}`);
        res.json({ message: 'Server connected successfully' });
    } catch (error) {
        console.error('Error connecting to MCP server:', error);
        res.status(500).json({ error: `Failed to connect to MCP server: ${error.message}`, details: error.stack });
    }
});

app.post('/v1/mcp/servers/:serverId/disconnect', async (req, res) => {
    try {
        const serverId = req.params.serverId;
        const client = mcpClients.get(serverId);

        if (!client) {
            return res.status(404).json({ error: 'Server is not connected' });
        }

        await client.close();
        mcpClients.delete(serverId);

        const server = mcpServers.get(serverId);
        if (server) {
            server.status = 'disconnected';
            mcpServers.set(serverId, server);
        }

        res.json({ message: 'Server disconnected successfully' });
    } catch (error) {
        console.error('Error disconnecting MCP server:', error);
        res.status(500).json({ error: 'Failed to disconnect MCP server' });
    }
});

// Tools discovery endpoint
app.post('/v1/mcp/servers/:serverId/tools/list', async (req, res) => {
    try {
        const serverId = req.params.serverId;
        console.log(`🔍 [TOOLS/LIST] Server: ${serverId}`);
        const client = mcpClients.get(serverId);

        if (!client) {
            console.log(`❌ [TOOLS/LIST] Server ${serverId} not found or not connected`);
            return res.status(404).json({ error: 'Server is not connected' });
        }

        const requestPayload = {
            method: 'tools/list',
            params: {}
        };

        console.log('📡 [TOOLS/LIST] Making request to MCP server...');
        console.log('📝 [TOOLS/LIST] Request payload:', JSON.stringify(requestPayload, null, 2));

        const result = await client.request(requestPayload);

        console.log('📨 [TOOLS/LIST] Raw response from MCP server:');
        console.log(JSON.stringify(result, null, 2));

        // Validate response structure
        if (!result) {
            console.error('❌ [TOOLS/LIST] No result returned from MCP server');
        } else if (!result.tools) {
            console.error('❌ [TOOLS/LIST] Missing "tools" field in response:', Object.keys(result));
        } else if (!Array.isArray(result.tools)) {
            console.error('❌ [TOOLS/LIST] "tools" field is not an array:', typeof result.tools);
        } else {
            console.log(`✅ [TOOLS/LIST] Found ${result.tools.length} tools in response`);
            result.tools.forEach((tool, index) => {
                console.log(`  Tool ${index}: ${tool.name || 'unnamed'}`);
                if (!tool.name) console.error(`    ❌ Missing name for tool ${index}`);
                if (!tool.description) console.log(`    ⚠️  Missing description for tool ${index}`);
                if (!tool.inputSchema) console.log(`    ⚠️  Missing inputSchema for tool ${index}`);
                else {
                    console.log(`    ✅ inputSchema type: ${tool.inputSchema.type}`);
                    if (tool.inputSchema.properties) {
                        console.log(`    ✅ Has ${Object.keys(tool.inputSchema.properties).length} properties`);
                    } else {
                        console.log(`    ⚠️  No properties in inputSchema`);
                    }
                }
            });
        }

        res.json({ result });
    } catch (error) {
        console.error('💥 [TOOLS/LIST] Error:', error);
        console.error('💥 [TOOLS/LIST] Error stack:', error.stack);
        console.error('💥 [TOOLS/LIST] Error details:', {
            name: error.name,
            message: error.message,
            code: error.code,
            stack: error.stack
        });
        res.status(500).json({ error: 'Failed to list tools on MCP server', details: error.message });
    }
});

app.post('/v1/mcp/servers/:serverId/tools/call', async (req, res) => {
    try {
        const serverId = req.params.serverId;
        console.log(`🔧 [TOOLS/CALL] Server: ${serverId}`);
        const client = mcpClients.get(serverId);

        if (!client) {
            console.log(`❌ [TOOLS/CALL] Server ${serverId} not found or not connected`);
            return res.status(404).json({ error: 'Server is not connected' });
        }

        const { toolName, parameters } = req.body;
        console.log('🔍 [TOOLS/CALL] Tool name:', toolName);
        console.log('🔍 [TOOLS/CALL] Parameters:', JSON.stringify(parameters, null, 2));

        if (!toolName) {
            console.log('❌ [TOOLS/CALL] toolName is required but missing');
            return res.status(400).json({ error: 'toolName is required' });
        }

        const requestPayload = {
            method: 'tools/call',
            params: {
                name: toolName,
                arguments: parameters || {}
            }
        };

        console.log('📡 [TOOLS/CALL] Making request to MCP server...');
        console.log('📝 [TOOLS/CALL] Request payload:', JSON.stringify(requestPayload, null, 2));

        const result = await client.request(requestPayload);

        console.log('📨 [TOOLS/CALL] Raw response from MCP server:');
        console.log(JSON.stringify(result, null, 2));

        // Validate response structure
        if (!result) {
            console.error('❌ [TOOLS/CALL] No result returned from MCP server');
        } else if (!result.content) {
            console.error('❌ [TOOLS/CALL] Missing "content" field in response:', Object.keys(result));
        } else if (!Array.isArray(result.content)) {
            console.error('❌ [TOOLS/CALL] "content" field is not an array:', typeof result.content);
        } else {
            console.log(`✅ [TOOLS/CALL] Found ${result.content.length} content items in response`);
            result.content.forEach((contentItem, index) => {
                console.log(`  Content ${index}: ${contentItem.type || 'unknown type'}`);
                if (contentItem.type === 'text') {
                    console.log(`    ✅ Text content: "${contentItem.text?.substring(0, 100)}${contentItem.text?.length > 100 ? '...' : ''}"`);
                } else {
                    console.log(`    ⚠️  Non-text content: ${JSON.stringify(contentItem)}`);
                }
            });
        }

        res.json({ result });
    } catch (error) {
        console.error('💥 [TOOLS/CALL] Error:', error);
        console.error('💥 [TOOLS/CALL] Error stack:', error.stack);
        console.error('💥 [TOOLS/CALL] Error details:', {
            name: error.name,
            message: error.message,
            code: error.code,
            stack: error.stack
        });
        res.status(500).json({ error: 'Failed to call tool on MCP server', details: error.message });
    }
});

const PORT = 8002;
app.listen(PORT, () => {
    console.log(`Proxy server running on http://localhost:${PORT}`);
}); 