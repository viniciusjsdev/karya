import { useCallback, useMemo, useState } from 'react'
import { ExternalLink, Maximize2 } from 'lucide-react'
import {
  Background,
  Controls,
  Handle,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { architectureEdges, architectureItems } from '../content/karya'

type ArchitectureData = { label: string; kind: string }

function StructuralNode({ data, selected }: NodeProps<Node<ArchitectureData>>) {
  return (
    <div className={`architecture-node ${data.kind}`} data-selected={selected} tabIndex={0}>
      <Handle type="target" position={Position.Top} />
      <span>{data.kind}</span>
      <strong>{data.label}</strong>
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}

function FitButton() {
  const { fitView } = useReactFlow()
  return (
    <button className="fit-button" type="button" onClick={() => void fitView({ padding: 0.2 })}>
      <Maximize2 size={16} />
      Reset view
    </button>
  )
}

function ArchitectureCanvas() {
  const [selectedId, setSelectedId] = useState('karya')
  const selected =
    architectureItems.find((item) => item.id === selectedId) ?? architectureItems.at(-1)!
  const nodes = useMemo<Node<ArchitectureData>[]>(
    () =>
      architectureItems.map((item) => ({
        id: item.id,
        type: 'structural',
        position: { x: item.x, y: item.y },
        data: { label: item.label, kind: item.kind },
      })),
    [],
  )
  const edges = useMemo<Edge[]>(
    () =>
      architectureEdges.map(([source, target], index) => ({
        id: `e-${index}`,
        source,
        target,
        animated: false,
        style: { stroke: 'var(--line-strong)', strokeWidth: 1.5 },
      })),
    [],
  )
  const nodeTypes = useMemo(() => ({ structural: StructuralNode }), [])
  const onNodeClick = useCallback((_: unknown, node: Node) => setSelectedId(node.id), [])

  return (
    <div className="architecture-layout">
      <div
        className="architecture-canvas"
        aria-label="Interactive graph connecting Project, Knowledge, Specs, Skills, Threads, Runtime, and Karya"
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodeClick={onNodeClick}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.55}
          maxZoom={1.5}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable
        >
          <Background color="var(--line)" gap={28} size={1} />
          <Controls showInteractive={false} />
          <FitButton />
        </ReactFlow>
      </div>
      <aside className="detail-panel architecture-detail" aria-live="polite">
        <span className="eyebrow">{selected.label}</span>
        <h3>{selected.what}</h3>
        <dl>
          <div>
            <dt>Why it exists</dt>
            <dd>{selected.why}</dd>
          </div>
          <div>
            <dt>What it contains</dt>
            <dd>{selected.contains}</dd>
          </div>
          <div>
            <dt>What it is not</dt>
            <dd>{selected.not}</dd>
          </div>
        </dl>
        <a href={selected.href} target="_blank" rel="noreferrer">
          Related documentation <ExternalLink size={14} />
        </a>
      </aside>
    </div>
  )
}

export default function ArchitectureDiagram() {
  return (
    <ReactFlowProvider>
      <ArchitectureCanvas />
    </ReactFlowProvider>
  )
}
