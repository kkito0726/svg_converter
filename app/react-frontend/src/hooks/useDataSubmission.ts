import { useState } from "react";
import {
  FormValues,
  initValue,
  isPowerValid,
  isSpeedValid,
} from "../types/FormValues";
import {
  ConverterErrorResponse,
  ConverterResponse,
} from "../types/ConverterResponse";
import {
  MAX_UPLOAD_BYTES,
  MAX_UPLOAD_MB,
  SVG2CSV_ENDPOINT,
} from "../config/api";

export type ConversionResult = ConverterResponse & {
  params: FormValues;
};

export const useDataSubmission = () => {
  const [values, setValues] = useState<FormValues>(initValue);
  const [isPost, setIsPost] = useState<boolean>(false);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [svgFile, setSvgFile] = useState<File | undefined>(undefined);

  const canSubmit =
    !!svgFile && !isPost && isPowerValid(values.power) && isSpeedValid(values.speed);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues((prev) =>
      name === "power"
        ? { ...prev, power: parseFloat(value) }
        : { ...prev, speed: parseInt(value, 10) }
    );
  };

  const handleInitialize = () => setValues(initValue);

  const selectFile = (file: File) => {
    const validationError = validateSvgFile(file);
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }
    setErrorMessage(null);
    setSvgFile(file);
  };

  const clearFile = () => setSvgFile(undefined);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!svgFile) {
      setErrorMessage("SVGファイルを選択してください");
      return;
    }
    if (!canSubmit) return;

    const params = { ...values };
    setIsPost(true);
    setErrorMessage(null);
    try {
      const formData = new FormData();
      formData.append("file", svgFile);
      formData.append("json_data", JSON.stringify(params));

      const res = await fetch(SVG2CSV_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error(await readErrorMessage(res));
      }
      const resData: ConverterResponse = await res.json();
      setResult({ ...resData, params });
    } catch (error) {
      setResult(null);
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
    result,
    errorMessage,
    svgFile,
    canSubmit,
    handleChange,
    handleInitialize,
    selectFile,
    clearFile,
    handleSubmit,
  } as const;
};

const validateSvgFile = (file: File): string | null => {
  if (!file.name.toLowerCase().endsWith(".svg")) {
    return "SVGファイル(.svg)を選択してください";
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return `ファイルサイズは ${MAX_UPLOAD_MB}MB 以下にしてください`;
  }
  return null;
};

const readErrorMessage = async (res: Response): Promise<string> => {
  if (res.status === 413) {
    return `ファイルサイズは ${MAX_UPLOAD_MB}MB 以下にしてください`;
  }
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
