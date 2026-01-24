import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Database, FileText, Table, Box, Layers, User, MoreHorizontal, ArrowRight } from 'lucide-react';

const icons = {
    'Database': Database,
    'Asset': FileText,
    'Table': Table,
    'Column': Box,
    'Domain': Layers,
    'User': User,
    'Unknown': MoreHorizontal
};

const CustomNode = ({ data, selected }) => {
    // Determine icon based on group
    const Icon = icons[Object.keys(icons).find(key => data.group?.includes(key)) || 'Unknown'];

    return (
        <div className={`px-4 py-3 shadow-md rounded-lg border-2 min-w-[200px] transition-all hover:shadow-lg dark:bg-gray-800 dark:border-gray-700 ${selected ? 'border-indigo-500 shadow-indigo-100 ring-2 ring-indigo-200 dark:ring-indigo-900 dark:shadow-none' : 'border-gray-200'
            }`}>
            {/* Input Handle (Left) */}
            <Handle
                type="target"
                position={Position.Left}
                className="!bg-gray-300 !w-3 !h-3 !-left-2 !border-2 !border-white"
            />

            <div className="flex items-center gap-3">
                <div className={`p-2 rounded-md shrink-0 flex items-center justify-center ${selected ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-300' : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                    <Icon size={18} />
                </div>

                <div className="flex flex-col overflow-hidden">
                    <div className="text-sm font-bold text-gray-900 dark:text-gray-100 truncate" title={data.label}>
                        {data.label}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate font-mono">
                        {data.group}
                    </div>
                </div>
            </div>

            {/* Output Handle (Right) */}
            <Handle
                type="source"
                position={Position.Right}
                className="!bg-indigo-400 !w-3 !h-3 !-right-2 !border-2 !border-white"
            />
        </div>
    );
};

export default memo(CustomNode);
