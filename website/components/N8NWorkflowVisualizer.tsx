import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Database, Zap, Cpu, Mail, Bell, Globe, Layout, Share2, MessageSquare, Play, ArrowRight, Users, Calculator, Trophy } from 'lucide-react';
import { RevealOnScroll } from './RevealOnScroll';

interface Step {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

interface Workflow {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  steps: Step[];
}

interface MagicParticle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  size: number;
  color: string;
}

const WORKFLOWS: Workflow[] = [
  {
    id: 'content-multiplier',
    title: 'The Content Multiplier',
    subtitle: 'N8N + Gemini + Airtable',
    description: 'Turn one piece of long-form content into a month of social media assets automatically.',
    steps: [
      { id: '1', label: 'Upload Content', icon: <Database size={20} />, description: 'New YouTube URL or PDF is detected in your Google Drive.' },
      { id: '2', label: 'AI Transcription', icon: <Cpu size={20} />, description: 'VerseBot extracts high-fidelity text and identifies key semantic clusters.' },
      { id: '3', label: 'Asset Generation', icon: <Zap size={20} />, description: 'AI generates blog posts, 10 tweets, and scripts for 3 viral reels.' },
      { id: '4', label: 'Human Approval', icon: <Bell size={20} />, description: 'A notification is sent to your Slack for a quick final review.' },
      { id: '5', label: 'Distribution', icon: <Share2 size={20} />, description: 'Content is auto-scheduled across Instagram, LinkedIn, and X.' },
    ]
  },
  {
    id: 'gamified-fulfillment',
    title: 'The Gamified Fulfillment Engine',
    subtitle: 'N8N + Rewards + Shopify',
    description: 'Boost team morale and speed by gamifying order fulfillment with real-time performance bonuses.',
    steps: [
      { id: '1', label: 'Order Intake', icon: <Layout size={20} />, description: 'A new order is placed on Shopify and synced to the fulfillment board.' },
      { id: '2', label: 'Smart Dispatch', icon: <Users size={20} />, description: 'N8N assigns the task to the best-performing employee currently available.' },
      { id: '3', label: 'Speed & Quality', icon: <Zap size={20} />, description: 'System tracks time-to-ship and verifies packing accuracy via photo AI.' },
      { id: '4', label: 'Customer Pulse', icon: <MessageSquare size={20} />, description: 'Post-delivery satisfaction survey feeds directly into the employee score.' },
      { id: '5', label: 'Bonus Trigger', icon: <Trophy size={20} />, description: 'AI calculates and triggers an instant cash bonus via payroll API.' },
    ]
  },
  {
    id: 'lead-machine',
    title: 'The Hyper-Lead Screener',
    subtitle: 'N8N + Apollo + CRM',
    description: 'Stop wasting time on low-fit leads. Automate the research and booking process.',
    steps: [
      { id: '1', label: 'New Inquiry', icon: <Mail size={20} />, description: 'A potential client submits your website form.' },
      { id: '2', label: 'Data Enrichment', icon: <Globe size={20} />, description: 'N8N scrapes their LinkedIn and company website for context.' },
      { id: '3', label: 'AI Evaluation', icon: <Cpu size={20} />, description: 'Gemini scores the lead (1-100) based on your Ideal Customer Profile.' },
      { id: '4', label: 'Auto-Booking', icon: <Layout size={20} />, description: 'High-fit leads get a personalized invite link sent instantly.' },
      { id: '5', label: 'CRM Sync', icon: <Database size={20} />, description: 'The lead is logged with full context in your HubSpot/Salesforce.' },
    ]
  }
];

const MAGIC_COLORS = ['#000000', '#3b82f6', '#60a5fa', '#93c5fd'];

