import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Timeline() {
  const [weeks, setWeeks] = useState([])
  const [open, setOpen] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.timeline().then(setWeeks).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-6 text-center text-slate-400">加载中…</div>

  const status = (c) => (c.done ? '✅' : c.is_weekend ? '🌤' : '○')

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-navy-800 mb-4">📅 学习路线图</h1>
      {/* 顶部横向进度条示意 */}
      <div className="flex gap-1 mb-5">
        {weeks.map((w) => (
          <button key={w.week} onClick={() => setOpen(open === w.week ? null : w.week)}
            className={`flex-1 h-2 rounded-full transition ${w.cards.some((c) => c.done) ? 'bg-ricegreen-500' : 'bg-slate-200 hover:bg-slate-300'}`}
            title={`第${w.week}周 ${w.week_topic}`} />
        ))}
      </div>

      <div className="space-y-3">
        {weeks.map((w) => {
          const doneCount = w.cards.filter((c) => c.done).length
          const isOpen = open === w.week
          return (
            <div key={w.week} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <button
                onClick={() => setOpen(isOpen ? null : w.week)}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-50 transition"
              >
                <div className="flex items-center gap-3">
                  <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${doneCount > 0 ? 'bg-ricegreen-500 text-white' : 'bg-slate-200 text-slate-500'}`}>{w.week}</span>
                  <div>
                    <div className="text-sm font-semibold text-navy-800">第{w.week}周 · {w.week_topic}</div>
                    <div className="text-xs text-slate-400">{doneCount}/7 已学</div>
                  </div>
                </div>
                <span className={`text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}>▾</span>
              </button>

              {isOpen && (
                <div className="px-4 pb-3 pt-1 border-t border-slate-100">
                  {w.cards.map((c) => (
                    <div key={c.id} className={`flex items-center gap-3 py-1.5 text-sm ${c.done ? 'text-slate-600' : c.is_weekend ? 'text-slate-500' : 'text-slate-400'}`}>
                      <span className="w-6 text-center">{status(c)}</span>
                      <span className="flex-1">{c.day} · {c.title}</span>
                      {c.done && <span className="text-xs text-ricegreen-600">已学</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
      <p className="mt-4 text-xs text-slate-400">绿色✅=已完成 · 灰色=未解锁 · 🌤=周末轻量内容</p>
    </div>
  )
}
