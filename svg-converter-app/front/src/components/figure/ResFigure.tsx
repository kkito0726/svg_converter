import { ConverterResponse } from "../../types/ConverterResponse";
import { Processing } from "../Processing";

type FigureProps = {
  isPost: boolean;
  converterResponse: ConverterResponse | null;
};
export const ResFigure: React.FC<FigureProps> = ({
  isPost,
  converterResponse,
}) => {
  const handleCopyToClipboard = async (img_url: string) => {
    try {
      const blob = await fetch(img_url).then((r) => r.blob());
      const item = new ClipboardItem({ "image/png": blob });
      await navigator.clipboard.write([item]);
    } catch (error) {
      console.error("Failed to copy image: ", error);
    }
  };

  const handleDownloadCSV = (csv_url: string) => {
    const link = document.createElement("a");
    link.href = csv_url;
    link.download = csv_url.split("/").pop() || "data.csv"; // Change the file name and extension to .csv
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="flex flex-col">
        {isPost ? <Processing message="処理中です..." /> : null}
        {converterResponse ? (
          <div className="flex items-center justify-center py-4 px-8">
            <div className="relative group">
              <img
                src={
                  "data:image/png;base64," + converterResponse.plot_base64_image
                }
                className="rounded max-w-screen-md"
                alt=""
              />

              <div className="absolute bottom-2 right-2">
                <button
                  onClick={() =>
                    handleCopyToClipboard(
                      "data:image/png;base64," +
                        converterResponse.plot_base64_image
                    )
                  }
                  className="text-slate-200 rounded-sm px-2 py-1 group-hover:opacity-100 transition-opacity hover:bg-gray-200 hover:text-gray-500"
                ></button>
                <button
                  onClick={() => handleDownloadCSV(converterResponse.csv_url)}
                  className="text-slate-200 bg-cyan-500 rounded-sm px-2 py-1 transition-opacity hover:bg-cyan-600"
                >
                  Download AMC Plot CSV File
                </button>
              </div>
            </div>
          </div>
        ) : isPost ? null : (
          <div className="flex flex-col justify-center items-center text-gray-200 px-11 absolute top-1/2 transform -translate-y-1/2">
            <span className="text-8xl">
              SVG <span className="text-cyan-400">Converter</span>
            </span>
            <div className="flex justify-end items-end w-full">
              <span className="text-2xl">
                Powered by LaR<span className="text-green-400">Code</span>
              </span>
            </div>
          </div>
        )}
      </div>
    </>
  );
};
