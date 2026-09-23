import { useEffect, useState } from "react";

// Blob / File からブラウザ内だけで有効な揮発性のURL (blob:) を作る。
// 対象が変わったとき・アンマウント時に破棄する (StrictMode でも安全なように effect 内で生成)。
export const useObjectUrl = (source: Blob | undefined): string | null => {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!source) {
      setUrl(null);
      return;
    }
    const objectUrl = URL.createObjectURL(source);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [source]);

  return url;
};
