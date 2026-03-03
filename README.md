# RandevuPro

Salon ve klinikler için randevu + CRM MVP (Türkiye pazarı). Django web uygulaması + REST API (mobil uygulama için).

## Özellikler

- **Web (sunucu taraflı):** Tailwind CSS, karanlık mod, Türkçe arayüz
- **Panel:** Özet, takvim, randevular, müşteriler, hizmetler, personel, ayarlar, faturalandırma (placeholder), bildirimler (placeholder), yardım
- **API (DRF):** JWT auth, CRUD (business, services, staff, customers, appointments), herkese açık randevu: `POST /api/v1/public/book/`
- **Roller:** OWNER (işletme sahibi), STAFF (personel). Müşteri girişi MVP’de yok.

## Gereksinimler

- Python 3.12+
- Node.js 18+ (Tailwind derlemesi için)
- PostgreSQL (isteğe bağlı; varsayılan SQLite)

## Kurulum

### 1. Sanal ortam ve bağımlılıklar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Ortam değişkenleri

```bash
cp .env.example .env
# .env içindeki DJANGO_SECRET_KEY ve isteğe bağlı DB_* değerlerini düzenleyin.
```

### 3. Veritabanı

```bash
python manage.py migrate
```

### 4. Tailwind CSS

```bash
npm install
npm run build:css
```

Geliştirme sırasında değişiklikleri sürekli derlemek için:

```bash
npm run dev:css
```

Not: `tailwind.css` yoksa veya boşsa önce bir kez `npm run build:css` çalıştırın. Bazı ortamlarda `npx tailwindcss ...` doğrudan çalışmayabilir; o zaman `node_modules/.bin/tailwindcss` kullanın veya `package.json` içindeki script’i buna göre güncelleyin.

### 5. Demo verisi (isteğe bağlı)

```bash
python manage.py seed_demo
```

### 6. Sunucuyu çalıştırma

```bash
python manage.py runserver
```

- Web: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/

## Demo hesaplar (seed_demo sonrası)

| Rol   | E-posta               | Şifre       |
|-------|------------------------|-------------|
| Owner | owner@randevupro.com   | Demo12345!  |
| Staff | staff@randevupro.com   | Demo12345!  |

Herkese açık randevu sayfası: `/b/demo-salon/`

## API uç noktaları (base: `/api/v1/`)

### Kimlik doğrulama (JWT)

- `POST /api/v1/auth/login/` — Body: `{ "email", "password" }` → `access`, `refresh`, `user`
- `POST /api/v1/auth/refresh/` — Body: `{ "refresh": "<token>" }` → yeni `access`
- `POST /api/v1/auth/register/` — Body: `email`, `password`, `business_name`, `business_slug` → owner + business oluşturur, token döner
- `POST /api/v1/auth/logout/` — (İsteğe bağlı; header: `Authorization: Bearer <access>`)

### Korumalı CRUD (Bearer token gerekli)

- `/api/v1/business/` — İşletme(ler)
- `/api/v1/services/` — Hizmetler
- `/api/v1/staff/` — Personel
- `/api/v1/customers/` — Müşteriler
- `/api/v1/appointments/` — Randevular  
  - Filtreler: `date_from`, `date_to`, `status`, `staff_id`, `service_id`

### Herkese açık (kimlik doğrulama yok)

- `POST /api/v1/public/book/` — Randevu oluştur  
  Body örneği:  
  `business_slug`, `service_id`, `staff_id` (opsiyonel), `date`, `time`, `customer_name`, `customer_phone`, `notes` (opsiyonel)

Tüm API için OpenAPI şeması ve denemek için: `/api/schema/swagger-ui/`

## Proje yapısı

- `config/` — Ayarlar, ana url
- `accounts/` — Özel User (email, role: OWNER/STAFF)
- `core/` — Business
- `catalog/` — Service
- `staff/` — StaffProfile
- `crm/` — Customer
- `scheduling/` — Appointment
- `web/` — Şablonlar ve sayfa view’ları (public + panel)
- `api/` — DRF serializers, viewsets, JWT, izinler

## Lisans

Proje kodu örnek/şablon amaçlıdır.
