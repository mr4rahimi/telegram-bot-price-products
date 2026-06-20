import { useState, useEffect, useCallback, useRef } from 'react'
import { productsApi } from '../api/products'
import { categoriesApi } from '../api/categories'
import PageHeader from '../components/PageHeader'
import Modal from '../components/Modal'
import styles from './ProductsPage.module.css'

// ── آپلود / پیش‌نمایش عکس ────────────────────────────────
function ImageUploader({ value, onChange }) {
  const inputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const handleFile = async (file) => {
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const result = await productsApi.uploadImage(file)
      onChange(result.url)
    } catch {
      setError('آپلود ناموفق بود')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <div className={styles.uploader}>
      {value ? (
        <div className={styles.preview}>
          <img src={value} alt="عکس محصول" className={styles.previewImg} />
          <button
            type="button"
            className={styles.removeImg}
            onClick={() => onChange(null)}
          >✕ حذف تصویر</button>
        </div>
      ) : (
        <div
          className={styles.dropzone}
          onDragOver={e => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          {uploading ? (
            <span className={styles.uploadingText}>در حال آپلود...</span>
          ) : (
            <>
              <span className={styles.dropIcon}>📷</span>
              <span className={styles.dropText}>کلیک کنید یا فایل را اینجا رها کنید</span>
              <span className={styles.dropSub}>JPG، PNG، WEBP حداکثر ۵ مگابایت</span>
            </>
          )}
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className={styles.fileInput}
        onChange={e => handleFile(e.target.files[0])}
      />
      {error && <p className={styles.uploadError}>{error}</p>}
    </div>
  )
}

// ── فرم محصول ────────────────────────────────────────────
function ProductForm({ initial, categories, onSave, onCancel }) {
  const [form, setForm] = useState({
    title: initial?.title ?? '',
    category_id: initial?.category_id ?? (categories[0]?.id ?? ''),
    image_url: initial?.image_url ?? null,
    mymonta_url: initial?.mymonta_url ?? '',
    basalam_url: initial?.basalam_url ?? '',
    snappshop_url: initial?.snappshop_url ?? '',
    tapsishop_url: initial?.tapsishop_url ?? '',
    website_url: initial?.website_url ?? '',
    description: initial?.description ?? '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim() || !form.category_id) return
    setLoading(true)
    setError('')
    try {
      const payload = {
        ...form,
        category_id: Number(form.category_id),
        mymonta_url: form.mymonta_url || null,
        basalam_url: form.basalam_url || null,
        snappshop_url: form.snappshop_url || null,
        tapsishop_url: form.tapsishop_url || null,
        website_url: form.website_url || null,
        description: form.description || null,
      }
      await onSave(payload)
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'خطایی رخ داد')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      {/* عکس */}
      <div className={styles.field}>
        <label className={styles.label}>تصویر محصول</label>
        <ImageUploader
          value={form.image_url}
          onChange={url => setForm(f => ({ ...f, image_url: url }))}
        />
      </div>

      {/* نام */}
      <div className={styles.field}>
        <label className={styles.label}>نام محصول <span className={styles.req}>*</span></label>
        <input
          className={styles.input}
          value={form.title}
          onChange={set('title')}
          placeholder="نام محصول را وارد کنید"
          required
        />
      </div>

      {/* دسته‌بندی */}
      <div className={styles.field}>
        <label className={styles.label}>دسته‌بندی <span className={styles.req}>*</span></label>
        <select
          className={styles.input}
          value={form.category_id}
          onChange={set('category_id')}
          required
        >
          <option value="">انتخاب دسته‌بندی</option>
          {categories.map(c => (
            <option key={c.id} value={c.id}>{c.title}</option>
          ))}
        </select>
      </div>

      {/* لینک‌ها */}
      <div className={styles.linksSection}>
        <p className={styles.sectionTitle}>لینک‌های محصول</p>
        <div className={styles.field}>
          <label className={styles.label}>سایت ما (مای‌مونتا)</label>
          <input
            className={styles.input}
            value={form.mymonta_url}
            onChange={set('mymonta_url')}
            placeholder="https://mymonta.ir/products/..."
            dir="ltr"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>باسلام</label>
          <input
            className={styles.input}
            value={form.basalam_url}
            onChange={set('basalam_url')}
            placeholder="https://basalam.com/..."
            dir="ltr"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>اسنپ‌شاپ</label>
          <input
            className={styles.input}
            value={form.snappshop_url}
            onChange={set('snappshop_url')}
            placeholder="https://snappshop.ir/..."
            dir="ltr"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>تپسی‌شاپ</label>
          <input
            className={styles.input}
            value={form.tapsishop_url}
            onChange={set('tapsishop_url')}
            placeholder="https://tapsi.shop/product/..."
            dir="ltr"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>سایت دیگر</label>
          <input
            className={styles.input}
            value={form.website_url}
            onChange={set('website_url')}
            placeholder="https://..."
            dir="ltr"
          />
        </div>
      </div>

      {/* توضیحات */}
      <div className={styles.field}>
        <label className={styles.label}>توضیحات (اختیاری)</label>
        <textarea
          className={`${styles.input} ${styles.textarea}`}
          value={form.description}
          onChange={set('description')}
          placeholder="توضیح کوتاه درباره محصول..."
          rows={3}
        />
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        <button type="button" className={styles.cancelBtn} onClick={onCancel}>انصراف</button>
        <button type="submit" className={styles.saveBtn} disabled={loading}>
          {loading ? '...' : initial ? 'ذخیره تغییرات' : 'افزودن محصول'}
        </button>
      </div>
    </form>
  )
}

// ── دیالوگ حذف ───────────────────────────────────────────
function DeleteConfirm({ name, onConfirm, onCancel, loading }) {
  return (
    <div className={styles.deleteBox}>
      <p className={styles.deleteMsg}>
        آیا از حذف محصول <strong>«{name}»</strong> مطمئن هستید؟
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

// ── لینک‌های پلتفرم ───────────────────────────────────────
function PlatformLinks({ basalam, snappshop, website, tapsishop, mymonta }) {
  const links = [
    { url: mymonta, label: 'سایت ما', color: '#7c3aed' },
    { url: basalam, label: 'باسلام', color: '#e85d26' },
    { url: snappshop, label: 'اسنپ‌شاپ', color: '#e31e63' },
    { url: tapsishop, label: 'تپسی‌شاپ', color: '#f59e0b' },
    { url: website, label: 'سایت', color: '#4a9eff' },
  ].filter(l => l.url)

  if (!links.length) return <span className={styles.noLinks}>—</span>

  return (
    <div className={styles.platformLinks}>
      {links.map(({ url, label, color }) => (
        <a
          key={label}
          href={url}
          target="_blank"
          rel="noreferrer"
          className={styles.platformTag}
          style={{ '--tag-color': color }}
        >
          {label}
        </a>
      ))}
    </div>
  )
}

// ── صفحه اصلی ────────────────────────────────────────────
export default function ProductsPage() {
  const [items, setItems] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterCat, setFilterCat] = useState('')
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [prods, cats] = await Promise.all([
        productsApi.list(filterCat || undefined),
        categoriesApi.list(),
      ])
      setItems(prods)
      setCategories(cats)
    } finally {
      setLoading(false)
    }
  }, [filterCat])

  useEffect(() => { load() }, [load])

  const handleAdd = async (payload) => {
    await productsApi.create(payload)
    await load()
    setModal(null)
  }

  const handleEdit = async (payload) => {
    await productsApi.update(modal.item.id, payload)
    await load()
    setModal(null)
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await productsApi.delete(modal.item.id)
      await load()
      setModal(null)
    } catch (err) {
      alert(err?.response?.data?.detail ?? 'خطا در حذف')
    } finally {
      setDeleteLoading(false)
    }
  }

  const getCatName = (id) => categories.find(c => c.id === id)?.title ?? '—'

  const filtered = items.filter(i =>
    i.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className={styles.page}>
      <PageHeader
        title="محصولات"
        count={items.length}
        onAdd={() => setModal({ type: 'add' })}
        addLabel="+ محصول جدید"
      />

      <div className={styles.content}>
        {/* فیلترها */}
        <div className={styles.toolbar}>
          <input
            className={styles.search}
            placeholder="جستجو در محصولات..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <select
            className={styles.catFilter}
            value={filterCat}
            onChange={e => setFilterCat(e.target.value)}
          >
            <option value="">همه دسته‌ها</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
        </div>

        {/* جدول */}
        {loading ? (
          <div className={styles.empty}>در حال بارگذاری...</div>
        ) : filtered.length === 0 ? (
          <div className={styles.empty}>
            {search || filterCat ? 'نتیجه‌ای یافت نشد' : 'هنوز محصولی ثبت نشده'}
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th} style={{ width: 56 }}>عکس</th>
                <th className={styles.th}>نام محصول</th>
                <th className={styles.th} style={{ width: 140 }}>دسته‌بندی</th>
                <th className={styles.th} style={{ width: 200 }}>پلتفرم‌ها</th>
                <th className={styles.th} style={{ width: 140, textAlign: 'center' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={styles.row}>
                  <td className={styles.td}>
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.title}
                        className={styles.thumb}
                      />
                    ) : (
                      <div className={styles.noThumb}>📦</div>
                    )}
                  </td>
                  <td className={styles.td}>
                    <span className={styles.productName}>{item.title}</span>
                    {item.description && (
                      <p className={styles.productDesc}>{item.description}</p>
                    )}
                  </td>
                  <td className={styles.td}>
                    <span className={styles.catBadge}>{getCatName(item.category_id)}</span>
                  </td>
                  <td className={styles.td}>
                    <PlatformLinks
                      mymonta={item.mymonta_url}
                      basalam={item.basalam_url}
                      snappshop={item.snappshop_url}
                      tapsishop={item.tapsishop_url}
                      website={item.website_url}
                    />
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
        <Modal title="محصول جدید" onClose={() => setModal(null)}>
          <ProductForm
            categories={categories}
            onSave={handleAdd}
            onCancel={() => setModal(null)}
          />
        </Modal>
      )}

      {/* مودال ویرایش */}
      {modal?.type === 'edit' && (
        <Modal title="ویرایش محصول" onClose={() => setModal(null)}>
          <ProductForm
            initial={modal.item}
            categories={categories}
            onSave={handleEdit}
            onCancel={() => setModal(null)}
          />
        </Modal>
      )}

      {/* مودال حذف */}
      {modal?.type === 'delete' && (
        <Modal title="حذف محصول" onClose={() => setModal(null)}>
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