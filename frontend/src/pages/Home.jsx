import React, { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Markdown } from '../utils/md.jsx'

export default function Home() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [noteOpen, setNoteOpen] = useState(false)
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState('')

  const load = () => {
    api.today().then(setData).catch((e) => setErr(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(''), 1800)
    return () => clearTimeout(t)
  }, [toast])

  const doCheckin = async () => {
    if (data?.today_checked) { setToast('今天已打过卡啦'); return }
    try {
      await api.checkin(data.card.id, note || '')
      setToast('打卡成功！连续天数 +1')
      setNoteOpen(false)
      load()
    } catch (e) { setToast('失败: ' + e.message) }
  }

  const doFavorite = async () => {
    try {
      if (data.is_favorite) await api.removeFavorite(data.card.id)
      else await api.addFavorite(data.card.id)
      load()
    } catch (e) { setToast('失败: ' + e.message) }
  }

  const saveNote = async () => {
    setSaving(true)
    try {
      await api.saveNote(data.card.id, note)
      setToast('笔记已保存')
      setNoteOpen(false)
      load()
    } catch (e) { setToast('失败: ' + e.message) }
    finally { setSaving(false) }
  }

  if (loading) return <div className="p-6 text-center text-slate-400">加载中…</div>
  if (err || !data) return <div className="p-6 text-center text-rose-600">加载失败：{err || '无数据'}</div>

  const card = data.card
  const pct = data.progress.total ? Math.round(data.progress.done / data.progress.total * 100) : 0

  return (
    <div className="p-4">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-navy-800">🎯 FDE 学习之路</h1>
          <span className="text-sm text-navy-600 font-medium">第{data.week_number}周 / 共12周</span>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-ricegreen-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
          <span className="text-xs text-slate-500 whitespace-nowrap">{data.progress.done}/84 ({pct}%)</span>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
        <div className="text-navy-700 font-bold text-base mb-1">📌 第{card.day_number}天/84天：{card.title}</div>
        {card.is_weekend ? (
          <div className="mt-3 text-slate-700"><p className="text-sm whitespace-pre-wrap">{card.content?.weekend_note}</p></div>
        ) : (
          <>
            <div className="mt-4">
              <div className="text-sm font-semibold text-navy-800 mb-2">🎯 核心知识点</div>
              <ul className="space-y-2">
                {card.content.points.map((p, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-700">
                    <span className="text-ricegreen-500 mt-0.5">•</span>
                    <span><Markdown text={p} /></span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-4 bg-slate-50 rounded-lg p-3">
              <div className="text-sm font-semibold text-navy-800 mb-1">🔧 动手练习（10分钟）</div>
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{card.content.exercise}</p>
            </div>
            {card.content.rice_project && (
              <div className="mt-3 bg-ricegreen-50 border border-ricegreen-200 rounded-lg p-3">
                <div className="text-sm font-semibold text-ricegreen-700 mb-1">🌾 水稻项目关联</div>
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{card.content.rice_project}</p>
              </div>
            )}
          </>
        )}

        <div className="mt-5 grid grid-cols-3 gap-2">
          <button onClick={doCheckin}
            className={`py-2.5 rounded-xl text-sm font-semibold transition ${data.today_checked ? 'bg-ricegreen-500 text-white cursor-default' : 'bg-ricegreen-500 hover:bg-ricegreen-600 text-white'}`}>
            {data.today_checked ? '✅ 已学' : '✅ 今日已学'}
          </button>
          <button onClick={doFavorite}
            className={`py-2.5 rounded-xl text-sm font-semibold border transition ${data.is_favorite ? 'bg-amber-50 border-amber-300 text-amber-700' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'}`}>
            🔖 {data.is_favorite ? '已收藏' : '收藏'}
          </button>
          <button onClick={() => setNoteOpen(!noteOpen)}
            className="py-2.5 rounded-xl text-sm font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition">
            💬 记笔记
          </button>
        </div>

        {noteOpen && (
          <div className="mt-4">
            <textarea value={note} onChange={(e) => setNote(e.target.value)}
              placeholder="写下今天的学习心得…（支持 Markdown）" rows={4}
              className="w-full border border-slate-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-navy-400" />
            <button onClick={saveNote} disabled={saving}
              className="mt-2 w-full py-2 rounded-lg bg-navy-700 text-white text-sm font-semibold disabled:opacity-50">
              {saving ? '保存中…' : '保存笔记'}
            </button>
          </div>
        )}
      </div>

      <div className="mt-4 bg-white rounded-xl border border-slate-200 p-3 text-center">
        <span className="text-sm text-slate-500">连续打卡</span>
        <span className="ml-2 text-2xl font-bold text-amber-500">🔥 {data.streak ?? 0} 天</span>
      </div>

      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-navy-800 text-white text-sm px-4 py-2 rounded-full shadow-lg">{toast}</div>
      )}
    </div>
  )
}
