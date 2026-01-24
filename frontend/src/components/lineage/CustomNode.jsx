import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
    Database, FileText, Table, Box, Layers, User,
    MoreHorizontal, Shield, Activity, GitBranch,
    Tag, Compass
} from 'lucide-react';

const icons = {
    'Database': Database,
    'Asset': FileText,
    'Table': Table,
    'Column': Box,
    'Domain': Layers,
    'User': User,
    'Data_Category': Tag,
    'Data_Concept': Compass,
    'Data_Quality_Rule': Activity,
    'Business_Asset': GitBranch,
    'Data_Issue': Shield,
    'Unknown': MoreHorizontal
};

const colors = {
    'Database': 'bg-blue-500',
    'Table': 'bg-emerald-500',
    'Column': 'bg-sky-500',
    'Domain': 'bg-purple-500',
    'User': 'bg-orange-500',
    'Data_Category': 'bg-indigo-500',
    'Data_Concept': 'bg-violet-500',
    'Data_Quality_Rule': 'bg-rose-500',
    'Business_Asset': 'bg-amber-500',
    'Data_Issue': 'bg-red-500',
    'Unknown': 'bg-gray-500'
};

const formatLabel = (str) => {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const CustomNode = ({ data, selected }) => {
    // Determine icon and color based on group
    const groupKey = Object.keys(icons).find(key => data.group === key) || 'Unknown';
    const Icon = icons[groupKey];
    const accentColor = colors[groupKey] || colors['Unknown'];

    return (
        <div className={`group relative bg-white dark:bg-gray-800 rounded-lg shadow-sm border transition-all duration-300 min-w-[220px] overflow-hidden ${selected
                ? 'ring-2 ring-indigo-500 border-transparent shadow-indigo-100 dark:shadow-none scale-105 z-50'
                : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-md'
            }`}>
            {/* Target Handle (Left) */}
            <Handle
                type="target"
                position={Position.Left}
                className="!w-2 !h-8 !rounded-none !bg-gray-200 dark:!bg-gray-700 !border-none !-left-1"
            />

            <div className="flex h-full">
                {/* Accent Bar */}
                <div className={`w-1.5 ${accentColor} shrink-0`} />

                <div className="flex-1 p-3 flex flex-col gap-1">
                    {/* Header: Icon + Type */}
                    <div className="flex items-center gap-2 mb-1">
                        <div className={`w-5 h-5 rounded flex items-center justify-center text-white ${accentColor}`}>
                            <Icon size={12} strokeWidth={2.5} />
                        </div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                            {formatLabel(data.group)}
                        </span>
                    </div>

                    {/* Label */}
                    <div className="text-sm font-semibold text-gray-900 dark:text-gray-100 line-clamp-2 leading-snug">
                        {data.label}
                    </div>

                    {/* Sub-info if available (e.g. Domain) */}
                    {data.properties?.Domain && (
                        <div className="mt-1 flex items-center gap-1.5">
                            <Layers size={10} className="text-gray-400" />
                            <span className="text-[10px] text-gray-500 dark:text-gray-400 truncate">
                                {data.properties.Domain}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* Source Handle (Right) */}
            <Handle
                type="source"
                position={Position.Right}
                className="!w-2 !h-8 !rounded-none !bg-indigo-500 !border-none !-right-1"
            />

            {/* Selected Indicator */}
            {selected && (
                <div className="absolute top-1 right-1">
                    <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                </div>
            )}
        </div>
    );
};

export default memo(CustomNode);
