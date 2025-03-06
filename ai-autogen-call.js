window.runWorkflow = async function(contentPrompt) {
    console.log('ai-autogen-call.js - runWorkflow called with:', contentPrompt);
    
    const userId = 'guestuser@gmail.com'; // Replace with actual user ID
    
    try {
        // First create a session
        const sessionResponse = await fetch('http://127.0.0.1:8081/api/sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                name: 'New Session',
                status: 'active'
            })
        });

        if (!sessionResponse.ok) {
            throw new Error(`HTTP error! status: ${sessionResponse.status} - ${sessionResponse.statusText}`);
        }

        const sessionData = await sessionResponse.json();
        const sessionId = sessionData.data.id;
        const workflowId = '2'; // Replace with actual workflow ID

        // Now run the workflow with the session ID
        const workflowResponse = await fetch(`http://127.0.0.1:8081/api/sessions/${sessionId}/workflow/${workflowId}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                content: contentPrompt,
                type: 'user',
                status: 'active',
                connection_id: 'connection_1'
            })
        });

        if (!workflowResponse.ok) {
            throw new Error(`HTTP error! status: ${workflowResponse.status} - ${workflowResponse.statusText}`);
        }

        const data = await workflowResponse.json();
        console.log('Workflow response:', data);
        
        // Extract the actual content from the response
        if (data.data && data.data.response) {
            return data.data.response;
        } else if (data.data && data.data.content) {
            return data.data.content;
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