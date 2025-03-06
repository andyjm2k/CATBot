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
