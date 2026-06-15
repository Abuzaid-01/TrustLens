import { useEffect, useRef, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  ShieldCheck, Database, Eye, ArrowLeft,
  AlertTriangle, XCircle, Clipboard
} from 'lucide-react'
import styles from './TrustScore.module.css'

const LEVEL_COLORS = { high: '#22c55e', medium: '#f59e0b', low: '#ef4444' }
const CONFETTI_COLORS = ['#a855f7', '#22c55e', '#3b82f6', '#f59e0b', '#ec4899', '#6366f1', '#06b6d4']
const CONFETTI_SHAPES = ['circle', 'rect', 'diamond']
const CONFETTI_PIECES = Array.from({ length: 24 }, (_, i) => ({
  id: i,
  shape: CONFETTI_SHAPES[i % CONFETTI_SHAPES.length],
  left: 20 + Math.random() * 60,
  color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
  delay: Math.random() * 0.4,
  duration: 1.2 + Math.random() * 0.8,
  rotation: Math.random() * 360,
}))

// Radar dimensions for 6-axis chart
const RADAR_DIMS = ['Purchase', 'Consistency', 'Duplicate', 'Behavior', 'Media', 'Overall']
const RADAR_CENTER = 50
const RADAR_R = 38

function polarToCart(angle, radius) {
  const rad = (angle - 90) * (Math.PI / 180)
  return {
    x: RADAR_CENTER + radius * Math.cos(rad),
    y: RADAR_CENTER + radius * Math.sin(rad),
  }
}

function getRadarPoints(values, maxR = RADAR_R) {
  return values.map((v, i) => {
    const angle = (360 / values.length) * i
    return polarToCart(angle, v * maxR)
  })
}

function RadarChart({ values, color }) {
  const gridLevels = [0.25, 0.5, 0.75, 1.0]
  const points = getRadarPoints(values)
  const polygon = points.map(p => `${p.x},${p.y}`).join(' ')

  return (
    <div className={styles.radarContainer}>
      <svg className={styles.radarSvg} viewBox="0 0 100 100">
        {/* Grid rings */}
        {gridLevels.map(level => {
          const gp = getRadarPoints(Array(6).fill(level))
          return (
            <polygon
              key={level}
              className={styles.radarGridLine}
              points={gp.map(p => `${p.x},${p.y}`).join(' ')}
            />
          )
        })}

        {/* Axis lines */}
        {RADAR_DIMS.map((_, i) => {
          const end = polarToCart((360 / 6) * i, RADAR_R)
          return (
            <line
              key={i}
              x1={RADAR_CENTER} y1={RADAR_CENTER}
              x2={end.x} y2={end.y}
              className={styles.radarAxis}
            />
          )
        })}

        {/* Data polygon */}
        <motion.polygon
          className={styles.radarArea}
          points={polygon}
          initial={{ opacity: 0, scale: 0.3 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
          style={{ transformOrigin: '50% 50%', fill: `${color}18`, stroke: color }}
        />

        {/* Data dots */}
        {points.map((p, i) => (
          <motion.circle
            key={i}
            cx={p.x} cy={p.y} r="1.8"
            className={styles.radarDot}
            style={{ fill: color }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5 + i * 0.06, type: 'spring' }}
          />
        ))}

        {/* Labels */}
        {RADAR_DIMS.map((label, i) => {
          const pos = polarToCart((360 / 6) * i, RADAR_R + 8)
          return (
            <text key={i} x={pos.x} y={pos.y + 1} className={styles.radarLabel}>
              {label}
            </text>
          )
        })}
      </svg>
    </div>
  )
}

// Animated count-up hook
function useCountUp(target, duration = 1200) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    const startTime = Date.now()
    const tick = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(eased * target))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [target, duration])
  return value
}

function Confetti() {
  return (
    <div className={styles.confettiWrap}>
      {CONFETTI_PIECES.map(piece => (
        <div
          key={piece.id}
          className={`${styles.confettiPiece} ${styles[`confetti_${piece.shape}`]}`}
          style={{
            left: `${piece.left}%`,
            top: '-10px',
            background: piece.color,
            animationDelay: `${piece.delay}s`,
            animationDuration: `${piece.duration}s`,
            transform: `rotate(${piece.rotation}deg)`,
          }}
        />
      ))}
    </div>
  )
}

