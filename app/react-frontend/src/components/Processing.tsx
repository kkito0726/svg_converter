type ProcessingProps = {
  message: string;
};

// プレビュー領域を覆い、レーザーが走査するようなラインを表示する
export const Processing: React.FC<ProcessingProps> = ({ message }) => {
  return (
    <div
      className="absolute inset-0 z-10 overflow-hidden rounded-2xl bg-canvas/75 backdrop-blur-sm"
      role="status"
      aria-live="polite"
    >
      <div className="absolute inset-x-6 top-6 bottom-6">
        <div className="absolute inset-x-0 h-px animate-scan bg-laser shadow-[0_0_12px_2px_rgb(var(--c-laser)/0.8),0_0_40px_8px_rgb(var(--c-laser)/0.25)]" />
      </div>
      <div className="absolute inset-0 grid place-items-center">
        <p className="rounded-full border border-line bg-panel/90 px-4 py-2 font-mono text-sm text-ink">
          <span className="mr-2 inline-block h-2 w-2 animate-pulse rounded-full bg-laser align-middle" />
          {message}
        </p>
      </div>
    </div>
  );
};
