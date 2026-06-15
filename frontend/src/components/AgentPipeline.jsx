import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ClipboardList, CreditCard, GitCompare, Copy,
  UserCheck, Image, ShieldCheck, Check, Terminal
} from 'lucide-react'
import styles from './AgentPipeline.module.css'

const AGENTS = [
  { id: 'intake', label: 'Intake', icon: ClipboardList, row: 0, col: 0 },
  { id: 'purchase', label: 'Purchase', icon: CreditCard, row: 0, col: 1 },
  { id: 'consistency', label: 'Consistency', icon: GitCompare, row: 0, col: 2 },
  { id: 'duplicate', label: 'Duplicate', icon: Copy, row: 0, col: 3 },
  { id: 'behavior', label: 'Behavior', icon: UserCheck, row: 1, col: 0 },
  { id: 'media_auth', label: 'Media Auth', icon: Image, row: 1, col: 1 },
  { id: 'trust_score', label: 'Trust Score', icon: ShieldCheck, row: 1, col: 2 },
]

const EDGES = [
  ['intake', 'purchase'],
  ['purchase', 'consistency'],
  ['consistency', 'duplicate'],
  ['duplicate', 'behavior'],
  ['behavior', 'media_auth'],
  ['media_auth', 'trust_score'],
]

const TERMINAL_LOGS = [
  { agent: 'Intake', msg: 'parsed review — 342 chars, 3 entities detected', type: 'success' },
  { agent: 'Purchase', msg: 'order verified in DB — customer match confirmed', type: 'success' },
  { agent: 'Consistency', msg: 'cross-check score 0.92 — review matches purchase data', type: 'success' },
  { agent: 'Duplicate', msg: 'plagiarism scan: 0% match — original content confirmed', type: 'success' },
  { agent: 'Behavior', msg: 'reviewer pattern: first-time reviewer — clean history', type: 'success' },
  { agent: 'Media Auth', msg: 'vision scan skipped — no images uploaded', type: 'info' },
  { agent: 'Trust Score', msg: 'aggregated: 85/100 — HIGH trust — recommend APPROVE', type: 'success' },
]

function getNodePos(row, col) {
  const xPositions = [12, 37, 63, 88]
  const yPositions = [30, 75]
  return { x: xPositions[col], y: yPositions[row] }
}

function getSvgPath(from, to) {
  const dx = to.x - from.x
  const cx1 = from.x + dx * 0.4
  const cy1 = from.y
  const cx2 = to.x - dx * 0.4
  const cy2 = to.y
  return `M ${from.x} ${from.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${to.x} ${to.y}`
}

