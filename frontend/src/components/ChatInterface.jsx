import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Database, Info } from 'lucide-react';
import { chatService } from '../api/client';
import { motion, AnimatePresence } from 'framer-motion';

const Message = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-indigo-600' : 'bg-emerald-600'
                    }`}>
                    {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                </div>

                <div className={`p-4 rounded-2xl ${isUser
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shadow-sm rounded-tl-none'
                    }`}>
                    <p className={`whitespace-pre-wrap leading-relaxed ${isUser ? 'text-indigo-50' : 'text-gray-700 dark:text-gray-300'}`}>
                        {message.content}
                    </p>

                    {/* Query Metrics/Info for Assistant */}
                    {!isUser && message.metadata && (
                        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-400 flex flex-col gap-1">
                            {message.metadata.cypher_query && (
                                <div className="bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-100 dark:border-gray-700 font-mono text-gray-500 dark:text-gray-400 overflow-x-auto">
                                    {message.metadata.cypher_query}
                                </div>
                            )}
                            <div className="flex justify-between items-center mt-1">
                                <span>Recieved {message.metadata.results?.length || 0} items</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default function ChatInterface() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your Collibra Data Assistant. Ask me anything about your metadata graph.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            // Format history for backend (exclude metadata)
            const history = messages.map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            const response = await chatService.sendMessage(userMessage, history);

            const assistantMessage = {
                role: 'assistant',
                content: response.answer,
                metadata: {
                    cypher_query: response.cypher_query,
                    results: response.results,
                    error: response.error
                }
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error connecting to the server. Please check if the backend is running.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 p-4 sticky top-0 z-10">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                            CA
                        </div>
                        <div>
                            <h1 className="font-bold text-gray-900 dark:text-white">Collibra Assistant</h1>
                            <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                Online
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6">
                <div className="max-w-3xl mx-auto">
                    {messages.map((msg, idx) => (
                        <Message key={idx} message={msg} />
                    ))}

                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex w-full mb-4 justify-start"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center shrink-0">
                                    <Bot size={16} className="text-white" />
                                </div>
                                <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2 text-gray-500 dark:text-gray-400">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span className="text-sm">Analyzing metadata...</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 p-4 sticky bottom-0">
                <div className="max-w-3xl mx-auto">
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask about assets, domains, or stewards..."
                            className="w-full pl-6 pr-14 py-4 rounded-2xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50 dark:bg-gray-900 focus:bg-white dark:focus:bg-gray-800"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                    <p className="text-center text-xs text-gray-400 mt-3">
                        AI-generated responses can be inaccurate. Verify important information.
                    </p>
                </div>
            </div>
        </div>
    );
}
