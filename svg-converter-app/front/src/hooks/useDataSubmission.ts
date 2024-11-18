import { ChangeEvent, useState } from "react";
import { FormValues, initValue } from "../types/FormValues";
import { ConverterResponse } from "../types/ConverterResponse";

export type SvgFile = {
  svgName: string;
  svgFile: File | undefined;
};
export const useDataSubmission = () => {
  const [values, setValues] = useState<FormValues>(initValue);
  const [isPost, setIsPost] = useState<boolean>(false);
  const [converterResponse, setConverterResponse] =
    useState<ConverterResponse | null>(null);

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
    setIsPost(true);
    // python-backendへリクエスト
    if (svgFile.svgFile) {
      const formData = new FormData();
      formData.append("file", svgFile.svgFile);
      formData.append("json_data", JSON.stringify(values));

      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const resData: ConverterResponse = await res.json();
      setConverterResponse(resData);
    }

    setIsPost(false);
  };

  return {
    values,
    isPost,
    converterResponse,
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