export default function AgentPipeline() {
  const [currentStep, setCurrentStep] = useState(0)
  const [doneSteps, setDoneSteps] = useState([])
  const [showBurst, setShowBurst] = useState(null)
  const [terminalLines, setTerminalLines] = useState([])

  // Simulate pipeline progression
  useEffect(() => {
    if (currentStep >= AGENTS.length) return

    const timer = setTimeout(() => {
      setDoneSteps(prev => [...prev, currentStep])
      setShowBurst(currentStep)
      setTimeout(() => setShowBurst(null), 600)

      // Add terminal log line
      setTerminalLines(prev => [...prev, {
        ...TERMINAL_LOGS[currentStep],
        time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      }])

      setCurrentStep(prev => prev + 1)
    }, 700 + currentStep * 100)

    return () => clearTimeout(timer)
  }, [currentStep])

  const positions = useMemo(() =>
    AGENTS.map(a => getNodePos(a.row, a.col)), [])

  const getStatus = (idx) => {
    if (doneSteps.includes(idx)) return 'done'
    if (idx === currentStep) return 'active'
    return 'waiting'
  }

  const getEdgeStatus = (fromIdx, toIdx) => {
    if (doneSteps.includes(toIdx)) return 'done'
    if (currentStep === toIdx && doneSteps.includes(fromIdx)) return 'active'
    return 'waiting'
  }

  const outputSnippets = ['Parsed', 'Verified', 'Score: 0.9', 'Original', 'Clean', 'Skipped', 'Score: 85']

  return (
    <div className={`card ${styles.container}`}>
      <p className="section-label" style={{ textAlign: 'center' }}>Pipeline</p>
      <h3 className={styles.title}>Agent Verification Pipeline</h3>
      <p className={styles.subtitle} style={{ maxWidth: 480 }}>
        7 AI agents processing your review through a directed acyclic graph
      </p>

      {/* ── Desktop: DAG Graph ── */}
      <div className={styles.dagContainer}>
        {/* Scan-line overlay */}
        <div className={styles.scanLine} />

        {/* SVG layer for edges + data packets */}
        <svg className={styles.dagSvg} viewBox="0 0 100 100" preserveAspectRatio="none">
          {EDGES.map(([fromId, toId], i) => {
            const fromIdx = AGENTS.findIndex(a => a.id === fromId)
            const toIdx = AGENTS.findIndex(a => a.id === toId)
            const from = positions[fromIdx]
            const to = positions[toIdx]
            const pathD = getSvgPath(from, to)
            const status = getEdgeStatus(fromIdx, toIdx)

            return (
              <g key={i}>
                <path
                  d={pathD}
                  className={`${styles.pathLine} ${
                    status === 'active' ? styles.pathActive : ''
                  } ${status === 'done' ? styles.pathDone : ''}`}
                  vectorEffect="non-scaling-stroke"
                />
                {status === 'active' && (
                  <circle r="1.2" className={styles.dataPacket}>
                    <animateMotion
                      dur="0.8s"
                      repeatCount="indefinite"
                      path={pathD}
                    />
                  </circle>
                )}
              </g>
            )
          })}
        </svg>

        {/* Nodes layer */}
        <div className={styles.nodesLayer}>
          {AGENTS.map((agent, idx) => {
            const pos = positions[idx]
            const status = getStatus(idx)
            const Icon = agent.icon
            const statusClass = status === 'active' ? styles.nodeActive
              : status === 'done' ? styles.nodeDone
              : styles.nodeWaiting

            return (
              <motion.div
                key={agent.id}
                className={`${styles.nodeWrap} ${statusClass}`}
                style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.08, type: 'spring', stiffness: 200 }}
              >
                <div className={styles.nodeCircle}>
                  <div className={styles.nodeRing} />

                  <AnimatePresence>
                    {showBurst === idx && (
                      <motion.div
                        className={styles.burstContainer}
                        initial={{ opacity: 1 }}
                        animate={{ opacity: 0 }}
                        transition={{ duration: 0.6 }}
                      >
                        <div className={styles.burstRing} />
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {status === 'done' ? (
                    <motion.div
                      initial={{ scale: 0, rotate: -90 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    >
                      <Check size={22} strokeWidth={3} />
                    </motion.div>
                  ) : (
                    <Icon size={20} />
                  )}
                </div>

                <span className={styles.nodeLabel}>{agent.label}</span>

                <AnimatePresence>
                  {status === 'done' && (
                    <motion.span
                      className={styles.nodeOutput}
                      initial={{ opacity: 0, y: 6, scale: 0.8 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{ type: 'spring', stiffness: 200 }}
                    >
                      ✓ {outputSnippets[idx]}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* ── Terminal Log ── */}
      <div className={styles.terminalWrap}>
        <div className={styles.terminalHeader}>
          <Terminal size={13} />
          <span>Agent Output Log</span>
          <div className={styles.terminalDots}>
            <span /><span /><span />
          </div>
        </div>
        <div className={styles.terminalBody}>
          {terminalLines.map((line, i) => (
            <motion.div
              key={i}
              className={styles.terminalLine}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <span className={styles.termTime}>[{line.time}]</span>
              <span className={line.type === 'success' ? styles.termSuccess : styles.termInfo}>✓</span>
              <span className={styles.termAgent}>{line.agent}</span>
              <span className={styles.termMsg}>— {line.msg}</span>
            </motion.div>
          ))}
          {currentStep < AGENTS.length && (
            <div className={styles.terminalLine}>
              <span className={styles.termCursor}>█</span>
              <span className={styles.termProcessing}>Processing {AGENTS[currentStep]?.label}...</span>
            </div>
          )}
          {currentStep >= AGENTS.length && (
            <motion.div
              className={`${styles.terminalLine} ${styles.termComplete}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <span className={styles.termTime}>[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
              <span style={{ color: 'var(--green)' }}>✅</span>
              <span style={{ color: 'var(--green)', fontWeight: 600 }}>Pipeline Complete — All 7 agents finished successfully</span>
            </motion.div>
          )}
        </div>
      </div>

      {/* ── Mobile: Vertical Steps ── */}
      <div className={styles.mobileSteps}>
        {AGENTS.map((agent, idx) => {
          const status = getStatus(idx)
          return (
            <motion.div
              key={agent.id}
              className={`${styles.mobileStep} ${
                status === 'active' ? styles.mobileStepActive :
                status === 'done' ? styles.mobileStepDone : ''
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.08 }}
            >
              <div className={styles.mobileStepLine + ' ' + (
                status === 'active' ? styles.mobileStepLineActive :
                status === 'done' ? styles.mobileStepLineDone : ''
              )} />
              <div className={styles.mobileStepNum}>
                {status === 'done' ? <Check size={16} strokeWidth={3} /> : idx + 1}
              </div>
              <div className={styles.mobileStepBody}>
                <div className={styles.mobileStepName}>{agent.label} Agent</div>
                <div className={styles.mobileStepStatus}>
                  {status === 'done' ? `✓ ${outputSnippets[idx]}` :
                   status === 'active' ? 'Processing...' : 'Waiting'}
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Status bar */}
      <div className={styles.statusBar}>
        {currentStep < AGENTS.length ? (
          <>
            <div className={styles.statusDot} />
            Processing: {AGENTS[currentStep]?.label} Agent
          </>
        ) : (
          <>✅ Pipeline Complete — All 7 agents finished</>
        )}
      </div>
    </div>
  )
}
