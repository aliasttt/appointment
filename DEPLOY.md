# Deploy — RandevuPro

راهنمای استقرار روی سرور لینوکس (مثلاً Ubuntu) با systemd و nginx. دامنهٔ نمونه: `heryerrandevu.com.tr`.

## پیش‌نیازها

- سرور با دسترسی `sudo`
- نصب: Git, Python 3.12+, pip, venv, nginx
- فایل env در `/etc/appointment.env` (مقادیر `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_*`, و در صورت نیاز `CORS_ALLOWED_ORIGINS`)
- سرویس systemd با نام `appointment` و nginx برای پروکسی به اپ

## اسکریپت استقرار

این اسکریپت را با کاربری که به `sudo` دسترسی دارد اجرا کنید (یک‌بار یا از CI/CD):

```bash
sudo -u root bash -lc "
cd /srv/appointment || exit 1

# Git
git config --global --add safe.directory /srv/appointment
git fetch origin
git reset --hard origin/main || exit 1

# Load ENV
set -a
source /etc/appointment.env
set +a

# Activate venv
source /srv/appointment/venv/bin/activate

# Install new packages if requirements changed
pip install -r requirements.txt || exit 1

# Django tasks
python manage.py migrate --noinput || exit 1
python manage.py collectstatic --noinput || exit 1

# Optional: clear cache if you add it later
# python manage.py clear_cache

"

# Restart services
sudo systemctl restart appointment
sudo systemctl reload nginx

# Health check
curl -I https://heryerrandevu.com.tr | head -n 20
```

## توضیح مراحل

| مرحله | توضیح |
|--------|--------|
| `cd /srv/appointment` | رفتن به دایرکتوری پروژه |
| `git config safe.directory` | اجازهٔ استفاده از این مسیر به عنوان مخزن امن |
| `git fetch` / `git reset --hard origin/main` | به‌روزرسانی کد از شاخهٔ `main` |
| `source /etc/appointment.env` | بارگذاری متغیرهای محیطی |
| `pip install -r requirements.txt` | نصب/به‌روز وابستگی‌های پایتون |
| `migrate --noinput` | اجرای مایگریشن‌های Django |
| `collectstatic --noinput` | جمع‌آوری فایل‌های استاتیک در `STATIC_ROOT` |
| `systemctl restart appointment` | ریستارت سرویس اپلیکیشن |
| `systemctl reload nginx` | بارگذاری مجدد پیکربندی nginx |
| `curl -I https://...` | بررسی اولیهٔ در دسترس بودن سایت |

## نکات

- مسیر پروژه و نام سرویس (`/srv/appointment`, `appointment`) را در صورت نیاز با محیط خود تطبیق دهید.
- برای محیط production در `appointment.env`: `DJANGO_DEBUG=False` و `DJANGO_SECRET_KEY` قوی و منحصر به‌فرد تنظیم شود.
- اگر از دیتابیس PostgreSQL استفاده می‌کنید، متغیرهای `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` را در `/etc/appointment.env` مقداردهی کنید.
