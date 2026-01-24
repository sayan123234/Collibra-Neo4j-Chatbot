import React, { useCallback, useEffect, useState, useMemo } from 'react';
import {
    ReactFlow,
    useNodesState,
    useEdgesState,
    addEdge,
    Controls,
    Background,
    MiniMap,
    MarkerType,
    useReactFlow,
    ReactFlowProvider
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { chatService } from '../api/client';
import CustomNode from './lineage/CustomNode';
import {
    Loader2, RefreshCw, X, Database, Info,
    Wand2, Maximize, MousePointer2, Layers
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const nodeTypes = {
    custom: CustomNode,
};

const formatLabel = (str) => {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Dagre Layout Calculation
const getLayoutedElements = (nodes, edges, direction = 'LR') => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    const nodeWidth = 260;
    const nodeHeight = 100;

    dagreGraph.setGraph({
        rankdir: direction,
        nodesep: 80,
        ranksep: 180,
        ranker: 'network-simplex'
    });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    const layoutedNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
            ...node,
            targetPosition: 'left',
            sourcePosition: 'right',
            position: {
                x: nodeWithPosition.x - nodeWidth / 2,
                y: nodeWithPosition.y - nodeHeight / 2,
            },
        };
    });

    return { nodes: layoutedNodes, edges };
};

