import { useState } from "react";
import { FormValues, initValue } from "../types/FormValues";
import { ConverterResponse } from "../types/ConverterResponse";

export const useDataSubmission = () => {
  const [values, setValues] = useState<FormValues>(initValue);
  const [isPost, setIsPost] = useState<boolean>(false);
  const [converterResponse, setConverterResponse] =
    useState<ConverterResponse | null>(null);

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

  const handleSubmit = () => {
    setIsPost(true);
    // TODO: python-backendへリクエスト

    setIsPost(false);
  };

  return {
    values,
    isPost,
    converterResponse,
    handleChange,
    handleInitialize,
    handleSubmit,
  } as const;
};
