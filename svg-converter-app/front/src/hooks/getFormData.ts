import { FormValues } from "../types/FormValues";

type FormData = {
  name: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
};

export const getFormData = (values: FormValues): FormData[] => {
  return [
    {
      name: "power",
      label: "Power (W)",
      value: values.power,
      min: 0.01,
      max: 1.22,
      step: 0.01,
    },
    {
      name: "end",
      label: "Speed (μm/s)",
      value: values.speed,
      min: 1,
      max: 10000,
      step: 1,
    },
  ];
};
