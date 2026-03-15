import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";

export const maxDuration = 30;

const SYSTEM_PROMPT = `You are go!'s onboarding assistant. The user is speaking to you. Learn about them through friendly conversation.

Extract when they share: interests, comfort going solo, walking distance, timing preferences, things they've been meaning to try.
Be warm, brief, and human. Keep responses short (1-3 sentences) since they'll be spoken aloud.
After 5-8 exchanges when you have a good picture, say something like: "Great, I've got a good picture. Ready to see what's out there?"`;

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const audioFile = formData.get("audio") as File | null;
    const historyJson = formData.get("history") as string | null;

    if (!audioFile || !audioFile.size) {
      return Response.json(
        { error: "No audio provided" },
        { status: 400 }
      );
    }

    const apiKey = process.env.OPENAI_API_KEY;
    const elevenLabsKey = process.env.ELEVENLABS_API_KEY;
    const voiceId = process.env.ELEVENLABS_VOICE_ID;

    if (!apiKey) {
      return Response.json(
        { error: "OpenAI API key not configured" },
        { status: 500 }
      );
    }

    // 1. Whisper STT
    const whisperFormData = new FormData();
    whisperFormData.append("file", audioFile);
    whisperFormData.append("model", "whisper-1");

    const whisperRes = await fetch("https://api.openai.com/v1/audio/transcriptions", {
      method: "POST",
      headers: { Authorization: `Bearer ${apiKey}` },
      body: whisperFormData,
    });

    if (!whisperRes.ok) {
      const err = await whisperRes.text();
      console.error("Whisper error:", err);
      return Response.json(
        { error: "Speech recognition failed" },
        { status: 500 }
      );
    }

    const whisperData = await whisperRes.json();
    const transcript = whisperData.text?.trim() || "";

    if (!transcript) {
      return Response.json(
        { error: "Could not understand audio" },
        { status: 400 }
      );
    }

    // 2. GPT-4o response
    const history: { role: "user" | "assistant"; content: string }[] =
      historyJson ? JSON.parse(historyJson) : [];

    const messages = [
      ...history.map((m) => ({ role: m.role, content: m.content })),
      { role: "user" as const, content: transcript },
    ];

    const { text: responseText } = await generateText({
      model: openai("gpt-4o"),
      system: SYSTEM_PROMPT,
      messages,
    });

    // 3. ElevenLabs TTS (if configured)
    let audioBase64: string | null = null;

    if (elevenLabsKey && voiceId) {
      const ttsRes = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}?output_format=mp3_44100_128`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "xi-api-key": elevenLabsKey,
          },
          body: JSON.stringify({
            text: responseText,
            model_id: "eleven_multilingual_v2",
          }),
        }
      );

      if (ttsRes.ok) {
        const audioBuffer = await ttsRes.arrayBuffer();
        audioBase64 = Buffer.from(audioBuffer).toString("base64");
      }
    }

    return Response.json({
      transcript,
      response_text: responseText,
      audio_base64: audioBase64,
    });
  } catch (err) {
    console.error("Voice API error:", err);
    return Response.json(
      { error: "Something went wrong" },
      { status: 500 }
    );
  }
}
