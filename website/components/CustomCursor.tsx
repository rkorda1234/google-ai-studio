
import React, { useEffect, useRef, useState, useCallback } from 'react';

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  size: number;
  color: string;
}

export const CustomCursor: React.FC = () => {
  const cursorRef = useRef<HTMLDivElement>(null);
  const [variant, setVariant] = useState<'default' | 'hover' | 'card' | 'magic'>('default');
  const [isVisible, setIsVisible] = useState(false);
  const [particles, setParticles] = useState<Particle[]>([]);
  const mousePos = useRef({ x: 0, y: 0 });
  const requestRef = useRef<number | null>(null);

  // Magic colors for the particles
  const MAGIC_COLORS = ['#ffffff', '#60a5fa', '#93c5fd', '#3b82f6'];

  const spawnParticle = useCallback((x: number, y: number) => {
    const newParticle: Particle = {
      id: Math.random(),
      x,
      y,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      life: 1,
      size: Math.random() * 4 + 2,
      color: MAGIC_COLORS[Math.floor(Math.random() * MAGIC_COLORS.length)],
    };
    setParticles((prev) => [...prev.slice(-20), newParticle]);
  }, []);

  const animate = useCallback(() => {
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
    requestRef.current = requestAnimationFrame(animate);
  }, []);

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [animate]);

  useEffect(() => {
    const updatePosition = (e: MouseEvent) => {
      if (!isVisible) setIsVisible(true);
      mousePos.current = { x: e.clientX, y: e.clientY };
      
      if (cursorRef.current) {
        cursorRef.current.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0) translate(-50%, -50%)`;
      }

      if (variant === 'magic') {
        spawnParticle(e.clientX, e.clientY);
      }
    };

    const updateVariant = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      
      const cursorTarget = target.closest('[data-cursor]');
      const isInteractive = 
        target.tagName === 'BUTTON' || 
        target.tagName === 'A' || 
        target.closest('button') || 
        target.closest('a') ||
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA';

      if (cursorTarget) {
        setVariant(cursorTarget.getAttribute('data-cursor') as any);
      } else if (isInteractive) {
        setVariant('hover');
      } else {
        setVariant('default');
      }
    };

    window.addEventListener('mousemove', updatePosition);
    document.addEventListener('mouseover', updateVariant);

    return () => {
      window.removeEventListener('mousemove', updatePosition);
      document.removeEventListener('mouseover', updateVariant);
    };
  }, [isVisible, variant, spawnParticle]);

  const getVariantClasses = () => {
    switch (variant) {
      case 'magic':
        return 'w-5 h-5 bg-white shadow-[0_0_15px_rgba(255,255,255,0.8)] mix-blend-difference';
      case 'card':
        return 'w-10 h-10 bg-white mix-blend-difference';
      case 'hover':
        return 'w-5 h-5 bg-white mix-blend-difference';
      default:
        return 'w-3 h-3 bg-white mix-blend-difference';
    }
  };

  if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(pointer: coarse)').matches) {
    return null; 
  }

  return (
    <>
      <div 
        ref={cursorRef}
        className={`fixed top-0 left-0 pointer-events-none rounded-full z-[9999] transition-[width,height,opacity] duration-200 ease-out flex items-center justify-center ${getVariantClasses()} ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        style={{ transform: 'translate3d(0, 0, 0) translate(-50%, -50%)' }}
      >
        {variant === 'magic' && (
          <div className="absolute inset-0 rounded-full animate-ping bg-white/20" />
        )}
      </div>
      
      {/* Magic Particles */}
      {particles.map((p) => (
        <div
          key={p.id}
          className="fixed top-0 left-0 pointer-events-none z-[9998] rounded-full"
          style={{
            transform: `translate3d(${p.x}px, ${p.y}px, 0)`,
            width: p.size,
            height: p.size,
            backgroundColor: p.color,
            opacity: p.life,
            boxShadow: `0 0 ${p.size * 2}px ${p.color}`,
          }}
        />
      ))}
    </>
  );
};
