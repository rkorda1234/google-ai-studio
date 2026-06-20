import React, { useState } from 'react';
import { Play, Sparkles, Loader2, CheckCircle2, Terminal, RefreshCw, Zap, Image as ImageIcon } from 'lucide-react';
import { GoogleGenAI } from "@google/genai";
import { RevealOnScroll } from './RevealOnScroll';

interface DemoWorkflow {
  id: string;
  name: string;
  description: string;
  placeholder: string;
  prompt: string;
  icon: React.ReactNode;
  type: 'text' | 'image';
}

const DEMO_WORKFLOWS: DemoWorkflow[] = [
  {
    id: 'lead-triage',
    name: 'Lead Triage',
    description: 'Automatically qualify and route inbound leads based on intent.',
    placeholder: 'Hi, I’m looking for a social media manager for my luxury watch brand. Budget is around $5k/mo. Can we talk?',
    icon: <CheckCircle2 className="w-5 h-5" />,
    prompt: "You are an AI Lead Triage agent. Analyze the following lead message. Categorize 'Sentiment', 'Urgency' (1-10), 'Service Needed', and provide a 'Suggested Next Step'. Output as a clean summary.",
    type: 'text'
  },
  {
    id: 'visual-concept',
    name: 'Visual Architect',
    description: 'Generate high-fidelity brand concepts and social media mood boards instantly.',
    placeholder: 'A futuristic skincare brand aesthetic, minimalist white packaging with holographic accents, luxury spa setting, soft morning light.',
    icon: <ImageIcon className="w-5 h-5" />,
    prompt: "A high-fidelity professional brand mood board and product concept for: ",
    type: 'image'
  },
  {
    id: 'content-architect',
    name: 'Content Architect',
    description: 'Turn a single idea into a 360° content distribution plan.',
    placeholder: 'Why real estate investors should look at Miami in 2025.',
    icon: <Sparkles className="w-5 h-5" />,
    prompt: "You are a Content Strategist. Based on this topic, provide: 1. A catchy Blog Title, 2. Three Instagram Reel hooks, and 3. A Twitter/X thread outline. Keep it punchy and viral.",
    type: 'text'
  }
];

