import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Menu, X, ArrowRight, Check, ExternalLink, Instagram, Facebook, PenTool, Cpu, Layers, TrendingUp, ClipboardList, Megaphone, Calculator, MessageSquare, Headphones, Briefcase, Users, Quote, Shield, Plus, ArrowUp, ShoppingCart, Trash2, ChevronLeft, Mic, Wand2, Sparkles, Loader2, RotateCcw, Lock, Settings, Video, Image as ImageIcon, Save, Play, Copy, Calendar, User as UserIcon, Star, Bell, Target, Zap, Building2, LayoutDashboard, Smartphone, Mail, Share2, MessageCircle, Globe, CreditCard, Bot, Phone, FileText, CheckCircle2, Tag, GitBranch, RefreshCcw, UserPlus, MapPin, Linkedin, Youtube, Twitter } from 'lucide-react';
import { AIBot } from './components/AIBot';
import { CustomCursor } from './components/CustomCursor';
import { RevealOnScroll } from './components/RevealOnScroll';
import { WorkflowSimulator } from './components/WorkflowSimulator';
import { N8NWorkflowVisualizer } from './components/N8NWorkflowVisualizer';
import { AbstractBackground } from './components/AbstractBackground';
import { TypewriterText } from './components/TypewriterText';
import { Plan, Project, Service, WorkflowCategory, BlogPost } from './types';
import { GoogleGenAI } from "@google/genai";

// --- Helper Functions ---

const openPaymentPopup = (url: string) => {
  const width = 600;
  const height = 800;
  const left = (window.screen.width / 2) - (width / 2);
  const top = (window.screen.height / 2) - (height / 2);
  window.open(
    url,
    'MarketingversePayment',
    `width=${width},height=${height},top=${top},left=${left},toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes`
  );
};

// --- Initial Data ---

const INITIAL_PROJECTS: Project[] = [
  {
    id: 'p1',
    title: 'Neon Commerce Scale-up',
    category: 'Social Media',
    description: 'Increased organic reach by 400% in 3 months for a streetwear brand.',
    imageUrl: 'https://picsum.photos/600/400?random=1'
  },
  {
    id: 'p2',
    title: 'FinTech AI Support',
    category: 'AI Automation',
    description: 'Deployed a custom Gemini-powered support bot reducing ticket volume by 60%.',
    imageUrl: 'https://picsum.photos/600/400?random=2'
  }
];

const INITIAL_BLOGS: BlogPost[] = [
  {
    id: 'b1',
    title: 'The "Lazy" CEO’s Guide to AI: Why Working Hard is So 2023',
    excerpt: 'Hustle culture lied to you. You don\'t need to wake up at 4 AM to dominate your market—you just need better scripts.',
    content: `Let’s be honest: "Hustle Culture" is exhausted. If you're still bragging about 80-hour work weeks in Miami or Manhattan, you're not winning; you're inefficient. The era of the "Grind" is dead, replaced by the era of the "Flow."

Enter the "Lazy" CEO. This isn't about sitting on a beach (though that's a nice perk); it's about leverage. AI agent swarms don't sleep, they don't complain about coffee breaks, and they process data faster than your entire ops team combined.

We recently helped a logistics firm in Austin replace their entire manual dispatch system with an N8N workflow. The result? The owner went from answering calls at 2 AM to… sleeping. 

The secret isn't working harder. It's building systems that work so you don't have to. If your business can't run for a week without you, you don't own a business; you own a job. Time to fire yourself from the grunt work.`,
    date: 'Dec 12, 2024',
    category: 'Productivity',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=101'
  },
  {
    id: 'b2',
    title: 'Your Brand Voice Sounds Like a Robot (Here’s How to Fix It)',
    excerpt: 'If I see one more LinkedIn post starting with "Delve into the landscape," I might actually scream. Authenticity is the new currency.',
    content: `We need to talk about "ChatGPT Voice." You know what I mean. The sentences are too perfect. The adjectives are "robust" and "transformative." It feels like a corporate press release written by a calculator.

In a world drowning in synthetic content, the most valuable asset you have is your humanity. But wait—doesn't Marketingverse sell AI? Yes. But we sell *smart* AI.

The trick isn't asking AI to "write a post." It's about Fine-Tuning. We take your last 500 emails, your Slack history, and your transcripts, and we build a "Style LoRA" (Low-Rank Adaptation) that actually sounds like *you*.

Don't let default settings destroy your brand equity. If your AI sounds like a robot, it’s not the AI’s fault. It’s your prompt’s fault.`,
    date: 'Dec 08, 2024',
    category: 'Branding',
    author: 'Elena Vance',
    imageUrl: 'https://picsum.photos/800/600?random=102'
  },
  {
    id: 'b3',
    title: 'SEO in the Age of SGE: Why "Keywords" Are Dying',
    excerpt: 'Google is changing. Search Generative Experience (SGE) means users might never visit your website. Here is how to survive.',
    content: `The old SEO playbook: Stuff keywords, buy backlinks, pray to the Google Gods. 
    
    The new SEO playbook: Information Gain.
    
    With Google's SGE (Search Generative Experience), the search engine gives the answer directly. If your blog just regurgitates what everyone else says, you are invisible. You need to provide unique data, contrarian opinions, or personal anecdotes that an LLM cannot hallucinate.

    For local businesses—from London dentists to Toronto roofers—this means "Entity Authority." Does the Knowledge Graph know who you are? Are your reviews responding automatically with semantic richness? 
    
    Stop optimizing for robots. Start optimizing for the "Click-Through to Reality."`,
    date: 'Nov 28, 2024',
    category: 'Marketing',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=103'
  },
  {
    id: 'b4',
    title: 'Content Alchemy: Turning One Zoom Call into 30 Assets',
    excerpt: 'Stop creating content from scratch every day. It is inefficient and painful. Learn the "Waterfall" method.',
    content: `Here is a tragedy I see every day: A founder gives a brilliant 30-minute talk on a Zoom call, and it vanishes into the ether. Gone forever.

    This is waste. At Marketingverse, we practice "Content Alchemy." 
    
    1. **The Source:** Record the video.
    2. **The Transmute:** AI extracts the transcript.
    3. **The Distill:** Gemini Pro summarizes it into a LinkedIn Carousel.
    4. **The Spark:** Claude 3.5 Sonnet writes a witty Twitter thread.
    5. **The Visual:** Midjourney creates a thumb-stopping cover image.
    6. **The Clip:** Opus Clip cuts the video into 5 viral TikToks.

    One input. Thirty outputs. Total time cost: 0 minutes (if you automate it). Welcome to the machine.`,
    date: 'Nov 15, 2024',
    category: 'Content',
    author: 'Elena Vance',
    imageUrl: 'https://picsum.photos/800/600?random=104'
  },
  {
    id: 'b5',
    title: 'The Math of Missed Calls: Why Your Voicemail is Burning Cash',
    excerpt: 'If you are a local service business, a missed call is a missed mortgage payment. AI Voice Agents are the receptionists that never sleep.',
    content: `Let’s do some napkin math. You run an HVAC company in Phoenix. Average job value: $450. You miss 3 calls a day because you're on a job site. That’s $1,350/day. That’s nearly $40k/month in lost revenue.

    Why? Because modern consumers don't leave voicemails. They hang up and call the next guy on Google Maps.

    This is where AI Voice Agents shine. We aren't talking about "Press 1 for Sales." We're talking about a human-sounding voice that picks up on the first ring, qualifies the lead, checks your calendar, and books the appointment directly into your CRM.

    It’s not "cool tech." It’s defensive revenue protection.`,
    date: 'Oct 30, 2024',
    category: 'Business',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=105'
  },
  {
    id: 'b6',
    title: 'Miami to Manhattan: The "Static-to-Video" Revolution in Real Estate',
    excerpt: 'Listing photos are boring. Drones are expensive. AI is animating the immobile and selling homes faster.',
    content: `Real Estate is a visual game. But for years, agents have been held hostage by videographer schedules and $2,000 drone packages. 

    Not anymore. New generative video models (like the ones powering our "Property Launchpad") can take a still image of a living room and generate a realistic camera pan, complete with shifting light and parallax depth.

    You can now turn a folder of iPhone photos into a cinematic 4K tour in minutes. For brokers in competitive markets like Miami or NYC, speed is everything. Getting a "video" listing up on TikTok before the photographer even edits their first photo? That's how you win the listing presentation.`,
    date: 'Oct 12, 2024',
    category: 'Real Estate',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=106'
  },
  {
    id: 'b7',
    title: 'Prediction: The Rise of the "One-Person Unicorn"',
    excerpt: 'Sam Altman predicts we will see a billion-dollar company run by a single person. Here is how they will do it.',
    content: `It sounds insane. A billion-dollar valuation with one employee? But look at the trajectory.
    
    Instagram had 13 employees when it was bought for $1B. WhatsApp had 55 when it sold for $19B. The headcount required to generate massive value is collapsing.

    The "One-Person Unicorn" won't be a genius coder doing it all. They will be a genius *orchestrator*. They will manage a fleet of AI agents: a Marketing Agent, a Sales Agent, a fulfillment bot, and a finance algorithm. 

    The skill of the future isn't "doing." It's "directing." Are you ready to be the conductor of your own digital orchestra?`,
    date: 'Sep 28, 2024',
    category: 'Future Trends',
    author: 'Elena Vance',
    imageUrl: 'https://picsum.photos/800/600?random=107'
  },
  {
    id: 'b8',
    title: 'TikTok SEO: The Hidden Goldmine You’re Ignoring',
    excerpt: 'Gen Z does not Google it. They TikTok it. If your video scripts aren\'t optimized for search, you don\'t exist.',
    content: `Google has a problem. Young people don't trust it. They trust faces. They trust video. When they want to know "Best brunch in Chicago" or "How to invest in stocks," they go to TikTok.

    But here is what most marketers miss: TikTok is a Search Engine, not just a viral slot machine. 

    The words you speak in your video, the text on screen, and your caption are all indexed. If you aren't treating your script like an SEO blog post, you are missing 50% of the traffic. 

    We use AI to reverse-engineer trending search queries and inject them naturally into video scripts. It’s not about dancing; it’s about answering questions.`,
    date: 'Sep 15, 2024',
    category: 'Social Media',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=108'
  },
  {
    id: 'b9',
    title: 'Hyper-Personalization: Stalking (Legally) at Scale',
    excerpt: 'Cold email is dead. Long live "Warm AI." How to automate networking without losing your soul.',
    content: `Nobody reads generic cold emails. "I hope this email finds you well" is the digital equivalent of a limp handshake.

    But imagine this: You receive an email that references the podcast you appeared on last week, compliments a specific point you made about supply chains, and relates it to a solution. You'd reply, right?

    Now imagine doing that for 1,000 people a day. That is "Warm AI." By combining scraping tools (like Clay or Apollo) with LLMs, we can analyze a prospect's entire digital footprint and generate a "p.s." line that proves you did your homework.

    It’s scaling intimacy. And it converts like crazy.`,
    date: 'Aug 30, 2024',
    category: 'Sales',
    author: 'Elena Vance',
    imageUrl: 'https://picsum.photos/800/600?random=109'
  },
  {
    id: 'b10',
    title: 'The Death of the Stock Photo: Why Generative Imagery Wins',
    excerpt: 'Generic men in blue suits shaking hands? Boring. Visuals are the first hook, and custom generation is the only way to stand out.',
    content: `We have all seen it. The "Corporate Happy Team" photo. The "Woman Laughing at Salad." Stock photos are the elevator music of the internet—inoffensive, ubiquitous, and completely ignored.

    Generative AI (Midjourney, Flux, Imagen) allows brands to create visuals that actually *mean* something. You can create a mascot in your brand colors, a surreal landscape that stops the scroll, or a hyper-specific diagram that explains your product perfectly.

    Your visual identity is the first thing a customer judges. Don't let it be generic. In the Marketingverse, we believe every pixel should fight for attention.`,
    date: 'Aug 14, 2024',
    category: 'Design',
    author: 'Marketingverse Team',
    imageUrl: 'https://picsum.photos/800/600?random=110'
  }
];

const SERVICES: Service[] = [
  {
    id: 'social',
    title: 'Social Media',
    description: 'We build your community and amplify your voice across all major platforms.',
    icon: 'Instagram',
    features: ['Content Calendar', 'Community Engagement', 'Analytics Reporting']
  },
  {
    id: 'content',
    title: 'Content Marketing',
    description: 'Strategic storytelling that ranks high and converts readers into loyal customers.',
    icon: 'PenTool',
    features: ['SEO Blog Writing', 'Email Newsletters', 'Whitepapers & E-books']
  },
  {
    id: 'ai',
    title: 'AI Automations',
    description: 'Future-proof your workflows with custom AI agents and process automation.',
    icon: 'Cpu',
    features: ['Custom Chatbots', 'Workflow Automation', 'CRM Integration']
  },
  {
    id: 'crm',
    title: 'Broker CRM',
    description: 'Complete CRM and marketing suite designed specifically for Real Estate Brokers.',
    icon: 'Building2',
    features: ['Agent Management', 'Automated Workflows', 'Reputation Management']
  }
];

