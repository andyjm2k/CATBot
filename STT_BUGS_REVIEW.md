# STT (Speech-to-Text) Bugs Review

## File: `index-dev.html`

### Bug 1: Missing Response Status Check in `sendAudioToWhisper`
**Location:** Lines 3567-3604
**Severity:** High
**Issue:** The function doesn't check if the HTTP response is successful (`response.ok`) before attempting to parse JSON. If the API returns an error status (401, 404, 500, etc.), it will try to parse the error response as JSON, which may fail or provide misleading error messages.

**Current Code:**
```3567:3604:index-dev.html
        async function sendAudioToWhisper(audioBlob) {
            const apiKey = apiKeyInput.value.trim();
            // Use the proxy server endpoint which has CORS configured
            const whisperEndpoint = 'http://localhost:8002/v1/audio/transcriptions';

            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');
            formData.append('model', 'whisper-1');

            try {
                console.log('Sending audio to Whisper...');
                const response = await fetch(whisperEndpoint, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: formData
                });
                const data = await response.json();
                console.log('Whisper response:', data);
                if (data.text) {
                    // Set the input with the transcribed text
                    const transcribedText = data.text.trim();
                    userInput.value = transcribedText + ' ';
                    status.textContent = "Transcription successful.";
                    
                    // Send the transcribed text to OpenAI
                    // Note: fetchOpenAIResponse will add the message to chat history
                    fetchOpenAIResponse(transcribedText);
                } else {
                    console.error('Unexpected response format:', data);
                    status.textContent = "Transcription failed. Please try again.";
                }
            } catch (error) {
                console.error('Error with OpenAI Whisper request:', error);
                status.textContent = "Transcription failed. Please try again.";
            }
        }
```

**Problem:** Line 3585 calls `response.json()` without checking `response.ok` first. If the server returns an error (e.g., 401 Unauthorized, 404 Not Found, 500 Internal Server Error), the code will still try to parse the error response as JSON, which may not have a `text` property, leading to a generic error message.

---

### Bug 2: Missing API Key Validation
**Location:** Line 3568
**Severity:** Medium
**Issue:** The function doesn't validate if the API key is empty before making the request. If the API key is missing, it will send a request with an empty Bearer token, which will always fail but with a less clear error message.

**Current Code:**
```3568:3568:index-dev.html
            const apiKey = apiKeyInput.value.trim();
```

**Problem:** No check is performed to ensure `apiKey` is not empty before using it in the Authorization header.

---

### Bug 3: Unsafe Disconnection in `stopRecording`
**Location:** Lines 3457-3458
**Severity:** Medium
**Issue:** The function disconnects `mediaStreamSource` and `recorderNode` without checking if they are actually connected. If they're already disconnected or were never connected, calling `disconnect()` can throw an error.

**Current Code:**
```3454:3475:index-dev.html
        // Update the stopRecording function
        function stopRecording() {
            if (isRecording && recorderNode && audioContext) {
                // Properly disconnect both ends of the audio nodes
                mediaStreamSource.disconnect();
                recorderNode.disconnect();
                
                // Update UI
                startRecordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                startRecordBtn.title = "Start Recording";
                status.textContent = "Processing recording...";
                
                // Set recording state to false BEFORE processing the audio
                isRecording = false;
                
                // Process the recorded audio if we have data
                if (audioData.length > 0) {
                    processAudioData();
                } else {
                    status.textContent = "No audio recorded";
                }
            }
        }
```

**Problem:** Lines 3457-3458 call `disconnect()` without checking if the nodes are actually connected. If `startRecording()` was never called or if there was an error during connection, this will throw an error.

---

### Bug 4: Audio Feedback Loop in `startRecording`
**Location:** Line 3442
**Severity:** Low (May be intentional)
**Issue:** The function connects `recorderNode` to `audioContext.destination`, which causes the recorded audio to play back through the speakers. This creates an audio feedback loop and may not be desired behavior.

**Current Code:**
```3440:3442:index-dev.html
                // Connect the nodes and start recording
                mediaStreamSource.connect(recorderNode);
                recorderNode.connect(audioContext.destination); // Add this line
```

**Problem:** Connecting the recorder node to the destination causes audio monitoring/feedback. This may be intentional for monitoring, but it's not clear and could cause issues if the user doesn't want to hear their own voice.

---

