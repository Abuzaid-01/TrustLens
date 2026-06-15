import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, FileText, BarChart3, Home } from 'lucide-react'
import styles from './Navbar.module.css'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function Navbar({ tab, onNavigate }) {
  const [online, setOnline] = useState(true)
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  // Health check
  useEffect(() => {
    const check = () =>
      fetch(`${API}/`)
        .then(r => setOnline(r.ok))
        .catch(() => setOnline(false))
    check()
    const iv = setInterval(check, 15000)
    return () => clearInterval(iv)
  }, [])

  // Scroll detection
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const navigate = (target) => {
    onNavigate?.(target)
    setMenuOpen(false)
  }

  const navItems = [
    { key: 'home', label: 'Home', icon: Home },
    { key: 'submit', label: 'Submit', icon: FileText },
    { key: 'history', label: 'History', icon: BarChart3 },
  ]

  return (
    <>
      <nav className={`${styles.navbar} ${scrolled ? styles.scrolled : ''}`}>
        <div className={styles.brand} onClick={() => navigate('home')}>
          <span className={styles.brandIcon}>🛡️</span>
          <span className={styles.brandName}>TrustLens</span>
          <span className={styles.brandTag}>v3.0</span>
        </div>

        {/* Desktop nav links */}
        <div className={styles.navLinks}>
          {navItems.map(item => (
            <button
              key={item.key}
              className={`${styles.navLink} ${tab === item.key ? styles.navLinkActive : ''}`}
              onClick={() => navigate(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className={styles.navRight}>
          <div className={`${styles.statusBadge} ${online ? '' : styles.offline}`}>
            <div className={styles.statusDot} />
            {online ? 'Live' : 'Offline'}
          </div>

          {/* Hamburger (mobile) */}
          <button className={styles.hamburger} onClick={() => setMenuOpen(true)}>
            <span /><span /><span />
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <>
            <motion.div
              className={styles.mobileOverlay}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMenuOpen(false)}
            />
            <motion.div
              className={styles.mobileMenu}
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              <button className={styles.closeBtn} onClick={() => setMenuOpen(false)}>
                <X size={16} />
              </button>
              {navItems.map(item => (
                <button
                  key={item.key}
                  className={`${styles.mobileMenuLink} ${tab === item.key ? styles.mobileMenuLinkActive : ''}`}
                  onClick={() => navigate(item.key)}
                >
                  <item.icon size={16} style={{ marginRight: 10, verticalAlign: -3 }} />
                  {item.label}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
