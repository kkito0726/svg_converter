import { forwardRef } from "react";
import { ConversionResult } from "../../hooks/useDataSubmission";
import { Processing } from "../Processing";
import { EmptyState } from "./EmptyState";
import { ResultToolbar } from "./ResultToolbar";

type FigureProps = {
  isPost: boolean;
  result: ConversionResult | null;
};

export const ResFigure = forwardRef<HTMLElement, FigureProps>(
  ({ isPost, result }, ref) => (
    <section
      ref={ref}
      aria-label="変換結果"
      className="panel relative flex min-h-[420px] scroll-mt-20 flex-col lg:min-h-[calc(100dvh-7rem)]"
    >
      {isPost ? <Processing message="変換中…" /> : null}
      {result ? (
        <div key={result.csv_name + result.csv_text.length} className="flex flex-1 animate-rise flex-col">
          <ResultToolbar result={result} />
          <div className="relative flex flex-1 items-center justify-center p-4 sm:p-6">
            <span className="crop-marks" />
            <img
              src={`data:image/png;base64,${result.plot_base64_image}`}
              className="h-auto w-full max-w-3xl rounded-lg bg-white object-contain shadow-2xl shadow-black/50 lg:max-h-[calc(100dvh-16rem)] lg:w-auto"
              alt={`${result.csv_name} の描画プレビュー`}
            />
          </div>
        </div>
      ) : (
        <div className="relative flex flex-1 items-center justify-center">
          <span className="crop-marks" />
          <EmptyState />
        </div>
      )}
    </section>
  )
);

ResFigure.displayName = "ResFigure";
