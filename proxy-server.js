const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();

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

const PORT = 8002;
app.listen(PORT, () => {
    console.log(`Proxy server running on http://localhost:${PORT}`);
}); 