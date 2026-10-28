import React, { useState } from 'react'
import Home from './pages/Home.jsx'
import Timeline from './pages/Timeline.jsx'
import Cards from './pages/Cards.jsx'
import Stats from './pages/Stats.jsx'
import Notes from './pages/Notes.jsx'
import Resources from './pages/Resources.jsx'

const NAV = [
  { key: 'home', label: '今日', icon: '🎯' },
  { key: 'timeline', label: '路线', icon: '📅' },
  { key: 'cards', label: '卡片', icon: '📚' },
  { key: 'resources', label: '资料', icon: '📁' },
  { key: 'stats', label: '统计', icon: '📊' },
  { key: 'notes', label: '笔记', icon: '📝' },
]

export default function App() {
  const [page, setPage] = useState('home')

  return (
    <div className="max-w-lg mx-auto min-h-screen flex flex-col bg-slate-50">
      {/* 内容区 */}
      <main className="flex-1 pb-20">
        {page === 'home' && <Home />}
        {page === 'timeline' && <Timeline />}
        {page === 'cards' && <Cards />}
        {page === 'resources' && <Resources />}
        {page === 'stats' && <Stats />}
        {page === 'notes' && <Notes />}
      </main>

      {/* 底部固定导航（移动端适配） */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white border-t border-slate-200 shadow-[0_-2px_8px_rgba(0,0,0,0.06)] pb-safe">
        <div className="grid grid-cols-6">
          {NAV.map((n) => (
            <button
              key={n.key}
              onClick={() => setPage(n.key)}
              className={`flex flex-col items-center py-2 text-[11px] transition ${
                page === n.key ? 'text-navy-700 font-semibold' : 'text-slate-400'
              }`}
            >
              <span className="text-lg leading-none mb-0.5">{n.icon}</span>
              {n.label}
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}
