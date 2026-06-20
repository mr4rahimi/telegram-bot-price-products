import styles from './PageHeader.module.css'

export default function PageHeader({ title, count, onAdd, addLabel = '+ افزودن' }) {
  return (
    <div className={styles.header}>
      <div className={styles.titleRow}>
        <h1 className={styles.title}>{title}</h1>
        {count !== undefined && (
          <span className={styles.badge}>{count}</span>
        )}
      </div>
      {onAdd && (
        <button className={styles.addBtn} onClick={onAdd}>
          {addLabel}
        </button>
      )}
    </div>
  )
}