import { useEffect, useRef } from "react";
import { useDataSubmission } from "../../hooks/useDataSubmission";
import { ResFigure } from "../figure/ResFigure";
import { Footer } from "../footer/Footer";
import { IconAlert } from "../icons";
import { FileDropzone } from "./FileDropzone";
import { Form } from "./form/Form";

// 1カラム表示 (lg 未満) のときは変換結果が画面外になるのでスクロールする
const STACKED_LAYOUT_QUERY = "(max-width: 1023px)";

export const Body: React.FC = () => {
  const {
    values,
    isPost,
    result,
    errorMessage,
    svgFile,
    canSubmit,
    handleChange,
    handleInitialize,
    selectFile,
    clearFile,
    handleSubmit,
  } = useDataSubmission();

  const previewRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (result && window.matchMedia(STACKED_LAYOUT_QUERY).matches) {
      previewRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  return (
    <main className="mx-auto grid w-full max-w-[1600px] flex-1 gap-4 p-4 sm:gap-6 sm:p-6 lg:grid-cols-[minmax(320px,380px)_minmax(0,1fr)]">
      <aside className="panel flex flex-col gap-6 self-start p-4 sm:p-5 lg:sticky lg:top-20">
        <section className="space-y-3">
          <h2 className="eyebrow">01 · Input</h2>
          <FileDropzone file={svgFile} onSelect={selectFile} onClear={clearFile} />
        </section>

        <section className="space-y-3">
          <h2 className="eyebrow">02 · Parameters</h2>
          <Form
            values={values}
            isPost={isPost}
            canSubmit={canSubmit}
            handleChange={handleChange}
            handleInitialize={handleInitialize}
            handleSubmit={handleSubmit}
          />
        </section>

        {errorMessage ? (
          <p
            role="alert"
            className="flex animate-rise items-start gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2.5 text-sm text-danger"
          >
            <IconAlert className="mt-0.5 h-4 w-4 shrink-0" />
            {errorMessage}
          </p>
        ) : null}

        <div className="border-t border-line/60 pt-4">
          <Footer />
        </div>
      </aside>

      <ResFigure ref={previewRef} isPost={isPost} result={result} />
    </main>
  );
};
