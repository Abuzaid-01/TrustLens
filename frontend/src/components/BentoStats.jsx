import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import styles from './BentoStats.module.css'

// Animated counter hook — counts up when visible
function useVisibleCounter(target, duration = 1800) {
  const [value, setValue] = useState(0)
  const [triggered, setTriggered] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting && !triggered) setTriggered(true) },
      { threshold: 0.3 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [triggered])

  useEffect(() => {
    if (!triggered) return
    const start = Date.now()
    const tick = () => {
      const progress = Math.min((Date.now() - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(eased * target))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [triggered, target, duration])

  return [value, ref]
}

const ITEMS = [
  { icon: '🤖', value: '6', label: 'AI Agents', desc: 'LangGraph-orchestrated pipeline', bg: 'rgba(168, 85, 247, 0.08)' },
  { icon: '👁', value: 'Vision', label: 'Llama 4 Scout', desc: 'AI image analysis', bg: 'rgba(236, 72, 153, 0.08)' },
  { icon: '🗄', value: 'SQLite', label: 'Real Database', desc: 'Order verification', bg: 'rgba(59, 130, 246, 0.08)' },
  { icon: '⚡', value: 'Groq', label: 'Inference', desc: '<100ms latency', bg: 'rgba(245, 158, 11, 0.08)' },
]

export default function BentoStats() {
  const [reviewsValue, reviewsRef] = useVisibleCounter(1247)
  const [fakesValue, fakesRef] = useVisibleCounter(89)

  return (
    <section className={styles.section}>
      <motion.p
        className="section-label"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        By the Numbers
      </motion.p>

      <div className={styles.bentoGrid}>
        {/* Featured card — spans 2 rows */}
        <motion.div
          className={`${styles.bentoItem} ${styles.featured}`}
          ref={reviewsRef}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className={styles.featuredLabel}>Live Stats</span>
          <div className={styles.counters}>
            <div className={styles.counter}>
              <span className={`${styles.counterNum} gradient-text`}>
                {reviewsValue.toLocaleString()}
              </span>
              <span className={styles.counterLabel}>Reviews Verified</span>
            </div>
            <div className={styles.counter} ref={fakesRef}>
              <span className={styles.counterNum} style={{ color: 'var(--red)' }}>
                {fakesValue}
              </span>
              <span className={styles.counterLabel}>Fakes Caught</span>
            </div>
          </div>
          <p className={styles.featuredDesc}>
            Every review passes through 7 specialized AI agents, each trained to
            detect different types of fraud — from text patterns to image manipulation.
          </p>
        </motion.div>

        {/* Regular stat cards */}
        {ITEMS.map((item, i) => (
          <motion.div
            key={item.label}
            className={styles.bentoItem}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 + i * 0.06, duration: 0.5 }}
          >
            <div className={styles.itemIcon} style={{ background: item.bg }}>
              {item.icon}
            </div>
            <div className={styles.itemValue}>{item.value}</div>
            <div className={styles.itemLabel}>{item.label}</div>
            <div className={styles.itemDesc}>{item.desc}</div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
