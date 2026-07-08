import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Mic, MessageSquare } from 'lucide-react';
import { sendMessageToGemini } from '../services/geminiService';
import { ChatMessage } from '../types';
import { VoiceBot } from './VoiceBot';

interface AIBotProps {
  context?: string;
  initialMessage?: string;
}

export const AIBot: React.FC<AIBotProps> = ({ context, initialMessage }) => {
  const [mode, setMode] = useState<'text' | 'voice'>('text');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'model',
      text: initialMessage || (context 
        ? "I've analyzed this article. Do you have any questions about how these strategies apply to your business?" 
        : "Hello! I'm VerseBot. Tell me about your business goals, and I'll recommend the best strategy for you."),
      timestamp: Date.now()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior
      });
    }
  };

  useEffect(() => {
    if (mode === 'text') {
      const timeoutId = setTimeout(() => scrollToBottom(), 100);
      return () => clearTimeout(timeoutId);
    }
  }, [messages, mode]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: inputValue,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const responseText = await sendMessageToGemini(userMsg.text, context);
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: responseText,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col h-[650px] transition-all duration-500">
      <div className="flex bg-neutral-100 p-1 rounded-2xl mb-4 w-fit mx-auto shadow-sm">
        <button 
          onClick={() => setMode('text')}
          className={`flex items-center gap-2 px-6 py-2 rounded-xl text-sm font-bold transition-all ${mode === 'text' ? 'bg-black text-white shadow-md' : 'text-neutral-500 hover:text-black'}`}
        >
          <MessageSquare size={16} /> {context ? 'Article Chat' : 'Text Agent'}
        </button>
        <button 
          onClick={() => setMode('voice')}
          className={`flex items-center gap-2 px-6 py-2 rounded-xl text-sm font-bold transition-all ${mode === 'voice' ? 'bg-black text-white shadow-md' : 'text-neutral-500 hover:text-black'}`}
        >
          <Mic size={16} /> Voice Live
        </button>
      </div>

      {mode === 'voice' ? (
        <VoiceBot />
      ) : (
        <div className="bg-neutral-50 border border-neutral-200 rounded-[2rem] shadow-xl overflow-hidden flex flex-col h-full animate-fade-in">
          <div className="bg-black text-white p-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/10 rounded-full">
                <Bot size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg">VerseBot Assistant</h3>
                <p className="text-xs text-neutral-400">{context ? 'Context: Reading Current Blog' : 'Powered by Gemini 3'}</p>
              </div>
            </div>
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse delay-75" />
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse delay-150" />
            </div>
          </div>

          <div 
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-6 bg-white scrollbar-hide"
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-4 ${
                  msg.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 border shadow-sm ${
                    msg.role === 'user' ? 'bg-black text-white border-black' : 'bg-neutral-100 text-neutral-700 border-neutral-200'
                  }`}
                >
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div
                  className={`max-w-[85%] p-5 rounded-2xl text-[15px] leading-relaxed shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-black text-white rounded-tr-none'
                      : 'bg-neutral-50 text-neutral-800 border border-neutral-100 rounded-tl-none'
                  }`}
                >
                  {msg.text.split('\n').map((line, i) => (
                    <p key={i} className={`${line.trim() === '' ? 'h-4' : 'mb-3'} last:mb-0`}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-neutral-100 border border-neutral-200 flex items-center justify-center">
                  <Bot size={20} className="text-neutral-500" />
                </div>
                <div className="bg-neutral-50 border border-neutral-100 p-5 rounded-2xl rounded-tl-none shadow-sm">
                  <Loader2 size={24} className="animate-spin text-neutral-400" />
                </div>
              </div>
            )}
          </div>

          <div className="p-6 bg-neutral-50 border-t border-neutral-200">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={context ? "Ask about this article..." : "What marketing goals can I help you scale today?"}
                className="flex-1 p-4 rounded-2xl border border-neutral-300 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent bg-white shadow-inner"
              />
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="p-4 bg-black text-white rounded-2xl hover:bg-neutral-800 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                <Send size={24} />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};