const SOCIAL_PLANS: Plan[] = [
  {
    name: 'Presence',
    price: '$85',
    description: 'Essential management to keep your brand active and professional.',
    features: ['12 FB/IG templatized cross-posts', '12 Templatized Stories', 'Automatic posting at best times'],
    paymentLink: 'https://buy.stripe.com/test_presence'
  },
  {
    name: 'Growth',
    price: '$450',
    description: 'Aggressive growth strategy for brands ready to scale rapidly.',
    recommended: true,
    features: ['1-1 Coaching', 'Brand Creation', 'Monthly Content shoot', '8 Video Posts', 'Community Management', '2 IG Boosts'],
    paymentLink: 'https://billing.the-marketingverse.com/subscribe/012b590903e576e21bb2f16ffd298a88a7726ba08b65d6ccad482bf477cf719e/SocialMediaGrowth'
  },
  {
    name: 'Dominance',
    price: '$850',
    description: 'Full-service content production and viral strategy.',
    features: ['Everything in Growth plan', 'Extra Video Content Shoot', 'Email Marketing', 'TikTok & GMB', '4 IG Boosts'],
    paymentLink: 'https://billing.the-marketingverse.com/subscribe/012b590903e576e21bb2f16ffd298a88a7726ba08b65d6ccad482bf477cf719e/SocualMediaDominance'
  }
];

const AI_PLANS: Plan[] = [
  {
    name: 'Pilot',
    price: '$1,500',
    description: 'Entry-level automation to solve specific bottlenecks.',
    features: ['1 Custom AI Workflow', 'Chatbot Integration (Web)', 'Basic CRM Connection', 'Training & Handoff', 'Standard Maintenance'],
    paymentLink: 'https://buy.stripe.com/test_pilot'
  },
  {
    name: 'Efficiency',
    price: '$4,500',
    description: 'Department-wide overhaul to maximize productivity.',
    recommended: true,
    features: ['3 Complex AI Workflows', 'Omnichannel AI Agents', 'Full CRM/ERP Integration', 'Staff AI Training', 'Priority Support & Updates'],
    paymentLink: 'https://buy.stripe.com/test_efficiency'
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'Fully autonomous agent swarms for large organizations.',
    features: ['Unlimited Workflows', 'Custom LLM Fine-tuning', 'On-premise Deployment', 'Dedicated Engineer', 'White-label Options'],
    paymentLink: '#ai-consultation'
  }
];

const BROKER_CRM_PLANS: Plan[] = [
  {
    name: 'Broker CRM Essential',
    price: '$450',
    description: 'The essential toolkit for modern brokerages.',
    features: [
      'Monthly Newsletter',
      '2 Email Campaigns',
      '2 SMS Cold Reach',
      'Landing Page',
      'Social Media Management Platform',
      'Reputation Management (Google & FB)',
      'Review Request Links',
      'Chat Widget',
      '10 Forms, 10 Custom Fields',
      '10 Trigger Links, 3 QR Codes',
      '3 Calendars',
      '2 Automated Workflows',
      'Access To Email & Website Templates'
    ],
    paymentLink: 'https://billing.the-marketingverse.com/subscribe/012b590903e576e21bb2f16ffd298a88a7726ba08b65d6ccad482bf477cf719e/CRM_Essential_Brokers'
  },
  {
    name: 'Broker CRM Pro',
    price: '$850',
    description: 'Advanced marketing and analytics for Brokers and their agents.',
    recommended: true,
    features: [
      'Everything in Essential, plus:',
      'Broker Branded Landing Page For Agents',
      '6 Broker Branded Emails For Agents',
      'Whatsapp Integration',
      'Google & FB Ads Analytics Setup',
      'Bi-Weekly Newsletter',
      '+1 Email Campaign',
      '+3 Automation Workflows',
      '+4 SMS Campaigns',
      '+2 Calendars',
      'Landing Page Tweaks',
      'Unlimited Forms, QR Codes, Custom Fields'
    ],
    paymentLink: 'https://billing.the-marketingverse.com/subscribe/012b590903e576e21bb2f16ffd298a88a7726ba08b65d6ccad482bf477cf719e/CRM_Brokers_Pro'
  },
  {
    name: 'Broker CRM Dominance',
    price: '$3000',
    description: 'Full-scale automation and AI agents for market leaders.',
    features: [
      'Everything in Pro, plus:',
      'Ai Voice & Conversation Agent',
      'Ads Manager',
      'Weekly Newsletter',
      '+1 Landing Page',
      '+2 Emails Campaigns',
      '+2 Automation Workflows',
      '+4 SMS Campaigns',
      'Broker Branded Marketing Templates',
      'CRM Setup for up to 10 Agents ($80/ea addl.)'
    ],
    paymentLink: 'https://billing.the-marketingverse.com/subscribe/012b590903e576e21bb2f16ffd298a88a7726ba08b65d6ccad482bf477cf719e/CRM_Broker_Dominance'
  }
];

const AI_WORKFLOWS: WorkflowCategory[] = [
  {
    title: "Sales",
    icon: "TrendingUp",
    items: [
      "Niche study", "Market report", "Competition listening", "Analyze sales calls", 
      "Train team", "Follow up", "Appointments", "Sales Scripts", "Notes", "Reports", 
      "CRM integration", "Order fulfillment", "Price adjustment based on market", "Presentations"
    ]
  },
  {
    title: "Administrative",
    icon: "ClipboardList",
    items: [
      "Email labeling and forwarding", "Input data & organize", "Events and Appts in calendar", 
      "Meeting analysis and tasks", "Assistant tasks", "Upload to drive", 
      "Make confirmation calls", "Presentations",
      "Document parsing & OCR", "Travel & Itinerary planning", "Expense report generation",
      "Meeting transcription & summaries", "Vendor contract management"
    ]
  },
  {
    title: "Marketing",
    icon: "Megaphone",
    items: [
      "Lead generation", "Content creation", "Content repurposing", "Blogs, social, videos, x", 
      "Avatar creation", "Scraping and listening", "Market research & competitive analysis", 
      "Trend listening", "Campaign analytics", "Ad campaign creation and optimization", 
      "CRM integration", "AI widgets to website", "GEO/SEO", "Presentations", 
      "Email newsletters, offers, fun"
    ]
  },
  {
    title: "Accounting",
    icon: "Calculator",
    items: [
      "Compare vendors and notify if better ones enter market", 
      "Tax analysis and recommendations", "New important laws monitoring",
      "Automated invoice processing", "Expense categorization", "Cash flow forecasting",
      "Fraud detection alerts", "Payroll automation assistance", "Receipt scanning & entry"
    ]
  },
  {
    title: "Communication",
    icon: "MessageSquare",
    items: [
      "Relay messages based on context", "Natural conversations with clients", 
      "Onboard and classify clients", "Video Avatars for questions, coaching, announcements",
      "Real-time translation", "Sentiment analysis on client messages", 
      "Internal knowledge base Q&A", "Voice note transcription", "Slack/Teams workflow bots"
    ]
  },
  {
    title: "Customer Service",
    icon: "Headphones",
    items: [
      "Avatars", "Bots", "Call analysis", "Personalized follow ups", 
      "AI surveys", "Social listening for client insights"
    ]
  },
  {
    title: "Fulfillment",
    icon: "Briefcase",
    items: [
      "Personal assistant", "Call notes", "Reminders", "Follow ups", "Appointments", 
      "Access to company data (pulse of company)", "Travel reservations", 
      "Lunch reservations", "Coaching", "Email summaries and analysis", 
      "Reply to emails", "Research", "Compare vendors"
    ]
  },
  {
    title: "Human Resources",
    icon: "Users",
    items: [
      "Days off tracking", "Hiring process", "Pre-interview qualification", 
      "Interview analysis", "Social listening to qualify", "Rate candidates", 
      "Onboarding", "Training", "Offboarding", "Reports"
    ]
  },
  {
    title: "IT Operations",
    icon: "Shield",
    items: [
      "Automated ticket routing", "Password reset bots", "System uptime monitoring",
      "Security anomaly detection", "Log analysis & reporting", "Software license tracking",
      "Database maintenance automation", "Phishing threat detection", "Access control audits"
    ]
  },
  ];

const A_LA_CARTE_ITEMS = [
  { id: 'content-gen', title: 'Content Gen Suite', title_original: 'Content Gen Suite', description: 'Automated Blogs, Social Posts, Video Scripts & HeyGen Avatars' },
  { id: 'scrape-content', title: 'Scrape & Create Engine', description: 'Turn Apify scraped data into engaging content automatically' },
  { id: 'prop-pres', title: 'Property Launchpad', description: 'Generate stunning presentations & landing pages instantly' },
  { id: 'tour-followup', title: 'Tour Feedback Loop', description: 'Tour presentations with automated follow-up survey emails' },
  { id: 'voice-assist', title: 'AI Voice Assistant', description: 'Intelligent voice interface for hands-free operations' },
  { id: 'pic-video', title: 'Static-to-Video AI', description: 'Transform property photos into dynamic video tours' },
  { id: 'avatar-post', title: 'Avatar Auto-Poster', description: 'Create HeyGen videos and automatically post them' },
  { id: 'trend-leads', title: 'Trend Hunter', description: 'Scrape Google Trends to identify and capture new leads' },
  { id: 'content-cal', title: 'Content Ops Center', description: 'Generate content calendars & send WhatsApp alerts' },
  { id: 'market-intel', title: 'Market Intel Bot', description: 'Research trends & write updated market report emails' },
  { id: 'auto-sched', title: 'Auto-Scheduler', description: 'Email coordination for seamless appointment booking' },
  { id: 'monthly-reps', title: 'Owner Reporter', description: 'Send monthly property reports based on market comps' },
  { id: 'deal-arch', title: 'Deal Architect', description: 'Analyze offers, prepare counter-offers & draft emails' },
  { id: 'invest-anal', title: 'Investment Analyzer', description: 'Analyze OM presentations & email investment insights' },
  { id: 'voice-agent', title: 'Conversational Voice Agent', description: 'Advanced AI agent for handling inbound/outbound calls' },
];

// --- Sub-Components ---

const ClientsSection: React.FC = () => {
  const clients = [
    { name: "Avanti Way", logo: "AVANTI WAY" },
    { name: "Servat Group", logo: "SERVAT GROUP", subtitle: "luxury real estate" },
    { name: "Viacom", logo: "viacom" },
    { name: "Sony Music", logo: "SONY MUSIC" },
    { name: "Quaker", logo: "QUAKER" },
    { name: "Proper Cloth", logo: "PROPER CLOTH" },
    { name: "Havaianas", logo: "havaianas" },
    { name: "Nickelodeon", logo: "nickelodeon" },
    { name: "HBO", logo: "HBO" },
    { name: "Jessica Hausmann", logo: "JESSICA HAUSMANN", subtitle: "Elevated Real Estate" }
  ];

  return (
    <section className="py-24 bg-white/40 backdrop-blur-lg border-t border-white/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <RevealOnScroll>
          <div className="text-center mb-16">
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 mb-4 block">Proven Performance</span>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Trusted by Industry Leaders</h2>
            <p className="text-neutral-500 max-w-2xl mx-auto">
              From global media giants to boutique luxury brands, we power the engines of tomorrow's market winners.
            </p>
          </div>
        </RevealOnScroll>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {clients.map((client, i) => (
            <RevealOnScroll key={i} delay={i * 50}>
              <div className="aspect-video bg-white/60 border border-white/20 rounded-2xl flex flex-col items-center justify-center p-6 transition-all hover:shadow-xl hover:-translate-y-1 group grayscale hover:grayscale-0 backdrop-blur-sm">
                <span className={`font-black text-xl tracking-tighter text-center leading-none ${client.name === 'HBO' ? 'text-4xl' : ''}`}>
                  {client.logo}
                </span>
                {client.subtitle && (
                  <span className="text-[8px] uppercase tracking-widest text-neutral-400 mt-1 font-bold">
                    {client.subtitle}
                  </span>
                )}
              </div>
            </RevealOnScroll>
          ))}
        </div>
      </div>
    </section>
  );
};

