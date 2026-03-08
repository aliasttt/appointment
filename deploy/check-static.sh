#!/bin/bash
# Run on the server to check why admin static might not load.
# Usage: bash deploy/check-static.sh

set -e
echo "=== 1. Static files on disk ==="
ls -la /srv/appointment/staticfiles/admin/css/ 2>/dev/null | head -5 || echo "NOT FOUND - run collectstatic"

echo ""
echo "=== 2. Test static URL (should be HTTP/2 200) ==="
curl -sI https://heryerrandevu.com.tr/static/admin/css/base.css | head -5

echo ""
echo "=== 3. Which nginx config has listen 443 and server_name? ==="
grep -l "listen.*443\|server_name" /etc/nginx/sites-enabled/* 2>/dev/null || true
echo ""
echo "=== 4. Does that config contain 'location /static/'? ==="
grep -A2 "location /static/" /etc/nginx/sites-enabled/* 2>/dev/null || echo "No 'location /static/' found in sites-enabled"
