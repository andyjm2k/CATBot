window.runWorkflow = async function(contentPrompt, options = {}) {
    console.log('ai-autogen-call.js - runWorkflow called with:', contentPrompt);

    // Capture hostname from calling page - use provided hostname, or fallback to window.location
    // This ensures we use the actual calling page's hostname, not localhost
    const hostname = options.hostname || window.location.hostname;
    const protocol = options.protocol || window.location.protocol;

    const endpointPath = '/v1/proxy/autogen';

    // Prefer same-origin endpoint first (works behind HTTPS/reverse proxies).
    // Fallback to explicit proxy host/port for direct deployments.
    const sameOriginUrl = endpointPath;
    const configuredProxyUrl = window.PROXY_BASE_URL
        ? `${window.PROXY_BASE_URL}${endpointPath}`
        : `${protocol}//${hostname}:8002${endpointPath}`;

    const candidateUrls = Array.from(new Set([sameOriginUrl, configuredProxyUrl]));

    if (protocol === 'https:') {
        // Last-resort fallback when proxy is only exposed over HTTP.
        // This may still be blocked by mixed-content rules depending on deployment.
        const httpFallback = `http://${hostname}:8002${endpointPath}`;
        candidateUrls.push(httpFallback);
    }

    let lastError = null;

    try {
        for (const targetUrl of candidateUrls) {
            try {
                console.log('ai-autogen-call.js - Trying proxy URL:', targetUrl);

                const response = await fetch(targetUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        input: contentPrompt
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
                }

                const data = await response.json();
                console.log('Autogen API response:', data);

                if (data.response) {
                    return data.response;
                } else if (data.output) {
                    return data.output;
                } else if (data.result) {
                    return data.result;
                } else if (data.message) {
                    return data.message;
                }

                return JSON.stringify(data, null, 2);
            } catch (error) {
                lastError = error;
                console.warn('ai-autogen-call.js - Request failed for URL:', targetUrl, error);
            }
        }

        throw lastError || new Error('Failed to reach AutoGen proxy endpoint.');
    } catch (error) {
        console.error('ai-autogen-call.js - Error:', error);
        throw error;
    }
};

// Optional: Add a check when the script loads
console.log('ai-autogen-call.js loaded, runWorkflow function available:', !!window.runWorkflow);
