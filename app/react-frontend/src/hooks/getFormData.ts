import {
  FormValues,
  POWER_RANGE,
  SPEED_RANGE,
  isPowerValid,
  isSpeedValid,
} from "../types/FormValues";

export type FormField = {
  name: keyof FormValues;
  label: string;
  unit: string;
  value: number;
  min: number;
  max: number;
  step: number;
  isValid: boolean;
};

export const getFormData = (values: FormValues): FormField[] => [
  {
    name: "power",
    label: "レーザーパワー",
    unit: "W",
    value: values.power,
    ...POWER_RANGE,
    isValid: isPowerValid(values.power),
  },
  {
    name: "speed",
    label: "ステージ速度",
    unit: "μm/s",
    value: values.speed,
    ...SPEED_RANGE,
    isValid: isSpeedValid(values.speed),
  },
];
