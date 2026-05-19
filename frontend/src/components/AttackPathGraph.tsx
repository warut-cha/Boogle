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

const getNodeColor = (type: AttackPathNodeType): string => {
  switch (type) {
    case 'secret': return '#f85149';
    case 'api': return '#ff7b72';
    case 'runtime': return '#d29922';
    case 'database': return '#a371f7';
    case 'infrastructure': return '#58a6ff';
    case 'impact': return '#f85149';
    default: return '#8b949e';
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
  // Convert attack path to ReactFlow format
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
              fontSize: '0.75rem',
              color: '#8b949e',
              textTransform: 'uppercase'
            }}>
              {node.type}
            </div>
          </div>
        ),
      },
      style: {
        background: '#161b22',
        border: `2px solid ${getNodeColor(node.type)}`,
        borderRadius: '12px',
        padding: '1rem',
        width: 200,
        color: '#e6edf3',
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
      style: { stroke: '#58a6ff', strokeWidth: 2 },
      labelStyle: {
        fill: '#e6edf3',
        fontSize: '0.75rem',
        fontWeight: 600,
      },
      labelBgStyle: {
        fill: '#161b22',
        fillOpacity: 0.9,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#58a6ff',
      },
    }));
  }, [attackPath.edges]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  if (attackPath.nodes.length === 0) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
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
      backgroundColor: '#161b22',
      border: '1px solid #30363d',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid #30363d'
      }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
          Attack Path Visualization
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#8b949e', margin: '0.5rem 0 0 0' }}>
          Correlated security signals showing the attack chain
        </p>
      </div>
      
      <div style={{ height: '600px', backgroundColor: '#0d1117' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          attributionPosition="bottom-left"
        >
          <Background color="#30363d" gap={16} />
          <Controls style={{ backgroundColor: '#161b22', color: '#e6edf3', border: '1px solid #30363d' } as any} />
          <MiniMap
            style={{
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
            }}
            nodeColor={(node) => {
              const pathNode = attackPath.nodes.find(n => n.id === node.id);
              return pathNode ? getNodeColor(pathNode.type) : '#8b949e';
            }}
          />
        </ReactFlow>
      </div>

      <div style={{
        padding: '1rem 1.5rem',
        borderTop: '1px solid #30363d',
        backgroundColor: '#0d1117'
      }}>
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('secret')
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Secret Exposure</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('api')
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>API Vulnerability</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('runtime')
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Runtime Anomaly</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('database')
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Database Activity</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: getNodeColor('impact')
            }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>Security Impact</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
