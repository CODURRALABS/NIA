import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    try {
        const { text, speaker = "meera", language_code = "hi-IN" } = await req.json();

        if (!text) {
            return NextResponse.json({ error: 'Text is required' }, { status: 400 });
        }

        // Sarvam AI Bulbul v3 Speaker Mapping
        const SPEAKER_MAP: Record<string, string> = {
            'meera': 'ritu',
            'pavithra': 'neha',
            'mahesh': 'aditya',
            'kumar': 'amit',
            'saranya': 'priya',
            'vignesh': 'rahul',
            'mishti': 'simran',
            'arvind': 'rohan'
        };
        const finalSpeaker = SPEAKER_MAP[speaker] || "ritu"; // Default for v3

        const payload = {
            inputs: [text],
            target_language_code: language_code,
            speaker: finalSpeaker,
            pace: 1.0,
            enable_preprocessing: true,
            model: "bulbul:v3"
        };

        const apiKey = process.env.SARVAM_API_KEY;
        if (!apiKey) {
            console.error("Missing SARVAM_API_KEY in environment");
            return NextResponse.json({ error: 'TTS Configuration Missing' }, { status: 500 });
        }

        const response = await fetch('https://api.sarvam.ai/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'api-subscription-key': apiKey
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log('Sarvam AI Response Status:', response.status);

        if (!response.ok) {
            console.error('Sarvam AI Error Details:', data);
            return NextResponse.json({ error: data.error?.message || 'Sarvam AI Error' }, { status: response.status });
        }

        // Bulbul v3 returns an array of base64 strings in "audios"
        const audioContent = data.audio_content || (data.audios && data.audios[0]);

        if (!audioContent) {
            console.error('No audio content in Sarvam response:', data);
            return NextResponse.json({ error: 'No audio content generated' }, { status: 500 });
        }

        return NextResponse.json({ audio: audioContent });
    } catch (error: any) {
        console.error('TTS API Route Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
