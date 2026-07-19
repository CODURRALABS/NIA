import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    // Utility to relay response to the Voice Engine daemon
    const _returnWithTTS = (text: string) => {
        try {
            fetch("http://127.0.0.1:8000/pulse/speak", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            }).catch(() => {});
        } catch (e) {}
        return NextResponse.json({ response: text });
    };

    try {
        const { prompt, model = "nia", mode = "execute" } = await req.json();

        if (!prompt) {
            return NextResponse.json({ error: 'Prompt logic required' }, { status: 400 });
        }

        const systemInstruction = 
            "You are NIA, an advanced 'Sovereign Operating Entity'. " +
            (mode === "planning" ? "You are in PLANNING MODE: Provide detailed, step-by-step reasoning. " : "You are in EXECUTE MODE: Provide extremely concise, high-velocity responses. ") +
            "Your identity is Sovereign. You operate local to the user's infrastructure.";

        // --- NIA DIRECT ENGINE (PURE SOVEREIGN MODE) ---
        // We are bypassing all cloud fallbacks as per mission directive.
        try {
            const res = await fetch("http://127.0.0.1:8000/pulse/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    prompt,
                    mode,
                    system_instruction: systemInstruction
                })
            });
            
            const data = await res.json();
            
            if (res.ok) {
                return _returnWithTTS(data.response);
            } else {
                // If NIA local fails, return the SPECIFIC error from the Python engine
                return NextResponse.json({ 
                    error: data.response || "NIA Engine connection refused. Check Pulse OS status." 
                }, { status: 500 });
            }
        } catch (e: any) {
            console.error("[SOVEREIGN_BRIDGE] Local Engine Unreachable:", e);
            return NextResponse.json({ 
                error: `Sovereign Bridge Failure: ${e.message}. Ensure NIA Engine is running.` 
            }, { status: 503 });
        }
    } catch (error: any) {
        console.error("Critical API Failure:", error);
        return NextResponse.json({ error: `System DNA Failure: ${error.message}` }, { status: 500 });
    }
}
