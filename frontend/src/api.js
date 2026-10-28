// 轻量 API 客户端。所有请求走相对路径 /api，开发时由 vite 代理到后端，生产由后端同源托管。
async function request(method, path, body) {
  const opts = { method, headers: {} }
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const res = await fetch(path, opts)
  if (!res.ok) {
    let msg = res.statusText
    try {
      const j = await res.json()
      if (j.detail) msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
    } catch (e) { /* ignore */ }
    throw new Error(msg)
  }
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return res.json()
  return res.text()
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, b) => request('POST', p, b),
  patch: (p, b) => request('PATCH', p, b),
  del: (p) => request('DELETE', p),

  // 卡片
  today: () => request('GET', '/api/cards/today'),
  listCards: (q = {}) => {
    const s = new URLSearchParams()
    if (q.search) s.set('search', q.search)
    if (q.category) s.set('category', q.category)
    const qs = s.toString()
    return request('GET', '/api/cards' + (qs ? `?${qs}` : ''))
  },
  timeline: () => request('GET', '/api/cards/timeline'),
  card: (id) => request('GET', `/api/cards/${id}`),
  cardCategories: () => request('GET', '/api/cards/categories'),

  // 打卡 / 收藏 / 笔记
  checkin: (cardId, notes = '') => request('POST', '/api/checkins', { card_id: cardId, notes }),
  favorites: () => request('GET', '/api/favorites'),
  addFavorite: (cardId) => request('POST', '/api/favorites', { card_id: cardId }),
  removeFavorite: (cardId) => request('DELETE', `/api/favorites/${cardId}`),
  saveNote: (cardId, notes) => request('POST', `/api/cards/${cardId}/note`, { card_id: cardId, notes }),
  notes: () => request('GET', '/api/notes'),

  // 统计
  stats: () => request('GET', '/api/stats'),

  // 资料
  listResources: (q = {}) => {
    const s = new URLSearchParams()
    for (const k of ['category', 'tags', 'search', 'status', 'type', 'related_card_id']) {
      if (q[k]) s.set(k, q[k])
    }
    const qs = s.toString()
    return request('GET', '/api/resources' + (qs ? `?${qs}` : ''))
  },
  resource: (id) => request('GET', `/api/resources/${id}`),
  addResource: (b) => request('POST', '/api/resources', b),
  updateResource: (id, b) => request('PATCH', `/api/resources/${id}`, b),
  deleteResource: (id) => request('DELETE', `/api/resources/${id}`),
  resourceCategories: () => request('GET', '/api/resources/categories'),
  uploadResource: (file, meta) => {
    const fd = new FormData()
    fd.append('file', file)
    if (meta.category) fd.append('category', meta.category)
    if (meta.summary) fd.append('summary', meta.summary)
    if (meta.tags) fd.append('tags', meta.tags)
    if (meta.title) fd.append('title', meta.title)
    return fetch('/api/resources/upload', { method: 'POST', body: fd }).then(async (res) => {
      if (!res.ok) {
        let m = res.statusText
        try { m = (await res.json()).detail || m } catch (e) {}
        throw new Error(m)
      }
      return res.json()
    })
  },
}
