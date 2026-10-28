import React, { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Markdown } from '../utils/md.jsx'

export default function Notes() {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.notes().then(setNotes).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-6 text-center text-slate-400">加载中…</div>

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-navy-800 mb-4">📝 我的笔记</h1>
      {notes.length === 0 ? (
        <div className="text-center text-slate-400 py-10">还没有笔记，去首页给卡片写一条吧</div>
      ) : (
        <div className="space-y-3">
          {notes.map((n) => (
            <div key={n.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>第{n.day_number}天 · {n.title}</span>
                <span>{n.checked_at.slice(0, 10)}</span>
              </div>
              <Markdown text={n.notes} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
