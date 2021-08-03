import { mapStackFramesToSource, parseBrowserStackTrace } from "@objectiv/developer-tools";

async function detectPosition() {
    const stackTrace = new Error().stack;
    const rawStackFrames = parseBrowserStackTrace(stackTrace);
    const mappedStackFrames = await mapStackFramesToSource(rawStackFrames);

    return {
        stackTrace,
        rawStackFrames,
        mappedStackFrames
    }
}

export default detectPosition;
