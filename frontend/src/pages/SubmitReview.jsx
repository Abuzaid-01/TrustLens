import { useState, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageSquareText, Store, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'
import OrderValidator from '../components/OrderValidator'
import ImageUpload from '../components/ImageUpload'
import AgentPipeline from '../components/AgentPipeline'
import TrustScore from '../components/TrustScore'
import { submitReview } from '../api/client'
import styles from './SubmitReview.module.css'

// Simple readability score (Flesch-like approximation)
function getReadability(text) {
  if (!text || text.length < 10) return { score: 0, label: '—', color: 'var(--text-3)' }
  const words = text.trim().split(/\s+/).length
  const sentences = (text.match(/[.!?]+/g) || []).length || 1
  const avgWordLen = text.replace(/\s/g, '').length / words
  // Simple heuristic: shorter words & shorter sentences = easier to read
  const score = Math.max(0, Math.min(100, Math.round(100 - (avgWordLen * 8) - (words / sentences * 2))))
  if (score >= 70) return { score, label: 'Easy', color: 'var(--green)' }
  if (score >= 40) return { score, label: 'Normal', color: 'var(--amber)' }
  return { score, label: 'Complex', color: 'var(--red)' }
}

export default function SubmitReview() {
  const [orderData, setOrderData] = useState(null)
  const [reviewText, setReviewText] = useState('')
  const [files, setFiles] = useState([])
  const [phase, setPhase] = useState('form')
  const [result, setResult] = useState(null)

  const wordCount = useMemo(() => reviewText.trim() ? reviewText.trim().split(/\s+/).length : 0, [reviewText])
  const readability = useMemo(() => getReadability(reviewText), [reviewText])
  const isValid = orderData && reviewText.trim().length >= 10

  const handleOrderValidated = useCallback((data) => {
    setOrderData(data)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!isValid) return

    setPhase('pipeline')

    try {
      const res = await submitReview({
        businessId: orderData.business_id,
        billId: orderData.order_id,
        reviewText,
        images: files,
      })
      await new Promise(r => setTimeout(r, 5200))
      setResult(res)
      setPhase('result')
      toast.success(`Trust Score: ${res.final_trust_score}/100 — ${res.trust_level}`)
    } catch (err) {
      toast.error(`Error: ${err.message}`)
      setPhase('form')
    }
  }

  const reset = () => {
    setOrderData(null)
    setReviewText('')
    setFiles([])
    setResult(null)
    setPhase('form')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <AnimatePresence mode="wait">
      {phase === 'form' && (
        <motion.div
          key="form"
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.4 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <Sparkles size={18} style={{ color: 'var(--accent)' }} />
            <h2 className={styles.title}>Submit Your Review</h2>
          </div>
          <p className={styles.subtitle}>
            Enter your order ID to verify your purchase, then share your honest experience.
            Our 7 AI agents will analyze your review in real-time.
          </p>

          <form onSubmit={handleSubmit}>
            <OrderValidator onValidated={handleOrderValidated} />

            <AnimatePresence>
              {orderData && (
                <motion.div
                  className={styles.formGroup}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label className="label"><Store size={15} /> Business</label>
                  <input
                    className="input"
                    value={orderData.business_name || orderData.business_id}
                    readOnly
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <div className={styles.formGroup}>
              <label className="label"><MessageSquareText size={15} /> Your Review</label>
              <textarea
                className="input textarea"
                value={reviewText}
                onChange={e => setReviewText(e.target.value)}
                placeholder="Share your honest experience... Be specific about what you liked or disliked, the quality of service, and any other details."
                required
              />

              {/* Text metadata: word count + readability */}
              <div className={styles.textMeta}>
                <div className={styles.charCount}>
                  <span>{reviewText.length} chars</span>
                  <span>{wordCount} words</span>
                  {reviewText.length > 0 && reviewText.length < 10 && (
                    <span className={styles.minWarning}>min 10 chars</span>
                  )}
                </div>

                {wordCount >= 3 && (
                  <div className={styles.readabilityBar}>
                    <div
                      className={styles.readabilityDot}
                      style={{ background: readability.color }}
                    />
                    {readability.label} readability
                  </div>
                )}
              </div>
            </div>

            <ImageUpload files={files} setFiles={setFiles} />

            <button type="submit" className="btn-primary" disabled={!isValid}>
              <Send size={16} style={{ marginRight: 8, verticalAlign: -3 }} />
              {files.length > 0
                ? `Verify Review + ${files.length} Image${files.length > 1 ? 's' : ''}`
                : 'Verify & Submit Review'
              }
            </button>
          </form>
        </motion.div>
      )}

      {phase === 'pipeline' && (
        <motion.div
          key="pipeline"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <AgentPipeline />
        </motion.div>
      )}

      {phase === 'result' && result && (
        <motion.div
          key="result"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <TrustScore result={result} onReset={reset} />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
