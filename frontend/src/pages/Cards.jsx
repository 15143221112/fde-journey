import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Cards() {
  const [cards, setCards] = useState([])
  const [categories, setCategories] = useState([])
  const [search, setSearch] = useState('')
  const [cat, setCat] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.listCards({ search, category: cat }).then(setCards).catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(() => { api.cardCategories().then(setCategories).catch(() => {}) }, [])
  useEffect(load, [search, cat])

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-navy-800 mb-4">📚 技术知识库</h1>

      {/* 搜索 */}
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="🔍 搜索卡片标题或内容…"
        className="w-full mb-3 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-400"
      />

      {/* 分类筛选 */}
      <div className="flex gap-1.5 flex-wrap mb-4">
        {['', ...categories].map((c) => (
          <button key={c || 'all'} onClick={() => setCat(c)}
            className={`px-3 py-1 rounded-full text-xs transition ${cat === c ? 'bg-navy-700 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            {c || '全部'}
          </button>
        ))}
      </div>

      {loading ? <div className="text-center text-slate-400 py-10">加载中…</div> : (
        <div className="space-y-2">
          {cards.map((c) => (
            <div key={c.id} className="bg-white rounded-xl border border-slate-200 p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">第{c.day_number}天 · 第{c.week_number}周</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-navy-50 text-navy-700">{c.category}</span>
              </div>
              <div className="mt-1 text-sm font-semibold text-navy-800">{c.is_weekend ? '🌤 ' : ''}{c.title}</div>
            </div>
          ))}
          {cards.length === 0 && <div className="text-center text-slate-400 py-10">没有匹配的卡片</div>}
        </div>
      )}
    </div>
  )
}
