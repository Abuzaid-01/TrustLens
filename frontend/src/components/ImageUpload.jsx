import { useCallback, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Eye, X, ImageIcon } from 'lucide-react'
import styles from './ImageUpload.module.css'

export default function ImageUpload({ files, setFiles }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const addFiles = useCallback((newFiles) => {
    const images = Array.from(newFiles).filter(f => f.type.startsWith('image/'))
    setFiles(prev => [...prev, ...images].slice(0, 5))
  }, [setFiles])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    addFiles(e.dataTransfer.files)
  }, [addFiles])

  const removeFile = useCallback((idx) => {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }, [setFiles])

  return (
    <div className={styles.wrapper}>
      <label className="label"><ImageIcon size={15} /> Photos (Optional)</label>

      <div
        className={`${styles.dropZone} ${dragging ? styles.dropActive : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <Upload size={28} className={styles.dropIcon} />
        <div className={styles.dropText}>
          <span className={styles.dropAccent}>Click to upload</span> or drag and drop
        </div>
        <div className={styles.dropHint}>PNG, JPG, WEBP — Max 5 images · Vision AI will analyze each</div>

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      {/* Preview Grid */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            className={styles.previewGrid}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {files.map((file, i) => (
              <motion.div
                key={file.name + i}
                className={styles.previewCard}
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.5 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15, delay: i * 0.05 }}
              >
                <img
                  className={styles.previewImg}
                  src={URL.createObjectURL(file)}
                  alt={file.name}
                />

                {/* AI overlay on hover */}
                <div className={styles.aiOverlay}>
                  <Eye size={18} />
                  <span className={styles.aiOverlayText}>AI will analyze this image</span>
                </div>

                {/* Remove button */}
                <button
                  className={styles.removeBtn}
                  onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                >
                  <X size={12} />
                </button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
