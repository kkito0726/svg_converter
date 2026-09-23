const UNITS = ["B", "KB", "MB", "GB"];

export const formatBytes = (bytes: number): string => {
  const exponent = Math.min(
    Math.floor(Math.log(Math.max(bytes, 1)) / Math.log(1024)),
    UNITS.length - 1
  );
  const value = bytes / 1024 ** exponent;
  return `${exponent === 0 ? value : value.toFixed(1)} ${UNITS[exponent]}`;
};

// AMCプロット用CSVの描画セグメント数 (mode 列が "M" の行数)
export const countSegments = (csvText: string): number =>
  csvText.split("\n").filter((line) => line.split(",")[2] === "M").length;
