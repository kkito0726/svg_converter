import { Body } from "../components/body/Body";
import { Topbar } from "../components/topbar/Topbar";

export const Converter = () => {
  return (
    <div className="flex min-h-dvh flex-col">
      <Topbar displayName="SVG → AMC描画用CSV 変換" />
      <Body />
    </div>
  );
};
