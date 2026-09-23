import { FormValues } from "../../../types/FormValues";
import { getFormData } from "../../../hooks/getFormData";
import { IconReset, IconSpinner } from "../../icons";

export type FormProps = {
  values: FormValues;
  isPost: boolean;
  canSubmit: boolean;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleInitialize: () => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};

export const Form: React.FC<FormProps> = ({
  values,
  isPost,
  canSubmit,
  handleChange,
  handleInitialize,
  handleSubmit,
}) => {
  const fields = getFormData(values);

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div className="grid grid-cols-2 gap-3">
        {fields.map((field) => (
          <div key={field.name}>
            <label
              htmlFor={field.name}
              className="mb-1.5 block text-xs font-medium text-muted"
            >
              {field.label}
            </label>
            <div
              className={`flex items-center rounded-lg border bg-canvas/60 transition focus-within:border-accent focus-within:shadow-[0_0_0_3px_rgb(var(--c-accent)/0.15)] ${
                field.isValid ? "border-line" : "border-danger/70"
              }`}
            >
              <input
                type="number"
                id={field.name}
                name={field.name}
                inputMode={field.step < 1 ? "decimal" : "numeric"}
                className="w-full min-w-0 bg-transparent py-2.5 pl-3 font-mono text-base text-ink outline-none [appearance:textfield] focus-visible:ring-0 focus-visible:ring-offset-0 [&::-webkit-inner-spin-button]:appearance-none"
                value={Number.isNaN(field.value) ? "" : field.value}
                min={field.min}
                max={field.max}
                step={field.step}
                aria-invalid={!field.isValid}
                aria-describedby={`${field.name}-hint`}
                onChange={handleChange}
              />
              <span className="pr-3 font-mono text-xs text-muted">
                {field.unit}
              </span>
            </div>
            <p
              id={`${field.name}-hint`}
              className={`mt-1 font-mono text-[11px] ${
                field.isValid ? "text-muted/70" : "text-danger"
              }`}
            >
              {field.min} – {field.max}
            </p>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleInitialize}
          className="btn-ghost"
          title="初期値に戻す"
        >
          <IconReset />
          <span className="sr-only sm:not-sr-only">リセット</span>
        </button>
        <button type="submit" className="btn-primary flex-1" disabled={!canSubmit}>
          {isPost ? (
            <>
              <IconSpinner />
              変換中…
            </>
          ) : (
            "CSVに変換"
          )}
        </button>
      </div>
    </form>
  );
};