const LineageContent = () => {
    const { fitView } = useReactFlow();
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);
    const [selectedNodeData, setSelectedNodeData] = useState(null);
    const [hoveredNode, setHoveredNode] = useState(null);

    const fetchLineage = async () => {
        setLoading(true);
        try {
            const data = await chatService.getLineage();

            const flowNodes = data.nodes.map(n => ({
                id: n.id,
                type: 'custom',
                data: { label: n.label, group: n.group, properties: n.properties },
                position: { x: 0, y: 0 }
            }));

            const flowEdges = data.links.map((l, i) => ({
                id: `e${l.source}-${l.target}-${i}`,
                source: l.source,
                target: l.target,
                label: formatLabel(l.type),
                type: 'step',
                animated: true,
                style: { stroke: '#6366f1', strokeWidth: 2, opacity: 0.6 },
                labelStyle: { fill: '#6366f1', fontWeight: 600, fontSize: 8, opacity: 0.8 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: '#6366f1',
                    width: 20,
                    height: 20
                },
            }));

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                flowNodes,
                flowEdges
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
            setTimeout(() => fitView({ padding: 0.2 }), 100);
        } catch (error) {
            console.error("Failed to fetch lineage:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLineage();
    }, []);

    // Path Highlighting Logic
    const highlightedEdges = useMemo(() => {
        if (!hoveredNode && !selectedNodeData) return new Set();
        const focusId = hoveredNode || selectedNodeData?.id;
        const connected = new Set();

        // Simple upstream/downstream check
        edges.forEach(edge => {
            if (edge.source === focusId || edge.target === focusId) {
                connected.add(edge.id);
            }
        });
        return connected;
    }, [hoveredNode, selectedNodeData, edges]);

    const onNodeClick = (event, node) => {
        setSelectedNodeData({ ...node.data, id: node.id });
    };

    const onPaneClick = () => {
        setSelectedNodeData(null);
    };

    return (
        <div className="h-full w-full bg-slate-50 dark:bg-slate-950 relative flex flex-col">
            {/* Top Controls Overlay */}
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
                <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-1.5 rounded-xl shadow-lg border border-slate-200 dark:border-slate-800 flex items-center gap-1">
                    <button
                        onClick={fetchLineage}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-300 transition-all flex items-center gap-2 text-xs font-semibold"
                        title="Refresh & Relayout"
                    >
                        <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                    </button>
                    <div className="w-px h-4 bg-slate-200 dark:bg-slate-700 mx-1" />
                    <button
                        onClick={() => fitView({ duration: 800 })}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-300 transition-all"
                        title="Fit to Screen"
                    >
                        <Maximize size={14} />
                    </button>
                </div>

                {/* Legend */}
                <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-3 rounded-xl shadow-lg border border-slate-200 dark:border-slate-800 flex flex-col gap-2 min-w-[140px]">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mb-1">Legend</div>
                    <div className="space-y-1.5">
                        {[
                            { label: 'Table', color: 'bg-emerald-500' },
                            { label: 'Column', color: 'bg-sky-500' },
                            { label: 'Business Asset', color: 'bg-amber-500' },
                            { label: 'User', color: 'bg-orange-500' }
                        ].map(item => (
                            <div key={item.label} className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${item.color}`} />
                                <span className="text-[10px] text-slate-600 dark:text-slate-400 font-medium">{item.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="flex-1 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4 text-slate-400">
                        <div className="relative">
                            <Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
                            <Wand2 className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-indigo-400" />
                        </div>
                        <p className="text-sm font-medium animate-pulse">Orchestrating Traceability...</p>
                    </div>
                </div>
            ) : (
                <div className="flex-1 h-full w-full">
                    <ReactFlow
                        nodes={nodes.map(n => ({
                            ...n,
                            data: { ...n.data, isHighlighted: highlightedEdges.size > 0 && Array.from(highlightedEdges).some(eid => eid.includes(n.id)) }
                        }))}
                        edges={edges.map(e => ({
                            ...e,
                            animated: highlightedEdges.has(e.id),
                            style: {
                                ...e.style,
                                stroke: highlightedEdges.has(e.id) ? '#6366f1' : '#cbd5e1',
                                strokeWidth: highlightedEdges.has(e.id) ? 3 : 2,
                                opacity: highlightedEdges.size > 0 && !highlightedEdges.has(e.id) ? 0.2 : 0.6
                            }
                        }))}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onNodeClick={onNodeClick}
                        onPaneClick={onPaneClick}
                        onNodeMouseEnter={(_, node) => setHoveredNode(node.id)}
                        onNodeMouseLeave={() => setHoveredNode(null)}
                        nodeTypes={nodeTypes}
                        fitView
                        attributionPosition="bottom-left"
                        minZoom={0.05}
                        maxZoom={2}
                    >
                        <Background color="#94a3b8" gap={20} size={1} />
                        <Controls position="bottom-right" className="!shadow-xl !border-none !rounded-xl overflow-hidden" />
                        <MiniMap
                            style={{ height: 120, width: 200 }}
                            className="!bg-white dark:!bg-slate-900 !rounded-xl !border !border-slate-200 dark:!border-slate-800 !shadow-lg"
                            nodeStrokeColor={(n) => '#e2e8f0'}
                            nodeColor={(n) => '#f8fafc'}
                        />
                    </ReactFlow>
                </div>
            )}

            {/* Details Panel Overlay */}
            <AnimatePresence>
                {selectedNodeData && (
                    <motion.div
                        initial={{ x: '100%', opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: '100%', opacity: 0 }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="absolute top-0 right-0 h-full w-[400px] bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-l border-slate-200 dark:border-slate-800 shadow-2xl overflow-y-auto z-20"
                    >
                        <div className="p-8">
                            <div className="flex justify-between items-start mb-8">
                                <div className="flex-1 pr-4">
                                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 mb-3 border border-indigo-100 dark:border-indigo-800">
                                        {formatLabel(selectedNodeData.group)}
                                    </div>
                                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white break-words leading-tight">{selectedNodeData.label}</h2>
                                </div>
                                <button
                                    onClick={() => setSelectedNodeData(null)}
                                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full text-slate-400 hover:text-slate-600 transition-colors shrink-0"
                                >
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="space-y-8">
                                {selectedNodeData.properties?.Domain && (
                                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                                        <div className="w-10 h-10 rounded-lg bg-white dark:bg-slate-900 flex items-center justify-center shadow-sm">
                                            <Layers className="text-indigo-500" size={20} />
                                        </div>
                                        <div>
                                            <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Domain</div>
                                            <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">{selectedNodeData.properties.Domain}</div>
                                        </div>
                                    </div>
                                )}

                                <div>
                                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                                        <Database size={14} className="text-indigo-500" />
                                        Metadata Properties
                                    </h3>
                                    <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                                        <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-800">
                                            <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
                                                {Object.entries(selectedNodeData.properties || {}).map(([key, value]) => (
                                                    <tr key={key} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                                                        <td className="px-5 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-50/30 dark:bg-slate-900/30 w-1/3">
                                                            {formatLabel(key)}
                                                        </td>
                                                        <td className="px-5 py-4 text-xs text-slate-700 dark:text-slate-300 break-all font-medium">
                                                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                                        </td>
                                                    </tr>
                                                ))}
                                                {(!selectedNodeData.properties || Object.keys(selectedNodeData.properties).length === 0) && (
                                                    <tr>
                                                        <td colSpan="2" className="px-5 py-8 text-xs text-slate-400 text-center italic">
                                                            No additional properties found
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const LineageView = () => (
    <ReactFlowProvider>
        <LineageContent />
    </ReactFlowProvider>
);

export default LineageView;
