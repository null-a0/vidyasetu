import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  ClipboardList,
  Inbox,
  LogOut,
  GraduationCap,
  Award,
  BarChart3,
  Bell,
  X,
  Users,
  Building2,
  CheckSquare,
  DollarSign,
  User,
  Sparkles,
  LifeBuoy,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRole } from "@/hooks/useRole";
import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/mock/mockData";

interface NavItem {
  to: string;
  label: string;
  icon: React.ElementType;
  roles: UserRole[];
}

const navItems: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "institution_admin", "educator", "student", "technical_support"] },
  { to: "/workshops", label: "Workshops", icon: BookOpen, roles: ["admin", "institution_admin", "educator", "student"] },
  { to: "/materials", label: "Materials", icon: FileText, roles: ["admin", "institution_admin", "educator"] },
  { to: "/assessments", label: "Assessments", icon: ClipboardList, roles: ["admin", "institution_admin", "educator", "student"] },
  { to: "/submissions", label: "Submissions", icon: Inbox, roles: ["admin", "institution_admin", "educator"] },
  { to: "/certificates", label: "Certificates", icon: Award, roles: ["admin", "institution_admin", "educator", "student"] },
  { to: "/reports", label: "Reports", icon: BarChart3, roles: ["admin", "institution_admin", "educator"] },
  { to: "/reports/ai", label: "AI Reports", icon: Sparkles, roles: ["admin", "institution_admin"] },
  { to: "/support", label: "Support", icon: LifeBuoy, roles: ["technical_support"] },
  { to: "/notifications", label: "Notifications", icon: Bell, roles: ["admin", "institution_admin", "educator", "student", "technical_support"] },
  // Management items
  { to: "/manage/students", label: "Students", icon: Users, roles: ["admin", "institution_admin"] },
  { to: "/manage/educators", label: "Educators", icon: GraduationCap, roles: ["admin", "institution_admin"] },
  { to: "/manage/institutes", label: "Institutes", icon: Building2, roles: ["admin"] },
  { to: "/manage/salary", label: "Salary", icon: DollarSign, roles: ["admin"] },
  { to: "/manage/approvals", label: "Approvals", icon: CheckSquare, roles: ["admin"] },
  { to: "/profile", label: "Profile", icon: User, roles: ["admin", "institution_admin", "educator", "student", "technical_support"] },
];

interface SidebarProps {
  onLogout: () => void;
  onClose?: () => void;
}

const Sidebar = ({ onLogout, onClose }: SidebarProps) => {
  const role = useRole();
  const { user: authUser } = useAuth();

  const filteredItems = navItems.filter((item) => role && item.roles.includes(role as UserRole));

  // Group items
  const mainItems = filteredItems.filter(i => !i.to.startsWith("/manage") && i.to !== "/profile");
  const manageItems = filteredItems.filter(i => i.to.startsWith("/manage"));
  const profileItem = filteredItems.find(i => i.to === "/profile");

  const resolveTo = (to: string) => {
    if (to === "/dashboard" && role) {
      if (role === "institution_admin") {
        return "/dashboard/institution";
      }
      return `/dashboard/${role}`;
    }
    return to;
  };

  const renderItem = ({ to, label, icon: Icon }: NavItem) => (
    <NavLink
      key={to}
      to={resolveTo(to)}
      onClick={onClose}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
          isActive
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-sidebar-muted hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        )
      }
    >
      <Icon className="h-[18px] w-[18px]" />
      {label}
    </NavLink>
  );

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl vidya-gradient">
            <GraduationCap className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold text-sidebar-foreground">VidyaSetu</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="lg:hidden rounded-lg p-1 text-sidebar-muted hover:bg-sidebar-accent">
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {mainItems.map(renderItem)}

        {manageItems.length > 0 && (
          <>
            <div className="pt-4 pb-1 px-3">
              <p className="text-[10px] uppercase tracking-widest text-sidebar-muted font-semibold">Management</p>
            </div>
            {manageItems.map(renderItem)}
          </>
        )}

        {profileItem && (
          <>
            <div className="pt-4 pb-1 px-3">
              <p className="text-[10px] uppercase tracking-widest text-sidebar-muted font-semibold">Account</p>
            </div>
            {renderItem(profileItem)}
          </>
        )}
      </nav>

      <div className="border-t border-sidebar-border p-3">
      {authUser && (
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full vidya-gradient text-primary-foreground text-sm font-bold">
            {authUser?.name?.split(" ").map((n) => n[0]).join("").slice(0, 2)}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-sidebar-foreground truncate">{authUser?.name}</p>
            <p className="text-xs text-sidebar-muted truncate">{authUser?.email}</p>
          </div>
        </div>
      )}
        <button
          onClick={onLogout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-sidebar-muted hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all"
        >
          <LogOut className="h-[18px] w-[18px]" />
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

