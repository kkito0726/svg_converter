import { ChangeEvent, DragEvent, useEffect, useRef, useState } from "react";
import { useObjectUrl } from "../../hooks/useObjectUrl";
import { formatBytes } from "../../utils/format";
import { MAX_UPLOAD_MB } from "../../config/api";
import { IconClose, IconFile, IconSwap, IconUpload } from "../icons";

type FileDropzoneProps = {
  file: File | undefined;
  onSelect: (file: File) => void;
  onClear: () => void;
};

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  file,
  onSelect,
  onClear,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const thumbnailUrl = useObjectUrl(file);
  // 描画できないSVGはプレースホルダーのアイコンを表示する
  const [thumbnailFailed, setThumbnailFailed] = useState(false);
  useEffect(() => setThumbnailFailed(false), [file]);

  const openPicker = () => inputRef.current?.click();

  const handleInput = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.item(0);
    if (selected) onSelect(selected);
    // 同じファイルを選び直しても onChange が発火するようにリセットする
    e.target.value = "";
  };

  const dragProps = {
    onDragOver: (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(true);
    },
    onDragLeave: () => setIsDragging(false),
    onDrop: (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files.item(0);
      if (dropped) onSelect(dropped);
    },
  };

  const ring = isDragging
    ? "border-accent bg-accent/10 shadow-[0_0_0_4px_rgb(var(--c-accent)/0.15)]"
    : "border-line";

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".svg,image/svg+xml"
        className="sr-only"
        tabIndex={-1}
        onChange={handleInput}
      />
      {file ? (
        <div
          {...dragProps}
          className={`flex animate-rise items-center gap-3 rounded-xl border bg-raised/70 p-3 transition ${ring}`}
        >
          <div className="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-lg bg-white ring-1 ring-black/10">
            {thumbnailUrl && !thumbnailFailed ? (
              <img
                src={thumbnailUrl}
                alt=""
                className="h-full w-full object-contain p-1"
                onError={() => setThumbnailFailed(true)}
              />
            ) : (
              <IconFile className="h-7 w-7 text-zinc-400" />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium text-ink" title={file.name}>
              {file.name}
            </p>
            <p className="mt-0.5 font-mono text-xs text-muted">
              <span className="mr-2 rounded bg-accent/15 px-1.5 py-0.5 text-accent">
                SVG
              </span>
              {formatBytes(file.size)}
            </p>
          </div>
          <div className="flex shrink-0 gap-1">
            <button
              type="button"
              onClick={openPicker}
              className="rounded-lg p-2 text-muted transition hover:bg-line/60 hover:text-ink"
              aria-label="別のファイルを選択"
              title="別のファイルを選択"
            >
              <IconSwap />
            </button>
            <button
              type="button"
              onClick={onClear}
              className="rounded-lg p-2 text-muted transition hover:bg-danger/15 hover:text-danger"
              aria-label="ファイルの選択を解除"
              title="選択を解除"
            >
              <IconClose />
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          {...dragProps}
          onClick={openPicker}
          className={`group flex w-full flex-col items-center gap-2 rounded-xl border border-dashed bg-canvas/40 px-4 py-8 text-center transition hover:border-accent/60 hover:bg-accent/5 ${ring}`}
        >
          <span className="grid h-12 w-12 place-items-center rounded-full bg-raised text-accent ring-1 ring-line transition group-hover:scale-105">
            <IconUpload />
          </span>
          <span className="text-sm font-medium text-ink">
            <span className="block">SVGファイルをドロップ</span>
            <span className="text-muted">または </span>
            <span className="whitespace-nowrap text-accent underline decoration-accent/40 underline-offset-4">
              クリックして選択
            </span>
          </span>
          <span className="font-mono text-[11px] text-muted">
            .svg · 最大 {MAX_UPLOAD_MB}MB
          </span>
        </button>
      )}
    </div>
  );
};
