import { useState, useEffect, useCallback } from 'react'
import { categoriesApi } from '../api/categories'
import PageHeader from '../components/PageHeader'
import Modal from '../components/Modal'
import styles from './CategoriesPage.module.css'

function CategoryForm({ initial, onSave, onCancel }) {
  const [title, setTitle] = useState(initial?.title ?? '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    setLoading(true)
    setError('')
    try {
      await onSave({ title: title.trim() })
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'خطایی رخ داد')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.field}>
        <label className={styles.label}>نام دسته‌بندی</label>
        <input
          className={styles.input}
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="مثلاً: لوازم جانبی موبایل"
          autoFocus
          required
        />
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        <button type="button" className={styles.cancelBtn} onClick={onCancel}>
          انصراف
        </button>
        <button type="submit" className={styles.saveBtn} disabled={loading || !title.trim()}>
          {loading ? '...' : initial ? 'ذخیره تغییرات' : 'افزودن'}
        </button>
      </div>
    </form>
  )
}


function DeleteConfirm({ name, onConfirm, onCancel, loading }) {
  return (
    <div className={styles.deleteBox}>
      <p className={styles.deleteMsg}>
        آیا از حذف دسته‌بندی <strong>«{name}»</strong> مطمئن هستید؟
        <br />
        <span className={styles.deleteWarn}>در صورت وجود محصول در این دسته، حذف انجام نمی‌شود.</span>
      </p>
      <div className={styles.actions}>
        <button className={styles.cancelBtn} onClick={onCancel}>انصراف</button>
        <button className={styles.dangerBtn} onClick={onConfirm} disabled={loading}>
          {loading ? '...' : 'بله، حذف کن'}
        </button>
      </div>
    </div>
  )
}


export default function CategoriesPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | {type:'add'} | {type:'edit', item} | {type:'delete', item}
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [search, setSearch] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await categoriesApi.list()
      setItems(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleAdd = async (payload) => {
    await categoriesApi.create(payload)
    await load()
    setModal(null)
  }

  const handleEdit = async (payload) => {
    await categoriesApi.update(modal.item.id, payload)
    await load()
    setModal(null)
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await categoriesApi.delete(modal.item.id)
      await load()
      setModal(null)
    } catch (err) {
      alert(err?.response?.data?.detail ?? 'خطا در حذف')
    } finally {
      setDeleteLoading(false)
    }
  }

  const filtered = items.filter(i =>
    i.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className={styles.page}>
      <PageHeader
        title="دسته‌بندی‌ها"
        count={items.length}
        onAdd={() => setModal({ type: 'add' })}
        addLabel="+ دسته‌بندی جدید"
      />

      <div className={styles.content}>
        {/* سرچ */}
        <div className={styles.toolbar}>
          <input
            className={styles.search}
            placeholder="جستجو در دسته‌بندی‌ها..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* جدول */}
        {loading ? (
          <div className={styles.empty}>در حال بارگذاری...</div>
        ) : filtered.length === 0 ? (
          <div className={styles.empty}>
            {search ? 'نتیجه‌ای یافت نشد' : 'هنوز دسته‌بندی‌ای ثبت نشده'}
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th} style={{ width: 60 }}>#</th>
                <th className={styles.th}>نام دسته‌بندی</th>
                <th className={styles.th} style={{ width: 140, textAlign: 'center' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item, idx) => (
                <tr key={item.id} className={styles.row}>
                  <td className={`${styles.td} ${styles.idCell}`}>{idx + 1}</td>
                  <td className={styles.td}>
                    <span className={styles.categoryName}>{item.title}</span>
                  </td>
                  <td className={styles.td}>
                    <div className={styles.rowActions}>
                      <button
                        className={styles.editBtn}
                        onClick={() => setModal({ type: 'edit', item })}
                      >
                        ویرایش
                      </button>
                      <button
                        className={styles.deleteRowBtn}
                        onClick={() => setModal({ type: 'delete', item })}
                      >
                        حذف
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* مودال افزودن */}
      {modal?.type === 'add' && (
        <Modal title="دسته‌بندی جدید" onClose={() => setModal(null)}>
          <CategoryForm onSave={handleAdd} onCancel={() => setModal(null)} />
        </Modal>
      )}

      {/* مودال ویرایش */}
      {modal?.type === 'edit' && (
        <Modal title="ویرایش دسته‌بندی" onClose={() => setModal(null)}>
          <CategoryForm
            initial={modal.item}
            onSave={handleEdit}
            onCancel={() => setModal(null)}
          />
        </Modal>
      )}

      {/* مودال حذف */}
      {modal?.type === 'delete' && (
        <Modal title="حذف دسته‌بندی" onClose={() => setModal(null)}>
          <DeleteConfirm
            name={modal.item.title}
            onConfirm={handleDelete}
            onCancel={() => setModal(null)}
            loading={deleteLoading}
          />
        </Modal>
      )}
    </div>
  )
}