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

'

sudo systemctl restart appointment
sudo systemctl reload nginx
curl -I https://heryerrandevu.com.tr | head -n 20










heryerrandevu2233#









خروجی موفق: در پاسخ `curl` خط `HTTP/2 200` به‌معنای در دسترس بودن سایت است. اگر بعد از دپلوی کد جدید لود نمی‌شود، حتماً `systemctl restart appointment` اجرا شده باشد.

## ورود کار نمی‌کند / خطا نمایش داده نمی‌شود

اگر با ایمیل و رمز درست هم نمی‌توانید وارد شوید و هیچ پیام خطایی نمی‌بینید، دو حالت داریم:

1. **الان در قالب لاگین خطا نمایش داده می‌شود** — اگر ایمیل یا رمز اشتباه باشد، پیام «E-posta veya şifre hatalı.» زیر فرم دیده می‌شود. اگر این پیام را می‌بینید یعنی کاربر در دیتابیس نیست یا رمز عوض شده (بخش بعد).
2. **کاربران بعد از دیپلوی پاک می‌شوند** — اگر هر بار بعد از دیپلوی سوپریوزر و یوزرهای بیزینس از بین می‌روند، دیتابیس شما پایدار نیست (بخش «یوزرها بعد از دیپلوی پاک می‌شوند» را ببینید).

## یوزرها بعد از دیپلوی پاک می‌شوند (سوپریوزر / بیزینس)

اگر بعد از هر دیپلوی نمی‌توانید با همان ایمیل قبلی لاگین کنید و انگار یوزرها پاک شده‌اند، معمولاً یکی از این دو است:

### ۱) استفاده از SQLite در مسیر پیش‌فرض

اگر از دیتابیس SQLite استفاده می‌کنید و در env فقط `DB_ENGINE` و `DB_NAME` را نگذاشته‌اید، فایل دیتابیس داخل پروژه (`db.sqlite3`) است. اگر سرور یا اسکریپت دیپلوی دایرکتوری پروژه را خالی یا دوباره کلون کند، این فایل از بین می‌رود و همهٔ یوزرها و داده‌ها پاک می‌شوند.

**راه‌حل:** دیتابیس را به یک مسیر **ثابت و بیرون از دایرکتوری پروژه** ببرید و بعد از اولین دیپلوی سوپریوزر را یک‌بار بسازید:

1. یک مسیر ثابت برای دیتابیس بسازید، مثلاً:
   ```bash
   sudo mkdir -p /var/lib/appointment
   sudo chown www-data:www-data /var/lib/appointment   # یا همان یوزری که سرویس با آن اجرا می‌شود
   ```
2. در `/etc/appointment.env` مقدار دیتابیس را ثابت کنید:
   ```bash
   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=/var/lib/appointment/db.sqlite3
   ```
   (بقیهٔ `DB_*` را خالی بگذارید.)
3. یک‌بار مایگریشن و ساخت سوپریوزر:
   ```bash
   cd /srv/appointment && source venv/bin/activate && set -a && source /etc/appointment.env && set +a
   python manage.py migrate --noinput
   python manage.py createsuperuser   # ایمیل و رمز دلخواه را وارد کنید
   ```
4. بعد از این، هر بار که دیپلوی می‌کنید فقط کد و استاتیک به‌روز می‌شوند؛ فایل `/var/lib/appointment/db.sqlite3` دست‌نخورده می‌ماند و یوزرها پاک نمی‌شوند.

### ۲) استفاده از PostgreSQL

اگر از PostgreSQL استفاده می‌کنید، معمولاً داده پاک نمی‌شود مگر اینکه خودتان دیتابیس را در migration یا اسکریپت drop کنید. مطمئن شوید در env همان `DB_*` را که یک‌بار ساختهاید استفاده می‌کنید و بعد از اولین دیپلوی حتماً `createsuperuser` را اجرا کرده‌اید:

```bash
cd /srv/appointment && source venv/bin/activate && set -a && source /etc/appointment.env && set +a
python manage.py createsuperuser
```

### خلاصه

- دیتابیس باید **پایدار** باشد (مسیر ثابت برای SQLite یا همان PostgreSQL برای production).
- سوپریوزر را **بعد از اولین دیپلوی** با `python manage.py createsuperuser` بسازید و بعد از آن دیگر لازم نیست مگر دیتابیس را عوض کنید.

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

## ادمین جنگو بدون استایل (صفحه ورود سوپریوزر خراب)

اگر بعد از دیپلوی و نصب WhiteNoise هنوز صفحه ورود ادمین بدون CSS و با مربع‌های سیاه است، **معمولاً nginx درخواست‌های `/static/` را به اپ نمی‌فرستد یا از مسیر اشتباه سرو می‌کند.** راه‌حل قطعی این است که **خود nginx** فایل‌های استاتیک را سرو کند.

### مرحلهٔ ۱: ویرایش کانفیگ nginx روی سرور

1. فایل کانفیگ همین سایت را باز کنید، مثلاً:
   ```bash
   sudo nano /etc/nginx/sites-available/heryerrandevu.com.tr
   ```
   (یا هر نامی که برای این دامنه دارید؛ ممکن است در `sites-available/default` باشد.)

