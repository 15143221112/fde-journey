import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

const WEEKDAYS = ['一', '二', '三', '四', '五', '六', '日']

export default function Stats() {
  const [s, setS] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.stats().then(setS).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-6 text-center text-slate-400">加载中…</div>
  if (!s) return <div className="p-6 text-center text-rose-600">加载失败</div>

  const pct = s.total_completion.total ? Math.round(s.total_completion.done / s.total_completion.total * 100) : 0
  const weekPct = s.week.total ? Math.round(s.week.done / s.week.total * 100) : 0

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-navy-800 mb-4">📊 学习统计</h1>

      {/* 连续打卡大数字 */}
      <div className="bg-navy-800 rounded-2xl text-white p-5 text-center mb-4">
        <div className="text-sm text-navy-200">连续打卡天数</div>
        <div className="text-5xl font-extrabold mt-1">🔥 {s.streak}</div>
        <div className="text-xs text-navy-200 mt-2">坚持就有收获</div>
      </div>

      {/* 完成率卡片 */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white rounded-xl border border-slate-200 p-3 text-center">
          <div className="text-2xl font-bold text-navy-700">{s.total_completion.done}<span className="text-sm text-slate-400">/{s.total_completion.total}</span></div>
          <div className="text-xs text-slate-500 mt-1">总完成率</div>
          <div className="text-[10px] text-ricegreen-600">{pct}%</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-3 text-center">
          <div className="text-2xl font-bold text-navy-700">{s.week.done}<span className="text-sm text-slate-400">/{s.week.total}</span></div>
          <div className="text-xs text-slate-500 mt-1">本周完成率</div>
          <div className="text-[10px] text-ricegreen-600">{weekPct}%</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-3 text-center">
          <div className="text-2xl font-bold text-navy-700">{s.week.week_number}</div>
          <div className="text-xs text-slate-500 mt-1">当前第几周</div>
        </div>
      </div>

      {/* 收藏 / 笔记 / 资料 */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: '收藏', value: s.favorites_count },
          { label: '笔记', value: s.notes_count },
          { label: '资料', value: s.resources_count },
        ].map((x) => (
          <div key={x.label} className="bg-white rounded-xl border border-slate-200 p-3 text-center">
            <div className="text-2xl font-bold text-slate-700">{x.value}</div>
            <div className="text-xs text-slate-500 mt-1">{x.label}</div>
          </div>
        ))}
      </div>

      {/* 最近7天热力图 */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="text-sm font-semibold text-navy-800 mb-3">最近 7 天打卡</div>
        <div className="flex items-center justify-between">
          {s.heatmap.map((d, i) => (
            <div key={d.date} className="flex flex-col items-center gap-1">
              <div className={`heat-cell ${d.checked ? 'bg-ricegreen-500' : 'bg-slate-200'}`} title={d.date} />
              <span className="text-[9px] text-slate-400">{WEEKDAYS[new Date(d.date + 'T00:00:00').getDay() === 0 ? 6 : new Date(d.date + 'T00:00:00').getDay() - 1]}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 进度条 */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mt-4">
        <div className="flex justify-between text-sm text-slate-600 mb-2">
          <span>总进度</span><span>{s.total_completion.done}/{s.total_completion.total}</span>
        </div>
        <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
          <div className="h-full bg-navy-600 rounded-full transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  )
}
