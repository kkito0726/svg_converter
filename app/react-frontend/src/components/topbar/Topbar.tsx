import { IconCrosshair } from "../icons";

type TopbarProps = {
  displayName: string;
};

export const Topbar: React.FC<TopbarProps> = ({ displayName }) => {
  return (
    <header className="sticky top-0 z-30 border-b border-line/60 bg-canvas/75 backdrop-blur-md">
      <div className="mx-auto flex h-14 w-full max-w-[1600px] items-center justify-between gap-4 px-4 sm:px-6">
        <a href="/" className="group flex items-center gap-2.5 rounded-lg">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent/10 text-accent ring-1 ring-accent/30 transition group-hover:bg-accent/20">
            <IconCrosshair className="h-[18px] w-[18px]" />
          </span>
          <span className="font-display text-lg font-semibold tracking-tight">
            SVG <span className="text-accent">Converter</span>
          </span>
        </a>
        <span className="hidden truncate text-sm text-muted md:block">
          {displayName}
        </span>
        <span className="hidden font-mono text-xs tracking-wide text-muted sm:block">
          LaRC FB Hosei Univ.
        </span>
      </div>
    </header>
  );
};
