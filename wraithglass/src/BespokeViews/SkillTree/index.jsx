import React, { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { ReactFlow, Controls, Background, useNodesState, useEdgesState, addEdge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Settings, Server, Command, Cpu, BrainCircuit, Globe, Zap, Database, Lock } from 'lucide-react';

// Custom Node for Luxury / Apple-like styling
const CustomNode = ({ data }) => {
  return (
    <div style={{
      padding: '16px 24px',
      borderRadius: '24px',
      background: 'rgba(25, 25, 30, 0.65)',
      backdropFilter: 'blur(24px) saturate(180%)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)',
      color: '#fff',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      minWidth: '220px',
      transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
      cursor: 'pointer'
    }} className="hover:scale-[1.02] hover:bg-white/10 group">
      <div style={{
        width: '44px', height: '44px', borderRadius: '14px',
        background: `linear-gradient(135deg, ${data.color1 || '#3B82F6'}, ${data.color2 || '#8B5CF6'})`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
      }}>
        {data.icon}
      </div>
      <div>
        <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 600, fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em', color: '#fff' }}>
          {data.label}
        </h4>
        <p style={{ margin: 0, fontSize: '12px', fontWeight: 400, fontFamily: 'Inter, sans-serif', color: 'rgba(255,255,255,0.5)', marginTop: '2px' }}>
          {data.desc}
        </p>
      </div>
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

const initialNodes = [
  { id: '1', type: 'custom', position: { x: 400, y: 100 }, data: { label: 'Wraithglass Core', desc: 'Neural Kernel engine', icon: <BrainCircuit size={20} color="#fff" />, color1: '#10B981', color2: '#059669' } },
  { id: '2', type: 'custom', position: { x: 200, y: 250 }, data: { label: 'Desktop OS Hook', desc: 'ctypes Windows API', icon: <Server size={20} color="#fff" />, color1: '#6366f1', color2: '#4f46e5' } },
  { id: '3', type: 'custom', position: { x: 600, y: 250 }, data: { label: 'Local Memory', desc: 'AES-256 Encrypted Bin', icon: <Database size={20} color="#fff" />, color1: '#f59e0b', color2: '#d97706' } },
  { id: '4', type: 'custom', position: { x: 400, y: 400 }, data: { label: 'Automated Actions', desc: 'PyAutoGUI Scripts', icon: <Zap size={20} color="#fff" />, color1: '#ef4444', color2: '#dc2626' } },
  { id: '5', type: 'custom', position: { x: 100, y: 400 }, data: { label: 'Command Shell', desc: 'PowerShell/CMD execution', icon: <Command size={20} color="#fff" />, color1: '#8b5cf6', color2: '#7c3aed' } },
  { id: '6', type: 'custom', position: { x: 700, y: 400 }, data: { label: 'Web Scraper', desc: 'Browser automation', icon: <Globe size={20} color="#fff" />, color1: '#ec4899', color2: '#db2777' } },
  { id: '7', type: 'custom', position: { x: 400, y: 550 }, data: { label: 'Offline Standby', desc: 'Failsafe caching queue', icon: <Lock size={20} color="#fff" />, color1: '#64748b', color2: '#475569' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
  { id: 'e1-3', source: '1', target: '3', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
  { id: 'e1-4', source: '1', target: '4', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
  { id: 'e2-5', source: '2', target: '5', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
  { id: 'e3-6', source: '3', target: '6', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
  { id: 'e4-7', source: '4', target: '7', type: 'smoothstep', animated: true, style: { stroke: 'rgba(255,255,255,0.4)', strokeWidth: 2 } },
];

export default function SkillTree({ isConnected }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: 'rgba(255,255,255,0.6)', strokeWidth: 2 } }, eds)),
    [setEdges],
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="w-full h-full relative flex flex-col"
    >
      <div className="absolute top-8 left-8 z-20 pointer-events-none">
        <h1 className="text-4xl font-bold tracking-tight text-white/90 drop-shadow-xl" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.03em' }}>
          Skill Tree
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-sm" style={{ fontFamily: 'Inter, sans-serif' }}>
          Drag, drop, and connect neural pathways to customize your VESPERA OS capabilities. Changes reflect in real-time.
        </p>
      </div>

      <div className="flex-1 w-full h-full bg-black/10 rounded-tl-3xl border-t border-l border-white/5 overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="dark"
        >
          <Background color="rgba(255,255,255,0.05)" gap={24} size={2} />
          <Controls className="opacity-40 hover:opacity-100 transition-opacity" style={{ 
            background: 'rgba(0,0,0,0.5)', 
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            overflow: 'hidden'
          }} />
        </ReactFlow>
      </div>
    </motion.div>
  );
}
