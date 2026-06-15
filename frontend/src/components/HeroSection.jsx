import { useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, ArrowRight, Zap, Lock, Brain } from 'lucide-react'
import styles from './HeroSection.module.css'

const WORDS = ['Verify', 'Every', 'Review', 'With', '7', 'AI', 'Agents']
const GRADIENT_WORDS = [0, 5, 6] // 'Verify', 'AI', 'Agents' get gradient

const LOGOS = [
  { name: 'Acme Co', icon: Zap },
  { name: 'Veritas', icon: Lock },
  { name: 'NovaTech', icon: Brain },
  { name: 'Helix', icon: ShieldCheck },
  { name: 'Prism AI', icon: Zap },
]

const MOCK_BARS = [
  { label: 'Purchase', pct: 92, color: '#22c55e' },
  { label: 'Consistency', pct: 88, color: '#a855f7' },
  { label: 'Duplicate', pct: 95, color: '#3b82f6' },
  { label: 'Behavior', pct: 85, color: '#06b6d4' },
]

export default function HeroSection({ onGetStarted }) {
  const cardRef = useRef(null)

  // Parallax on mouse move
  const handleMouse = useCallback((e) => {
    if (!cardRef.current) return
    const rect = cardRef.current.parentElement.getBoundingClientRect()
    const x = (e.clientX - rect.left - rect.width / 2) / 20
    const y = (e.clientY - rect.top - rect.height / 2) / 20
    cardRef.current.style.transform = `rotateY(${x}deg) rotateX(${-y}deg) translateZ(12px)`
  }, [])

  const handleLeave = useCallback(() => {
    if (!cardRef.current) return
    cardRef.current.style.transform = 'rotateY(0deg) rotateX(0deg) translateZ(0px)'
  }, [])

  return (
    <>
      <div className={styles.hero}>
        {/* Left: Headline + CTA */}
        <div className={styles.heroLeft}>
          <motion.div
            className={styles.heroBadge}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <span className={styles.heroBadgeDot} />
            AI-Powered Verification
          </motion.div>

          <h1 className={styles.headline}>
            {WORDS.map((word, i) => (
              <motion.span
                key={i}
                className={`${styles.word} ${GRADIENT_WORDS.includes(i) ? styles.wordGlow : ''}`}
                initial={{ opacity: 0, y: 24, filter: 'blur(6px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                transition={{
                  delay: 0.15 + i * 0.08,
                  duration: 0.6,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                {word}
              </motion.span>
            ))}
          </h1>

          {/* Animated underline */}
          <motion.div
            className={styles.headlineUnderline}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.8, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          />

          <motion.p
            className={styles.heroSub}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            Our multi-agent pipeline powered by LangGraph, Groq, and Vision AI
            validates every review against real purchase data, detecting fakes
            with 95%+ accuracy.
          </motion.p>

          <motion.div
            className={styles.heroCtas}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.85 }}
          >
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started <ArrowRight size={16} style={{ marginLeft: 6, verticalAlign: -3 }} />
            </button>
            <button className="btn-ghost" onClick={() => {
              document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
            }}>
              See How It Works
            </button>
          </motion.div>
        </div>

        {/* Right: Floating mockup card */}
        <div
          className={styles.heroRight}
          onMouseMove={handleMouse}
          onMouseLeave={handleLeave}
        >
          <motion.div
            ref={cardRef}
            className={styles.mockupCard}
            initial={{ opacity: 0, scale: 0.85, rotateY: -15 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{ delay: 0.5, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Rotating border glow */}
            <div className={styles.mockupBorderGlow} />

            <div className={styles.mockupInner}>
              <div className={styles.mockupHeader}>
                <div className={styles.mockupDots}>
                  <span /><span /><span />
                </div>
                <span className={styles.mockupTitle}>Trust Analysis</span>
              </div>

              <div className={styles.mockupScoreWrap}>
                <div className={styles.mockupScoreGlow} />
                <div className={styles.mockupScore} style={{ color: 'var(--green)' }}>87</div>
                <div className={styles.mockupLabel}>Trust Score / 100</div>
              </div>

              {MOCK_BARS.map((bar, i) => (
                <div key={bar.label} className={styles.mockupBarRow}>
                  <span className={styles.mockupBarLabel}>{bar.label}</span>
                  <div className={styles.mockupBar}>
                    <motion.div
                      className={styles.mockupBarFill}
                      style={{ background: bar.color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${bar.pct}%` }}
                      transition={{ delay: 1 + i * 0.15, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    />
                  </div>
                  <span className={styles.mockupBarPct}>{bar.pct}%</span>
                </div>
              ))}

              <div className={styles.mockupBadge}>
                <ShieldCheck size={12} /> High Trust — Approved
              </div>
            </div>
          </motion.div>

          {/* Floating accent elements behind the card */}
          <div className={styles.floatingOrb1} />
          <div className={styles.floatingOrb2} />
        </div>
      </div>

      {/* Trusted-by logos */}
      <motion.div
        className={styles.trustedBy}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <div className={styles.trustedByLabel}>Trusted by innovative companies</div>
        <div className={styles.logoStrip}>
          {LOGOS.map(({ name, icon: Icon }) => (
            <div key={name} className={styles.logoPlaceholder}>
              <Icon size={12} style={{ opacity: 0.5 }} />
              <span>{name}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </>
  )
}
