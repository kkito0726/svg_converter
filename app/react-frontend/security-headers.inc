# インターネット公開 (Cloudflare Tunnel) 向けのセキュリティヘッダー
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header X-Frame-Options "DENY" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" always;
