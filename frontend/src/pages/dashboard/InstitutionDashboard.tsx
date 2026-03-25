import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BookOpen, Users, ClipboardList, Award, TrendingUp, TrendingDown, Plus, AlertCircle, Eye, Calendar, CheckSquare } from "lucide-react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useVToast } from "@/components/ui-custom/VToast";
import { fetchWorkshops } from "@/services/api";
import type { Workshop } from "@/mock/mockData";

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-success/10 text-success",
];

const statsData = [
  { label: "Institution Workshops", value: "12", icon: BookOpen, trend: "+3", up: true },
  { label: "Educators", value: "8", icon: Users, trend: "+2", up: true },
  { label: "Active Assessments", value: "6", icon: ClipboardList, trend: "-1", up: false },
  { label: "Certificates Issued", value: "145", icon: Award, trend: "+22%", up: true },
];

const alerts = [
  { id: "1", text: "Cloud Computing Basics workshop starting in 2 weeks", type: "warning" },
  { id: "2", text: "5 students pending certificate approval", type: "info" },
  { id: "3", text: "React Fundamentals enrollment target reached", type: "success" },
];

const recentActivity = [
  { id: "1", text: "Dr. Anand uploaded 'React Hooks Guide'", time: "10 min ago" },
  { id: "2", text: "42 students enrolled in React Fundamentals", time: "1 hour ago" },
  { id: "3", text: "Assessment results published for UI/UX", time: "3 hours ago" },
  { id: "4", text: "New educator Dr. Meera onboarded", time: "Yesterday" },
];

const enrollmentData = [
  { month: "Jan", students: 120 },
  { month: "Feb", students: 185 },
  { month: "Mar", students: 210 },
  { month: "Apr", students: 165 },
  { month: "May", students: 240 },
  { month: "Jun", students: 280 },
];

const studentData = [
  { id: "1", name: "Aarav Sharma", email: "aarav@student.com", workshop: "React Fundamentals", status: "Active" },
  { id: "2", name: "Priya Patel", email: "priya@student.com", workshop: "React Fundamentals", status: "Active" },
  { id: "3", name: "Rohan Gupta", email: "rohan@student.com", workshop: "Python for Data Science", status: "Active" },
  { id: "4", name: "Sneha Reddy", email: "sneha@student.com", workshop: "Cloud Computing Basics", status: "Inactive" },
  { id: "5", name: "Vikram Singh", email: "vikram@student.com", workshop: "UI/UX Design Principles", status: "Completed" },
  { id: "6", name: "Ananya Iyer", email: "ananya@student.com", workshop: "React Fundamentals", status: "Active" },
];

const attendanceData = [
  { student: "Aarav Sharma", mon: true, tue: true, wed: false, thu: true, fri: true },
  { student: "Priya Patel", mon: true, tue: true, wed: true, thu: true, fri: true },
  { student: "Rohan Gupta", mon: false, tue: true, wed: true, thu: false, fri: true },
  { student: "Sneha Reddy", mon: true, tue: false, wed: true, thu: true, fri: false },
  { student: "Vikram Singh", mon: true, tue: true, wed: true, thu: true, fri: true },
];

const InstitutionDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const [activeTab, setActiveTab] = useState<"overview" | "students" | "attendance" | "reports">("overview");
  const [createModal, setCreateModal] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(new Set());

  const toggleStudent = (id: string) => {
    setSelectedStudents(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (selectedStudents.size === studentData.length) setSelectedStudents(new Set());
    else setSelectedStudents(new Set(studentData.map(s => s.id)));
  };

  const columns = [
    { key: "name", header: "Workshop" },
    { key: "startDate", header: "Start" },
    { key: "endDate", header: "End" },
    { key: "studentsEnrolled", header: "Students" },
    { key: "status", header: "Status", render: (r: Workshop) => (
      <VBadge variant={r.status === "Active" ? "success" : r.status === "Upcoming" ? "warning" : "outline"}>
        {r.status}
      </VBadge>
    )},
    { key: "actions", header: "", render: (r: Workshop) => (
      <VButton variant="secondary" size="sm" onClick={() => { navigate(`/workshops/${r.id}`); }}>
        <Eye className="h-3.5 w-3.5" /> View
      </VButton>
    )},
  ];

  const tabs = [
    { key: "overview", label: "Overview" },
    { key: "students", label: "Students" },
    { key: "attendance", label: "Attendance" },
    { key: "reports", label: "Reports" },
  ];

  return (
    <DashboardLayout title="Institution Dashboard">
      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-border overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
              activeTab === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ═══ OVERVIEW ═══ */}
      {activeTab === "overview" && (
        <>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
            {statsData.map(({ label, value, icon: Icon, trend, up }, i) => (
              <VCard key={label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", label, `Showing ${label.toLowerCase()} details`)}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconColors[i]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${up ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"}`}>
                    {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {trend}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold text-foreground mt-1">{value}</p>
              </VCard>
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-2 mb-8">
            {/* Alerts */}
            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Alerts & Reminders</h3>
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <button
                    key={alert.id}
                    onClick={() => showToast(alert.type as any, alert.text)}
                    className="flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left hover:bg-accent transition-colors"
                  >
                    <AlertCircle className={`h-5 w-5 mt-0.5 shrink-0 ${
                      alert.type === "warning" ? "text-warning" : alert.type === "success" ? "text-success" : "text-info"
                    }`} />
                    <p className="text-sm text-foreground">{alert.text}</p>
                  </button>
                ))}
              </div>
            </VCard>

            {/* Recent Activity */}
            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Recent Activity</h3>
              <div className="space-y-1">
                {recentActivity.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => showToast("info", item.text)}
                    className="flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left hover:bg-accent transition-colors"
                  >
                    <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                    <div>
                      <p className="text-sm text-foreground">{item.text}</p>
                      <p className="text-xs text-muted-foreground">{item.time}</p>
                    </div>
                  </button>
                ))}
              </div>
            </VCard>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Institution Workshops</h2>
            <VButton onClick={() => setCreateModal(true)}>
              <Plus className="h-4 w-4" /> Create Workshop
            </VButton>
          </div>
          <div className="overflow-x-auto">
            <VTable columns={columns} data={workshops} />
          </div>
        </>
      )}

      {/* ═══ STUDENTS ═══ */}
      {activeTab === "students" && (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">{selectedStudents.size} selected</p>
            <div className="flex gap-2">
              {selectedStudents.size > 0 && (
                <>
                  <VButton variant="secondary" size="sm" onClick={() => { showToast("info", "Export", `Exporting ${selectedStudents.size} student records`); }}>
                    Export Selected
                  </VButton>
                  <VButton variant="destructive" size="sm" onClick={() => { showToast("warning", "Bulk Action", `Action applied to ${selectedStudents.size} students`); setSelectedStudents(new Set()); }}>
                    Bulk Action
                  </VButton>
                </>
              )}
            </div>
          </div>
          <VCard className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-4 py-3 text-left">
                    <input type="checkbox" checked={selectedStudents.size === studentData.length} onChange={toggleAll} className="rounded border-border" />
                  </th>
                  <th className="vidya-table-header px-4 py-3 text-left">Name</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Email</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Workshop</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Status</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {studentData.map((s) => (
                  <tr key={s.id} className={`border-b border-border last:border-0 transition-colors ${selectedStudents.has(s.id) ? "bg-primary/5" : "hover:bg-accent/50"}`}>
                    <td className="px-4 py-4">
                      <input type="checkbox" checked={selectedStudents.has(s.id)} onChange={() => toggleStudent(s.id)} className="rounded border-border" />
                    </td>
                    <td className="px-4 py-4 font-medium text-foreground">{s.name}</td>
                    <td className="px-4 py-4 text-muted-foreground">{s.email}</td>
                    <td className="px-4 py-4 text-foreground">{s.workshop}</td>
                    <td className="px-4 py-4">
                      <VBadge variant={s.status === "Active" ? "success" : s.status === "Completed" ? "default" : "warning"}>
                        {s.status}
                      </VBadge>
                    </td>
                    <td className="px-4 py-4">
                      <VButton variant="secondary" size="sm" onClick={() => showToast("info", `Viewing ${s.name}'s profile`)}>
                        <Eye className="h-3.5 w-3.5" /> View
                      </VButton>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </VCard>
        </>
      )}

      {/* ═══ ATTENDANCE ═══ */}
      {activeTab === "attendance" && (
        <VCard className="overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h3 className="text-base font-semibold text-foreground">Weekly Attendance — React Fundamentals</h3>
            <VButton variant="secondary" size="sm" onClick={() => showToast("info", "Attendance exported")}>
              <Calendar className="h-3.5 w-3.5" /> Export
            </VButton>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="vidya-table-header px-4 py-3 text-left">Student</th>
                {["Mon", "Tue", "Wed", "Thu", "Fri"].map(d => (
                  <th key={d} className="vidya-table-header px-4 py-3 text-center">{d}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {attendanceData.map((row) => (
                <tr key={row.student} className="border-b border-border last:border-0 hover:bg-accent/50 transition-colors">
                  <td className="px-4 py-4 font-medium text-foreground">{row.student}</td>
                  {["mon", "tue", "wed", "thu", "fri"].map((day) => (
                    <td key={day} className="px-4 py-4 text-center">
                      <span className={`inline-flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold ${
                        (row as any)[day] ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
                      }`}>
                        {(row as any)[day] ? <CheckSquare className="h-4 w-4" /> : "✗"}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </VCard>
      )}

      {/* ═══ REPORTS ═══ */}
      {activeTab === "reports" && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Enrollment Trends</h3>
            <VButton variant="secondary" size="sm" onClick={() => showToast("success", "Report Exported", "PDF report downloaded successfully")}>
              Export Report
            </VButton>
          </div>
          <VCard className="p-0 mb-8">
            <div className="h-64 px-2 py-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={enrollmentData}>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                  <Bar dataKey="students" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </VCard>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Average Score", value: "76%", desc: "Across all assessments" },
              { label: "Completion Rate", value: "82%", desc: "Workshop completion" },
              { label: "Top Workshop", value: "React", desc: "Highest enrollment" },
              { label: "Pass Rate", value: "89%", desc: "Assessment pass rate" },
            ].map((item) => (
              <VCard key={item.label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", item.label, item.desc)}>
                <p className="text-sm text-muted-foreground">{item.label}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{item.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
              </VCard>
            ))}
          </div>
        </>
      )}

      {/* Create Workshop Modal */}
      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Workshop">
        <div className="space-y-4">
          <VInput id="inst-w-name" label="Workshop Name" placeholder="e.g. React Fundamentals" />
          <div className="space-y-1.5"><label className="vidya-label">Description</label><textarea placeholder="Workshop description..." rows={3} className="vidya-input resize-none" /></div>
          <VSelect id="inst-w-status" label="Status" options={[
            { value: "Upcoming", label: "Upcoming" },
            { value: "Active", label: "Active" },
          ]} />
          <div className="flex justify-end gap-3 pt-2">
            <VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton>
            <VButton onClick={() => { setCreateModal(false); showToast("success", "Workshop Created", "New workshop added successfully"); }}>
              Create Workshop
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default InstitutionDashboard;
