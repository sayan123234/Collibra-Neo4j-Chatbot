import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import LineageView from './components/LineageView';
import { MessageSquare, Share2, Sun, Moon } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage or system preference
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
      return true;
    } else {
      document.documentElement.classList.remove('dark');
      return false;
    }
  });

  const toggleDarkMode = () => {
    setDarkMode(prev => {
      const newMode = !prev;
      if (newMode) {
        document.documentElement.classList.add('dark');
        localStorage.theme = 'dark';
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.theme = 'light';
      }
      return newMode;
    });
  };

  return (
    <div className={`h-screen w-screen flex transition-colors duration-200 ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Sidebar Navigation (Mini) */}
      <div className={`w-16 border-r flex flex-col items-center py-6 gap-6 z-20 shrink-0 ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100'
        }`}>
        <div className="w-10 h-10 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold shrink-0">
          CA
        </div>

        <div className="flex flex-col gap-4 w-full flex-1">
          <button
            onClick={() => setActiveTab('chat')}
            className={`p-3 relative group transition-all duration-200 ${activeTab === 'chat'
              ? 'text-indigo-400'
              : (darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600')
              }`}
            title="Chat"
          >
            <MessageSquare size={24} />
            {activeTab === 'chat' && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-500 rounded-r-full" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('lineage')}
            className={`p-3 relative group transition-all duration-200 ${activeTab === 'lineage'
              ? 'text-indigo-400'
              : (darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600')
              }`}
            title="Lineage Visualization"
          >
            <Share2 size={24} />
            {activeTab === 'lineage' && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-500 rounded-r-full" />
            )}
          </button>
        </div>

        {/* Dark Mode Toggle */}
        <div className="mt-auto">
          <button
            onClick={toggleDarkMode}
            className={`p-3 rounded-xl transition-all ${darkMode ? 'text-yellow-400 hover:bg-gray-700' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-900'
              }`}
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? (
              <Sun size={24} />
            ) : (
              <Moon size={24} />
            )}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {activeTab === 'chat' ? (
          <ChatInterface />
        ) : (
          <LineageView />
        )}
      </div>
    </div>
  );
}

export default App;
