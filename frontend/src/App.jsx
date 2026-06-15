import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, BarChart3, Info } from 'lucide-react'
import Navbar from './components/Navbar'
import HeroSection from './components/HeroSection'
import BentoStats from './components/BentoStats'
import HowItWorks from './components/HowItWorks'
import Footer from './components/Footer'
import SubmitReview from './pages/SubmitReview'
import ReviewHistory from './pages/ReviewHistory'
import './index.css'

const pageVariants = {
  initial: { opacity: 0, y: 30, filter: 'blur(6px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -20, filter: 'blur(4px)' },
}

// Generate particle config once
const PARTICLE_COLORS = ['violet', 'blue', 'pink', 'cyan']
const PARTICLES = Array.from({ length: 32 }, (_, i) => ({
  id: i,
  size: 2 + Math.random() * 4,
  left: Math.random() * 100,
  delay: Math.random() * 20,
  duration: 18 + Math.random() * 22,
  driftX: -60 + Math.random() * 120,
  color: PARTICLE_COLORS[i % PARTICLE_COLORS.length],
}))

export default function App() {
  const [tab, setTab] = useState('home')
  const appRef = useRef(null)

  // Cursor spotlight
  useEffect(() => {
    const handleMouse = (e) => {
      document.documentElement.style.setProperty('--cursor-x', e.clientX + 'px')
      document.documentElement.style.setProperty('--cursor-y', e.clientY + 'px')
    }
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [])

  const goToSubmit = useCallback(() => {
    setTab('submit')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  const goTo = useCallback((target) => {
    setTab(target)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  return (
    <>
      {/* Background layers */}
      <div className="bg-mesh" />
      <div className="bg-mesh-pink" />
      <div className="bg-noise" />
      <div className="bg-grid" />
      <div className="cursor-glow" />

      {/* Floating particle field */}
      <div className="particles-container">
        {PARTICLES.map(p => (
          <div
            key={p.id}
            className={`particle particle--${p.color}`}
            style={{
              width: p.size,
              height: p.size,
              left: `${p.left}%`,
              animationDelay: `${p.delay}s`,
              animationDuration: `${p.duration}s`,
              '--drift-x': `${p.driftX}px`,
            }}
          />
        ))}
      </div>

      <div className="app-shell" ref={appRef}>
        <Navbar tab={tab} onNavigate={goTo} />

        <AnimatePresence mode="wait">
          {tab === 'home' && (
            <motion.div
              key="home"
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <HeroSection onGetStarted={goToSubmit} />
              <BentoStats />
              <HowItWorks />

              {/* CTA Section */}
              <motion.div
                className="card"
                style={{ textAlign: 'center', padding: '48px 24px', marginTop: 12 }}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.6 }}
              >
                <p className="section-label">Ready?</p>
                <h3 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: 10 }}>
                  Verify Your First Review
                </h3>
                <p style={{ color: 'var(--text-2)', fontSize: '0.92rem', marginBottom: 28, maxWidth: 420, margin: '0 auto 28px' }}>
                  Submit a review and watch 7 AI agents analyze it in real-time with full transparency.
                </p>
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button className="btn-primary" onClick={goToSubmit} style={{ width: 'auto', padding: '14px 36px' }}>
                    Submit a Review →
                  </button>
                  <button className="btn-ghost" onClick={() => goTo('history')} style={{ width: 'auto', padding: '14px 36px' }}>
                    View History
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}

          {(tab === 'submit' || tab === 'history') && (
            <motion.div
              key="app-inner"
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Tab Navigation */}
              <div className="tabs-bar">
                <TabButton
                  active={tab === 'submit'}
                  onClick={() => goTo('submit')}
                  icon={<FileText size={15} />}
                  label="Submit Review"
                />
                <TabButton
                  active={tab === 'history'}
                  onClick={() => goTo('history')}
                  icon={<BarChart3 size={15} />}
                  label="Review History"
                />
                <TabButton
                  active={false}
                  onClick={() => goTo('home')}
                  icon={<Info size={15} />}
                  label="How It Works"
                />
              </div>

              {/* Tab Content */}
              <AnimatePresence mode="wait">
                {tab === 'submit' && (
                  <motion.div
                    key="submit"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -12 }}
                    transition={{ duration: 0.3 }}
                  >
                    <SubmitReview />
                  </motion.div>
                )}
                {tab === 'history' && (
                  <motion.div
                    key="history"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -12 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ReviewHistory />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>

        <Footer />
      </div>
    </>
  )
}

function TabButton({ active, onClick, icon, label }) {
  return (
    <button className={`tab-button ${active ? 'tab-active' : ''}`} onClick={onClick}>
      {icon} {label}
    </button>
  )
}
