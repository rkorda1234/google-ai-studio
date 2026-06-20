
import React from 'react';

export const AbstractBackground: React.FC = () => {
  return (
    <>
      <style>
        {`
          @keyframes moveInCircle {
            0% { transform: rotate(0deg); }
            50% { transform: rotate(180deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes moveVertical {
            0% { transform: translateY(-50%); }
            50% { transform: translateY(50%); }
            100% { transform: translateY(-50%); }
          }
          @keyframes moveHorizontal {
            0% { transform: translateX(-50%) translateY(-10%); }
            50% { transform: translateX(50%) translateY(10%); }
            100% { transform: translateX(-50%) translateY(-10%); }
          }
          .gradient-bg {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            background: #ffffff;
            z-index: 0;
            overflow: hidden;
          }
          .g1, .g2, .g3, .g4, .g5 {
            position: absolute;
            background: radial-gradient(circle at center, rgba(var(--color), 0.8) 0, rgba(var(--color), 0) 50%) no-repeat;
            mix-blend-mode: hard-light;
            width: var(--size);
            height: var(--size);
            top: calc(50% - var(--size) / 2);
            left: calc(50% - var(--size) / 2);
            opacity: 0.7;
          }
          .g1 {
            --color: 18, 113, 255;
            --size: 80%;
            animation: moveVertical 30s ease infinite;
          }
          .g2 {
            --color: 221, 74, 255;
            --size: 80%;
            transform-origin: calc(50% - 400px);
            animation: moveInCircle 20s reverse infinite;
          }
          .g3 {
            --color: 100, 220, 255;
            --size: 80%;
            transform-origin: calc(50% + 400px);
            animation: moveInCircle 40s linear infinite;
          }
          .g4 {
            --color: 200, 50, 50;
            --size: 80%;
            transform-origin: calc(50% - 200px);
            animation: moveHorizontal 40s ease infinite;
            opacity: 0.4;
          }
          .g5 {
            --color: 180, 180, 50;
            --size: 80%;
            transform-origin: calc(50% - 800px) calc(50% + 200px);
            animation: moveInCircle 20s ease infinite;
            opacity: 0.4;
          }
        `}
      </style>
      <div className="gradient-bg pointer-events-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="hidden">
          <defs>
            <filter id="goo">
              <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
              <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" />
              <feBlend in="SourceGraphic" in2="goo" />
            </filter>
          </defs>
        </svg>
        <div className="g1"></div>
        <div className="g2"></div>
        <div className="g3"></div>
        <div className="g4"></div>
        <div className="g5"></div>
      </div>
    </>
  );
};
