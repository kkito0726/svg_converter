import { Body } from "../components/body/Body";
import { Sidebar } from "../components/sidebar/Sidebar";
import { Topbar } from "../components/topbar/Topbar";
import { PageName } from "../enum/PageName";

export const Converter = () => {
  return (
    <div className="min-h-screen w-screen">
      <div className="overflow-auto">
        <Topbar displayName="SVGをAMC描画用CSVへ変換" />
        <div className="flex">
          <Sidebar name={PageName.CONVERTER} />
          <Body pageName={PageName.CONVERTER} />
        </div>
      </div>
    </div>
  );
};
