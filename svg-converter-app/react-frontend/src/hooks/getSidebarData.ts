import { PageName } from "../enum/PageName";
import { PagePath } from "../enum/PagePath";

type SidebarData = {
  name: string;
  link: string;
  label: string;
};

export const sidebarData: SidebarData[] = [
  {
    name: PageName.CONVERTER,
    link: PagePath.CONVERTER,
    label: "Convert",
  },
  {
    name: PageName.DOWNLOAD,
    link: PagePath.DOWNLOAD,
    label: "Downloads",
  },
];
