import { Link } from "react-router-dom";
import { sidebarData } from "../../hooks/getSidebarData";

type SidebarProps = {
  name: string;
};
export const Sidebar: React.FC<SidebarProps> = ({ name }) => {
  const buttonCss = "p-3 cursor-pointer hover:bg-zinc-800 ";
  const selectCss = "bg-zinc-900";
  return (
    <div className="cursor-pointer">
      <ul key="sidebar-item" className="p-0 m-0 list-none text-slate-300">
        {sidebarData.map((data, i) => {
          return (
            <Link key={i} to={data.link}>
              <li
                className={
                  name === data.name ? buttonCss + selectCss : buttonCss
                }
              >
                <p>{data.label}</p>
              </li>
            </Link>
          );
        })}
      </ul>
    </div>
  );
};
