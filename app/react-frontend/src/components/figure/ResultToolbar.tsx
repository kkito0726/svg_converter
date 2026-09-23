import { useEffect, useMemo, useState } from "react";
import { handleDownloadCSV } from "../../hooks/download";
import { useObjectUrl } from "../../hooks/useObjectUrl";
import { ConversionResult } from "../../hooks/useDataSubmission";
import { countSegments } from "../../utils/format";
import { IconCheck, IconCopy, IconDownload } from "../icons";

type ResultToolbarProps = {
  result: ConversionResult;
};

// クリップボードへの画像コピーは HTTPS / localhost でのみ利用できる
const canCopyImage = () =>
  typeof ClipboardItem !== "undefined" && !!navigator.clipboard?.write;

const COPIED_FEEDBACK_MS = 2000;

type CopyState = "idle" | "copied" | "failed";

const COPY_LABELS: Record<CopyState, string> = {
  idle: "画像をコピー",
  copied: "コピーしました",
  failed: "コピーできませんでした",
};

export const ResultToolbar: React.FC<ResultToolbarProps> = ({ result }) => {
  const csvBlob = useMemo(
    () => new Blob([result.csv_text], { type: "text/csv" }),
    [result.csv_text]
  );
  const csvUrl = useObjectUrl(csvBlob);
  const segments = useMemo(() => countSegments(result.csv_text), [result.csv_text]);
  const [copyState, setCopyState] = useState<CopyState>("idle");

  useEffect(() => {
    if (copyState === "idle") return;
    const timer = setTimeout(() => setCopyState("idle"), COPIED_FEEDBACK_MS);
    return () => clearTimeout(timer);
  }, [copyState]);

  const handleCopyImage = async () => {
    try {
      const blob = await fetch(
        `data:image/png;base64,${result.plot_base64_image}`
      ).then((r) => r.blob());
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
  };

  const stats = [
    { label: "Power", value: `${result.params.power} W` },
    { label: "Speed", value: `${result.params.speed} μm/s` },
    { label: "Segments", value: segments.toLocaleString() },
  ];

  return (
    <div className="flex flex-col gap-4 border-b border-line/70 p-4 sm:p-5 xl:flex-row xl:items-center xl:justify-between">
      <div className="min-w-0">
        <p className="eyebrow">Output</p>
        <p
          className="mt-1 truncate font-mono text-sm text-ink sm:text-base"
          title={result.csv_name}
        >
          {result.csv_name}
        </p>
        <dl className="mt-2 flex flex-wrap gap-1.5">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="flex items-center gap-1.5 rounded-md border border-line/80 bg-canvas/50 px-2 py-1 font-mono text-[11px]"
            >
              <dt className="text-muted">{stat.label}</dt>
              <dd className="text-ink">{stat.value}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="flex shrink-0 gap-2">
        {canCopyImage() ? (
          <button
            type="button"
            onClick={handleCopyImage}
            className="btn-ghost"
            aria-label={COPY_LABELS[copyState]}
            title={COPY_LABELS[copyState]}
          >
            {copyState === "copied" ? (
              <IconCheck className="h-4 w-4 text-accent" />
            ) : (
              <IconCopy />
            )}
            <span className="hidden whitespace-nowrap sm:inline">
              {COPY_LABELS[copyState]}
            </span>
          </button>
        ) : null}
        <button
          type="button"
          onClick={() => csvUrl && handleDownloadCSV(csvUrl, result.csv_name)}
          disabled={!csvUrl}
          className="btn-primary flex-1 xl:flex-none"
        >
          <IconDownload />
          <span className="whitespace-nowrap">CSVをダウンロード</span>
        </button>
      </div>
    </div>
  );
};
