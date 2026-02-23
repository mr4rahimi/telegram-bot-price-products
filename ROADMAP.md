پروپوزال پروژه ربات تلگرام نمایش محصولات با قیمت روز (Basalam + Snappshop)
0) هدف پروژه

ساخت یک ربات تلگرام برای فروشگاه که کاربر:

وارد ربات شود و دسته‌بندی انتخاب کند

سپس محصولات آن دسته را ببیند (اطلاعات محصول از قبل وارد شده)

برای هر محصول، قیمت روز را از:

باسلام

اسنپ‌شاپ (فقط فروشنده‌ی خودمان)

خرید مستقیم (لینک مستقیم + در صورت نیاز قیمت ثابت/یا بعداً قیمت‌خوان)

نمایش دهد و لینک هر پلتفرم را ارائه کند.

نکته: فعلاً دیجی‌کالا از MVP خارج است، ولی معماری باید آماده‌ی اضافه‌شدن “adapter” جدید باشد.

1) خروجی‌های اصلی (Deliverables)
1.1 ربات تلگرام

انتخاب دسته‌بندی با InlineKeyboard

لیست محصولات دسته (صفحه‌بندی)

صفحه جزئیات محصول (عکس/ویژگی‌ها/توضیح) + قیمت‌های به‌روز + دکمه لینک‌ها

دکمه 🔄 بروزرسانی قیمت برای همان محصول

1.2 سرویس قیمت‌خوان (Price Service)

Basalam Price Fetcher

Snappshop Price Fetcher (فقط seller مشخص)

کش قیمت در دیتابیس با TTL

لاگ و هندل خطا

1.3 پنل ادمین (Admin Panel)

CRUD دسته‌بندی‌ها و محصولات و offerها (لینک‌های باسلام/اسنپ‌شاپ/مستقیم)

تعیین seller name برای اسنپ‌شاپ

مشاهده آخرین قیمت/زمان آپدیت

ابزار تست “استخراج قیمت” برای یک offer (برای دیباگ)

1.4 استقرار

اجرای محلی (Ubuntu)

انتقال به سرور لیارا (PostgreSQL + اپلیکیشن)

تنظیمات محیطی و healthcheck

2) تصمیمات فنی (Tech Stack)
زبان و ساختار

Python 3.11+ (ترجیحاً 3.12 اگر روی سرور مشکلی ندارد)

Bot framework: aiogram (async)

HTTP client: httpx

HTML parsing: lxml (یا BeautifulSoup؛ ترجیحاً lxml برای سرعت)

ORM: SQLAlchemy 2.x

Migration: Alembic

Config: pydantic-settings

Logging: استاندارد Python logging + ساختار JSON-like (اختیاری)

دیتابیس

PostgreSQL (محلی و روی لیارا)

کش قیمت داخل DB

پنل ادمین

دو مسیر پیشنهادی؛ انتخاب نهایی در مرحله پنل:

FastAPI + SQLAdmin (یا Starlette Admin)
سریع، سبک، قابل دیپلوی، UI قابل قبول.

Django Admin
سریع‌ترین برای CRUD استاندارد، اما سنگین‌تر و ساختار پروژه را تغییر می‌دهد.

پیشنهاد اجرایی: چون Bot async است و ما سرویس قیمت‌خوان هم داریم، FastAPI + SQLAdmin معمولاً تمیزتر می‌شود (یک backend یکپارچه).

3) معماری کلی سیستم
3.1 لایه‌ها

Bot Layer (Telegram)

هندلرهای start/category/product

ساخت پیام‌ها و کیبوردها

فراخوانی Price Service با TTL

Domain + Data Layer

مدل‌های SQLAlchemy

Repository/Service برای خواندن دسته‌ها/محصولات/offerها

Price Service Layer

Interface مشترک: fetch_price(offer) -> PriceResult

Implementations:

BasalamFetcher

SnappshopFetcher

Normalization: تبدیل به تومان int + وضعیت (available/unavailable/error)

Admin API/Panel

احراز هویت ساده (Basic / Token / Session)

CRUD + ابزار تست قیمت

3.2 سیاست کش قیمت (TTL)

هر offer در DB:

price_last (تومان)

price_updated_at

ttl_seconds (پیش‌فرض 900 = 15 دقیقه)

هنگام نمایش محصول:

اگر قیمت تازه است → همان نمایش

اگر قدیمی است → fetch و update

خطاها:

اگر fetch خطا داد → آخرین قیمت (اگر موجود) + برچسب “آخرین بروزرسانی: …” یا “ناموفق”

4) مدل داده (Schema پیشنهادی)
جدول categories

id (PK)

title

description (nullable)

image_file_id (nullable) ← بهتر از URL برای تلگرام

sort_order (int, default 0)

is_active (bool)

جدول products

id (PK)

category_id (FK)

title

description (nullable)

image_file_id (nullable)

features_json (jsonb, nullable) ← مثلا [{"k":"جنس","v":"برنج"}, ...]

is_active (bool)

created_at / updated_at

جدول offers

id (PK)

product_id (FK)

platform (enum: basalam, snappshop, direct)

url

seller_name (nullable) ← فقط snappshop

price_last (int, nullable) ← تومان

price_updated_at (nullable datetime)

ttl_seconds (int default 900)

last_error (text nullable)

is_active (bool)

جدول bot_users (اختیاری برای آنالیتیکس/محدودسازی)

id

telegram_user_id

first_seen_at / last_seen_at

5) ساختار پروژه (در مسیر شما)

