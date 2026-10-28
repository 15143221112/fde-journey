import React from 'react'

/**
 * 极简 Markdown -> React 渲染器。
 * 支持：标题(# ## ###)、列表(- / 1.)、代码块(```)、行内代码(`)、粗体(**)、链接([]())。
 * 足够笔记与卡片展示使用，避免引入重型依赖、保证离线可用。
 */

function inline(text) {
  // 先处理行内代码，避免和粗体/链接冲突
  const nodes = []
  const codeRe = /`([^`]+)`/g
  let last = 0
  let m
  let key = 0
  while ((m = codeRe.exec(text))) {
    if (m.index > last) nodes.push(renderInlinePlain(text.slice(last, m.index), key++))
    nodes.push(<code key={`c${key++}`}>{m[1]}</code>)
    last = codeRe.lastIndex
  }
  if (last < text.length) nodes.push(renderInlinePlain(text.slice(last), key++))
  return nodes
}

function renderInlinePlain(text, k) {
  // 粗体 **xx**
  const parts = []
  const re = /\*\*([^*]+)\*\*/g
  let last = 0
  let m
  let i = 0
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push(text.slice(last, m.index))
    parts.push(<strong key={`b${i++}`}>{m[1]}</strong>)
    last = re.lastIndex
  }
  if (last < text.length) parts.push(text.slice(last))
  return <React.Fragment key={k}>{parts}</React.Fragment>
}

export function Markdown({ text }) {
  if (!text) return null
  const lines = String(text).split(/\r?\n/)
  const blocks = []
  let i = 0
  let key = 0
  while (i < lines.length) {
    const line = lines[i]
    // 代码块
    if (/^\s*```/.test(line)) {
      const buf = []
      i++
      while (i < lines.length && !/^\s*```/.test(lines[i])) {
        buf.push(lines[i]); i++
      }
      i++ // 跳过结束```
      blocks.push(<pre key={key++}><code>{buf.join('\n')}</code></pre>)
      continue
    }
    const trim = line.trim()
    if (!trim) { i++; continue }
    const h = /^(#{1,3})\s+(.*)$/.exec(trim)
    if (h) {
      const lv = h[1].length
      const Tag = `h${lv}`
      blocks.push(<Tag key={key++}>{inline(h[2])}</Tag>)
      i++
      continue
    }
    // 列表项
    const li = /^(\s*)[-*]\s+(.*)$/.exec(trim) || /^\d+[.)]\s+(.*)$/.exec(trim)
    if (li) {
      const items = []
      while (i < lines.length) {
        const t = lines[i].trim()
        const m2 = /^[-*]\s+(.*)$/.exec(t) || /^\d+[.)]\s+(.*)$/.exec(t)
        if (m2) { items.push(<li key={items.length}>{inline(m2[1])}</li>); i++ }
        else break
      }
      blocks.push(<ul key={key++}>{items}</ul>)
      continue
    }
    // 引用
    if (trim.startsWith('>')) {
      blocks.push(<blockquote key={key++}>{inline(trim.replace(/^>\s?/, ''))}</blockquote>)
      i++
      continue
    }
    blocks.push(<p key={key++}>{inline(line)}</p>)
    i++
  }
  return <div className="md-note">{blocks}</div>
}