### Bug 5: Missing Null Check in `processAudioData`
**Location:** Line 3482
**Severity:** High
**Issue:** The function doesn't check if `audioContext` exists or if `audioContext.sampleRate` is valid before using it. If `audioContext` is null or undefined, this will throw a runtime error.

**Current Code:**
```3477:3492:index-dev.html
        function processAudioData() {
    // Flatten the audio data
    let flatData = flattenArray(audioData);

    // Encode the data into WAV format
    let wavBlob = encodeWAV(flatData, audioContext.sampleRate);

    // Save the WAV file for testing
    // saveWAVFile(wavBlob);

    // Clear audioData for next recording
    audioData = [];

    // Send to Whisper
    sendAudioToWhisper(wavBlob);
}
```

**Problem:** Line 3482 uses `audioContext.sampleRate` without checking if `audioContext` is defined. If `audioContext` was never initialized or was destroyed, this will throw a `TypeError`.

---

### Bug 6: Missing Error Details in `sendAudioToWhisper`
**Location:** Lines 3596-3602
**Severity:** Medium
**Issue:** When the API request fails, the error handling doesn't provide detailed information about what went wrong. The user only sees a generic "Transcription failed" message without knowing if it was a network error, authentication error, or server error.

**Current Code:**
```3596:3602:index-dev.html
                } else {
                    console.error('Unexpected response format:', data);
                    status.textContent = "Transcription failed. Please try again.";
                }
            } catch (error) {
                console.error('Error with OpenAI Whisper request:', error);
                status.textContent = "Transcription failed. Please try again.";
            }
```

**Problem:** The error messages are too generic and don't help users understand what went wrong (e.g., "API key missing", "Server unavailable", "Network error").

---

### Bug 7: Potential Race Condition in Recording State
**Location:** Lines 3448, 3466
**Severity:** Low
**Issue:** The `isRecording` flag is set to `true` in `startRecording()` and `false` in `stopRecording()`, but if `stopRecording()` is called multiple times quickly or if there's an error, the state might become inconsistent.

**Current Code:**
```3448:3448:index-dev.html
                isRecording = true;
```

```3466:3466:index-dev.html
                isRecording = false;
```

**Problem:** No additional guards prevent multiple calls to `stopRecording()` or ensure the state is properly reset on errors.

---

## File: `recorder-worklet-processor.js`

### Bug 8: Console.log in AudioWorklet Thread
**Location:** Line 14
**Severity:** Low
**Issue:** The `console.log` statement in the AudioWorklet processor runs in a separate thread and may not work in all browsers. Additionally, logging in the audio processing thread can cause performance issues.

**Current Code:**
```1:22:recorder-worklet-processor.js
class RecorderWorkletProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0]; // Assuming mono audio
            // Send the audio data to the main thread
            this.port.postMessage(channelData.slice());

            // Add this line to log the audio data length
            console.log('Audio data chunk length:', channelData.length);
        }
        // Keep processor alive
        return true;
    }
}

registerProcessor('recorder-worklet', RecorderWorkletProcessor);
```

**Problem:** Line 14 uses `console.log` in the AudioWorklet thread, which:
1. May not work in all browsers (AudioWorklets run in a separate thread)
2. Can cause significant performance degradation due to frequent logging (called ~128 times per second at 44.1kHz)
3. Should be removed or conditionally enabled only for debugging

---

### Bug 9: Missing Input Validation in Worklet
**Location:** Lines 8-9
**Severity:** Low
**Issue:** The code assumes `input[0]` exists and has data, but doesn't validate the input structure thoroughly. If the input format is unexpected, it could cause errors.

**Current Code:**
```8:9:recorder-worklet-processor.js
        if (input && input.length > 0) {
            const channelData = input[0]; // Assuming mono audio
```

**Problem:** The code checks if `input` exists and has length, but doesn't verify that `input[0]` is a valid Float32Array or that it has the expected structure.

---

## Summary

**Total Bugs Found:** 9
- **High Severity:** 2 (Bugs 1, 5)
- **Medium Severity:** 3 (Bugs 2, 3, 6)
- **Low Severity:** 4 (Bugs 4, 7, 8, 9)

**Recommendations:**
1. Add proper HTTP response status checking before parsing JSON
2. Validate API key before making requests
3. Add null/undefined checks for audio context and nodes
4. Wrap disconnection calls in try-catch or check connection state
5. Remove or conditionally enable console.log in AudioWorklet
6. Provide more detailed error messages to users
7. Consider removing audio feedback loop or making it optional

