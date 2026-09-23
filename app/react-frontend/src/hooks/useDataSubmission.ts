import { ChangeEvent, useState } from "react";
import { FormValues, initValue } from "../types/FormValues";
import {
  ConverterErrorResponse,
  ConverterResponse,
} from "../types/ConverterResponse";
import { SVG2CSV_ENDPOINT } from "../config/api";

export type SvgFile = {
  svgName: string;
  svgFile: File | undefined;
};
export const useDataSubmission = () => {
  const [values, setValues] = useState<FormValues>(initValue);
  const [isPost, setIsPost] = useState<boolean>(false);
  const [converterResponse, setConverterResponse] =
    useState<ConverterResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [svgFile, setSvgFile] = useState<SvgFile>({
    svgName: "",
    svgFile: undefined,
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    if (name === "power") {
      setValues({
        ...values,
        power: parseFloat(value),
      });
    } else {
      setValues({
        ...values,
        speed: parseInt(value),
      });
    }
  };

  const handleInitialize = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    setValues(initValue);
  };

  const handleSvg = (e: ChangeEvent<HTMLInputElement>) => {
    const file = handleFileFromChangeEvent(e);
    if (file) {
      setSvgFile({
        svgName: file.name,
        svgFile: file,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!svgFile.svgFile) {
      setErrorMessage("SVGファイルを選択してください");
      return;
    }

    setIsPost(true);
    setErrorMessage(null);
    try {
      const formData = new FormData();
      formData.append("file", svgFile.svgFile);
      formData.append("json_data", JSON.stringify(values));

      const res = await fetch(SVG2CSV_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error(await readErrorMessage(res));
      }
      const resData: ConverterResponse = await res.json();
      setConverterResponse(resData);
    } catch (error) {
      setConverterResponse(null);
      setErrorMessage(
        error instanceof Error ? error.message : "変換に失敗しました"
      );
    } finally {
      setIsPost(false);
    }
  };

  return {
    values,
    isPost,
    converterResponse,
    errorMessage,
    svgFile,
    handleChange,
    handleInitialize,
    handleSvg,
    handleSubmit,
  } as const;
};

const handleFileFromChangeEvent = (
  e: ChangeEvent<HTMLInputElement>
): File | undefined => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.item(0);

  if (!file) {
    return;
  }
  return file;
};

const readErrorMessage = async (res: Response): Promise<string> => {
  if (res.status === 429) {
    return "リクエストが多すぎます。少し時間をおいて再度お試しください";
  }
  try {
    const body: ConverterErrorResponse = await res.json();
    return body.error || `変換に失敗しました (HTTP ${res.status})`;
  } catch {
    return `変換に失敗しました (HTTP ${res.status})`;
  }
};
