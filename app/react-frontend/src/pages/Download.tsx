import { Csvs } from "../components/body/Csvs";
import { Sidebar } from "../components/sidebar/Sidebar";
import { Topbar } from "../components/topbar/Topbar";
import { PageName } from "../enum/PageName";

export const Download = () => {
  return (
    <div className="min-h-screen w-screen">
      <div className="overflow-auto">
        <Topbar displayName="SVGをAMC描画用CSVへ変換" />
        <div className="flex">
          <Sidebar name={PageName.DOWNLOAD} />
          <Csvs />
        </div>
      </div>
    </div>
  );
};
