import { motion } from 'framer-motion'
import { FileText, Database, BarChart3, Bot, Eye, Star, Save, ArrowRight } from 'lucide-react'
import styles from './HowItWorks.module.css'

const STEPS = [
  {
    icon: FileText,
    num: '01',
    name: 'Review Intake',
    desc: 'Analyzes review content and decides which verification agents to activate based on the text and media.',
    color: '#3b82f6',
  },
  {
    icon: Database,
    num: '02',
    name: 'Purchase Verification',
    desc: 'Checks the order ID against our real SQLite database — verifying customer name, items purchased, and amount.',
    color: '#06b6d4',
  },
  {
    icon: BarChart3,
    num: '03',
    name: 'Experience Consistency',
    desc: 'Detects contradictions, impossible claims, exaggerations, and inconsistencies in the review text.',
    color: '#f59e0b',
  },
  {
    icon: Bot,
    num: '04',
    name: 'Text Authenticity',
    desc: 'Uses AI to detect machine-generated text, spam patterns, template reviews, and suspicious language.',
    color: '#a855f7',
  },
  {
    icon: Eye,
    num: '05',
    name: 'Vision Analysis',
    desc: 'Llama 4 Scout vision model inspects uploaded photos — checking if image content matches the review text.',
    color: '#ec4899',
  },
  {
    icon: Star,
    num: '06',
    name: 'Trust Score',
    desc: 'Aggregates all signals into a final 0–100 trust score with a High/Medium/Low verdict and action recommendation.',
    color: '#eab308',
  },
]

export default function HowItWorks() {
  return (
    <section className={styles.section} id="how-it-works">
      <motion.div
        className={styles.header}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <span className={styles.sectionBadge}>Agent Workflow</span>
        <h2 className={styles.sectionTitle}>How TrustLens Works</h2>
        <p className={styles.sectionDesc}>
          Every review passes through 7 specialized AI agents connected in a LangGraph state machine.
          Each agent adds verified data points before the final trust score is calculated.
        </p>
      </motion.div>

      <div className={styles.timeline}>
        {STEPS.map((step, i) => {
          const Icon = step.icon
          return (
            <motion.div
              key={step.num}
              className={styles.step}
              initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className={styles.stepLine}>
                <div
                  className={styles.stepDot}
                  style={{ background: step.color, boxShadow: `0 0 16px ${step.color}40` }}
                />
                {i < STEPS.length - 1 && <div className={styles.connector} />}
              </div>

              <div className={styles.stepCard}>
                <div className={styles.stepHeader}>
                  <div className={styles.stepIcon} style={{ background: `${step.color}15`, borderColor: `${step.color}30` }}>
                    <Icon size={20} style={{ color: step.color }} />
                  </div>
                  <div>
                    <span className={styles.stepNum} style={{ color: step.color }}>{step.num}</span>
                    <h3 className={styles.stepName}>{step.name}</h3>
                  </div>
                </div>
                <p className={styles.stepDesc}>{step.desc}</p>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Flow diagram mini */}
      <motion.div
        className={styles.flowDiagram}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className={styles.flowTitle}>
          <Save size={14} /> End-to-End Pipeline
        </div>
        <div className={styles.flowRow}>
          {['Intake', 'Purchase', 'Consistency', 'Text Auth', 'Vision', 'Trust Score', 'Save DB'].map((name, i) => (
            <span key={name} className={styles.flowItem}>
              <span className={styles.flowNode}>{name}</span>
              {i < 6 && <ArrowRight size={14} className={styles.flowArrow} />}
            </span>
          ))}
        </div>
      </motion.div>
    </section>
  )
}
