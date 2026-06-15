import styles from './Footer.module.css'

const TECH = [
  'LangGraph', 'LangChain', 'Groq', 'Llama 4 Scout', 'React', 'Vite',
  'FastAPI', 'SQLite', 'Framer Motion', 'Vision AI', 'Multi-Agent Pipeline',
  'TrustLens v4.0',
]

export default function Footer() {
  // Duplicate for seamless loop
  const items = [...TECH, ...TECH]

  return (
    <footer className={styles.footer}>
      {/* Gradient shimmer divider */}
      <div className={styles.shimmerDivider} />

      <div className={styles.marqueeWrap}>
        <div className={styles.marqueeTrack}>
          {items.map((name, i) => (
            <span key={i} className={styles.marqueeGroup}>
              <span className={styles.marqueeItem}>{name}</span>
              <span className={styles.marqueeDot}>◆</span>
            </span>
          ))}
        </div>
      </div>

      <div className={styles.footerBottom}>
        <p className={styles.footerText}>
          TrustLens · LangGraph + LangChain + Groq + Llama 4 Scout
        </p>
        <div className={styles.builtWith}>
          <span className={styles.builtDot} />
          Built with AI
        </div>
      </div>
    </footer>
  )
}
