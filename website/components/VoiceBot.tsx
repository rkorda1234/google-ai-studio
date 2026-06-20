import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2, Phone, PhoneOff } from 'lucide-react';
import { GoogleGenAI, LiveServerMessage, Modality, Blob } from '@google/genai';

// --- Helper Functions ---
function decode(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

function encode(bytes: Uint8Array) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number,
  numChannels: number,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}

const SYSTEM_INSTRUCTION = `
You are "VerseBot Live", the voice-enabled agency consultant for Marketingverse.
Your voice is energetic, helpful, and high-authority.

### YOUR KNOWLEDGE BASE:
- Social Media: Presence ($85), Growth ($450 - Includes Monthly Shoot), Dominance ($850).
- AI Automations: Pilot ($1,500), Efficiency ($4,500), Enterprise (Custom).
- AI A La Carte: Content Gen, Scrape & Create, Property Launchpad, Voice Agents, Static-to-Video.

### YOUR GOAL:
1. Listen to the user's business challenges.
2. Recommend a specific plan by name and price.
3. Keep answers very short and snappy (voice conversations need fast turns).
4. If they are a Realtor, always mention the "Property Launchpad" or "Static-to-Video" features.
5. If they are a small business owner, suggest the Growth ($450) Social plan because of the content shoots.

Keep the energy high. Be the assistant that gets them excited about scaling.
`;

