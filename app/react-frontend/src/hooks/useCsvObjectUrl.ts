import { useEffect, useState } from "react";

// CSV文字列からブラウザ内だけで有効な揮発性のダウンロードURL (blob:) を作る。
// 新しい変換結果が来たとき・画面を離れたとき・リロード時に破棄される。
export const useCsvObjectUrl = (csvText: string | undefined): string | null => {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!csvText) {
      setUrl(null);
      return;
    }
    const objectUrl = URL.createObjectURL(
      new Blob([csvText], { type: "text/csv" })
    );
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [csvText]);

  return url;
};