ریپو در:
/home/mr4rahimi/Projects/telegram-bot-price

ساختار پیشنهادی:

telegram-bot-price/
  README.md
  ROADMAP.md              # همین پروپوزال (قابل آپدیت)
  .env.example
  docker-compose.yml      # برای postgres محلی
  pyproject.toml
  alembic/
  src/
    app/
      main.py             # entrypoint (bot + optional api)
      config.py
      logging.py
      db/
        session.py
        models.py
        migrations/       # اگر داخل alembic نیست
      repositories/
        categories.py
        products.py
        offers.py
      services/
        price/
          base.py
          basalam.py
          snappshop.py
          normalize.py
        catalog.py
      bot/
        dispatcher.py
        handlers/
          start.py
          categories.py
          products.py
        ui/
          keyboards.py
          messages.py
      admin/
        api.py             # FastAPI
        auth.py
        views.py
  scripts/
    seed.py               # وارد کردن نمونه دیتا


اگر تصمیم گرفتید Bot و Admin جدا اجرا شوند، main.py به دو entrypoint تقسیم می‌شود.

6) مراحل اجرای پروژه (Phase-by-Phase)
Phase 1 — پایه‌گذاری ریپو و محیط توسعه (Done Criteria مشخص)

هدف: پروژه قابل اجرا با دیتابیس محلی.

 ساخت venv و pyproject

 docker-compose برای PostgreSQL محلی

 تنظیم config با .env

 اتصال SQLAlchemy + Alembic + migration اولیه

 ساخت مدل‌ها (categories/products/offers)

خروجی قابل تست:
اجرای migration و اتصال موفق به DB.

Phase 2 — کاتالوگ بدون قیمت (Bot MVP اولیه)

هدف: ربات کار کند و اطلاعات ثابت را نمایش دهد (بدون قیمت‌خوان).

 /start + نمایش دسته‌ها

 انتخاب دسته → لیست محصولات

 انتخاب محصول → صفحه جزئیات + لینک‌ها (بدون قیمت یا “در حال آماده‌سازی”)

Done Criteria:
یک مسیر کامل UX از start تا نمایش محصول بدون price fetch.

Phase 3 — قیمت‌خوان باسلام + کش

هدف: قیمت باسلام از صفحه استخراج شود و در DB کش شود.

 BasalamFetcher (httpx + parser)

 normalize به تومان int

 منطق TTL از offers

 نمایش قیمت باسلام در صفحه محصول

 هندل خطا + last_error

Done Criteria:
قیمت باسلام برای یک محصول نمایش داده شود و price_updated_at آپدیت شود.

Phase 4 — قیمت‌خوان اسنپ‌شاپ (فقط فروشنده خودمان) + کش

هدف: پیدا کردن قیمت offer مربوط به seller مشخص.

 SnappshopFetcher

 جستجوی seller_name و استخراج قیمت همان

 fallback رفتار (عدم وجود seller → ناموجود)

 نمایش قیمت در صفحه محصول

Done Criteria:
قیمت اسنپ‌شاپ مطابق seller درست نشان داده شود.

Phase 5 — بهینه‌سازی UX/کارایی

 صفحه‌بندی محصولات

 دکمه 🔄 بروزرسانی قیمت (force refresh برای همان محصول)

 rate limit ساده (مثلاً هر کاربر هر X ثانیه)

 timeout و retry کنترل‌شده برای fetch

Done Criteria:
تجربه کاربری روان، بدون کندی شدید.

Phase 6 — پنل ادمین (CRUD واقعی)

هدف: مدیریت داده‌ها بدون دستکاری مستقیم DB.

 انتخاب ابزار پنل: FastAPI + SQLAdmin (پیشنهادی)

 احراز هویت ساده (username/password از env)

 CRUD:

categories

products

offers

 تست دستی fetch قیمت از داخل پنل (دکمه/endpoint test)

Done Criteria:
مدیر بتواند محصول/دسته/offer بسازد و در Bot نمایش ببیند.

Phase 7 — آماده‌سازی برای دیپلوی لیارا

 تنظیمات production (env vars)

 اجرای migration در startup یا اسکریپت جدا

 لاگ مناسب

 health endpoint (برای admin/api)

 مستندسازی استقرار

Done Criteria:
روی لیارا بدون تغییر کد major اجرا شود.

7) ریسک‌ها و راهکارها
7.1 تغییر ساختار صفحات (Basalam/Snappshop)

راهکار: داشتن تست دستی “offer test” در پنل + لاگ مناسب + نگه‌داشتن extractor جدا.

7.2 کندی و فشار به سایت‌ها

راهکار: TTL اجباری + timeout + محدودسازی بروزرسانی (force refresh) + امکان زمان‌بندی (بعداً).

7.3 ضدبات/کپچا

برای این دو پلتفرم فعلاً احتمالاً کمتر از دیجی‌کالاست.

در صورت بروز: تغییر هدرها، کاهش نرخ، یا استفاده از روش‌های جایگزین.

8) استانداردهای کیفیت و نگهداری

هر Phase یک PR/commit مشخص

اضافه کردن تست حداقلی برای normalize و extractorها (حتی با HTML fixture)

لاگ خطاها همراه با offer_id و platform

عدم ذخیره اطلاعات حساس در ریپو (فقط .env.example)

9) تعریف “Done” کلی پروژه MVP

Bot: دسته→محصول→جزئیات

قیمت باسلام و اسنپ‌شاپ با TTL

پنل ادمین برای مدیریت داده‌ها

آماده دیپلوی روی لیارا