export const VoiceBot: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [inputTranscription, setInputTranscription] = useState('');
  const [outputTranscription, setOutputTranscription] = useState('');
  
  const sessionRef = useRef<any>(null);
  const audioContextsRef = useRef<{ input: AudioContext; output: AudioContext } | null>(null);
  const streamsRef = useRef<{ mic: MediaStream; processor: ScriptProcessorNode } | null>(null);
  const nextStartTimeRef = useRef<number>(0);
  const sourcesRef = useRef<Set<AudioBufferSourceNode>>(new Set());

  const stopSession = useCallback(() => {
    if (sessionRef.current) {
      sessionRef.current.close();
      sessionRef.current = null;
    }

    if (streamsRef.current) {
      streamsRef.current.mic.getTracks().forEach(track => track.stop());
      streamsRef.current.processor.disconnect();
      streamsRef.current = null;
    }

    if (audioContextsRef.current) {
      audioContextsRef.current.input.close();
      audioContextsRef.current.output.close();
      audioContextsRef.current = null;
    }

    sourcesRef.current.forEach(source => source.stop());
    sourcesRef.current.clear();
    nextStartTimeRef.current = 0;
    setIsActive(false);
    setIsConnecting(false);
  }, []);

  const startSession = async () => {
    setIsConnecting(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      const inputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      const outputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
      audioContextsRef.current = { input: inputCtx, output: outputCtx };

      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const sessionPromise = ai.live.connect({
        model: 'gemini-2.5-flash-native-audio-preview-12-2025',
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Zephyr' } },
          },
          systemInstruction: SYSTEM_INSTRUCTION,
          inputAudioTranscription: {},
          outputAudioTranscription: {},
        },
        callbacks: {
          onopen: () => {
            setIsConnecting(false);
            setIsActive(true);
            
            const source = inputCtx.createMediaStreamSource(micStream);
            const scriptProcessor = inputCtx.createScriptProcessor(4096, 1, 1);
            
            scriptProcessor.onaudioprocess = (e) => {
              const inputData = e.inputBuffer.getChannelData(0);
              const l = inputData.length;
              const int16 = new Int16Array(l);
              for (let i = 0; i < l; i++) {
                int16[i] = inputData[i] * 32768;
              }
              const pcmBlob: Blob = {
                data: encode(new Uint8Array(int16.buffer)),
                mimeType: 'audio/pcm;rate=16000',
              };
              
              if (sessionRef.current) {
                sessionRef.current.sendRealtimeInput({ media: pcmBlob });
              }
            };

            source.connect(scriptProcessor);
            scriptProcessor.connect(inputCtx.destination);
            streamsRef.current = { mic: micStream, processor: scriptProcessor };
          },
          onmessage: async (message: LiveServerMessage) => {
            if (message.serverContent?.inputTranscription) {
              setInputTranscription(prev => prev + message.serverContent!.inputTranscription!.text);
            }
            if (message.serverContent?.outputTranscription) {
              setOutputTranscription(prev => prev + message.serverContent!.outputTranscription!.text);
            }
            if (message.serverContent?.turnComplete) {
              setInputTranscription('');
              setOutputTranscription('');
            }

            const base64Audio = message.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
            if (base64Audio && audioContextsRef.current) {
              const outCtx = audioContextsRef.current.output;
              nextStartTimeRef.current = Math.max(nextStartTimeRef.current, outCtx.currentTime);
              
              const audioBuffer = await decodeAudioData(decode(base64Audio), outCtx, 24000, 1);
              const source = outCtx.createBufferSource();
              source.buffer = audioBuffer;
              source.connect(outCtx.destination);
              
              source.onended = () => sourcesRef.current.delete(source);
              source.start(nextStartTimeRef.current);
              nextStartTimeRef.current += audioBuffer.duration;
              sourcesRef.current.add(source);
            }

            if (message.serverContent?.interrupted) {
              sourcesRef.current.forEach(s => {
                try { s.stop(); } catch(e) {}
              });
              sourcesRef.current.clear();
              nextStartTimeRef.current = 0;
            }
          },
          onerror: (e) => {
            console.error('Live API Error:', e);
            stopSession();
          },
          onclose: () => {
            stopSession();
          },
        },
      });

      sessionRef.current = await sessionPromise;
    } catch (err) {
      console.error('Failed to start Gemini Live:', err);
      setIsConnecting(false);
      stopSession();
    }
  };

  useEffect(() => {
    return () => stopSession();
  }, [stopSession]);

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-neutral-900 text-white rounded-[2.5rem] shadow-2xl border border-neutral-800 h-[600px] relative overflow-hidden">
      {isActive && (
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500/10 via-transparent to-transparent animate-pulse" />
        </div>
      )}

      <div className="relative z-10 flex flex-col items-center text-center">
        <div className={`w-32 h-32 rounded-full flex items-center justify-center mb-8 transition-all duration-500 border-4 ${
          isActive ? 'bg-white text-black border-white scale-110 shadow-[0_0_50px_rgba(255,255,255,0.3)]' : 'bg-neutral-800 text-neutral-500 border-neutral-700'
        }`}>
          {isConnecting ? <Loader2 size={48} className="animate-spin" /> : isActive ? <Volume2 size={48} /> : <Phone size={48} />}
        </div>

        <h3 className="text-2xl font-bold mb-2">VerseBot Live</h3>
        <p className="text-neutral-400 mb-8 max-w-xs">
          {isActive ? 'Connected. Speak now to discuss your marketing strategy.' : isConnecting ? 'Establishing secure voice link...' : 'Ready for a real-time voice consultation.'}
        </p>

        {isActive && (
          <div className="flex gap-1 items-end h-8 mb-8">
            {[1, 2, 3, 4, 5, 6, 7].map(i => (
              <div key={i} className="w-1 bg-white rounded-full animate-bounce" style={{ height: `${20 + Math.random() * 80}%`, animationDelay: `${i * 0.1}s` }} />
            ))}
          </div>
        )}

        <button
          onClick={isActive ? stopSession : startSession}
          disabled={isConnecting}
          className={`px-10 py-5 rounded-2xl font-bold text-lg transition-all transform hover:scale-105 flex items-center gap-3 ${
            isActive ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20' : 'bg-white text-black hover:bg-neutral-200 shadow-lg shadow-white/10'
          }`}
        >
          {isActive ? <><PhoneOff size={24} /> End Conversation</> : <><Mic size={24} /> Start Voice Chat</>}
        </button>

        {(inputTranscription || outputTranscription) && (
          <div className="mt-8 p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 w-full max-w-md text-left animate-fade-in">
             {inputTranscription && (
               <div className="mb-4">
                 <span className="text-[10px] uppercase tracking-widest text-neutral-500 block mb-1">You</span>
                 <p className="text-sm text-neutral-200 leading-relaxed italic">"{inputTranscription}"</p>
               </div>
             )}
             {outputTranscription && (
               <div>
                 <span className="text-[10px] uppercase tracking-widest text-neutral-500 block mb-1">VerseBot</span>
                 <p className="text-sm text-white leading-relaxed">{outputTranscription}</p>
               </div>
             )}
          </div>
        )}
      </div>
    </div>
  );
};