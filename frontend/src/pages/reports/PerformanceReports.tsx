import { useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import { useVToast } from "@/components/ui-custom/VToast";
import { Download } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchAllUsers, fetchStudentAnalytics, fetchWorkshopAnalytics, fetchWorkshops } from "@/services/api";

type WorkshopAnalytics = {
  workshop_id: string;
  enrollment?: { total_enrolled?: number; completed?: number; dropped?: number };
  assessment?: { total_submissions?: number; avg_percentage?: number; pass_rate_percentage?: number };
};

type StudentAnalytics = {
  student_id: string;
  enrolled_workshops?: number;
  assessment?: {
    avg_percentage?: number;
    passed?: number;
    failed?: number;
    score_trend?: { percentage?: number | null; submitted_at?: string | null }[];
  };
};

const PerformanceReports = () => {
  const { showToast } = useVToast();
  const [hoveredStudent, setHoveredStudent] = useState<string | null>(null);

  const workshopsQuery = useQuery({
    queryKey: ["workshops"],
    queryFn: fetchWorkshops,
  });

  const studentsQuery = useQuery({
    queryKey: ["students"],
    queryFn: async () => {
      const users = await fetchAllUsers({ max: 500 });
      return users.filter((u) => u.role === "student");
    },
  });

  const workshopIdsKey = useMemo(() => (workshopsQuery.data ?? []).map((w) => w.id).slice(0, 20).sort().join(","), [workshopsQuery.data]);

  const workshopAnalyticsQuery = useQuery({
    queryKey: ["workshopAnalytics", workshopIdsKey],
    queryFn: async () => {
      const workshops = workshopsQuery.data ?? [];
      const limited = workshops.slice(0, 20);
      const results = await Promise.all(
        limited.map(async (w) => {
          try {
            const data = (await fetchWorkshopAnalytics(w.id)) as WorkshopAnalytics;
            return { workshopId: w.id, title: w.name, data };
          } catch {
            return { workshopId: w.id, title: w.name, data: { workshop_id: w.id } as WorkshopAnalytics };
          }
        })
      );
      return results;
    },
    enabled: (workshopsQuery.data?.length ?? 0) > 0,
  });

  const studentIdsKey = useMemo(() => (studentsQuery.data ?? []).map((s) => s.id).slice(0, 10).sort().join(","), [studentsQuery.data]);

  const studentAnalyticsQuery = useQuery({
    queryKey: ["studentAnalytics", studentIdsKey],
    queryFn: async () => {
      const students = studentsQuery.data ?? [];
      const limited = students.slice(0, 10);
      const results = await Promise.all(
        limited.map(async (s) => {
          try {
            const data = (await fetchStudentAnalytics(s.id)) as StudentAnalytics;
            return { studentId: s.id, name: s.name || s.email, data };
          } catch {
            return { studentId: s.id, name: s.name || s.email, data: { student_id: s.id } as StudentAnalytics };
          }
        })
      );
      return results;
    },
    enabled: (studentsQuery.data?.length ?? 0) > 0,
  });

  const reportData = useMemo(() => {
    const wa = workshopAnalyticsQuery.data ?? [];

    const totals = wa.reduce(
      (acc, w) => {
        const enrolled = w.data.enrollment?.total_enrolled ?? 0;
        const completed = w.data.enrollment?.completed ?? 0;
        const submissions = w.data.assessment?.total_submissions ?? 0;
        const avgPct = w.data.assessment?.avg_percentage ?? 0;
        const passRate = w.data.assessment?.pass_rate_percentage ?? 0;

        acc.totalEnrolled += enrolled;
        acc.totalCompleted += completed;
        acc.totalSubmissions += submissions;
        acc.sumAvgPct += avgPct;
        acc.sumPassRateWeighted += passRate * submissions;
        acc.avgPctCount += submissions > 0 ? 1 : 0;

        if (enrolled > acc.topEnrollment) {
          acc.topEnrollment = enrolled;
          acc.topWorkshop = w.title;
        }
        return acc;
      },
      {
        totalEnrolled: 0,
        totalCompleted: 0,
        totalSubmissions: 0,
        sumAvgPct: 0,
        sumPassRateWeighted: 0,
        avgPctCount: 0,
        topEnrollment: 0,
        topWorkshop: "",
      }
    );

    const avgScore = totals.avgPctCount > 0 ? Math.round(totals.sumAvgPct / totals.avgPctCount) : 0;
    const completion = totals.totalEnrolled > 0 ? Math.round((totals.totalCompleted / totals.totalEnrolled) * 100) : 0;
    const passRate = totals.totalSubmissions > 0 ? Math.round(totals.sumPassRateWeighted / totals.totalSubmissions) : 0;

    return [
      { label: "Average Score", value: `${avgScore}%`, description: "Across available assessments" },
      { label: "Completion Rate", value: `${completion}%`, description: "Workshop completion (enrollments)" },
      { label: "Top Workshop", value: totals.topWorkshop || "—", description: "Highest enrollment (sampled)" },
      { label: "Pass Rate", value: `${passRate}%`, description: "Across available submissions" },
    ];
  }, [workshopAnalyticsQuery.data]);

  const studentPerformance = useMemo(() => {
    const results = studentAnalyticsQuery.data ?? [];
    const rows = results.map((r) => ({
      name: r.name,
      avgScore: Math.round(r.data.assessment?.avg_percentage ?? 0),
      workshopsCompleted: r.data.enrolled_workshops ?? 0,
      passed: r.data.assessment?.passed ?? 0,
      failed: r.data.assessment?.failed ?? 0,
      trend: r.data.assessment?.score_trend ?? [],
    }));
    // Prefer higher avg score.
    rows.sort((a, b) => b.avgScore - a.avgScore);
    return rows.slice(0, 5);
  }, [studentAnalyticsQuery.data]);

  const barData = useMemo(() => {
    // Build a 6-month trend from student score_trend submissions.
    const now = new Date();
    const buckets = Array.from({ length: 6 }).map((_, idx) => {
      const d = new Date(now);
      d.setMonth(now.getMonth() - (5 - idx));
      const key = d.toISOString().slice(0, 7);
      return { key, month: d.toLocaleString("en-US", { month: "short" }), scores: [] as number[] };
    });

    const scorePoints = studentPerformance.flatMap((s) => s.trend || []);
    for (const p of scorePoints) {
      const dt = p.submitted_at ? new Date(p.submitted_at) : null;
      if (!dt || Number.isNaN(dt.getTime())) continue;
      const key = dt.toISOString().slice(0, 7);
      const bucket = buckets.find((b) => b.key === key);
      if (!bucket) continue;
      const pct = p.percentage ?? null;
      if (pct === null || pct === undefined) continue;
      bucket.scores.push(Number(pct));
    }

    return buckets.map((b) => {
      const avg = b.scores.length > 0 ? Math.round(b.scores.reduce((s, n) => s + n, 0) / b.scores.length) : 0;
      return { month: b.month, score: avg };
    });
  }, [studentPerformance]);

  const pieData = useMemo(() => {
    const passed = studentPerformance.reduce((s, r) => s + (r.passed || 0), 0);
    const failed = studentPerformance.reduce((s, r) => s + (r.failed || 0), 0);
    const total = passed + failed;
    const passPct = total > 0 ? Math.round((passed / total) * 100) : 0;
    const failPct = total > 0 ? 100 - passPct : 0;
    return [
      { name: "Passed", value: passPct, color: "hsl(var(--success))" },
      { name: "Failed", value: failPct, color: "hsl(var(--destructive))" },
    ];
  }, [studentPerformance]);

  const isLoading =
    workshopsQuery.isLoading || studentsQuery.isLoading || workshopAnalyticsQuery.isLoading || studentAnalyticsQuery.isLoading;

  return (
    <DashboardLayout title="Performance Reports">
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">
          Comprehensive performance analytics {isLoading ? "(loading...)" : ""}
        </p>
        <VButton variant="secondary" onClick={() => showToast("success", "Report Exported", "PDF report downloaded")}>
          <Download className="h-4 w-4" /> Export PDF
        </VButton>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {reportData.map((item) => (
          <VCard key={item.label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", item.label, item.description)}>
            <p className="text-sm text-muted-foreground">{item.label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{item.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
          </VCard>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2 mb-8">
        <VCard className="p-0">
          <div className="px-5 pt-5 pb-2">
            <h3 className="text-base font-semibold text-foreground">Monthly Score Trend</h3>
            <p className="text-sm text-muted-foreground">Average across sampled student submissions</p>
          </div>
          <div className="h-56 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} domain={[0, 100]} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                <Bar dataKey="score" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </VCard>

        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-2">Pass/Fail Distribution</h3>
          <p className="text-sm text-muted-foreground mb-4">Across sampled student submissions</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2">
            {pieData.map((d) => (
              <div key={d.name} className="flex items-center gap-2 text-sm">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-muted-foreground">{d.name}: {d.value}%</span>
              </div>
            ))}
          </div>
        </VCard>
      </div>

      <h2 className="text-lg font-semibold text-foreground mb-4">Student Performance</h2>
      <VCard className="overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="vidya-table-header px-6 py-3 text-left">Student</th>
              <th className="vidya-table-header px-6 py-3 text-left">Avg Score</th>
              <th className="vidya-table-header px-6 py-3 text-left">Workshops</th>
              <th className="vidya-table-header px-6 py-3 text-left">Progress</th>
            </tr>
          </thead>
          <tbody>
            {studentPerformance.map((s) => (
              <tr
                key={s.name}
                onMouseEnter={() => setHoveredStudent(s.name)}
                onMouseLeave={() => setHoveredStudent(null)}
                onClick={() => showToast("info", s.name, `Average score: ${s.avgScore}%, Workshops: ${s.workshopsCompleted}`)}
                className={`border-b border-border last:border-0 cursor-pointer transition-colors ${hoveredStudent === s.name ? "bg-primary/5" : "hover:bg-accent/50"}`}
              >
                <td className="px-6 py-4 text-foreground font-medium">{s.name}</td>
                <td className="px-6 py-4 text-foreground">{s.avgScore}%</td>
                <td className="px-6 py-4 text-foreground">{s.workshopsCompleted}</td>
                <td className="px-6 py-4">
                  <div className="w-32 h-2 rounded-full bg-secondary">
                    <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${s.avgScore}%` }} />
                  </div>
                </td>
              </tr>
            ))}
            {studentPerformance.length === 0 && (
              <tr>
                <td className="px-6 py-6 text-muted-foreground" colSpan={4}>
                  {isLoading ? "Loading..." : "No student analytics found."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </VCard>
    </DashboardLayout>
  );
};

export default PerformanceReports;
