import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";

export const maxDuration = 30;
const OPENAI_TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions";
const ELEVENLABS_TRANSCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text";
const ELEVENLABS_TRANSCRIBE_MODEL =
  process.env.ELEVENLABS_STT_MODEL_ID ?? "scribe_v1";
const OPENAI_FAST_MODEL = process.env.OPENAI_MODEL_FAST ?? "gpt-4o-mini";
const BACKEND_API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const SYSTEM_PROMPT = `You are go!'s onboarding assistant. The user is speaking to you. Learn about them through friendly conversation.

Extract when they share: interests, comfort going solo, walking distance, timing preferences, things they've been meaning to try.
Be warm, brief, and human. Keep responses short (1-3 sentences) since they'll be spoken aloud.
After 5-8 exchanges when you have a good picture, say something like: "Great, I've got a good picture. Ready to see what's out there?"`;

interface ProfileIngestResult {
  applied: boolean;
  inferred_preferences: string[];
  comfort_level: string | null;
  willingness_radius_km: number | null;
  detail?: string;
}

async function transcribeWithElevenLabs(
  audioFile: File,
  apiKey: string
): Promise<string | null> {
  const body = new FormData();
  body.append("file", audioFile);
  body.append("model_id", ELEVENLABS_TRANSCRIBE_MODEL);

  const res = await fetch(ELEVENLABS_TRANSCRIBE_URL, {
    method: "POST",
    headers: {
      "xi-api-key": apiKey,
    },
    body,
  });
  if (!res.ok) {
    const errorText = await res.text();
    console.warn("ElevenLabs STT error:", errorText);
    return null;
  }

  const payload = await res.json().catch(() => ({} as Record<string, unknown>));
  const text =
    typeof payload.text === "string"
      ? payload.text.trim()
      : typeof payload.transcript === "string"
        ? payload.transcript.trim()
        : "";
  return text || null;
}

async function transcribeWithOpenAI(
  audioFile: File,
  apiKey: string
): Promise<string | null> {
  const body = new FormData();
  body.append("file", audioFile);
  body.append("model", "whisper-1");

  const res = await fetch(OPENAI_TRANSCRIBE_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
    body,
  });
  if (!res.ok) {
    const errorText = await res.text();
    console.warn("OpenAI whisper error:", errorText);
    return null;
  }

  const payload = await res.json().catch(() => ({} as Record<string, unknown>));
  return typeof payload.text === "string" ? payload.text.trim() : null;
}

async function ingestTranscriptToProfile(
  transcript: string,
  authHeader: string | null
): Promise<ProfileIngestResult> {
  if (!authHeader) {
    return {
      applied: false,
      inferred_preferences: [],
      comfort_level: null,
      willingness_radius_km: null,
      detail: "missing_auth_header",
    };
  }

  try {
    const res = await fetch(`${BACKEND_API_BASE}/users/me/voice-intake`, {
      method: "POST",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ transcript }),
    });
    if (!res.ok) {
      const errorText = await res.text();
      console.warn("Voice intake sync error:", errorText);
      return {
        applied: false,
        inferred_preferences: [],
        comfort_level: null,
        willingness_radius_km: null,
        detail: `backend_sync_failed_${res.status}`,
      };
    }

    const payload = await res.json().catch(() => ({} as Record<string, unknown>));
    return {
      applied: true,
      inferred_preferences: Array.isArray(payload.inferred_preferences)
        ? payload.inferred_preferences.filter(
            (value: unknown): value is string => typeof value === "string"
          )
        : [],
      comfort_level:
        typeof payload.comfort_level === "string" ? payload.comfort_level : null,
      willingness_radius_km:
        typeof payload.willingness_radius_km === "number"
          ? payload.willingness_radius_km
          : null,
      detail: "synced",
    };
  } catch (error) {
    console.warn("Voice intake sync exception:", error);
    return {
      applied: false,
      inferred_preferences: [],
      comfort_level: null,
      willingness_radius_km: null,
      detail: "backend_sync_exception",
    };
  }
}

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
    const authHeader = req.headers.get("authorization");

    if (!apiKey) {
      return Response.json(
        { error: "OpenAI API key not configured" },
        { status: 500 }
      );
    }

    // 1. STT: prefer ElevenLabs, fallback to OpenAI Whisper.
    const transcript =
      (elevenLabsKey
        ? await transcribeWithElevenLabs(audioFile, elevenLabsKey)
        : null) ?? (await transcribeWithOpenAI(audioFile, apiKey)) ?? "";

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
      model: openai(OPENAI_FAST_MODEL),
      system: SYSTEM_PROMPT,
      messages,
    });
    const profileIngest = await ingestTranscriptToProfile(transcript, authHeader);

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
      profile_ingest: profileIngest,
    });
  } catch (err) {
    console.error("Voice API error:", err);
    return Response.json(
      { error: "Something went wrong" },
      { status: 500 }
    );
  }
}