// Orbital particles around the ring
function OrbitalParticles({ color }) {
  return (
    <div className={styles.orbitalWrap}>
      {[0, 1, 2, 3].map(i => (
        <div
          key={i}
          className={styles.orbitalDot}
          style={{
            animationDelay: `${i * 1.2}s`,
            background: color,
            boxShadow: `0 0 8px ${color}80`,
          }}
        />
      ))}
    </div>
  )
}

export default function TrustScore({ result, onReset }) {
  const ringRef = useRef(null)
  const score = result.final_trust_score || 0
  const level = (result.trust_level || 'medium').toLowerCase()
  const color = LEVEL_COLORS[level] || LEVEL_COLORS.medium
  const bd = useMemo(() => result.breakdown || {}, [result.breakdown])
  const media = result.media_analysis
  const animatedScore = useCountUp(score, 1400)
  const hasMedia = (bd.media_points ?? 0) > 0 || !!media

  // Radar values (normalized 0-1)
  const radarValues = useMemo(() => {
    const maxPurch = hasMedia ? 25 : 30
    const maxCons = hasMedia ? 25 : 30
    const maxDup = hasMedia ? 15 : 20
    const maxBeh = hasMedia ? 15 : 20
    return [
      (bd.purchase_points ?? 0) / maxPurch,
      (bd.consistency_points ?? 0) / maxCons,
      (bd.duplicate_points ?? 0) / maxDup,
      (bd.behavior_points ?? 0) / maxBeh,
      hasMedia ? (bd.media_points ?? 0) / 20 : 0.1,
      Math.min(1, (score ?? 0) / 100),
    ]
  }, [bd, hasMedia, score])

  useEffect(() => {
    if (!ringRef.current) return
    const circumference = 2 * Math.PI * 76
    const offset = circumference - (score / 100) * circumference
    requestAnimationFrame(() => {
      ringRef.current.style.strokeDashoffset = offset
      ringRef.current.style.stroke = color
    })
  }, [score, color])

  const circumference = 2 * Math.PI * 76

  const VerdictIcon = level === 'high' ? ShieldCheck : level === 'medium' ? AlertTriangle : XCircle
  const verdictClass = level === 'high' ? styles.verdictHigh
    : level === 'medium' ? styles.verdictMedium : styles.verdictLow

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 30, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{ position: 'relative', overflow: 'visible' }}
    >
      {/* Confetti for high scores */}
      {level === 'high' && <Confetti />}

      {/* Verdict Card with animated border */}
      <motion.div
        className={`${styles.verdictCard} ${verdictClass}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.5 }}
      >
        <div className={styles.verdictIcon}>
          <VerdictIcon size={26} />
        </div>
        <div className={styles.verdictBody}>
          <div className={styles.verdictLevel}>
            {result.trust_level} Trust — {result.action === 'approve' ? 'Approved' : result.action === 'reject' ? 'Rejected' : 'Needs Review'}
          </div>
          <div className={styles.verdictText}>
            {result.recommendation || 'Analysis complete.'}
          </div>
        </div>
        <div className={styles.verdictBadge}>
          {result.action?.toUpperCase()}
        </div>
      </motion.div>

      {/* Score Ring + Radar */}
      <div className={styles.scoreArea}>
        <div className={styles.ringContainer}>
          {/* Pulsing glow behind ring */}
          <div className={styles.ringGlow} style={{ background: `radial-gradient(circle, ${color}15 0%, transparent 70%)` }} />

          {/* Orbital particles */}
          <OrbitalParticles color={color} />

          <svg className={styles.ring} viewBox="0 0 170 170">
            <circle className={styles.ringBg} cx="85" cy="85" r="76" />
            <circle
              ref={ringRef}
              className={styles.ringFill}
              cx="85" cy="85" r="76"
              strokeDasharray={circumference}
              strokeDashoffset={circumference}
            />
          </svg>
          <div className={styles.scoreValue}>
            <motion.span
              className={styles.scoreNum}
              style={{ color }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              {animatedScore}
            </motion.span>
            <span className={styles.scoreSuffix}>/ 100</span>
          </div>
        </div>

        {result.db_verified && (
          <div className={styles.dbBadge}>
            <Database size={12} />
            Database Verified
          </div>
        )}

        <RadarChart values={radarValues} color={color} />
      </div>

      {/* Breakdown */}
      <p className="section-label">Breakdown</p>
      <h3 className={styles.sectionTitle}>Verification Results</h3>
      <p className={styles.sectionSub}>Points awarded by each verification agent</p>

      <div className={styles.grid}>
        {(() => {
          const items = [
            { label: 'Purchase Verification', pts: bd.purchase_points, max: hasMedia ? 25 : 30 },
            { label: 'Consistency Check', pts: bd.consistency_points, max: hasMedia ? 25 : 30 },
            { label: 'Duplicate Detection', pts: bd.duplicate_points, max: hasMedia ? 15 : 20 },
            { label: 'Reviewer Behavior', pts: bd.behavior_points, max: hasMedia ? 15 : 20 },
          ]
          if (hasMedia) {
            items.push({ label: 'Media Verification', pts: bd.media_points, max: 20 })
          }
          return items.map((item, i) => (
            <motion.div
              key={item.label}
              className={styles.breakdownCard}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className={styles.breakdownLabel}>{item.label}</div>
              <div className={styles.breakdownRow}>
                <span className={styles.breakdownPts}>{item.pts ?? 0}</span>
                <span className={styles.breakdownMax}>/ {item.max}</span>
              </div>
              <div className={styles.bar}>
                <motion.div
                  className={styles.barFill}
                  initial={{ width: 0 }}
                  animate={{ width: `${((item.pts ?? 0) / item.max) * 100}%` }}
                  transition={{
                    delay: 0.7 + i * 0.1,
                    duration: 1,
                    type: 'spring',
                    stiffness: 60,
                    damping: 15,
                  }}
                  style={{ background: color }}
                />
              </div>
            </motion.div>
          ))
        })()}

        {/* No media card */}
        {!hasMedia && (
          <motion.div
            className={styles.breakdownCard}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            style={{ opacity: 0.4 }}
          >
            <div className={styles.breakdownLabel}>Media Verification</div>
            <div className={styles.breakdownRow}>
              <span className={styles.breakdownPts} style={{ fontSize: '0.9rem' }}>N/A</span>
            </div>
            <div className={styles.bar} />
            <div style={{ fontSize: '0.68rem', color: 'var(--text-3)', marginTop: 4 }}>No photos uploaded</div>
          </motion.div>
        )}
      </div>

      {/* Vision Analysis */}
      {media && (
        <motion.div
          className={styles.visionCard}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
        >
          <h4 className={styles.visionTitle}>
            <Eye size={16} /> AI Vision Analysis
          </h4>
          <div className={styles.visionRow}>
            <span className={styles.visionLabel}>What AI Sees</span>
            <span className={styles.visionVal}>{media.image_description || 'N/A'}</span>
          </div>
          <div className={styles.visionRow}>
            <span className={styles.visionLabel}>Matches Review</span>
            <span className={styles.visionVal}>
              {media.matches_review ? '✅ Yes' : '❌ No'} ({Math.round(media.match_score * 100)}%)
            </span>
          </div>
          {media.match_explanation && (
            <div className={styles.visionRow}>
              <span className={styles.visionLabel}>Explanation</span>
              <span className={styles.visionVal}>{media.match_explanation}</span>
            </div>
          )}
        </motion.div>
      )}

      {/* Recommendation */}
      <motion.div
        className={styles.recCard}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.1 }}
      >
        <h4><Clipboard size={15} /> Recommendation</h4>
        <p>{result.recommendation || '--'}</p>
      </motion.div>

      <button className="btn-ghost" onClick={onReset} style={{ marginTop: 8 }}>
        <ArrowLeft size={16} style={{ marginRight: 8, verticalAlign: -3 }} />
        Submit Another Review
      </button>
    </motion.div>
  )
}
