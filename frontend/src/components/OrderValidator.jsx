import { useState, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Hash, Check, X, Calendar, DollarSign, Package } from 'lucide-react'
import styles from './OrderValidator.module.css'

const API = import.meta.env.VITE_API_URL || 'https://trustlens-ille.onrender.com'

export default function OrderValidator({ onValidated }) {
  const [orderId, setOrderId] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [data, setData] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')
  const timerRef = useRef(null)

  const lookup = useCallback(async (id) => {
    if (!id || id.length < 4) {
      setStatus('idle')
      setData(null)
      onValidated(null)
      return
    }

    setStatus('loading')

    try {
      const res = await fetch(`${API}/api/orders/lookup?order_id=${encodeURIComponent(id)}`)
      const json = await res.json()

      if (json.found && !json.already_reviewed) {
        setStatus('success')
        setData(json)
        onValidated(json)
      } else {
        setStatus('error')
        setErrorMsg(json.already_reviewed
          ? 'This order has already been reviewed.'
          : 'Order not found in our database. Check your ID.')
        setData(null)
        onValidated(null)
      }
    } catch {
      setStatus('error')
      setErrorMsg('Cannot reach server. Is the backend running?')
      setData(null)
      onValidated(null)
    }
  }, [onValidated])

  const handleChange = (e) => {
    const val = e.target.value.toUpperCase()
    setOrderId(val)
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => lookup(val), 500)
  }

  return (
    <div className={styles.wrapper}>
      <label className="label"><Hash size={15} /> Order ID</label>
      <div className={styles.inputRow}>
        <input
          className="input"
          value={orderId}
          onChange={handleChange}
          placeholder="Enter your order/bill ID (e.g., BILL_SBX20260115_789)"
          style={{ paddingRight: 44 }}
        />

        {/* Status icon — morphing spinner → check/X */}
        <div className={styles.statusIcon}>
          <AnimatePresence mode="wait">
            {status === 'loading' && (
              <motion.div
                key="spin"
                className={styles.spinner}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              />
            )}
            {status === 'success' && (
              <motion.div
                key="check"
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                exit={{ scale: 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <Check size={20} color="var(--green)" strokeWidth={3} />
              </motion.div>
            )}
            {status === 'error' && (
              <motion.div
                key="x"
                initial={{ scale: 0, rotate: 90 }}
                animate={{ scale: 1, rotate: 0 }}
                exit={{ scale: 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <X size={20} color="var(--red)" strokeWidth={3} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Success: customer info + item chips */}
      <AnimatePresence>
        {status === 'success' && data && (
          <motion.div
            className={styles.successBanner}
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: 'auto', marginTop: 12 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className={styles.customerName}>
              <Check size={14} /> {data.customer_name}
            </div>

            <div className={styles.orderMeta}>
              <span><Calendar size={11} style={{ verticalAlign: -1.5 }} /> {data.order_date?.split(' ')[0]}</span>
              <span><DollarSign size={11} style={{ verticalAlign: -1.5 }} /> ${data.amount}</span>
              <span><Package size={11} style={{ verticalAlign: -1.5 }} /> {data.items?.length || 0} items</span>
            </div>

            <div className={styles.chipRow}>
              {(data.items || []).map((item, i) => (
                <motion.span
                  key={item}
                  className={styles.chip}
                  initial={{ opacity: 0, scale: 0.5, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  transition={{
                    delay: 0.15 + i * 0.08,
                    type: 'spring',
                    stiffness: 200,
                    damping: 15,
                  }}
                >
                  {item}
                </motion.span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error banner */}
      <AnimatePresence>
        {status === 'error' && (
          <motion.div
            className={styles.errorBanner}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <X size={16} /> {errorMsg}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