export const WorkflowSimulator: React.FC = () => {
  const [selectedId, setSelectedId] = useState(DEMO_WORKFLOWS[0].id);
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const selectedWorkflow = DEMO_WORKFLOWS.find(w => w.id === selectedId)!;

  const runSimulation = async () => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    setOutput(null);
    setImageUrl(null);
    setLogs(['Initializing AI Agent...', 'Authenticating workflow...', 'Allocating VerseGPU resources...']);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      
      if (selectedWorkflow.type === 'image') {
        setTimeout(() => setLogs(prev => [...prev, 'Synthesizing visual layers...']), 800);
        setTimeout(() => setLogs(prev => [...prev, 'Applying brand style guides...']), 1600);
        
        const response = await ai.models.generateContent({
          model: 'gemini-2.5-flash-image',
          contents: {
            parts: [{ text: `${selectedWorkflow.prompt}${input}` }]
          }
        });

        let foundImage = false;
        if (response.candidates?.[0]?.content?.parts) {
          for (const part of response.candidates[0].content.parts) {
            if (part.inlineData) {
              const base64EncodeString = part.inlineData.data;
              setImageUrl(`data:image/png;base64,${base64EncodeString}`);
              foundImage = true;
            } else if (part.text) {
              setOutput(part.text);
            }
          }
        }
        
        if (!foundImage && !output) throw new Error("No output generated");
        setLogs(prev => [...prev, 'Visual asset generated successfully.']);
      } else {
        setTimeout(() => setLogs(prev => [...prev, 'Analyzing input context...']), 800);
        setTimeout(() => setLogs(prev => [...prev, 'Running heuristic models...']), 1600);

        const response = await ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: `${selectedWorkflow.prompt}\n\nUser Input: ${input}`,
          config: {
            temperature: 0.7,
          }
        });

        setOutput(response.text || "Simulation complete with no output.");
        setLogs(prev => [...prev, 'Workflow logic completed successfully.']);
      }
    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, 'ERROR: Simulation failed. Check API configuration.']);
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setInput('');
    setOutput(null);
    setImageUrl(null);
    setLogs([]);
  };

  return (
    <section className="py-24 bg-white">
      <RevealOnScroll>
        <div className="text-center mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-neutral-400 mb-3 block">Live Testing Ground</span>
          <h2 className="text-4xl font-bold mb-4">AI Smart Lab</h2>
          <p className="text-neutral-600 max-w-2xl mx-auto">
            Test our AI and creative logic in real-time. Select a module and see how Marketingverse intelligence handles your vision.
          </p>
        </div>
      </RevealOnScroll>

      <div className="max-w-6xl mx-auto px-4 grid lg:grid-cols-2 gap-12">
        {/* Left Side: Input Controls */}
        <RevealOnScroll delay={100}>
          <div className="space-y-8">
            <div className="flex flex-wrap gap-3">
              {DEMO_WORKFLOWS.map((w) => (
                <button
                  key={w.id}
                  onClick={() => { setSelectedId(w.id); reset(); }}
                  className={`flex items-center gap-2 px-5 py-3 rounded-2xl text-sm font-bold transition-all border ${
                    selectedId === w.id 
                      ? 'bg-black text-white border-black shadow-lg scale-105' 
                      : 'bg-neutral-50 text-neutral-500 border-neutral-100 hover:border-neutral-300'
                  }`}
                >
                  {w.icon} {w.name}
                </button>
              ))}
            </div>

            <div className="bg-neutral-50 p-8 rounded-[2rem] border border-neutral-200 shadow-sm">
              <h3 className="text-lg font-bold mb-2">Step 1: Provide Context</h3>
              <p className="text-sm text-neutral-500 mb-6">{selectedWorkflow.description}</p>
              
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={selectedWorkflow.placeholder}
                className="w-full h-40 p-5 rounded-2xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent bg-white shadow-inner text-sm leading-relaxed resize-none mb-6"
              />

              <div className="flex gap-4">
                <button
                  onClick={runSimulation}
                  disabled={!input.trim() || isProcessing}
                  className="flex-1 px-8 py-4 bg-black text-white rounded-xl font-bold hover:bg-neutral-800 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  {isProcessing ? <Loader2 className="animate-spin" /> : <Play size={18} className="group-hover:translate-x-1 transition-transform" />}
                  {isProcessing ? 'Simulating...' : 'Run Simulation'}
                </button>
                <button
                  onClick={reset}
                  className="p-4 bg-white border border-neutral-200 text-neutral-500 rounded-xl hover:bg-neutral-100 transition-all"
                >
                  <RefreshCw size={18} />
                </button>
              </div>
            </div>
          </div>
        </RevealOnScroll>

        {/* Right Side: Output Terminal */}
        <RevealOnScroll delay={200}>
          <div className="bg-neutral-900 rounded-[2.5rem] p-8 h-full min-h-[500px] flex flex-col shadow-2xl relative overflow-hidden group">
            {/* Terminal Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/20 group-hover:bg-red-500 transition-colors" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/20 group-hover:bg-yellow-500 transition-colors" />
                <div className="w-3 h-3 rounded-full bg-green-500/20 group-hover:bg-green-500 transition-colors" />
              </div>
              <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-neutral-500 font-bold">
                <Zap size={10} className="text-yellow-400" /> VerseOS v2.5.0-Active
              </div>
            </div>

            {/* Terminal Content */}
            <div className="flex-1 flex flex-col gap-6 overflow-y-auto scrollbar-hide">
              {logs.length === 0 && !output && !imageUrl && (
                <div className="flex-1 flex flex-col items-center justify-center text-center opacity-30">
                  <Terminal size={48} className="text-neutral-500 mb-4" />
                  <p className="text-sm font-mono text-neutral-500">Awaiting workflow initialization...</p>
                </div>
              )}

              {logs.map((log, i) => (
                <div key={i} className="flex gap-3 text-[13px] font-mono animate-fade-in">
                  <span className="text-neutral-600">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                  <span className={log.includes('ERROR') ? 'text-red-400' : 'text-neutral-400'}>
                    {log.includes('successfully') ? '✔ ' : '> '}{log}
                  </span>
                </div>
              ))}

              {(output || imageUrl) && (
                <div className="mt-4 p-6 bg-white/5 border border-white/10 rounded-2xl animate-fade-in">
                  <div className="flex items-center gap-2 mb-4 text-xs font-bold text-white uppercase tracking-widest">
                    <Sparkles size={14} className="text-blue-400" /> Simulated Result
                  </div>
                  
                  {imageUrl && (
                    <div className="mb-4 rounded-xl overflow-hidden border border-white/10 shadow-2xl">
                      <img src={imageUrl} alt="Generated brand concept" className="w-full h-auto object-cover" />
                    </div>
                  )}
                  
                  {output && (
                    <div className="text-neutral-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
                      {output}
                    </div>
                  )}
                </div>
              )}

              {isProcessing && (
                <div className="flex items-center gap-2 text-blue-400 text-sm font-mono animate-pulse">
                  <Loader2 size={14} className="animate-spin" /> Fetching intelligent response...
                </div>
              )}
            </div>

            {/* Terminal Footer Overlay */}
            <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-neutral-900 to-transparent pointer-events-none" />
          </div>
        </RevealOnScroll>
      </div>
    </section>
  );
};