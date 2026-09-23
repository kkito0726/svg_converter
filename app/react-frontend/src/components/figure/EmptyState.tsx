import { IconCrosshair } from "../icons";

const STEPS = [
  "SVGファイルを選択",
  "パワーと速度を入力",
  "CSVに変換してダウンロード",
];

export const EmptyState = () => (
  <div className="flex flex-col items-center justify-center gap-8 px-6 py-16 text-center sm:py-24">
    <div className="relative grid h-20 w-20 place-items-center text-accent/80">
      <span className="absolute inset-0 rounded-full border border-dashed border-accent/30" />
      <IconCrosshair className="h-9 w-9" />
      <span className="absolute -bottom-6 whitespace-nowrap font-mono text-[10px] tracking-widest text-muted">
        X 0.0 · Y 0.0
      </span>
    </div>
    <div>
      <h2 className="font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl lg:text-6xl">
        SVG <span className="text-accent">Converter</span>
      </h2>
      <p className="mt-3 text-sm text-muted sm:text-base">
        Inkscape で作成した SVG を AMC 描画用 CSV に変換します
      </p>
    </div>
    <ol className="flex flex-col gap-2 text-left text-sm sm:flex-row sm:gap-6">
      {STEPS.map((step, i) => (
        <li key={step} className="flex items-center gap-2 text-muted">
          <span className="grid h-6 w-6 place-items-center rounded-full border border-line font-mono text-xs text-accent">
            {i + 1}
          </span>
          {step}
        </li>
      ))}
    </ol>
  </div>
);
