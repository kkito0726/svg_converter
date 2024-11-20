import { useRef } from "react";
import { useDataSubmission } from "../../hooks/useDataSubmission";
import { ResFigure } from "../figure/ResFigure";
import { Form } from "./form/Form";

type BodyProps = {
  pageName: string;
};
export const Body: React.FC<BodyProps> = ({ pageName }) => {
  const {
    values,
    isPost,
    converterResponse,
    svgFile,
    handleChange,
    handleInitialize,
    handleSvg,
    handleSubmit,
  } = useDataSubmission();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="flex h-screen-minus-topbar">
      <div className="flex flex-col w-input bg-zinc-700 overflow-y-auto hide-scrollbar">
        <div className="flex flex-col px-4 pb-1">
          <span className="block font-medium text-gray-300 rounded-sm text-sm px-1">
            .svgファイルを選択
          </span>
          <button
            type="button"
            className="mt-1 block w-full px-4 py-2 text-center text-gray-200 bg-cyan-600 rounded-md shadow-sm hover:bg-cyan-700 focus:outline-none"
            onClick={handleFileButtonClick}
          >
            ファイルを選択
          </button>
          <input
            ref={fileInputRef}
            onChange={handleSvg}
            type="file"
            accept=".svg"
            className="hidden"
          />
          {svgFile.svgName ? (
            <div className="flex flex-col pb-2">
              <div className="flex justify-between">
                <div>
                  <span className="text-gray-300">{svgFile.svgName}</span>
                </div>
              </div>
            </div>
          ) : (
            <span className="text-gray-300">
              ファイルが読み込まれていません
            </span>
          )}
        </div>
        <Form
          values={values}
          handleChange={handleChange}
          handleInitialize={handleInitialize}
          handleSubmit={handleSubmit}
        />
      </div>
      <div className="overflow-y-auto">
        <ResFigure isPost={isPost} converterResponse={converterResponse} />
      </div>
    </div>
  );
};
