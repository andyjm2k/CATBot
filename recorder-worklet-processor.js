class RecorderWorkletProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        // Validate input structure before processing
        const input = inputs[0];
        // Check if input exists, has channels, and first channel has valid data
        if (input && input.length > 0 && input[0] && input[0].length > 0) {
            // Get the first channel data (assuming mono audio)
            const channelData = input[0];
            // Validate that channelData is a valid Float32Array
            if (channelData instanceof Float32Array || Array.isArray(channelData)) {
                // Send the audio data to the main thread
                // Use slice() to create a copy and avoid reference issues
                this.port.postMessage(channelData.slice());
            }
            // Note: Removed console.log to avoid performance issues in AudioWorklet thread
            // Logging in audio processing thread can cause significant performance degradation
        }
        // Keep processor alive by returning true
        return true;
    }
}

registerProcessor('recorder-worklet', RecorderWorkletProcessor);
