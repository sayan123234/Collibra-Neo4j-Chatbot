import React, { useCallback, useEffect, useState } from 'react';
import {
    ReactFlow,
    useNodesState,
    useEdgesState,
    addEdge,
    Controls,
    Background,
    applyNodeChanges,
    applyEdgeChanges,
    MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { chatService } from '../api/client';
import CustomNode from './lineage/CustomNode';
import { Loader2, RefreshCw, X, Database, Info, Wand2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const nodeTypes = {
    custom: CustomNode,
};

// Dagre Layout Calculation
const getLayoutedElements = (nodes, edges, direction = 'LR') => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    const nodeWidth = 240;
    const nodeHeight = 80;

    dagreGraph.setGraph({ rankdir: direction });

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

const LineageView = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState(null);

    const fetchLineage = async () => {
        setLoading(true);
        try {
            const data = await chatService.getLineage();

            // Transform data for React Flow
            const flowNodes = data.nodes.map(n => ({
                id: n.id,
                type: 'custom',
                data: { label: n.label, group: n.group, properties: n.properties },
                position: { x: 0, y: 0 } // Layout will fix this
            }));

            const flowEdges = data.links.map((l, i) => ({
                id: `e${l.source}-${l.target}-${i}`,
                source: l.source,
                target: l.target,
                label: l.type,
                type: 'smoothstep',
                animated: true,
                style: { stroke: '#6366f1', strokeWidth: 1.5 },
                labelStyle: { fill: '#6b7280', fontWeight: 500, fontSize: 10 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: '#6366f1',
                },
            }));

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                flowNodes,
                flowEdges
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
        } catch (error) {
            console.error("Failed to fetch lineage:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLineage();
    }, []);

    const onNodeClick = (event, node) => {
        setSelectedNode(node.data);
    };

    const onPaneClick = () => {
        setSelectedNode(null);
    };

    return (
        <div className="h-full w-full bg-gray-50 dark:bg-gray-900 relative flex flex-col">
            {/* Controls */}
            <div className="absolute top-4 left-4 z-10 bg-white dark:bg-gray-800 p-2 rounded-lg shadow-md border border-gray-100 dark:border-gray-700 flex gap-2">
                <button
                    onClick={fetchLineage}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md text-gray-600 dark:text-gray-300 transition-colors flex items-center gap-2 text-sm font-medium"
                    title="Refresh Layout"
                >
                    <Wand2 size={16} />
                    Auto Layout
                </button>
            </div>

            {loading ? (
                <div className="flex-1 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-3 text-gray-400">
                        <Loader2 className="w-8 h-8 animate-spin" />
                        <p>Calculating layout...</p>
                    </div>
                </div>
            ) : (
                <div className="flex-1 h-full w-full">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onNodeClick={onNodeClick}
                        onPaneClick={onPaneClick}
                        nodeTypes={nodeTypes}
                        fitView
                        attributionPosition="bottom-left"
                        minZoom={0.1}
                    >
                        <Background className="dark:fill-gray-700" gap={16} size={1} />
                        <Controls className="!bg-white dark:!bg-gray-800 !border-gray-100 dark:!border-gray-700 !shadow-md !rounded-lg overflow-hidden !m-4 [&>button]:!fill-gray-600 [&>button]:dark:!fill-gray-300 [&>button]:!border-b-gray-100 [&>button]:dark:!border-b-gray-700 hover:[&>button]:!bg-gray-50 hover:[&>button]:dark:!bg-gray-700" />
                    </ReactFlow>
                </div>
            )}

            {/* Details Panel Overlay */}
            <AnimatePresence>
                {selectedNode && (
                    <motion.div
                        initial={{ x: '100%', opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: '100%', opacity: 0 }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="absolute top-0 right-0 h-full w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 shadow-xl overflow-y-auto z-20"
                    >
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 mb-2">
                                        {selectedNode.group}
                                    </div>
                                    <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 break-words">{selectedNode.label}</h2>
                                </div>
                                <button
                                    onClick={() => setSelectedNode(null)}
                                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                                >
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-sm font-medium text-gray-500 mb-3 flex items-center gap-2">
                                        <Database size={16} />
                                        Properties
                                    </h3>
                                    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden border border-gray-100 dark:border-gray-700">
                                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                                {Object.entries(selectedNode.properties || {}).map(([key, value]) => (
                                                    <tr key={key}>
                                                        <td className="px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-50/50 dark:bg-gray-800 w-1/3">
                                                            {key}
                                                        </td>
                                                        <td className="px-4 py-3 text-xs text-gray-900 dark:text-gray-300 break-all">
                                                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                                        </td>
                                                    </tr>
                                                ))}
                                                {(!selectedNode.properties || Object.keys(selectedNode.properties).length === 0) && (
                                                    <tr>
                                                        <td colSpan="2" className="px-4 py-3 text-xs text-gray-400 text-center italic">
                                                            No properties found
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

export default LineageView;