const SocialEcosystem: React.FC = () => {
  return (
    <div className="relative w-full h-[600px] bg-neutral-900 rounded-[2.5rem] overflow-hidden flex items-center justify-center shadow-2xl border border-neutral-800 group">
       {/* Background Gradient */}
       <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#3b82f630_0%,_transparent_70%)] opacity-60 animate-pulse" />
       
       {/* Grid Effect */}
       <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>

       {/* Orbit Rings */}
       <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-[280px] h-[280px] border border-white/5 rounded-full animate-[spin_20s_linear_infinite]" />
          <div className="w-[480px] h-[480px] border border-white/5 rounded-full animate-[spin_35s_linear_infinite_reverse]" />
          <div className="w-[650px] h-[650px] border border-white/5 rounded-full animate-[spin_50s_linear_infinite]" />
       </div>

       {/* Central Hub */}
       <div className="relative z-20 w-32 h-32 bg-gradient-to-br from-white to-neutral-200 rounded-3xl flex items-center justify-center shadow-[0_0_80px_rgba(255,255,255,0.2)] transform hover:scale-110 transition-transform duration-500">
          <div className="absolute inset-0 bg-white/20 rounded-3xl animate-ping opacity-20" />
          <div className="text-center">
             <img src="https://the-marketingverse.com/wp-content/uploads/2023/11/Mverse_Logo_Transparent_1-copy.png" className="w-16 h-auto opacity-90 mx-auto mb-1" alt="Core" />
             <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-800">Hub</span>
          </div>
       </div>

       {/* Floating Satellites - Using inline styles for absolute positioning around the center */}
       
       {/* Inner Orbit */}
       <div className="absolute animate-[spin_20s_linear_infinite] w-[280px] h-[280px] pointer-events-none">
          <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-xl shadow-lg shadow-purple-500/30 animate-[spin_20s_linear_infinite_reverse]">
             <Instagram size={20} className="text-white" />
          </div>
          <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-600/30 animate-[spin_20s_linear_infinite_reverse]">
             <Facebook size={20} className="text-white" />
          </div>
       </div>

       {/* Middle Orbit */}
       <div className="absolute animate-[spin_35s_linear_infinite_reverse] w-[480px] h-[480px] pointer-events-none">
          <div className="absolute top-1/4 -right-3 bg-black border border-neutral-700 p-2 rounded-xl shadow-lg animate-[spin_35s_linear_infinite]">
             <Twitter size={20} className="text-white" />
          </div>
          <div className="absolute bottom-1/4 -left-3 bg-red-600 p-2 rounded-xl shadow-lg shadow-red-600/30 animate-[spin_35s_linear_infinite]">
             <Youtube size={20} className="text-white" />
          </div>
          <div className="absolute -bottom-3 left-1/2 bg-blue-500 p-2 rounded-xl shadow-lg shadow-blue-500/30 animate-[spin_35s_linear_infinite]">
             <Linkedin size={20} className="text-white" />
          </div>
       </div>

       {/* Outer Orbit Stats Pills */}
       <div className="absolute animate-[spin_50s_linear_infinite] w-[650px] h-[650px] pointer-events-none">
          <div className="absolute top-10 left-20 px-4 py-2 bg-neutral-800/80 backdrop-blur-md rounded-full border border-white/10 text-white text-xs font-bold flex items-center gap-2 shadow-xl animate-[spin_50s_linear_infinite_reverse]">
             <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /> Reach +450%
          </div>
          <div className="absolute bottom-20 right-20 px-4 py-2 bg-neutral-800/80 backdrop-blur-md rounded-full border border-white/10 text-white text-xs font-bold flex items-center gap-2 shadow-xl animate-[spin_50s_linear_infinite_reverse]">
             <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" /> New Lead
          </div>
       </div>

       {/* Floating Particles */}
       <div className="absolute inset-0 pointer-events-none">
          {[...Array(8)].map((_, i) => (
             <div 
               key={i}
               className="absolute w-1 h-1 bg-white rounded-full opacity-0 animate-[ping_4s_ease-in-out_infinite]"
               style={{
                  top: `${Math.random() * 100}%`,
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 5}s`
               }}
             />
          ))}
       </div>
    </div>
  );
};

const SocialAdvantageSection: React.FC = () => {
  const items = [
    { icon: <Star size={20} />, title: "Dominant Branding", description: "Your 24/7 digital resume that builds instant trust with customers." },
    { icon: <Bell size={20} />, title: "Top-of-Mind Awareness", description: "Stay relevant to your target audience every single day, not just once a month." },
    { icon: <Users size={20} />, title: "Deepened Relationships", description: "Scale your personal touch and nurture past clients automatically." },
    { icon: <Target size={20} />, title: "Direct Prospecting", description: "High-velocity lead discovery through data-driven authority content." }
  ];

  return (
    <section className="py-24 bg-white/60 backdrop-blur-lg overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Column */}
          <RevealOnScroll>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 mb-6 block">The Modern Business Engine</span>
              <h2 className="text-5xl md:text-6xl font-bold leading-[1.1] mb-8">
                Social Media is <br />
                <span className="text-neutral-400">A Must.</span>
              </h2>
              <p className="text-lg text-neutral-500 mb-12 leading-relaxed max-w-lg">
                In today's fast-paced market, social media isn't just a platform—it's your digital storefront, your prospecting engine, and your primary relationship nurture tool.
              </p>
              
              <div className="space-y-8">
                {items.map((item, i) => (
                  <div key={i} className="flex gap-6 group">
                    <div className="w-12 h-12 rounded-full bg-white border border-neutral-100 flex items-center justify-center shrink-0 shadow-sm transition-all group-hover:bg-black group-hover:text-white group-hover:scale-110">
                      {item.icon}
                    </div>
                    <div>
                      <h4 className="font-bold text-lg mb-1">{item.title}</h4>
                      <p className="text-neutral-500 text-sm max-w-sm leading-relaxed">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </RevealOnScroll>

          {/* Right Column (The Stat Card) */}
          <RevealOnScroll delay={200}>
            <div className="relative">
              <div className="bg-neutral-900 rounded-[3rem] p-10 md:p-14 shadow-2xl relative overflow-hidden group">
                {/* Header of card */}
                <div className="flex items-center gap-3 mb-10">
                  <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-white">
                    <Users size={20} />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Consumer Choice</span>
                </div>

                {/* Big Stat */}
                <h3 className="text-8xl font-bold text-white mb-6">90%</h3>
                <p className="text-neutral-400 text-xl max-w-xs mb-12">
                  of consumers use social and web discovery to find their next brand partner.
                </p>

                <div className="h-px bg-white/10 mb-12" />

                {/* Previews */}
                <div className="grid grid-cols-3 gap-4 mb-10 items-start">
                   {/* Embed 1 */}
                   <div className="rounded-2xl overflow-hidden relative w-full border border-white/10 bg-black shadow-lg">
                      <div style={{padding:'177.78% 0 0 0', position:'relative'}}>
                        <iframe src="https://player.vimeo.com/video/503202988?title=0&byline=0&portrait=0&badge=0&autopause=0&player_id=0&app_id=58479" frameBorder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerPolicy="strict-origin-when-cross-origin" style={{position:'absolute',top:0,left:0,width:'100%',height:'100%'}} title="2iD_CasaArmani_ IGTV"></iframe>
                      </div>
                   </div>
                   {/* Embed 2 */}
                   <div className="rounded-2xl overflow-hidden relative w-full border border-white/10 bg-black shadow-lg">
                      <div style={{padding:'177.78% 0 0 0', position:'relative'}}>
                        <iframe src="https://player.vimeo.com/video/878437211?badge=0&autopause=0&player_id=0&app_id=58479" frameBorder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerPolicy="strict-origin-when-cross-origin" style={{position:'absolute',top:0,left:0,width:'100%',height:'100%'}} title="Mverse_ChristianG_Video_Avanti"></iframe>
                      </div>
                   </div>
                   {/* Embed 3 */}
                   <div className="rounded-2xl overflow-hidden relative w-full border border-white/10 bg-black shadow-lg">
                      <div style={{padding:'177.78% 0 0 0', position:'relative'}}>
                        <iframe src="https://player.vimeo.com/video/572254653?badge=0&autopause=0&player_id=0&app_id=58479" frameBorder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerPolicy="strict-origin-when-cross-origin" style={{position:'absolute',top:0,left:0,width:'100%',height:'100%'}} title="Artizan_Film_4_Story"></iframe>
                      </div>
                   </div>
                </div>

                {/* Footer text */}
                <div className="flex justify-between items-center">
                   <span className="text-[9px] font-bold uppercase tracking-widest text-neutral-600">Marketingverse Content Engine Preview</span>
                   <div className="flex gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-neutral-700" />
                      <div className="w-6 h-1.5 rounded-full bg-white" />
                      <div className="w-1.5 h-1.5 rounded-full bg-neutral-700" />
                   </div>
                </div>
              </div>

              {/* Decorative floating element */}
              <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-neutral-100 rounded-full blur-3xl -z-10" />
            </div>
          </RevealOnScroll>
        </div>
      </div>
    </section>
  );
};

const LiveAvatarDemo: React.FC = () => (
  <RevealOnScroll>
    <div className="mb-24">
      {/* Container: Frosted White */}
      <div className="bg-white/30 backdrop-blur-xl border border-white/50 rounded-[2.5rem] p-8 md:p-12 overflow-hidden relative shadow-2xl">
        {/* Background blobs - adjusted for light theme */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px] translate-y-1/3 -translate-x-1/3 pointer-events-none" />
        
        <div className="relative z-10 grid lg:grid-cols-5 gap-12 items-center">
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              {/* Badge */}
              <span className="px-3 py-1 bg-black/5 border border-black/5 text-black text-[10px] font-bold uppercase tracking-widest rounded-full backdrop-blur-sm">Interactive Demo</span>
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-600"></span>
                </span>
                <span className="text-green-600 text-[10px] font-bold uppercase tracking-widest">Live</span>
              </div>
            </div>
            
            {/* Heading - Dark Text */}
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-6 leading-tight">
              Meet Your New <br/>
              {/* Gradient text needs to be darker to read on white */}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">AI Support Agent</span>
            </h2>
            <p className="text-neutral-600 leading-relaxed mb-8">
              Experience the future of customer service. This autonomous interactive avatar can handle inquiries, book appointments, and provide 24/7 human-like support with zero latency.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-neutral-700 text-sm">
                <div className="w-8 h-8 rounded-full bg-white/60 flex items-center justify-center border border-white/60 shadow-sm">
                  <Mic size={14} className="text-black" />
                </div>
                <span>Microphone enabled conversation</span>
              </div>
              <div className="flex items-center gap-3 text-neutral-700 text-sm">
                <div className="w-8 h-8 rounded-full bg-white/60 flex items-center justify-center border border-white/60 shadow-sm">
                  <Zap size={14} className="text-black" />
                </div>
                <span>Real-time emotional intelligence</span>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-3">
            {/* Iframe container - Light glass */}
            <div className="rounded-2xl overflow-hidden shadow-2xl border border-white/60 bg-white/40 backdrop-blur-md relative" style={{ paddingTop: '56.25%' }}>
              <iframe 
                src="https://embed.liveavatar.com/v1/bb28ae02-2c79-41e6-a610-c104c8ad804e" 
                allow="microphone" 
                title="LiveAvatar Embed" 
                className="absolute top-0 left-0 w-full h-full border-none"
              ></iframe>
            </div>
            <div className="flex justify-between items-center mt-4 px-2">
              <p className="text-neutral-500 text-xs">
                * Click "Start" to begin the interaction
              </p>
               <span className="text-neutral-400 text-[10px] uppercase tracking-widest font-bold">Powered by Marketingverse AI</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </RevealOnScroll>
);

// --- CRM Visualizer Components ---
const WorkflowNode = ({ icon, title, subtitle, type = 'default', active = false }: any) => (
  <div className={`
    relative z-10 flex items-center gap-3 p-4 rounded-xl border shadow-lg w-60 transition-all duration-500
    ${type === 'condition' ? 'bg-amber-50 border-amber-200' : 'bg-white border-neutral-100'}
    ${active ? 'scale-105 ring-2 ring-blue-500/20 shadow-blue-500/10' : 'scale-100 opacity-80'}
  `}>
    <div className={`
      w-10 h-10 rounded-lg flex items-center justify-center shadow-sm
      ${type === 'condition' ? 'bg-amber-100 text-amber-600' : 'bg-neutral-50 text-neutral-600'}
    `}>
      {icon}
    </div>
    <div>
      <div className="font-bold text-sm text-neutral-800">{title}</div>
      <div className="text-[10px] text-neutral-500 font-mono">{subtitle}</div>
    </div>
  </div>
);

const Connector = ({ vertical, small, active = false }: any) => (
  <div className={`flex justify-center items-center ${vertical ? (small ? 'h-8' : 'h-10') : 'w-8'}`}>
    <div className={`w-0.5 h-full transition-colors duration-500 ${active ? 'bg-blue-500' : 'bg-neutral-200'}`}></div>
  </div>
);

const CRMWorkflowVisualizer: React.FC = () => {
  const [activePath, setActivePath] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActivePath(prev => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mb-20">
      <RevealOnScroll>
        <div className="text-center mb-10">
          <h3 className="text-3xl font-bold mb-4">Visual Workflow Builder</h3>
          <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
            Design complex customer journeys with our drag-and-drop automation engine.
          </p>
        </div>
      </RevealOnScroll>

      <div className="w-full bg-neutral-50/90 backdrop-blur-md border border-neutral-200 rounded-3xl overflow-hidden relative min-h-[700px] flex flex-col shadow-xl">
        {/* Toolbar */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-neutral-200 p-4 flex justify-between items-center z-20 relative">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <div className="w-3 h-3 rounded-full bg-green-400"></div>
          </div>
          <div className="flex items-center gap-4">
             <div className="text-xs font-bold uppercase tracking-widest text-neutral-500">Mverse Automations Builder</div>
          </div>
          <div className="flex items-center gap-3">
             <span className="text-xs text-neutral-400">Last saved: Just now</span>
             <div className="px-4 py-1.5 bg-black text-white text-xs font-bold rounded-full">Publish</div>
          </div>
        </div>
       
        {/* Canvas */}
        <div className="flex-1 relative overflow-hidden bg-[radial-gradient(#e5e5e5_1px,transparent_1px)] [background-size:20px_20px] p-8 md:p-12 flex justify-center overflow-x-auto">
          <div className="flex flex-col items-center min-w-[800px] relative z-10">
             
             {/* Trigger Node */}
             <WorkflowNode 
               icon={<Tag size={18} className="text-blue-600" />} 
               title="Contact Tag Added" 
               subtitle="Tag: 'new lead'" 
               active={true}
             />
             
             <Connector vertical active={true} />
             
             {/* Action Node */}
             <WorkflowNode 
               icon={<Bot size={18} className="text-purple-600" />} 
               title="AI VerseBot" 
               subtitle="Action: Qualify Lead" 
               active={true}
             />
             
             <Connector vertical active={true} />
             
             {/* Condition Node */}
             <WorkflowNode 
               icon={<GitBranch size={18} className="text-amber-600" />} 
               title="Check Budget" 
               subtitle="Condition: > $5,000" 
               type="condition" 
               active={true}
             />
             
             {/* Branching Logic */}
             <div className="relative flex justify-center gap-12 mt-8 w-full">
                {/* SVG Connections for branches */}
                <svg className="absolute -top-8 left-0 w-full h-8 z-0 pointer-events-none overflow-visible">
                   {/* Base Lines */}
                   <path d="M 50% 0 L 50% 15 L 16% 15 L 16% 32" fill="none" stroke="#e5e5e5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                   <path d="M 50% 0 L 50% 32" fill="none" stroke="#e5e5e5" strokeWidth="2" strokeLinecap="round" />
                   <path d="M 50% 0 L 50% 15 L 84% 15 L 84% 32" fill="none" stroke="#e5e5e5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                   
                   {/* Animated Highlighting Lines */}
                   {/* Left Path */}
                   <path 
                     d="M 50% 0 L 50% 15 L 16% 15 L 16% 32" 
                     fill="none" 
                     stroke={activePath === 0 ? "#3b82f6" : "transparent"} 
                     strokeWidth="3" 
                     strokeLinecap="round"
                     strokeLinejoin="round"
                     className="transition-all duration-700"
                     style={{ 
                       strokeDasharray: '200',
                       strokeDashoffset: activePath === 0 ? '0' : '200',
                       opacity: activePath === 0 ? 1 : 0
                     }}
                   />
                   {/* Middle Path */}
                   <path 
                     d="M 50% 0 L 50% 32" 
                     fill="none" 
                     stroke={activePath === 1 ? "#3b82f6" : "transparent"} 
                     strokeWidth="3" 
                     strokeLinecap="round"
                     className="transition-all duration-700"
                     style={{ 
                       strokeDasharray: '100',
                       strokeDashoffset: activePath === 1 ? '0' : '100',
                       opacity: activePath === 1 ? 1 : 0
                     }}
                   />
                   {/* Right Path */}
                   <path 
                     d="M 50% 0 L 50% 15 L 84% 15 L 84% 32" 
                     fill="none" 
                     stroke={activePath === 2 ? "#3b82f6" : "transparent"} 
                     strokeWidth="3" 
                     strokeLinecap="round"
                     strokeLinejoin="round"
                     className="transition-all duration-700"
                     style={{ 
                       strokeDasharray: '200',
                       strokeDashoffset: activePath === 2 ? '0' : '200',
                       opacity: activePath === 2 ? 1 : 0
                     }}
                   />
                </svg>

                {/* Branch 1: High Budget */}
                <div className={`flex flex-col items-center w-64 transition-all duration-500 ${activePath === 0 ? 'opacity-100 transform translate-y-0' : 'opacity-40 transform translate-y-2'}`}>
                   <div className="mb-3 px-3 py-1 bg-green-100 text-green-700 text-[10px] font-bold uppercase rounded-full shadow-sm">High Value Lead</div>
                   <WorkflowNode icon={<RefreshCcw size={16} />} title="Update Pipeline" subtitle="Stage: Hot Lead" active={activePath === 0} />
                   <Connector vertical small active={activePath === 0} />
                   <WorkflowNode icon={<UserPlus size={16} />} title="Assign Agent" subtitle="Round Robin: Luxury Team" active={activePath === 0} />
                   <Connector vertical small active={activePath === 0} />
                   <WorkflowNode icon={<MessageSquare size={16} />} title="SMS Intro" subtitle="Personalized Booking Link" active={activePath === 0} />
                </div>

                {/* Branch 2: Unsure */}
                <div className={`flex flex-col items-center w-64 transition-all duration-500 ${activePath === 1 ? 'opacity-100 transform translate-y-0' : 'opacity-40 transform translate-y-2'}`}>
                   <div className="mb-3 px-3 py-1 bg-neutral-200 text-neutral-600 text-[10px] font-bold uppercase rounded-full shadow-sm">Unknown Budget</div>
                   <WorkflowNode icon={<Bot size={16} />} title="AI Nurture" subtitle="Ask qualifying questions" active={activePath === 1} />
                   <Connector vertical small active={activePath === 1} />
                   <WorkflowNode icon={<Zap size={16} />} title="Wait" subtitle="24 Hours" active={activePath === 1} />
                   <Connector vertical small active={activePath === 1} />
                   <WorkflowNode icon={<Mail size={16} />} title="Follow-up Email" subtitle="Case study sent" active={activePath === 1} />
                </div>

                {/* Branch 3: Low Budget */}
                <div className={`flex flex-col items-center w-64 transition-all duration-500 ${activePath === 2 ? 'opacity-100 transform translate-y-0' : 'opacity-40 transform translate-y-2'}`}>
                   <div className="mb-3 px-3 py-1 bg-red-100 text-red-700 text-[10px] font-bold uppercase rounded-full shadow-sm">Low Budget</div>
                   <WorkflowNode icon={<Tag size={16} />} title="Add Tag" subtitle="nurture-long-term" active={activePath === 2} />
                   <Connector vertical small active={activePath === 2} />
                   <WorkflowNode icon={<Mail size={16} />} title="Add to Newsletter" subtitle="Weekly drip campaign" active={activePath === 2} />
                </div>
             </div>

          </div>
        </div>
      </div>
    </div>
  );
};

const AdminPortal: React.FC<{ projects: Project[]; setProjects: React.Dispatch<React.SetStateAction<Project[]>>; onClose: () => void }> = ({ projects, setProjects, onClose }) => {
  const [newProject, setNewProject] = useState<Partial<Project>>({ title: '', category: '', description: '', imageUrl: '', videoUrl: '' });
  const [copied, setCopied] = useState(false);

  const handleAdd = () => {
    if (!newProject.title || !newProject.imageUrl) return;
    const p: Project = {
      ...newProject as Project,
      id: `p-${Date.now()}`
    };
    const updated = [p, ...projects];
    setProjects(updated);
    localStorage.setItem('mverse_projects', JSON.stringify(updated));
    setNewProject({ title: '', category: '', description: '', imageUrl: '', videoUrl: '' });
  };

  const handleDelete = (id: string) => {
    const updated = projects.filter(p => p.id !== id);
    setProjects(updated);
    localStorage.setItem('mverse_projects', JSON.stringify(updated));
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(projects, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-[200] bg-black/95 backdrop-blur-xl p-6 md:p-12 overflow-y-auto animate-fade-in">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <Settings className="text-neutral-500" /> Project Command Center
            </h2>
            <p className="text-neutral-500 uppercase tracking-widest text-[10px] font-bold">Marketingverse Admin Portal</p>
          </div>
          <button onClick={onClose} className="p-3 bg-white/10 text-white rounded-full hover:bg-white/20 transition-all">
            <X size={24} />
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-12">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 space-y-4">
              <h3 className="text-xl font-bold text-white mb-4">Add New Project</h3>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase">Project Title</label>
                <input value={newProject.title} onChange={e => setNewProject({...newProject, title: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none" placeholder="e.g. Real Estate AI Overhaul" />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase">Category</label>
                <input value={newProject.category} onChange={e => setNewProject({...newProject, category: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none" placeholder="e.g. AI Automation" />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase">Description</label>
                <textarea value={newProject.description} onChange={e => setNewProject({...newProject, description: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none h-32 resize-none" placeholder="Describe the impact..." />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase">Image URL</label>
                <input value={newProject.imageUrl} onChange={e => setNewProject({...newProject, imageUrl: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none" placeholder="https://..." />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase">Video URL (Optional)</label>
                <input value={newProject.videoUrl} onChange={e => setNewProject({...newProject, videoUrl: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white outline-none" placeholder="https://..." />
              </div>
              <button onClick={handleAdd} className="w-full py-4 bg-white text-black rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-neutral-200 transition-all">
                <Save size={18} /> Push Project to Site
              </button>
            </div>
            <button onClick={copyToClipboard} className="w-full py-4 bg-neutral-800 text-neutral-400 border border-neutral-700 rounded-2xl font-bold flex items-center justify-center gap-2 hover:text-white transition-all">
              {copied ? <Check size={18} /> : <Copy size={18} />} {copied ? 'Copied JSON!' : 'Copy Code for Dev'}
            </button>
          </div>
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-xl font-bold text-white mb-6">Active Portfolio ({projects.length})</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {projects.map(p => (
                <div key={p.id} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex gap-4 group">
                  <div className="w-24 h-24 rounded-xl overflow-hidden shrink-0">
                    <img src={p.imageUrl} alt={p.title} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-white font-bold truncate">{p.title}</h4>
                    <p className="text-neutral-500 text-xs mb-2">{p.category}</p>
                    <button onClick={() => handleDelete(p.id)} className="p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500 hover:text-white transition-all">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProjectCard: React.FC<{ project: Project }> = ({ project }) => {
  const [showVideo, setShowVideo] = useState(false);
  return (
    <div data-cursor="card" className="group relative bg-neutral-50/90 backdrop-blur-md rounded-3xl overflow-hidden border border-neutral-100 hover:shadow-xl hover:-translate-y-2 transition-all duration-300">
      <div className="aspect-[16/10] overflow-hidden relative">
        <img src={project.imageUrl} alt={project.title} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700" />
        {project.videoUrl && (
          <button onClick={() => setShowVideo(true)} className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/40 transition-colors z-10">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-2xl transform group-hover:scale-105 transition-transform">
              <Play className="text-black fill-current" size={24} />
            </div>
          </button>
        )}
      </div>
      <div className="p-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 mb-2 block">{project.category}</span>
            <h3 className="text-2xl font-bold tracking-tight">{project.title}</h3>
          </div>
          <button className="p-3 bg-white rounded-full border border-neutral-100 hover:bg-black hover:text-white transition-all shadow-sm">
            <ExternalLink size={18} />
          </button>
        </div>
        <p className="text-neutral-600 leading-relaxed">{project.description}</p>
      </div>
      {showVideo && (
        <div className="fixed inset-0 z-[300] bg-black/95 flex items-center justify-center p-4 animate-fade-in" onClick={() => setShowVideo(false)}>
          <button className="absolute top-8 right-8 text-white p-4 hover:bg-white/10 rounded-full transition-colors"><X size={32} /></button>
          <div className="w-full max-w-5xl aspect-video bg-black rounded-3xl overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
            <iframe src={project.videoUrl?.includes('vimeo') ? `${project.videoUrl}?autoplay=1` : project.videoUrl} className="w-full h-full" allow="autoplay; fullscreen" title={project.title} />
          </div>
        </div>
      )}
    </div>
  );
};

const BackToTop: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  useEffect(() => {
    const toggle = () => setIsVisible(window.pageYOffset > 300);
    window.addEventListener('scroll', toggle);
    return () => window.removeEventListener('scroll', toggle);
  }, []);
  return (
    <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className={`fixed bottom-8 left-8 z-[90] p-4 bg-black text-white rounded-full shadow-2xl transition-all duration-300 transform hover:scale-110 active:scale-95 border border-neutral-800 flex items-center justify-center ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
      <ArrowUp size={24} />
    </button>
  );
};

const BookingModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in" onClick={onClose}>
      <div className="bg-white w-full max-w-4xl h-[90vh] rounded-2xl overflow-hidden relative shadow-2xl flex flex-col" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} className="absolute top-4 right-4 z-10 p-2 bg-white/80 rounded-full hover:bg-neutral-100 transition-colors border border-neutral-200"><X size={24} /></button>
        <iframe src="https://api.leadconnectorhq.com/widget/booking/8pROsd9gdPhAtmnP5YHd" className="w-full h-full border-none" title="Booking Consultation" />
      </div>
    </div>
  );
};

const ServiceIcon = ({ icon }: { icon: string }) => {
  switch (icon) {
    case 'Instagram': return <Instagram size={32} />;
    case 'PenTool': return <PenTool size={32} />;
    case 'Cpu': return <Cpu size={32} />;
    case 'Building2': return <Building2 size={32} />;
    default: return <Layers size={32} />;
  }
};

const WorkflowIcon = ({ icon }: { icon: string }) => {
  const props = { size: 24 };
  switch (icon) {
    case 'TrendingUp': return <TrendingUp {...props} />;
    case 'ClipboardList': return <ClipboardList {...props} />;
    case 'Megaphone': return <Megaphone {...props} />;
    case 'Calculator': return <Calculator {...props} />;
    case 'MessageSquare': return <MessageSquare {...props} />;
    case 'Headphones': return <Headphones {...props} />;
    case 'Briefcase': return <Briefcase {...props} />;
    case 'Users': return <Users {...props} />;
    case 'Shield': return <Shield {...props} />;
    default: return <Layers {...props} />;
  }
};

const ConsultationCTA: React.FC<{ onBookConsultation: () => void }> = ({ onBookConsultation }) => (
  <RevealOnScroll delay={100}>
    {/* Container: Frosted White */}
    <div className="w-full py-32 bg-white/30 backdrop-blur-xl border-t border-white/50 relative overflow-hidden mt-20">
      {/* Background pattern - light version */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#000000_1px,transparent_1px)] [background-size:24px_24px] opacity-[0.03]"></div>
      {/* Ambient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-blue-400/10 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
        <h2 className="text-5xl md:text-7xl font-bold mb-8 tracking-tighter text-neutral-900">Ready To Take It Up A Notch?</h2>
        <p className="text-xl text-neutral-600 mb-12 max-w-2xl mx-auto">
          Book a free consultation to discuss your specific needs and find the perfect strategy for you.
        </p>
        <button 
          onClick={onBookConsultation} 
          className="px-10 py-5 bg-black text-white rounded-full font-bold text-lg hover:bg-neutral-800 transition-all hover:scale-105 inline-flex items-center gap-3 shadow-xl"
        >
          Schedule Consultation <ArrowRight size={20} />
        </button>
      </div>
    </div>
  </RevealOnScroll>
);

const CustomPlanBuilder: React.FC<{ onOrderNow: () => void }> = ({ onOrderNow }) => {
  const [selected, setSelected] = useState<string[]>([]);
  const [isSummaryView, setIsSummaryView] = useState(false);

  const toggleItem = (id: string) => {
    setSelected(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleReviewSelection = () => {
    setIsSummaryView(true);
    const container = document.getElementById('plan-builder-container');
    if (container) container.scrollIntoView({ behavior: 'smooth' });
  };

  const handleOrder = () => {
    const selectedTitles = A_LA_CARTE_ITEMS.filter(i => selected.includes(i.id)).map(i => i.title).join(', ');
    const body = `Hi Marketingverse Team,%0D%0A%0D%0AI would like to order the following custom AI workflows:%0D%0A%0D%0A${selectedTitles}%0D%0A%0D%0APlease let me know the next steps.`;
    window.location.href = `mailto:hello@marketingverse.ai?subject=Order for Custom AI Workflows&body=${body}`;
    onOrderNow();
  };

  const selectedWorkflows = A_LA_CARTE_ITEMS.filter(item => selected.includes(item.id));

  return (
    <div id="plan-builder-container" className="py-20 border-t border-neutral-200 min-h-[600px]">
       {!isSummaryView ? (
         <>
           <RevealOnScroll>
             <div className="text-center mb-12">
               <h2 className="text-3xl font-bold mb-4">Build Your Custom A La Carte Plan</h2>
               <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
                 Mix and match specific workflows to create a package that fits your exact needs.
               </p>
             </div>
           </RevealOnScroll>
           
           <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
             {A_LA_CARTE_ITEMS.map((item, index) => {
                const isSelected = selected.includes(item.id);
                return (
                  <RevealOnScroll key={item.id} delay={index * 30}>
                    <div 
                      onClick={() => toggleItem(item.id)} 
                      className={`p-6 rounded-2xl border cursor-pointer transition-all duration-200 h-full flex flex-col relative group ${
                        isSelected 
                          ? 'bg-black text-white border-black shadow-lg transform scale-[1.02]' 
                          : 'bg-white/90 backdrop-blur-sm text-neutral-900 border-neutral-200 hover:border-black hover:shadow-md'
                      }`}
                      data-cursor="hover"
                    >
                       <div className="flex justify-between items-start mb-3">
                         <h3 className="font-bold text-lg pr-8">{item.title}</h3>
                         <div className={`w-6 h-6 rounded-full flex items-center justify-center border ${
                           isSelected ? 'bg-white border-white' : 'border-neutral-300'
                         }`}>
                            {isSelected ? <Check size={14} className="text-black" /> : <Plus size={14} className="text-neutral-300 group-hover:text-black" />}
                         </div>
                       </div>
                       <p className={`text-sm leading-relaxed ${isSelected ? 'text-neutral-300' : 'text-neutral-600'}`}>
                         {item.description}
                       </p>
                    </div>
                  </RevealOnScroll>
                );
             })}
           </div>

           <div className={`fixed bottom-8 left-0 right-0 z-50 flex justify-center transition-all duration-500 transform ${selected.length > 0 ? 'translate-y-0 opacity-100' : 'translate-y-24 opacity-0'}`}>
             <div className="bg-black text-white pl-6 pr-2 py-2 rounded-full shadow-2xl flex items-center gap-6 border border-neutral-800">
                <div className="flex items-center gap-3">
                   <div className="w-8 h-8 bg-white/10 rounded-full flex items-center justify-center">
                      <ShoppingCart size={16} />
                   </div>
                   <span className="font-bold">{selected.length} Workflow{selected.length !== 1 && 's'} Selected</span>
                </div>
                <button 
                  onClick={handleReviewSelection}
                  className="bg-white text-black px-6 py-3 rounded-full font-bold hover:bg-neutral-200 transition-colors flex items-center gap-2"
                >
                  Review Selection <ArrowRight size={16} />
                </button>
             </div>
           </div>
         </>
       ) : (
         <div className="animate-fade-in max-w-4xl mx-auto px-4">
            <button 
              onClick={() => setIsSummaryView(false)}
              className="mb-8 flex items-center gap-2 text-neutral-500 hover:text-black transition-colors font-medium"
            >
              <ChevronLeft size={20} /> Back to Selection
            </button>
            <div className="bg-neutral-50/90 backdrop-blur-md border border-neutral-200 rounded-3xl p-8 md:p-12 shadow-sm">
               <div className="flex justify-between items-end mb-10 border-b border-neutral-200 pb-8">
                  <div>
                     <h2 className="text-3xl font-bold mb-2">Custom Package Summary</h2>
                     <p className="text-neutral-600">Review your selected workflows before placing your order.</p>
                  </div>
               </div>
               <div className="space-y-6 mb-12">
                  {selectedWorkflows.map((item) => (
                    <div key={item.id} className="flex justify-between items-start gap-4 p-6 bg-white rounded-2xl border border-neutral-100 shadow-sm">
                       <div>
                          <h4 className="font-bold text-lg mb-1">{item.title}</h4>
                          <p className="text-neutral-500 text-sm">{item.description}</p>
                       </div>
                       <button 
                         onClick={() => {
                            toggleItem(item.id);
                            if (selected.length <= 1) setIsSummaryView(false);
                         }}
                         className="p-2 text-neutral-300 hover:text-red-500 transition-colors"
                       >
                         <Trash2 size={18} />
                       </button>
                    </div>
                  ))}
               </div>
               <div className="bg-black text-white p-8 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-8">
                  <h3 className="text-xl font-bold">Ready to initiate your custom build?</h3>
                  <button 
                    onClick={handleOrder}
                    data-cursor="magic"
                    className="w-full md:w-auto px-10 py-5 bg-white text-black rounded-xl font-bold text-lg hover:bg-neutral-200 transition-all transform hover:scale-105 shadow-xl flex items-center justify-center gap-3"
                  >
                    Order Now <ArrowRight size={22} />
                  </button>
               </div>
            </div>
         </div>
       )}
    </div>
  );
};

const NavBar: React.FC<{ active: string; setView: (v: string) => void; onBookConsultation: () => void }> = ({ active, setView, onBookConsultation }) => (
  <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-white/20 h-20 flex items-center shadow-sm">
    <div className="max-w-7xl mx-auto px-4 w-full flex justify-between items-center">
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => setView('home')}>
        <img src="https://the-marketingverse.com/wp-content/uploads/2023/11/Mverse_Logo_Transparent_1-copy.png" alt="Marketingverse Logo" className="h-5 w-auto object-contain" />
      </div>
      <div className="hidden md:flex gap-8 items-center">
        {['home', 'social', 'crm', 'integrations', 'blog', 'projects', 'contact'].map(id => (
          <button 
            key={id} 
            onClick={() => setView(id)} 
            className={`text-sm font-medium ${active === id ? 'text-black font-bold' : 'text-neutral-500 hover:text-black'}`}
          >
            {id === 'integrations' ? 'AI Integrations' : id === 'crm' ? 'Broker CRM' : (id.charAt(0).toUpperCase() + id.slice(1))}
          </button>
        ))}
        <button onClick={onBookConsultation} className="bg-black text-white px-5 py-2.5 rounded-full text-sm font-bold hover:bg-neutral-800 transition-colors">Book a Call</button>
      </div>
    </div>
  </nav>
);

const Footer: React.FC<{ onOpenAdmin: () => void }> = ({ onOpenAdmin }) => (
  <footer className="bg-black text-white py-12 border-t border-white/5 relative z-10">
    <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <img src="https://the-marketingverse.com/wp-content/uploads/2023/11/Mverse_Logo_Transparent_1-copy.png" alt="Logo" className="h-6 w-auto invert" />
        </div>
        <button onClick={onOpenAdmin} className="text-neutral-800 hover:text-neutral-500 transition-colors" title="Admin Portal">
          <Lock size={14} />
        </button>
      </div>
      <div className="flex gap-6 text-neutral-400">
        <Facebook size={18} className="hover:text-white cursor-pointer" />
        <Instagram size={18} className="hover:text-white cursor-pointer" />
      </div>
      <div className="text-neutral-500 text-sm">© {new Date().getFullYear()} Marketingverse.</div>
    </div>
  </footer>
);

// --- Views ---

const HomeView: React.FC<{ changeView: (v: string) => void; onBookConsultation: () => void }> = ({ changeView, onBookConsultation }) => {
  const handleServiceClick = (id: string) => {
    if (id === 'social') changeView('social');
    else if (id === 'ai') changeView('integrations');
    else if (id === 'content') changeView('blog');
    else if (id === 'crm') changeView('crm');
  };

  return (
    <div className="animate-fade-in relative z-10">
      <section className="relative py-20 lg:py-32 text-center overflow-hidden">
        {/* Removed opaque background for abstract background visibility */}
        <RevealOnScroll>
          <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-6 drop-shadow-sm">Marketingverse</h1>
          <p className="text-xl text-neutral-600 max-w-2xl mx-auto mb-10 leading-relaxed">Scaling brands with AI storytelling and high-performance social workflows.</p>
          
          <div className="flex flex-col md:flex-row flex-wrap justify-center gap-4 mt-8 px-4">
            <button 
              onClick={() => changeView('social')} 
              className="px-8 py-4 bg-black text-white rounded-2xl font-bold flex items-center justify-center gap-3 hover:scale-105 transition-transform shadow-lg group"
            >
              <Instagram size={20} className="group-hover:text-pink-400 transition-colors" />
              Social Media
            </button>
            <button 
              onClick={() => changeView('crm')} 
              className="px-8 py-4 bg-white/80 backdrop-blur-sm border border-neutral-200 text-black rounded-2xl font-bold flex items-center justify-center gap-3 hover:bg-neutral-50 hover:border-black hover:scale-105 transition-all shadow-sm group"
            >
              <Building2 size={20} className="group-hover:text-blue-600 transition-colors" />
              Broker CRM
            </button>
            <button 
              onClick={() => changeView('integrations')} 
              className="px-8 py-4 bg-white/80 backdrop-blur-sm border border-neutral-200 text-black rounded-2xl font-bold flex items-center justify-center gap-3 hover:bg-neutral-50 hover:border-black hover:scale-105 transition-all shadow-sm group"
            >
              <Bot size={20} className="group-hover:text-purple-600 transition-colors" />
              AI Systems
            </button>
          </div>
          
          <div className="mt-8">
             <button onClick={onBookConsultation} className="text-sm font-bold text-neutral-500 hover:text-black flex items-center gap-2 mx-auto transition-colors group">
                 Not sure what you need? Book a Strategy Call <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
             </button>
          </div>
        </RevealOnScroll>
      </section>

      <section className="py-20 bg-neutral-50/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {SERVICES.map(s => (
              <div 
                key={s.id} 
                onClick={() => handleServiceClick(s.id)}
                data-cursor="hover"
                className="bg-white/80 p-8 rounded-3xl border border-neutral-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 cursor-pointer group backdrop-blur-sm"
              >
                <div className="mb-6 group-hover:scale-110 transition-transform"><ServiceIcon icon={s.icon} /></div>
                <h3 className="text-xl font-bold mb-3 group-hover:text-black">{s.title}</h3>
                <p className="text-neutral-600 mb-6">{s.description}</p>
                <div className="flex items-center gap-2 text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                  Learn More <ArrowRight size={14} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <SocialAdvantageSection />

      <section className="relative w-full h-[80vh] bg-black overflow-hidden" style={{ clipPath: 'inset(0)' }}>
        <div className="fixed inset-0 w-full h-full -z-10">
           <iframe 
             src="https://player.vimeo.com/video/647525886?background=1&autoplay=1&loop=1&badge=0&autopause=0&player_id=0&app_id=58479" 
             className="absolute top-1/2 left-1/2 w-[177.77vh] min-w-full min-h-full -translate-x-1/2 -translate-y-1/2 object-cover pointer-events-none"
             frameBorder="0" 
             allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" 
             title="Avanti_AgentVideo_Guillermo Teran"
           />
        </div>
        <div className="absolute inset-0 bg-black/20" />
      </section>

      <section id="ai-consultation" className="py-24 bg-white/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <RevealOnScroll>
              <div>
                <span className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3 block">Next-Gen Consulting</span>
                <h2 className="text-5xl font-bold mb-8 leading-tight">Identify Your Strategy. <br />Instant & Live.</h2>
                <p className="text-xl text-neutral-600 mb-10 leading-relaxed">
                  Our advanced AI ecosystem is ready to analyze your challenges. Switch to <span className="font-bold text-black">Voice Mode</span> for a direct human-like conversation about your growth.
                </p>
                <div className="space-y-8">
                  <div className="flex gap-5">
                      <div className="w-14 h-14 rounded-2xl bg-neutral-100 flex items-center justify-center shrink-0 border border-neutral-200">
                        <Check size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Instant Tailored Roadmaps</h4>
                        <p className="text-neutral-600">Get specific recommendations for your niche in seconds.</p>
                      </div>
                  </div>
                  <div className="flex gap-5">
                      <div className="w-14 h-14 rounded-2xl bg-neutral-100 flex items-center justify-center shrink-0 border border-neutral-200">
                        <Mic size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg">Real-time Voice Interaction</h4>
                        <p className="text-neutral-600">Natural conversations powered by Gemini 2.5 Live API.</p>
                      </div>
                  </div>
                </div>
              </div>
            </RevealOnScroll>
            <RevealOnScroll delay={200}>
              <div className="relative">
                <div className="absolute -inset-8 bg-gradient-to-br from-neutral-200/50 via-neutral-100 to-transparent rounded-[3rem] opacity-40 blur-3xl"></div>
                <div className="relative">
                  <AIBot />
                </div>
              </div>
            </RevealOnScroll>
          </div>
        </div>
      </section>

      <ClientsSection />

      <ConsultationCTA onBookConsultation={onBookConsultation} />
    </div>
  );
};

const BrokerCRMView: React.FC<{ onSubscribe: (plan: Plan) => void; onBookConsultation: () => void }> = ({ onSubscribe, onBookConsultation }) => (
  <div className="animate-fade-in py-20 relative z-10">
    <div className="max-w-7xl mx-auto px-4">
      <RevealOnScroll>
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Broker CRM Suite</h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto">
            Empower your agents, automate your marketing, and dominate your local market with our all-in-one brokerage operating system.
          </p>
        </div>
      </RevealOnScroll>

      {/* Visual Showcase Section */}
      <div className="mb-32 space-y-24">
        {/* Section 1 */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <RevealOnScroll className="relative group">
              <div className="absolute inset-0 bg-blue-600 blur-[100px] opacity-20 rounded-full"></div>
              <div className="relative rounded-2xl overflow-hidden border border-neutral-200 shadow-2xl">
                <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=2426" alt="Broker Dashboard" className="w-full" />
              </div>
          </RevealOnScroll>
          <RevealOnScroll delay={200}>
              <h3 className="text-3xl font-bold mb-4">The Command Center Your Brokerage Deserves</h3>
              <p className="text-lg text-neutral-600 mb-6">Gain complete visibility into your agents' performance. From lead distribution to pipeline value, manage your entire organization from a single, intuitive dashboard.</p>
              <ul className="space-y-4">
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-blue-500" size={24} /></div> <span className="font-bold text-lg">Global Analytics & Reporting</span></li>
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-blue-500" size={24} /></div> <span className="font-bold text-lg">Route Leads & Track Activity</span></li>
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-blue-500" size={24} /></div> <span className="font-bold text-lg">Cohesive Branding & Marketing</span></li>
              </ul>
          </RevealOnScroll>
        </div>

        {/* Section 2 */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <RevealOnScroll className="lg:order-2 relative group">
              <div className="absolute inset-0 bg-purple-600 blur-[100px] opacity-20 rounded-full"></div>
              <div className="relative rounded-2xl overflow-hidden border border-neutral-200 shadow-2xl">
                <img src="https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&q=80&w=2664" alt="Agent Tools" className="w-full" />
              </div>
          </RevealOnScroll>
          <RevealOnScroll delay={200} className="lg:order-1">
              <h3 className="text-3xl font-bold mb-4">Equip Every Agent with Enterprise-Grade Marketing</h3>
              <p className="text-lg text-neutral-600 mb-6">Don't just hire agents—empower them. Provide a full marketing suite including landing pages, email automation, and social planners instantly upon onboarding.</p>
              <ul className="space-y-4">
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-purple-500" size={24} /></div> <span className="font-bold text-lg">Personalized Agent Sub-accounts</span></li>
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-purple-500" size={24} /></div> <span className="font-bold text-lg">One-Click Marketing Funnels</span></li>
                <li className="flex gap-3 items-center"><div data-cursor="magic" className="p-1"><CheckCircle2 className="text-purple-500" size={24} /></div> <span className="font-bold text-lg">Built-in Dialer & SMS</span></li>
              </ul>
          </RevealOnScroll>
        </div>
      </div>

      <RevealOnScroll>
        <div className="text-center mb-16 h-32 flex flex-col justify-center">
           <p className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-4">Powerful Capabilities</p>
           <h3 className="text-4xl md:text-6xl font-bold">
             <span className="text-neutral-400">You can </span>
             <TypewriterText 
                texts={[
                  "Automate Lead Follow-ups", 
                  "Track Agent Performance", 
                  "Launch Facebook Ads", 
                  "Collect 5-Star Reviews", 
                  "Build Custom Funnels",
                  "Send SMS Campaigns"
                ]} 
                className="text-black" 
             />
           </h3>
        </div>
      </RevealOnScroll>

      <div className="grid lg:grid-cols-3 gap-8 mb-20 items-start">
        {BROKER_CRM_PLANS.map((plan, i) => (
          <RevealOnScroll key={i} delay={i * 100} className="h-full">
            <div 
              className={`rounded-3xl p-8 border flex flex-col h-full transition-all duration-300 hover:shadow-2xl relative ${
                plan.recommended 
                  ? 'bg-black text-white border-black shadow-2xl scale-105 z-10' 
                  : 'bg-white/90 backdrop-blur-sm text-neutral-900 border-neutral-200 hover:-translate-y-2'
              }`}
            >
              {plan.recommended && (
                 <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold uppercase tracking-widest rounded-full shadow-lg">
                    Most Popular
                 </div>
              )}
              
              <div className="mb-8">
                <h3 className="text-xl font-bold mb-2 uppercase tracking-wide opacity-80">{plan.name}</h3>
                <div className="flex items-baseline gap-1">
                   <span className="text-5xl font-bold tracking-tight">{plan.price}</span>
                   <span className="text-sm opacity-60 font-medium">/month</span>
                </div>
                <p className="mt-4 text-sm opacity-70 leading-relaxed">{plan.description}</p>
                <div className="mt-2 text-xs font-bold uppercase tracking-widest opacity-50">Billed Monthly</div>
                <div className="text-[10px] font-medium opacity-50 mt-1">*Plus activation fee</div>
              </div>

              <div className="h-px bg-current opacity-10 mb-8" />
              
              <ul className="space-y-4 mb-10 flex-grow">
                {plan.features.map((f, idx) => {
                   const isHeader = f.startsWith('Everything in') || f.startsWith('Includes everything');
                   return (
                      <li key={idx} className={`flex items-start gap-3 ${isHeader ? 'font-bold mt-2 mb-2' : ''}`}>
                        {!isHeader && <Check size={16} className={`mt-0.5 shrink-0 ${plan.recommended ? 'text-white' : 'text-black'}`} />}
                        <span className="text-sm leading-relaxed">{f}</span>
                      </li>
                   );
                })}
              </ul>
              
              <button 
                onClick={() => {
                  if (plan.paymentLink && plan.paymentLink.startsWith('http')) {
                    openPaymentPopup(plan.paymentLink);
                  } else {
                    onSubscribe(plan);
                  }
                }}
                data-cursor="magic"
                className={`w-full py-4 rounded-xl font-bold transition-transform active:scale-95 shadow-lg ${
                  plan.recommended 
                    ? 'bg-white text-black hover:bg-neutral-200' 
                    : 'bg-black text-white hover:bg-neutral-800'
                }`}
              >
                Subscribe
              </button>
            </div>
          </RevealOnScroll>
        ))}
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
         {[
            { icon: <LayoutDashboard size={24} />, title: "Agent Dashboards", desc: "Individual logins and lead tracking for every agent." },
            { icon: <Smartphone size={24} />, title: "Mobile App", desc: "Manage leads, calls, and tasks on the go." },
            { icon: <Share2 size={24} />, title: "Social Planner", desc: "Plan, schedule and post content across all channels." },
            { icon: <Target size={24} />, title: "Ads Launcher", desc: "Launch Facebook & Google ads in 3 clicks with real-time analytics." },
            { icon: <Mail size={24} />, title: "Email Marketing", desc: "Drag-and-drop builder for newsletters and automated blasts." },
            { icon: <MessageCircle size={24} />, title: "SMS & WhatsApp", desc: "Direct 2-way messaging automated for higher response rates." },
            { icon: <Globe size={24} />, title: "Website Builder", desc: "High-converting landing pages and funnels for every listing." },
            { icon: <Calendar size={24} />, title: "Smart Calendars", desc: "Automated booking and round-robin scheduling for teams." },
            { icon: <Zap size={24} />, title: "Automations", desc: "Trigger actions based on lead behavior automatically." },
            { icon: <Users size={24} />, title: "Community Hub", desc: "Unified inbox for all your social interactions and DMs." },
            { icon: <Star size={24} />, title: "Reputation Mgmt", desc: "Auto-request reviews to boost Google ranking." },
            { icon: <CreditCard size={24} />, title: "Payments", desc: "Send invoices and collect payments seamlessly." },
            { icon: <Bot size={24} />, title: "AI Agents", desc: "24/7 intelligent assistants to qualify leads instantly." },
            { icon: <Phone size={24} />, title: "VoIP System", desc: "Dedicated business lines with call recording and tracking." },
            { icon: <Video size={24} />, title: "TikTok Ads", desc: "Sync leads directly from your viral video campaigns." },
            { icon: <FileText size={24} />, title: "Quickbooks", desc: "Seamless accounting integration for commissions." }
         ].map((feat, i) => (
            <RevealOnScroll key={i} delay={i * 50}>
               <div className="p-6 bg-neutral-50/80 backdrop-blur-sm rounded-2xl border border-neutral-100 text-center hover:bg-white hover:shadow-lg transition-all h-full">
                  <div className="w-12 h-12 mx-auto bg-white rounded-xl shadow-sm flex items-center justify-center mb-4 text-neutral-800">
                     {feat.icon}
                  </div>
                  <h4 className="font-bold mb-2">{feat.title}</h4>
                  <p className="text-sm text-neutral-500">{feat.desc}</p>
               </div>
            </RevealOnScroll>
         ))}
      </div>
      
      <CRMWorkflowVisualizer />

      <ConsultationCTA onBookConsultation={onBookConsultation} />
    </div>
  </div>
);

const SocialMediaView: React.FC<{ onInitiateGrowth: (plan: Plan) => void; onBookConsultation: () => void }> = ({ onInitiateGrowth, onBookConsultation }) => (
  <div className="animate-fade-in py-20 relative z-10">
    <div className="max-w-7xl mx-auto px-4">
      {/* New Intro Section */}
      <RevealOnScroll>
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-32">
           <div className="relative group">
              <SocialEcosystem />
           </div>
           
           <div className="lg:pl-8">
             <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-600 mb-6 block">The Core Engine</span>
             <h2 className="text-4xl md:text-5xl font-bold mb-8 leading-tight">
               Your Digital Storefront <br/>
               <span className="text-neutral-400">To The World.</span>
             </h2>
             <div className="space-y-6 text-lg text-neutral-600 leading-relaxed">
               <p>
                 We don't view social media as a side dish; we see it as the main course. It is the single most powerful engine to merge the <span className="text-black font-bold">personal</span> and <span className="text-black font-bold">professional</span> sides of your business and the people behind it.
               </p>
               <p>
                 In a digital-first world, your feed is your handshake. It works tirelessly as branding, top-of-mind awareness, relationship building, prospecting, and entertainment. By educating while you entertain, we build the one thing AI can't fake: <span className="text-black font-bold">Trust and Connection.</span>
               </p>
               <p>
                 Beyond human connection, high-quality social presence warms up the algorithms, maximizing ROI for every other marketing dollar you spend. It is the heartbeat of your growth.
               </p>
             </div>
             
             <div className="mt-10 grid grid-cols-2 gap-4">
                <div className="p-5 bg-neutral-50/80 backdrop-blur-sm rounded-2xl border border-neutral-100 hover:border-black transition-colors group">
                  <div className="mb-3 p-2 bg-white rounded-lg w-fit shadow-sm text-blue-600 group-hover:bg-black group-hover:text-white transition-colors">
                    <TrendingUp size={20} />
                  </div>
                  <h4 className="font-bold mb-1">Algorithm Warm-up</h4>
                  <p className="text-xs text-neutral-500">Consistent signals boost organic reach.</p>
                </div>
                <div className="p-5 bg-neutral-50/80 backdrop-blur-sm rounded-2xl border border-neutral-100 hover:border-black transition-colors group">
                  <div className="mb-3 p-2 bg-white rounded-lg w-fit shadow-sm text-purple-600 group-hover:bg-black group-hover:text-white transition-colors">
                    <Shield size={20} />
                  </div>
                  <h4 className="font-bold mb-1">Trust Architecture</h4>
                  <p className="text-xs text-neutral-500">Authenticity scales conversion.</p>
                </div>
             </div>
           </div>
        </div>
      </RevealOnScroll>

      <RevealOnScroll>
        <div className="mb-32">
          <div className="text-center mb-10">
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 mb-4 block">Cinematic Excellence</span>
            <h2 className="text-4xl font-bold mb-4">Content That Stops The Scroll</h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
              See what we've done for our clients
            </p>
          </div>
          <div className="rounded-[2.5rem] overflow-hidden shadow-2xl border border-neutral-100 bg-black">
             <div style={{padding:'56.25% 0 0 0', position:'relative'}}>
               <iframe src='https://vimeo.com/showcase/9806547/embed2' allow='autoplay; fullscreen; picture-in-picture; gyroscope; accelerometer; clipboard-write; encrypted-media; web-share' frameBorder='0' style={{position:'absolute', top:0, left:0, width:'100%', height:'100%'}} title="Marketingverse Video Showcase"></iframe>
             </div>
          </div>
        </div>
      </RevealOnScroll>

      <div className="text-center mb-16"><h2 className="text-4xl font-bold mb-4">Social Media Packages</h2></div>
      <div className="grid md:grid-cols-3 gap-8 mb-20">
        {SOCIAL_PLANS.map((plan, i) => (
          <div key={i} className={`rounded-3xl p-8 border flex flex-col transition-all duration-300 hover:shadow-2xl ${plan.recommended ? 'bg-black text-white border-black shadow-2xl scale-105' : 'bg-white/90 backdrop-blur-sm hover:-translate-y-2'}`}>
            <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
            <div className="text-4xl font-bold mb-6">{plan.price}<span className="text-sm opacity-50">/mo</span></div>
            <ul className="space-y-4 mb-8 flex-grow">
              {plan.features.map((f, idx) => <li key={idx} className="flex items-center gap-3"><Check size={14} /> <span className="text-sm">{f}</span></li>)}
            </ul>
            <button 
              onClick={() => {
                if (plan.paymentLink && plan.paymentLink.startsWith('http')) {
                  openPaymentPopup(plan.paymentLink);
                } else {
                  onInitiateGrowth(plan);
                }
              }} 
              data-cursor="magic"
              className={`w-full py-4 rounded-xl font-bold transition-transform active:scale-95 ${plan.recommended ? 'bg-white text-black hover:bg-neutral-100' : 'bg-black text-white hover:bg-neutral-800'}`}
            >
              Initiate Growth
            </button>
          </div>
        ))}
      </div>
      <ConsultationCTA onBookConsultation={onBookConsultation} />
    </div>
  </div>
);

const AIWorkflowsView: React.FC<{ onInitiateRequest: (plan: Plan) => void; onBookConsultation: () => void }> = ({ onInitiateRequest, onBookConsultation }) => (
  <div className="animate-fade-in py-20 relative z-10">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <RevealOnScroll>
        <div className="mb-16 text-center">
          <h2 className="text-4xl font-bold mb-4">AI Integration Workflows</h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto">Revolutionize your operations with our comprehensive suite of AI-powered integrations.</p>
        </div>
      </RevealOnScroll>
      
      <LiveAvatarDemo />

      <RevealOnScroll>
        <div className="mb-16">
           <h3 className="text-2xl font-bold mb-6 text-center uppercase tracking-widest text-neutral-400">Implementation Example</h3>
           <div className="rounded-3xl overflow-hidden shadow-lg border border-neutral-100 bg-black">
              <div style={{padding:'56.25% 0 0 0', position:'relative'}}>
                <iframe src="https://player.vimeo.com/video/1112989697?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479&amp;loop=1" frameBorder="0" allow="autoplay; fullscreen; picture-in-picture" style={{position:'absolute', top:0, left:0, width:'100%', height:'100%'}} title="AI Integration Example"></iframe>
              </div>
           </div>
        </div>
      </RevealOnScroll>
      <div className="py-20 border-b border-neutral-100 mb-16">
        <div className="text-center mb-10"><h3 className="text-2xl font-bold">Choose Your Integration Level</h3></div>
        <div className="grid md:grid-cols-3 gap-8 items-start">
          {AI_PLANS.map((plan, index) => (
            <RevealOnScroll key={index} delay={index * 150} className="h-full">
              <div data-cursor="card" className={`rounded-3xl p-8 border h-full transition-all duration-300 hover:shadow-2xl flex flex-col ${plan.recommended ? 'bg-black text-white border-black shadow-2xl scale-105' : 'bg-white/90 backdrop-blur-sm hover:-translate-y-2'}`}>
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className={`text-sm opacity-50`}>+ Development</span>}
                </div>
                <p className={`mb-8 leading-relaxed opacity-80`}>{plan.description}</p>
                <ul className="space-y-4 mb-8 flex-grow">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check size={14} className="mt-1" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button 
                  onClick={() => onInitiateRequest(plan)} 
                  data-cursor="magic"
                  className={`w-full py-4 rounded-xl font-bold transition-transform active:scale-95 ${plan.recommended ? 'bg-white text-black hover:bg-neutral-100' : 'bg-black text-white hover:bg-neutral-800'}`}
                >
                  Request Integration
                </button>
              </div>
            </RevealOnScroll>
          ))}
        </div>
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
         {AI_WORKFLOWS.map((category, index) => (
            <RevealOnScroll key={category.title} delay={index * 50} className="h-full">
              <div data-cursor="card" className="bg-neutral-50/80 backdrop-blur-sm rounded-3xl p-8 border border-neutral-100 hover:border-black hover:bg-white hover:shadow-xl hover:-translate-y-2 transition-all duration-300 h-full group">
                  <div className="flex items-center gap-4 mb-6">
                      <div className="p-3 bg-white text-black border border-neutral-100 rounded-xl group-hover:bg-black group-hover:text-white transition-colors duration-300">
                          <WorkflowIcon icon={category.icon} />
                      </div>
                      <h3 className="text-xl font-bold">{category.title}</h3>
                  </div>
                  <ul className="space-y-3">
                      {category.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-3 text-sm text-neutral-500">
                              <div className="w-1 h-1 bg-neutral-300 rounded-full mt-2 shrink-0" />
                              <span className="leading-relaxed">{item}</span>
                          </li>
                      ))}
                  </ul>
              </div>
            </RevealOnScroll>
         ))}
      </div>
      <WorkflowSimulator />
      <N8NWorkflowVisualizer />
      <CustomPlanBuilder onOrderNow={onBookConsultation} />
      <ConsultationCTA onBookConsultation={onBookConsultation} />
    </div>
  </div>
);

