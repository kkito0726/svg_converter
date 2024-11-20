import { useEffect, useState } from "react";
import { handleDownloadCSV } from "../../hooks/download";

export const Csvs = () => {
  const [csvNames, setCsvNames] = useState<string[]>([]);

  useEffect(() => {
    const fetchCsvNames = async () => {
      try {
        const response = await fetch("http://localhost:5002/all-csvs");
        if (!response.ok) {
          throw new Error(`HTTPエラー! ステータス: ${response.status}`);
        }
        const data: string[] = await response.json();
        setCsvNames(data); // ステートにデータを保存
      } catch (error) {
        console.error("CSV名の取得中にエラーが発生しました:", error);
      }
    };
    fetchCsvNames();
  }, []);

  const handleDelete = async (idx: number) => {
    try {
      await fetch("http://localhost:5002/csv", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          csv_name: csvNames[idx],
        }),
      });
      const newCsvs = csvNames.filter((_, i) => i !== idx);
      setCsvNames(newCsvs);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="p-3">
      <span className="text-slate-200">CSV出力履歴</span>
      <div>
        {csvNames.map((csvName, i) => (
          <div
            key={i}
            className="flex items-center justify-between px-4 py-2 bg-zinc-600 rounded-lg shadow-md mb-2 hover:shadow-lg transition-shadow duration-300"
          >
            <button
              onClick={() =>
                handleDownloadCSV(`http://localhost:5002/static/${csvName}`)
              }
              className="text-lg text-slate-200 font-semibold hover:text-cyan-400 hover:underline"
            >
              {csvName}
            </button>
            <button
              className="ml-2 px-2 py-1 bg-orange-600 text-white text-sm font-medium rounded-md shadow-sm hover:bg-red-500 transition-all"
              onClick={() => handleDelete(i)} // Replace with your handler
            >
              削除
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
