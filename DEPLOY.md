# Deploy — RandevuPro

راهنمای استقرار روی سرور لینوکس (مثلاً Ubuntu) با systemd و nginx. دامنهٔ نمونه: `heryerrandevu.com.tr`.

## پیش‌نیازها

- سرور با دسترسی `sudo`
- نصب: Git, Python 3.12+, pip, venv, nginx
- فایل env در `/etc/appointment.env` (مقادیر `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_*`, و در صورت نیاز `CORS_ALLOWED_ORIGINS`)
- سرویس systemd با نام `appointment` و nginx برای پروکسی به اپ

## اسکریپت استقرار

این اسکریپت را با کاربری که به `sudo` دسترسی دارد اجرا کنید (یک‌بار یا از CI/CD). **دستورات `systemctl` و `curl` حتماً خارج از بلوک `bash -lc` باشند** تا بعد از به‌روزرسانی کد، سرویس ریستارت و سپس سلامت سایت چک شود.





sudo -u root bash -lc '
cd /srv/appointment || exit 1
git config --global --add safe.directory /srv/appointment
git fetch origin
git reset --hard origin/main || exit 1
set -a
source /etc/appointment.env
set +a
source /srv/appointment/venv/bin/activate
pip install -r requirements.txt || exit 1
python manage.py migrate --noinput || exit 1
python manage.py collectstatic --noinput || exit 1

python manage.py createsuperuser
'

sudo systemctl restart appointment
sudo systemctl reload nginx
curl -I https://heryerrandevu.com.tr | head -n 20










heryerrandevu2233#









خروجی موفق: در پاسخ `curl` خط `HTTP/2 200` به‌معنای در دسترس بودن سایت است. اگر بعد از دپلوی کد جدید لود نمی‌شود، حتماً `systemctl restart appointment` اجرا شده باشد.

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

## Nginx: سرو فایل‌های استاتیک (ادمین و استاتیک اپ)

اگر ادمین جنگو بدون استایل (بدون CSS) نمایش داده می‌شود، nginx باید مسیر `/static/` را از همان پوشه‌ای که `collectstatic` پر می‌کند سرو کند. داخل بلوک `server` مربوط به همین سایت، قبل از `location /` این بلوک را اضافه کنید:

```nginx
location /static/ {
    alias /srv/appointment/staticfiles/;
}
```

سپس `sudo nginx -t` و `sudo systemctl reload nginx` را اجرا کنید. مطمئن شوید بعد از هر deploy دستور `python manage.py collectstatic --noinput` اجرا شده باشد.

## نکات

- مسیر پروژه و نام سرویس (`/srv/appointment`, `appointment`) را در صورت نیاز با محیط خود تطبیق دهید.
- برای محیط production در `appointment.env`: `DJANGO_DEBUG=False` و `DJANGO_SECRET_KEY` قوی و منحصر به‌فرد تنظیم شود.
- اگر از دیتابیس PostgreSQL استفاده می‌کنید، متغیرهای `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` را در `/etc/appointment.env` مقداردهی کنید.