2. داخل بلوک `server { ... }` مربوط به `heryerrandevu.com.tr`، **قبل از** بلوک `location / { ... }` این بلوک را اضافه کنید (اگر از قبل دارید، فقط مسیر `alias` را چک کنید):

   ```nginx
   location /static/ {
       alias /srv/appointment/staticfiles/;
   }
   ```

3. ذخیره و خروج. سپس تست و ریلود:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. در مرورگر صفحه ادمین را با رفرش سخت (Ctrl+F5) یا در حالت ناشناس باز کنید.

### مرحلهٔ ۲ (اختیاری): تست از روی خود سرور

اگر باز هم کار نکرد، روی سرور اجرا کنید تا ببینید آیا فایل استاتیک از روی دیسک خوانده می‌شود:

```bash
ls -la /srv/appointment/staticfiles/admin/css/ | head -5
curl -I https://heryerrandevu.com.tr/static/admin/css/base.css
```

خروجی `curl` باید `HTTP/2 200` و `content-type: text/css` باشد. اگر ۴۰۴ است، یا بلوک `location /static/` را اضافه نکرده‌اید یا مسیر `alias` اشتباه است (باید دقیقاً `/srv/appointment/staticfiles/` با اسلش آخر باشد).

### رفع 404 برای `/static/admin/css/base.css`

اگر روی سرور این دستور ۴۰۴ می‌دهد:

```bash
curl -I https://heryerrandevu.com.tr/static/admin/css/base.css
```

دو حالت داریم:

**الف) مطمئن شوید فایل روی دیسک هست:**

```bash
ls -la /srv/appointment/staticfiles/admin/css/base.css
```

اگر «No such file» بود، دوباره collectstatic بزنید و بعد nginx را چک کنید:

```bash
cd /srv/appointment && source venv/bin/activate && source /etc/appointment.env && python manage.py collectstatic --noinput
```

**ب) بلوک `location /static/` باید داخل همان `server`ی باشد که `listen 443` دارد.**

فایل کانفیگ را باز کنید (معمولاً همانی که برای این دامنه استفاده می‌کنید):

```bash
sudo nano /etc/nginx/sites-available/default
```

در فایل، بلوک `server {`ی را پیدا کنید که داخلش **`listen 443`** هست (نه فقط `listen 80`). داخل **همان** بلوک، حتماً **قبل از** `location / {` این را بگذارید (اگر از قبل هست، فقط مسیر را چک کنید):

```nginx
    location /static/ {
        alias /srv/appointment/staticfiles/;
    }
```

- بعد از `alias` حتماً اسلش آخر باشد: `.../staticfiles/`
- مسیر دقیقاً: `/srv/appointment/staticfiles/`

ذخیره کنید، سپس:

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -I https://heryerrandevu.com.tr/static/admin/css/base.css
```

باید در خط اول `HTTP/2 200` بیاید.

### اگر هنوز درست نشد: بلوک درست را ویرایش کنید

سایت با **HTTPS** باز می‌شود؛ پس nginx معمولاً دو بلوک `server` دارد: یکی `listen 80` و یکی `listen 443 ssl`. باید `location /static/` را داخل **همان بلوکی** بگذارید که `listen 443` و `server_name heryerrandevu.com.tr` دارد.

روی سرور این را اجرا کنید تا ببینید کدام فایل/بلوک این دامنه را سرو می‌کند:

```bash
grep -r "heryerrandevu\|443\|server_name" /etc/nginx/sites-enabled/
```

سپس آن فایل را باز کنید و داخل بلوک `server {` که `listen 443` دارد، دقیقاً قبل از `location / {` این را اضافه کنید:

```nginx
    location /static/ {
        alias /srv/appointment/staticfiles/;
    }
```

**مثال** — اگر فایل شما شبیه این است:

```nginx
server {
    listen 443 ssl;
    server_name heryerrandevu.com.tr;
    # ... ssl_certificate و بقیه ...

    location / {
        proxy_pass http://127.0.0.1:8000;
        ...
    }
}
```

باید شود:

```nginx
server {
    listen 443 ssl;
    server_name heryerrandevu.com.tr;
    # ... ssl و بقیه ...

    location /static/ {
        alias /srv/appointment/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        ...
    }
}
```

ذخیره، سپس `sudo nginx -t && sudo systemctl reload nginx`. بعد دوباره تست:

```bash
curl -I https://heryerrandevu.com.tr/static/admin/css/base.css
```

باید در خط اول `HTTP/2 200` بیاید.

نمونهٔ کامل بلوک‌های nginx در `deploy/nginx-appointment.conf.example` است.

## نکات

- مسیر پروژه و نام سرویس (`/srv/appointment`, `appointment`) را در صورت نیاز با محیط خود تطبیق دهید.
- برای محیط production در `appointment.env`: `DJANGO_DEBUG=False` و `DJANGO_SECRET_KEY` قوی و منحصر به‌فرد تنظیم شود.
- اگر از دیتابیس PostgreSQL استفاده می‌کنید، متغیرهای `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` را در `/etc/appointment.env` مقداردهی کنید.
