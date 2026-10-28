import React, { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

const TYPE_META = {
  link: { icon: '🔗', label: '网页链接' },
  file: { icon: '📄', label: '本地文件' },
  code: { icon: '💻', label: '代码片段' },
  video: { icon: '🎬', label: '视频' },
  note: { icon: '📌', label: '随手记' },
}
const STATUS = { unread: '未读', reading: '在读', read: '已读' }
const STATUS_CLASS = { unread: 'bg-slate-100 text-slate-500', reading: 'bg-amber-50 text-amber-700', read: 'bg-ricegreen-50 text-ricegreen-700' }

const emptyForm = {
  title: '', type: 'link', url: '', code_content: '', note_content: '',
  category: 'LangGraph', tags: '', summary: '', related_week: '', read_status: 'unread',
}

export default function Resources() {
  const [items, setItems] = useState([])
  const [cats, setCats] = useState([])
  const [cat, setCat] = useState('')
  const [search, setSearch] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState('')
  const [expanded, setExpanded] = useState(null)
  const fileRef = useRef(null)

  const load = () => {
    api.listResources({ category: cat, search }).then(setItems).catch(() => {})
  }
  useEffect(() => {
    api.resourceCategories().then(setCats).catch(() => {})
  }, [])
  useEffect(load, [cat, search])

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(''), 1800)
    return () => clearTimeout(t)
  }, [toast])

  const submit = async () => {
    if (!form.title.trim()) { setToast('请填写标题'); return }
    setSaving(true)
    try {
      const body = { ...form, related_week: form.related_week ? Number(form.related_week) : null }
      await api.addResource(body)
      setToast('资料已添加')
      setShowAdd(false)
      setForm(emptyForm)
      load()
    } catch (e) { setToast('失败: ' + e.message) }
    finally { setSaving(false) }
  }

  const onUpload = async (file) => {
    if (!file) return
    setSaving(true)
    try {
      await api.uploadResource(file, { category: cat || '其他', summary: '', tags: '' })
      setToast('文件已上传')
      load()
    } catch (e) { setToast('失败: ' + e.message) }
    finally { setSaving(false); fileRef.current.value = '' }
  }

  const toggleStatus = async (r) => {
    const next = r.read_status === 'unread' ? 'reading' : r.read_status === 'reading' ? 'read' : 'unread'
    await api.updateResource(r.id, { read_status: next })
    load()
  }

  const del = async (r) => {
    if (!window.confirm(`删除资料「${r.title}」？`)) return
    await api.deleteResource(r.id)
    setToast('已删除')
    load()
  }

  const exportJson = async () => {
    try {
      const txt = await api.get('/api/resources/export?fmt=json')
      const blob = new Blob([typeof txt === 'string' ? txt : JSON.stringify(txt, null, 2)], { type: 'application/json' })
      download(blob, 'fde-resources.json')
    } catch (e) { setToast('导出失败') }
  }
  const exportMd = async () => {
    try {
      const txt = await api.get('/api/resources/export?fmt=markdown')
      const blob = new Blob([txt], { type: 'text/markdown' })
      download(blob, 'fde-resources.md')
    } catch (e) { setToast('导出失败') }
  }
  const download = (blob, name) => {
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = name
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const openFile = (r) => {
    if (r.url) window.open(r.url, '_blank')
    else if (r.file_name) window.open(`/api/resources/${r.id}/download`, '_blank')
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-navy-800">📁 资料库</h1>
        <button onClick={() => setShowAdd(!showAdd)} className="px-3 py-1.5 rounded-lg bg-navy-700 text-white text-sm font-semibold">
          + 添加资料
        </button>
      </div>

      {/* 分类筛选 */}
      <div className="flex gap-1.5 flex-wrap mb-2">
        {['', ...cats].map((c) => (
          <button key={c || 'all'} onClick={() => setCat(c)}
            className={`px-3 py-1 rounded-full text-xs transition ${cat === c ? 'bg-navy-700 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            {c || '全部'}
          </button>
        ))}
      </div>

      {/* 搜索 + 导出 */}
      <div className="flex gap-2 mb-4">
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 搜索标题 / 摘要 / 标签 / 代码…" className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-400" />
        <button onClick={exportMd} title="导出 Markdown" className="px-2.5 rounded-lg border border-slate-300 text-slate-600 text-xs">.md</button>
        <button onClick={exportJson} title="导出 JSON" className="px-2.5 rounded-lg border border-slate-300 text-slate-600 text-xs">JSON</button>
      </div>

      {/* 添加资料表单 */}
      {showAdd && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4 space-y-3">
          <div className="flex gap-2">
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="资料标题 *" className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
              className="border border-slate-300 rounded-lg px-2 py-2 text-sm bg-white">
              {Object.entries(TYPE_META).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
            </select>
          </div>

          {form.type === 'link' || form.type === 'video' ? (
            <input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder={form.type === 'link' ? 'URL 链接' : '视频链接（B站/YouTube）'} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          ) : null}
          {form.type === 'code' ? (
            <textarea value={form.code_content} onChange={(e) => setForm({ ...form, code_content: e.target.value })}
              placeholder="代码内容" rows={4} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono" />
          ) : null}
          {form.type === 'note' ? (
            <textarea value={form.note_content} onChange={(e) => setForm({ ...form, note_content: e.target.value })}
              placeholder="随手记内容" rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          ) : null}
          {form.type === 'file' ? (
            <div className="border border-dashed border-slate-300 rounded-lg p-3 text-sm text-slate-500">
              上传文件：<input ref={fileRef} type="file" onChange={(e) => onUpload(e.target.files[0])} className="text-xs" />
            </div>
          ) : null}

          <div className="grid grid-cols-2 gap-2">
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="border border-slate-300 rounded-lg px-2 py-2 text-sm bg-white">
              {cats.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <select value={form.read_status} onChange={(e) => setForm({ ...form, read_status: e.target.value })}
              className="border border-slate-300 rounded-lg px-2 py-2 text-sm bg-white">
              {Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })}
            placeholder="标签，逗号分隔（如：状态机,节点,边）" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          <textarea value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })}
            placeholder="一句话摘要" rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          <input value={form.related_week} onChange={(e) => setForm({ ...form, related_week: e.target.value })}
            placeholder="关联周次（1-12，可选）" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />

          <div className="flex gap-2">
            <button onClick={submit} disabled={saving}
              className="flex-1 py-2 rounded-lg bg-navy-700 text-white text-sm font-semibold disabled:opacity-50">
              {saving ? '保存中…' : '保存资料'}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-lg border border-slate-300 text-slate-600 text-sm">取消</button>
          </div>
        </div>
      )}

      {/* 资料列表 */}
      {items.length === 0 ? (
        <div className="text-center text-slate-400 py-10">还没有资料，点右上角添加</div>
      ) : (
        <div className="space-y-2">
          {items.map((r) => (
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-3 cursor-pointer hover:bg-slate-50"
              onClick={() => setExpanded(expanded === r.id ? null : r.id)}>
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-navy-800">{TYPE_META[r.type]?.icon} {r.title}</div>
                  <div className="text-xs text-slate-500 mt-0.5 truncate">
                    {r.category}{r.tags ? ` | ${r.tags}` : ''}
                  </div>
                  <div className="flex items-center gap-2 mt-1.5 text-[10px] text-slate-400">
                    {r.related_week ? <span>第{r.related_week}周</span> : null}
                    <span>{r.created_at.slice(0, 10)}</span>
                  </div>
                </div>
                <button onClick={(e) => { e.stopPropagation(); toggleStatus(r) }}
                  className={`ml-2 px-2 py-0.5 rounded-full text-[10px] font-medium ${STATUS_CLASS[r.read_status]}`}>
                  {STATUS[r.read_status]}
                </button>
              </div>

              {expanded === r.id && (
                <div className="mt-2 pt-2 border-t border-slate-100 text-sm text-slate-600 space-y-1.5"
                  onClick={(e) => e.stopPropagation()}>
                  {r.summary && <p className="text-xs">{r.summary}</p>}
                  {r.url && <button onClick={() => window.open(r.url, '_blank')} className="text-navy-600 underline text-xs">打开链接 ↗</button>}
                  {r.file_name && <button onClick={() => openFile(r)} className="text-navy-600 underline text-xs">下载文件 {r.file_name}</button>}
                  {r.note_content && <p className="text-xs bg-slate-50 p-2 rounded">{r.note_content}</p>}
                  {r.code_content && <pre className="code-block">{r.code_content}</pre>}
                  <div className="flex gap-2 pt-1">
                    {r.type === 'link' && <button onClick={() => { navigator.clipboard.writeText(r.url); setToast('链接已复制') }} className="text-xs text-slate-400 hover:text-navy-600">复制链接</button>}
                    <button onClick={() => del(r)} className="text-xs text-rose-500 hover:text-rose-700">删除</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-navy-800 text-white text-sm px-4 py-2 rounded-full shadow-lg">{toast}</div>
      )}
    </div>
  )
}