const BlogView: React.FC<{ blogs: BlogPost[]; onReadMore: (blog: BlogPost) => void }> = ({ blogs, onReadMore }) => (
  <div className="animate-fade-in py-20 relative z-10">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <RevealOnScroll>
        <div className="mb-16 text-center">
          <h2 className="text-5xl font-bold mb-4">The Verse Journal</h2>
          <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
            Insights, strategies, and futurist predictions from the Marketingverse team.
          </p>
        </div>
      </RevealOnScroll>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {blogs.map((blog, i) => (
          <RevealOnScroll key={blog.id} delay={i * 50}>
            <div 
              onClick={() => onReadMore(blog)}
              className="group cursor-pointer bg-white/80 backdrop-blur-sm rounded-3xl overflow-hidden border border-neutral-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 h-full flex flex-col"
            >
              <div className="aspect-[16/10] overflow-hidden relative">
                <img src={blog.imageUrl} alt={blog.title} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700" />
                <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                  {blog.category}
                </div>
              </div>
              <div className="p-8 flex flex-col flex-grow">
                <div className="flex items-center gap-2 text-xs text-neutral-400 mb-4 font-bold uppercase tracking-widest">
                  <span>{blog.date}</span>
                  <span>•</span>
                  <span>{blog.author}</span>
                </div>
                <h3 className="text-xl font-bold mb-3 group-hover:text-blue-600 transition-colors leading-tight">
                  {blog.title}
                </h3>
                <p className="text-neutral-600 text-sm leading-relaxed mb-6 line-clamp-3">
                  {blog.excerpt}
                </p>
                <div className="mt-auto flex items-center gap-2 text-sm font-bold text-black opacity-60 group-hover:opacity-100 transition-opacity">
                  Read Article <ArrowRight size={16} />
                </div>
              </div>
            </div>
          </RevealOnScroll>
        ))}
      </div>
    </div>
  </div>
);

