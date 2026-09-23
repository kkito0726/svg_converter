// nginx (本番) / vite dev server (開発) が /api をバックエンドへプロキシする
export const API_BASE = "/api";
export const SVG2CSV_ENDPOINT = `${API_BASE}/svg2csv`;

// バックエンドの MAX_UPLOAD_MB / nginx の client_max_body_size と揃える
export const MAX_UPLOAD_MB = 20;
export const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024;