export const N8NWorkflowVisualizer: React.FC = () => {
  const [activeWorkflow, setActiveWorkflow] = useState(WORKFLOWS[0]);
  const [activeStep, setActiveStep] = useState(0);
  const [particles, setParticles] = useState<MagicParticle[]>([]);
  const [isJumping, setIsJumping] = useState(false);
  const dotRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const requestRef = useRef<number | null>(null);

  // Step rotation
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % activeWorkflow.steps.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [activeWorkflow]);

  // Handle workflow switch with instant reset
  const handleWorkflowSwitch = (wf: Workflow) => {
    if (wf.id === activeWorkflow.id) return;
    
    setIsJumping(true);
    setActiveWorkflow(wf);
    setActiveStep(0);
    
    // Briefly disable transition to allow instant snap-to-start
    setTimeout(() => {
      setIsJumping(false);
    }, 50);
  };

  // Magic Particle System
  const spawnParticle = useCallback((x: number, y: number) => {
    const newParticle: MagicParticle = {
      id: Math.random(),
      x,
      y,
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      life: 1,
      size: Math.random() * 3 + 2,
      color: MAGIC_COLORS[Math.floor(Math.random() * MAGIC_COLORS.length)],
    };
    setParticles((prev) => [...prev.slice(-15), newParticle]);
  }, []);

  const animate = useCallback(() => {
    // Update particle states
    setParticles((prev) =>
      prev
        .map((p) => ({
          ...p,
          x: p.x + p.vx,
          y: p.y + p.vy,
          life: p.life - 0.02,
        }))
        .filter((p) => p.life > 0)
    );

    // Spawn new particles at the dot's current position
    if (dotRef.current && containerRef.current) {
      const dotRect = dotRef.current.getBoundingClientRect();
      const containerRect = containerRef.current.getBoundingClientRect();
      
      const x = dotRect.left - containerRect.left + (dotRect.width / 2);
      const y = dotRect.top - containerRect.top + (dotRect.height / 2);
      
      spawnParticle(x, y);
    }

    requestRef.current = requestAnimationFrame(animate);
  }, [spawnParticle]);

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [animate]);

  return (
    <section className="py-24 bg-neutral-50 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <RevealOnScroll>
          <div className="text-center mb-16">
            <span className="px-4 py-1.5 bg-black text-white text-[10px] font-bold uppercase tracking-widest rounded-full mb-4 inline-block">Complex Automations</span>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Built with N8N Efficiency</h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
              We design intricate "Lego-like" workflows that bridge your favorite apps with custom AI logic.
            </p>
          </div>
        </RevealOnScroll>

        <div className="grid lg:grid-cols-12 gap-12 items-center">
          {/* Controls */}
          <div className="lg:col-span-4 space-y-4">
            {WORKFLOWS.map((wf) => (
              <button
                key={wf.id}
                onClick={() => handleWorkflowSwitch(wf)}
                className={`w-full p-6 text-left rounded-3xl border transition-all duration-300 ${
                  activeWorkflow.id === wf.id 
                    ? 'bg-white border-black shadow-xl ring-1 ring-black/5' 
                    : 'bg-transparent border-neutral-200 opacity-60 hover:opacity-100'
                }`}
              >
                <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 mb-1">{wf.subtitle}</div>
                <h3 className="text-xl font-bold mb-2">{wf.title}</h3>
                <p className="text-sm text-neutral-500 leading-relaxed">{wf.description}</p>
              </button>
            ))}
          </div>

          {/* Visualization Area */}
          <div ref={containerRef} className="lg:col-span-8 relative min-h-[500px] flex items-center justify-center">
            {/* Background Path (SVG) */}
            <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
               <svg width="100%" height="200" viewBox="0 0 800 200" className="w-full">
                  <path d="M 50,100 C 150,100 250,100 350,100 C 450,100 550,100 650,100 L 750,100" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="8 8" />
               </svg>
            </div>

            {/* Magic Particles for the trail */}
            {particles.map((p) => (
              <div
                key={p.id}
                className="absolute pointer-events-none z-20 rounded-full"
                style={{
                  left: `${p.x}px`,
                  top: `${p.y}px`,
                  width: p.size,
                  height: p.size,
                  backgroundColor: p.color,
                  opacity: p.life,
                  boxShadow: `0 0 ${p.size * 2}px ${p.color}`,
                  transform: 'translate(-50%, -50%)'
                }}
              />
            ))}

            {/* Steps Nodes Container */}
            <div className="relative w-full flex justify-between px-8 z-10 items-center">
              {activeWorkflow.steps.map((step, idx) => {
                const isActive = idx === activeStep;
                const isCompleted = idx < activeStep;
                
                return (
                  <div key={step.id} className="relative group flex flex-col items-center">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-700 border-2 ${
                      isActive 
                        ? 'bg-black text-white border-black scale-125 shadow-2xl' 
                        : isCompleted
                        ? 'bg-white text-black border-neutral-900 shadow-lg'
                        : 'bg-white text-neutral-300 border-neutral-100'
                    }`}>
                      {step.icon}
                      
                      {/* Active Indicator Pulse */}
                      {isActive && (
                        <div className="absolute inset-0 rounded-2xl animate-ping border border-black" />
                      )}
                    </div>
                    
                    {/* Tooltip Description */}
                    <div className={`absolute top-24 w-40 text-center transition-all duration-500 transform ${
                      isActive ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
                    }`}>
                      <h4 className="font-bold text-sm mb-1">{step.label}</h4>
                      <p className="text-[10px] text-neutral-500 leading-tight">{step.description}</p>
                    </div>

                    {!isActive && (
                       <div className="absolute top-20 text-center w-32">
                          <span className="text-[10px] font-bold text-neutral-300 uppercase tracking-tighter">{step.label}</span>
                       </div>
                    )}
                  </div>
                );
              })}

              {/* Moving Particle Dot - Conditional transition duration */}
              <div 
                ref={dotRef}
                className={`absolute h-4 w-4 bg-black rounded-full shadow-[0_0_20px_rgba(0,0,0,0.5)] z-30 ${isJumping ? '' : 'transition-all duration-[4000ms] ease-linear'}`}
                style={{ 
                  left: `${8 + (activeStep * (84 / (activeWorkflow.steps.length - 1)))}%`,
                  top: '50%',
                  transform: 'translate(-50%, -50%)',
                  opacity: 1
                }}
              >
                <div className="absolute inset-0 bg-black rounded-full animate-ping opacity-20" />
                <div className="absolute inset-[-4px] bg-black/10 rounded-full blur-md" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};