const ContactView: React.FC = () => {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const body = `Name: ${formData.name}%0D%0AEmail: ${formData.email}%0D%0ASubject: ${formData.subject}%0D%0AMessage: ${formData.message}`;
    window.location.href = `mailto:rkorda@the-marketingverse.com?subject=Contact Form: ${formData.subject}&body=${body}`;
    setSubmitted(true);
  };

  return (
    <div className="animate-fade-in py-20 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <RevealOnScroll>
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-6">Let's Build Something Great.</h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
              Whether you have a question about our services, pricing, or just want to talk strategy, we're here to help.
            </p>
          </div>
        </RevealOnScroll>

        <div className="grid lg:grid-cols-2 gap-16 items-start">
          <RevealOnScroll delay={100}>
            <div className="bg-white/80 backdrop-blur-md p-10 rounded-[2.5rem] border border-neutral-100 shadow-xl">
              <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">
                <MessageSquare className="text-blue-600" /> Send a Message
              </h3>
              {submitted ? (
                <div className="bg-green-50 text-green-800 p-8 rounded-2xl text-center">
                  <CheckCircle2 size={48} className="mx-auto mb-4" />
                  <h4 className="text-xl font-bold mb-2">Message Sent!</h4>
                  <p>We'll get back to you within 24 hours.</p>
                  <button onClick={() => setSubmitted(false)} className="mt-6 text-sm font-bold underline">Send another</button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-widest text-neutral-500">Name</label>
                      <input 
                        required 
                        type="text" 
                        value={formData.name}
                        onChange={e => setFormData({...formData, name: e.target.value})}
                        className="w-full p-4 bg-white rounded-xl border border-neutral-200 focus:ring-2 focus:ring-black focus:outline-none transition-all"
                        placeholder="John Doe" 
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-widest text-neutral-500">Email</label>
                      <input 
                        required 
                        type="email" 
                        value={formData.email}
                        onChange={e => setFormData({...formData, email: e.target.value})}
                        className="w-full p-4 bg-white rounded-xl border border-neutral-200 focus:ring-2 focus:ring-black focus:outline-none transition-all"
                        placeholder="john@example.com" 
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-neutral-500">Subject</label>
                    <input 
                      required 
                      type="text" 
                      value={formData.subject}
                      onChange={e => setFormData({...formData, subject: e.target.value})}
                      className="w-full p-4 bg-white rounded-xl border border-neutral-200 focus:ring-2 focus:ring-black focus:outline-none transition-all"
                      placeholder="Project Inquiry..." 
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-neutral-500">Message</label>
                    <textarea 
                      required 
                      value={formData.message}
                      onChange={e => setFormData({...formData, message: e.target.value})}
                      className="w-full p-4 bg-white rounded-xl border border-neutral-200 focus:ring-2 focus:ring-black focus:outline-none transition-all h-40 resize-none"
                      placeholder="Tell us about your project..." 
                    />
                  </div>
                  <button 
                    type="submit" 
                    data-cursor="magic"
                    className="w-full py-5 bg-black text-white rounded-xl font-bold text-lg hover:bg-neutral-800 transition-all flex items-center justify-center gap-2 shadow-lg hover:scale-[1.02]"
                  >
                    Send Message <ArrowRight size={20} />
                  </button>
                </form>
              )}
            </div>
          </RevealOnScroll>

          <RevealOnScroll delay={200}>
            <div className="space-y-10">
              <div className="bg-neutral-900 text-white p-10 rounded-[2.5rem] shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2" />
                <div className="relative z-10">
                  <h3 className="text-2xl font-bold mb-6">Contact Information</h3>
                  <div className="space-y-8">
                    <a href="mailto:rkorda@the-marketingverse.com" className="flex items-center gap-6 group/item cursor-pointer hover:opacity-80 transition-opacity">
                      <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center group-hover/item:bg-white group-hover/item:text-black transition-colors shrink-0">
                        <Mail size={20} />
                      </div>
                      <div>
                        <p className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-1">Email Us</p>
                        <p className="text-xl font-bold break-all">rkorda@the-marketingverse.com</p>
                      </div>
                    </a>
                    <a href="https://maps.google.com/?q=8400+NW+33rd+St+Suite+104+Doral+FL+33122" target="_blank" rel="noopener noreferrer" className="flex items-center gap-6 group/item cursor-pointer hover:opacity-80 transition-opacity">
                      <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center group-hover/item:bg-white group-hover/item:text-black transition-colors shrink-0">
                        <MapPin size={20} />
                      </div>
                      <div>
                        <p className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-1">HQ Location</p>
                        <p className="text-xl font-bold leading-tight">8400 NW 33rd. St, Suite 104,<br/> Doral, FL 33122, United States</p>
                      </div>
                    </a>
                    <a href="tel:+17867053154" className="flex items-center gap-6 group/item cursor-pointer hover:opacity-80 transition-opacity">
                      <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center group-hover/item:bg-white group-hover/item:text-black transition-colors shrink-0">
                        <Phone size={20} />
                      </div>
                      <div>
                        <p className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-1">Support</p>
                        <p className="text-xl font-bold">+1 (786) 705-3154</p>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/60 backdrop-blur-sm p-8 rounded-3xl border border-neutral-100">
                <h4 className="font-bold text-lg mb-4">Connect on Social</h4>
                <div className="flex gap-4">
                  {[
                    { icon: <Instagram size={20} />, label: "Instagram" },
                    { icon: <Linkedin size={20} />, label: "LinkedIn" },
                    { icon: <Twitter size={20} />, label: "Twitter/X" },
                    { icon: <Youtube size={20} />, label: "YouTube" }
                  ].map((social, i) => (
                    <button key={i} className="flex-1 py-4 bg-white border border-neutral-200 rounded-xl flex items-center justify-center hover:bg-black hover:text-white hover:border-black transition-all group">
                      {social.icon}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </RevealOnScroll>
        </div>
        
        <RevealOnScroll delay={300}>
           <div className="mt-16 rounded-[2.5rem] overflow-hidden shadow-2xl border border-neutral-200 h-[450px] relative w-full">
              <iframe 
                src="https://maps.google.com/maps?q=8400%20NW%2033rd%20St%20Suite%20104%20Doral%20FL%2033122&t=&z=15&ie=UTF8&iwloc=&output=embed" 
                width="100%" 
                height="100%" 
                style={{border:0}} 
                allowFullScreen={true} 
                loading="lazy" 
                referrerPolicy="no-referrer-when-downgrade"
                title="Marketingverse HQ Map"
              ></iframe>
           </div>
        </RevealOnScroll>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [view, setView] = useState('home');
  const [isBookingOpen, setIsBookingOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [selectedBlog, setSelectedBlog] = useState<BlogPost | null>(null);
  const [projects, setProjects] = useState<Project[]>(() => {
    try {
      const saved = localStorage.getItem('mverse_projects');
      return saved ? JSON.parse(saved) : INITIAL_PROJECTS;
    } catch (e) {
      return INITIAL_PROJECTS;
    }
  });

  useEffect(() => {
    window.scrollTo(0, 0);
    if (view !== 'blog') {
      setSelectedBlog(null);
    }
  }, [view]);

  // Scroll to top when opening a blog post
  useEffect(() => {
    if (selectedBlog) {
      window.scrollTo(0, 0);
    }
  }, [selectedBlog]);

  const renderView = () => {
    switch (view) {
      case 'home':
        return <HomeView changeView={setView} onBookConsultation={() => setIsBookingOpen(true)} />;
      case 'contact':
        return <ContactView />;
      case 'social':
        return <SocialMediaView onInitiateGrowth={() => setIsBookingOpen(true)} onBookConsultation={() => setIsBookingOpen(true)} />;
      case 'crm':
        return <BrokerCRMView onSubscribe={() => setIsBookingOpen(true)} onBookConsultation={() => setIsBookingOpen(true)} />;
      case 'integrations':
        return <AIWorkflowsView onInitiateRequest={() => setIsBookingOpen(true)} onBookConsultation={() => setIsBookingOpen(true)} />;
      case 'blog':
        if (selectedBlog) {
          return (
            <div className="animate-fade-in relative z-10 pt-32 pb-24">
               <div className="max-w-3xl mx-auto px-4">
                  <button onClick={() => setSelectedBlog(null)} className="mb-8 flex items-center gap-2 text-sm font-bold text-neutral-500 hover:text-black transition-colors group">
                    <ChevronLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> Back to Articles
                  </button>
                  
                  <div className="mb-8 rounded-3xl overflow-hidden aspect-video shadow-lg">
                     <img src={selectedBlog.imageUrl} alt={selectedBlog.title} className="w-full h-full object-cover" />
                  </div>
                  
                  <div className="flex items-center gap-3 text-xs md:text-sm text-neutral-500 mb-6 font-bold uppercase tracking-widest">
                     <span>{selectedBlog.date}</span>
                     <span className="w-1 h-1 bg-neutral-300 rounded-full" />
                     <span>{selectedBlog.category}</span>
                     <span className="w-1 h-1 bg-neutral-300 rounded-full" />
                     <span>{selectedBlog.author}</span>
                  </div>
                  
                  <h1 className="text-3xl md:text-5xl font-bold mb-10 leading-tight">{selectedBlog.title}</h1>
                  
                  <div className="prose prose-lg text-neutral-600 leading-relaxed whitespace-pre-line mb-16">
                     {selectedBlog.content}
                  </div>
                  
                  <div className="bg-neutral-50 rounded-[2.5rem] p-8 md:p-12 border border-neutral-200">
                     <h3 className="text-2xl font-bold mb-6">Have questions about this strategy?</h3>
                     <p className="text-neutral-600 mb-8">Our AI agent has read this article and can answer questions or help you implement these ideas.</p>
                     <AIBot context={`Article Title: ${selectedBlog.title}\n\nArticle Content:\n${selectedBlog.content}`} initialMessage="I've analyzed this article. What would you like to know about applying this strategy?" />
                  </div>
               </div>
            </div>
          );
        }
        return (
           <div className="animate-fade-in relative z-10 pt-32 pb-24">
              <div className="max-w-4xl mx-auto px-4">
                 <div className="text-center mb-20">
                   <h2 className="text-5xl font-bold mb-6">Marketing Intelligence</h2>
                   <p className="text-xl text-neutral-600">Insights, trends, and strategies from the Marketingverse team.</p>
                 </div>
                 <div className="space-y-16">
                   {INITIAL_BLOGS.map((blog) => (
                     <article 
                        key={blog.id} 
                        onClick={() => setSelectedBlog(blog)}
                        className="group cursor-pointer"
                     >
                        <div className="aspect-[2/1] rounded-3xl overflow-hidden mb-8 border border-neutral-200 shadow-sm relative">
                           <img src={blog.imageUrl} alt={blog.title} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700" />
                           <div className="absolute top-6 left-6 bg-white/90 backdrop-blur-md px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest">{blog.category}</div>
                        </div>
                        <div className="max-w-3xl mx-auto">
                           <div className="flex items-center gap-3 text-sm text-neutral-500 mb-4">
                             <span>{blog.date}</span>
                             <span className="w-1 h-1 bg-neutral-300 rounded-full" />
                             <span>{blog.author}</span>
                           </div>
                           <h3 className="text-3xl font-bold mb-4 group-hover:text-blue-600 transition-colors">{blog.title}</h3>
                           <p className="text-neutral-600 leading-relaxed mb-6 text-lg">{blog.excerpt}</p>
                           <div className="flex items-center text-sm font-bold border-b border-black pb-1 w-fit group-hover:border-blue-600 group-hover:text-blue-600 transition-colors">
                             Read Full Article <ArrowRight size={16} className="ml-2" />
                           </div>
                        </div>
                     </article>
                   ))}
                 </div>
              </div>
           </div>
        );
      case 'projects':
        return (
           <div className="animate-fade-in relative z-10 pt-32 pb-24">
              <div className="max-w-7xl mx-auto px-4">
                 <div className="text-center mb-20">
                   <h2 className="text-5xl font-bold mb-6">Featured Work</h2>
                   <p className="text-xl text-neutral-600 max-w-2xl mx-auto">See how we've helped brands scale through content and automation.</p>
                 </div>
                 <div className="mb-20 rounded-[2.5rem] overflow-hidden shadow-2xl border border-neutral-200 bg-black">
                    <div style={{padding:'56.25% 0 0 0', position:'relative'}}>
                      <iframe src='https://vimeo.com/showcase/9806547/embed2' allow='autoplay; fullscreen; picture-in-picture; gyroscope; accelerometer; clipboard-write; encrypted-media; web-share' frameBorder='0' style={{position:'absolute',top:0,left:0,width:'100%',height:'100%'}} title="Marketingverse Project Showcase"></iframe>
                    </div>
                 </div>
                 <div className="grid md:grid-cols-2 gap-10">
                   {projects.map((p) => (
                     <ProjectCard key={p.id} project={p} />
                   ))}
                 </div>
              </div>
           </div>
        );
      default:
        return <HomeView changeView={setView} onBookConsultation={() => setIsBookingOpen(true)} />;
    }
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans selection:bg-black selection:text-white overflow-x-hidden">
      <CustomCursor />
      <AbstractBackground />
      <NavBar active={view} setView={setView} onBookConsultation={() => setIsBookingOpen(true)} />
      
      <main className="relative z-10 min-h-screen">
        {renderView()}
      </main>

      <Footer onOpenAdmin={() => setIsAdminOpen(true)} />
      
      <BackToTop />
      <BookingModal isOpen={isBookingOpen} onClose={() => setIsBookingOpen(false)} />
      {isAdminOpen && <AdminPortal projects={projects} setProjects={setProjects} onClose={() => setIsAdminOpen(false)} />}
    </div>
  );
};

export default App;