export type FormValues = {
  power: number;
  speed: number;
};

export const initValue: FormValues = {
  power: 0.5,
  speed: 2000,
};

export const POWER_RANGE = { min: 0.01, max: 1.22, step: 0.01 } as const;
export const SPEED_RANGE = { min: 1, max: 10000, step: 1 } as const;

export const isPowerValid = (power: number): boolean =>
  Number.isFinite(power) &&
  power >= POWER_RANGE.min &&
  power <= POWER_RANGE.max;

export const isSpeedValid = (speed: number): boolean =>
  Number.isInteger(speed) &&
  speed >= SPEED_RANGE.min &&
  speed <= SPEED_RANGE.max;
