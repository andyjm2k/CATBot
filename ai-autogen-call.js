window.runWorkflow = async function(contentPrompt) {
    console.log('ai-autogen-call.js - runWorkflow called with:', contentPrompt);
    
    try {
        // Call the autogen API through the proxy server to avoid CORS issues
        const response = await fetch('http://localhost:8002/v1/proxy/autogen', {
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
        
        // Extract the actual content from the response
        // Adjust this based on the actual response structure from the new API
        if (data.response) {
            return data.response;
        } else if (data.output) {
            return data.output;
        } else if (data.result) {
            return data.result;
        } else if (data.message) {
            return data.message;
        } else {
            return JSON.stringify(data, null, 2);
        }

    } catch (error) {
        console.error('ai-autogen-call.js - Error:', error);
        throw error; // Let the caller handle the error
    }
};

// Optional: Add a check when the script loads
console.log('ai-autogen-call.js loaded, runWorkflow function available:', !!window.runWorkflow);