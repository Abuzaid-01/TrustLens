import { useState, useEffect, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Search, RefreshCw } from 'lucide-react'
import styles from './ReviewHistory.module.css'

const API = import.meta.env.VITE_API_URL || 'https://trustlens-ille.onrender.com'

export default function ReviewHistory() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState('created_at')
  const [sortDir, setSortDir] = useState('desc')
  const [expanded, setExpanded] = useState(null)

  const fetchReviews = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/reviews`)
      const data = await res.json()
      setReviews(data.reviews || [])
    } catch { setReviews([]) }
    setLoading(false)
  }, [])

  useEffect(() => {
    const timer = setTimeout(fetchReviews, 0)
    return () => clearTimeout(timer)
  }, [fetchReviews])

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const filtered = useMemo(() => {
    let items = [...reviews]
    if (search) {
      const q = search.toLowerCase()
      items = items.filter(r =>
        (r.business_name || r.business_id || '').toLowerCase().includes(q) ||
        (r.review_text || '').toLowerCase().includes(q) ||
        (r.trust_level || '').toLowerCase().includes(q)
      )
    }
    items.sort((a, b) => {
      let av = a[sortKey], bv = b[sortKey]
      if (typeof av === 'string') av = av.toLowerCase()
      if (typeof bv === 'string') bv = bv.toLowerCase()
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1 : -1
      return 0
    })
    return items
  }, [reviews, search, sortKey, sortDir])

  // Stats
  const totalReviews = reviews.length
  const avgScore = totalReviews > 0
    ? Math.round(reviews.reduce((s, r) => s + (r.trust_score || 0), 0) / totalReviews)
    : 0
  const flaggedPct = totalReviews > 0
    ? Math.round((reviews.filter(r => r.action === 'reject' || r.action === 'review').length / totalReviews) * 100)
    : 0

  const getLevelClass = (level) => {
    const l = (level || '').toLowerCase()
    if (l === 'high') return styles.badgeHigh
    if (l === 'medium') return styles.badgeMedium
    return styles.badgeLow
  }

  const getActionClass = (action) => {
    if (action === 'approve') return styles.actionApprove
    if (action === 'reject') return styles.actionReject
    return styles.actionReview
  }

  return (
    <div className={styles.wrapper}>
      {/* Stats Summary */}
      <div className={styles.statsBar}>
        <motion.div
          className={styles.statItem}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className={styles.statValue} style={{ color: 'var(--accent)' }}>{totalReviews}</div>
          <div className={styles.statLabel}>Total Reviews</div>
        </motion.div>
        <motion.div
          className={styles.statItem}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <div className={styles.statValue}>{avgScore}</div>
          <div className={styles.statLabel}>Avg Trust Score</div>
        </motion.div>
        <motion.div
          className={styles.statItem}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className={styles.statValue} style={{ color: flaggedPct > 30 ? 'var(--red)' : 'var(--green)' }}>
            {flaggedPct}%
          </div>
          <div className={styles.statLabel}>Flagged</div>
        </motion.div>
      </div>

      {/* Filter / Search */}
      <div className={`card ${styles.filterRow}`} style={{ padding: 14 }}>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Search reviews, businesses, or status..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <button className="btn-ghost" style={{ width: 'auto', padding: '8px 14px', fontSize: '0.78rem' }} onClick={fetchReviews}>
          <RefreshCw size={14} style={{ marginRight: 4, verticalAlign: -2 }} /> Refresh
        </button>
      </div>

      {/* Data Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>⏳</div>
            <div className={styles.emptyTitle}>Loading...</div>
          </div>
        ) : filtered.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>🔍</div>
            <div className={styles.emptyTitle}>No Reviews Found</div>
            <div className={styles.emptyDesc}>
              {search ? 'Try a different search term' : 'Submit your first review to see it here'}
            </div>
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                {[
                  { key: 'business_name', label: 'Business' },
                  { key: 'review_text', label: 'Review' },
                  { key: 'trust_score', label: 'Score' },
                  { key: 'trust_level', label: 'Level' },
                  { key: 'action', label: 'Action' },
                  { key: 'created_at', label: 'Date' },
                ].map(col => (
                  <th key={col.key} onClick={() => handleSort(col.key)}>
                    {col.label}
                    {sortKey === col.key && (
                      <span className={styles.sortArrow}>
                        {sortDir === 'asc' ? '▲' : '▼'}
                      </span>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((review, i) => (
                <>
                  <motion.tr
                    key={review.id || i}
                    onClick={() => setExpanded(expanded === i ? null : i)}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <td style={{ fontWeight: 600 }}>{review.business_name || review.business_id}</td>
                    <td>
                      <div className={styles.reviewPreview}>{review.review_text}</div>
                    </td>
                    <td>
                      <span className={`${styles.trustBadge} ${getLevelClass(review.trust_level)}`}>
                        {review.trust_score}
                      </span>
                    </td>
                    <td style={{ color: getLevelClass(review.trust_level).includes('High') ? 'var(--green)' : 'var(--text-2)' }}>
                      {review.trust_level}
                    </td>
                    <td>
                      <span className={`${styles.actionBadge} ${getActionClass(review.action)}`}>
                        {review.action}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.72rem', color: 'var(--text-3)', fontFamily: 'var(--mono)' }}>
                      {review.created_at?.split('T')[0] || '—'}
                    </td>
                  </motion.tr>

                  {/* Expanded breakdown */}
                  {expanded === i && (
                    <tr key={`expand-${i}`}>
                      <td colSpan={6} style={{ padding: 0 }}>
                        <motion.div
                          className={styles.expandedRow}
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-2)', marginBottom: 8, lineHeight: 1.6 }}>
                            "{review.review_text}"
                          </div>
                          <div className={styles.breakdownGrid}>
                            {review.breakdown && Object.entries(review.breakdown).map(([key, val]) => (
                              <div key={key} className={styles.bdCard}>
                                <div className={styles.bdLabel}>{key.replace(/_/g, ' ')}</div>
                                <div className={styles.bdValue}>{val}</div>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
