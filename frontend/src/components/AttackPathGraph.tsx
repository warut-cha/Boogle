import { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { AttackPath, AttackPathNodeType } from '../api/types';

interface AttackPathGraphProps {
  attackPath: AttackPath;
}

// Modern neon color scheme for attack paths
const getNodeColor = (type: AttackPathNodeType): string => {
  switch (type) {
    case 'secret': return '#ff0040';
    case 'api': return '#ff6b35';
    case 'runtime': return '#ffd700';
    case 'database': return '#a371f7';
    case 'infrastructure': return '#00bfff';
    case 'impact': return '#ff0040';
    default: return '#6c757d';
  }
};

const getNodeIcon = (type: AttackPathNodeType): string => {
  switch (type) {
    case 'secret': return '🔑';
    case 'api': return '🌐';
    case 'runtime': return '⚡';
    case 'database': return '🗄️';
    case 'infrastructure': return '🏗️';
    case 'impact': return '💥';
    default: return '⚠️';
  }
};

export default function AttackPathGraph({ attackPath }: AttackPathGraphProps) {
  // Convert attack path to ReactFlow format with modern styling
  const initialNodes: Node[] = useMemo(() => {
    return attackPath.nodes.map((node, index) => ({
      id: node.id,
      type: 'default',
      position: { x: 250, y: index * 150 },
      data: {
        label: (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem'
          }}>
            <div style={{ fontSize: '1.5rem' }}>
              {getNodeIcon(node.type)}
            </div>
            <div style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              textAlign: 'center',
              color: '#e6edf3'
            }}>
              {node.label}
            </div>
            <div style={{
              fontSize: '0.7rem',
              color: getNodeColor(node.type),
              textTransform: 'uppercase',
              fontWeight: 600,
              letterSpacing: '0.5px',
            }}>
              {node.type}
            </div>
          </div>
        ),
      },
      style: {
        background: 'rgba(15, 20, 35, 0.9)',
        backdropFilter: 'blur(10px)',
        border: `2px solid ${getNodeColor(node.type)}`,
        borderRadius: '12px',
        padding: '1rem',
        width: 200,
        color: '#e6edf3',
        boxShadow: `0 4px 20px ${getNodeColor(node.type)}40, 0 0 40px ${getNodeColor(node.type)}20`,
      },
    }));
  }, [attackPath.nodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return attackPath.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.from,
      target: edge.to,
      label: edge.label,
      type: 'smoothstep',
      animated: true,
      style: { 
        stroke: '#ff0040', 
        strokeWidth: 3,
        filter: 'drop-shadow(0 0 8px #ff004080)',
      },
      labelStyle: {
        fill: '#e6edf3',
        fontSize: '0.75rem',
        fontWeight: 600,
      },
      labelBgStyle: {
        fill: 'rgba(15, 20, 35, 0.95)',
        fillOpacity: 1,
        rx: 4,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#ff0040',
      },
    }));
  }, [attackPath.edges]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  if (attackPath.nodes.length === 0) {
    return (
      <div style={{
        background: 'rgba(15, 20, 35, 0.7)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(0, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '2rem',
        textAlign: 'center',
        color: '#8b949e'
      }}>
        No attack path data available
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(15, 20, 35, 0.7)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(0, 255, 255, 0.1)',
      borderRadius: '12px',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    }}>
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        background: 'rgba(0, 0, 0, 0.2)',
      }}>
        <h2 style={{ 
          fontSize: '1.125rem', 
          fontWeight: 600, 
          color: '#e6edf3', 
          margin: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <span style={{ color: '#ff0040' }}>🎯</span>
          Attack Path Visualization
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#8b949e', margin: '0.5rem 0 0 0' }}>
          Correlated security signals showing the attack chain
        </p>
      </div>
      
      <div style={{ 
        height: '600px', 
        background: 'linear-gradient(135deg, rgba(10, 14, 39, 0.8) 0%, rgba(26, 31, 58, 0.8) 100%)',
      }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          attributionPosition="bottom-left"
        >
          <Background 
            color="rgba(0, 255, 255, 0.1)" 
            gap={20} 
            style={{ 
              background: 'transparent',
            }}
          />
          <Controls 
            style={{ 
              background: 'rgba(15, 20, 35, 0.9)',
              backdropFilter: 'blur(10px)',
              color: '#e6edf3', 
              border: '1px solid rgba(0, 255, 255, 0.2)',
              borderRadius: '8px',
            } as any} 
          />
          <MiniMap
            style={{
              background: 'rgba(15, 20, 35, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0, 255, 255, 0.2)',
              borderRadius: '8px',
            }}
            nodeColor={(node) => {
              const pathNode = attackPath.nodes.find(n => n.id === node.id);
              return pathNode ? getNodeColor(pathNode.type) : '#6c757d';
            }}
          />
        </ReactFlow>
      </div>

      <div style={{
        padding: '1rem 1.5rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        background: 'rgba(0, 0, 0, 0.2)',
      }}>
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('secret'),
              boxShadow: `0 0 10px ${getNodeColor('secret')}80`,
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Secret Exposure</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('api'),
              boxShadow: `0 0 10px ${getNodeColor('api')}80`,
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>API Vulnerability</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('runtime'),
              boxShadow: `0 0 10px ${getNodeColor('runtime')}80`,
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Runtime Anomaly</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('database'),
              boxShadow: `0 0 10px ${getNodeColor('database')}80`,
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Database Activity</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('impact'),
              boxShadow: `0 0 10px ${getNodeColor('impact')}80`,
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Security Impact</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
