// 利用者数を把握するための匿名 ID (docs/logging-design.md 5.3)。
// ブラウザごとにランダムに作るだけで、個人の情報は含まない
export const CLIENT_ID_HEADER = "X-Client-ID";
const STORAGE_KEY = "svg-converter:client-id";

// crypto.randomUUID は HTTPS / localhost でしか使えないので、
// 研究室 PC (http://<IP>:4174) でも動く getRandomValues で UUID v4 を作る
const createUuidV4 = (): string => {
  const hex = Array.from(crypto.getRandomValues(new Uint8Array(16)), (byte, i) => {
    if (i === 6) return (byte & 0x0f) | 0x40; // version 4
    if (i === 8) return (byte & 0x3f) | 0x80; // variant 10xx
    return byte;
  })
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
  return [
    hex.slice(0, 8),
    hex.slice(8, 12),
    hex.slice(12, 16),
    hex.slice(16, 20),
    hex.slice(20),
  ].join("-");
};

// localStorage が使えない (プライベートモード等) 場合は、ページを開いている間だけの ID にする
const sessionClientId = createUuidV4();

export const getClientId = (): string => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    localStorage.setItem(STORAGE_KEY, sessionClientId);
    return sessionClientId;
  } catch {
    return sessionClientId;
  }
};
