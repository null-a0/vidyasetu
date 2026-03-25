import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BookOpen, ClipboardList, Award, TrendingUp, TrendingDown, Play, CheckCircle2, Clock, Star, Search, Filter, FileText, Users } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import { fetchStudentStats, fetchWorkshops, fetchEnrollments, enrollInWorkshop } from "@/services/api";
import type { Workshop } from "@/mock/mockData";

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-success/10 text-success",
];

const trends = ["+2", "+5", "+4.2%", "+1"];

const statCards = [
  { key: "enrolledWorkshops", label: "Enrolled Workshops", icon: BookOpen },
  { key: "completedAssessments", label: "Assessments Done", icon: ClipboardList },
  { key: "averageScore", label: "Average Score", icon: TrendingUp },
  { key: "certificatesEarned", label: "Certificates", icon: Award },
] as const;

const progressData = [
  { week: "W1", score: 65 },
  { week: "W2", score: 72 },
  { week: "W3", score: 70 },
  { week: "W4", score: 85 },
  { week: "W5", score: 82 },
  { week: "W6", score: 90 },
];

type MyCourse = {
  id: string;
  workshopId: string;
  name: string;
  progress: number;
  status: "In Progress" | "Completed";
  modules: number;
  completed: number;
};
const categories = ["All", "Programming", "Data Science", "Design", "Cloud", "DevOps"];

const StudentDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const { user } = useAuth();
  const { data: stats } = useQuery({
    queryKey: ["studentStats", user?.id],
    queryFn: () => fetchStudentStats(user?.id ?? ""),
    enabled: Boolean(user),
  });
  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const { data: enrollments, refetch: refetchEnrollments } = useQuery({
    queryKey: ["enrollments", user?.id],
    queryFn: () => fetchEnrollments(user?.id ?? ""),
    enabled: Boolean(user),
  });
  const enrolledIds = useMemo(
    () => (enrollments?.items.map((item) => item.workshop_id).filter(Boolean) as string[]) ?? [],
    [enrollments]
  );
  const myCourses = useMemo<MyCourse[]>(() => {
    const workshopById = Object.fromEntries(workshops.map((w) => [w.id, w]));
    const now = Date.now();
    const MODULES = 8;

    const map = new Map<string, MyCourse>();
    for (const enr of enrollments?.items ?? []) {
      const workshopId = enr.workshop_id ?? '';
      if (!workshopId) continue;
      const w = workshopById[workshopId];
      if (!w) continue;

      const statusRaw = (enr.status ?? '').toLowerCase();
      const isCompleted = statusRaw === 'completed';

      let progress = isCompleted ? 100 : 35;
      if (!isCompleted) {
        const startMs = w.startDate ? Date.parse(w.startDate) : NaN;
        const endMs = w.endDate ? Date.parse(w.endDate) : NaN;
        if (!Number.isNaN(startMs) && !Number.isNaN(endMs) && endMs > startMs) {
          const ratio = (now - startMs) / (endMs - startMs);
          progress = Math.max(0, Math.min(99, Math.round(ratio * 100)));
        }
      }

      const completedModules = isCompleted ? MODULES : Math.max(1, Math.round((progress / 100) * MODULES));

      map.set(workshopId, {
        id: workshopId,
        workshopId,
        name: w.name,
        progress: isCompleted ? 100 : progress,
        status: isCompleted ? 'Completed' : 'In Progress',
        modules: MODULES,
        completed: isCompleted ? MODULES : completedModules,
      });
    }

    return Array.from(map.values()).sort((a, b) => {
      if (a.status !== b.status) return a.status === 'In Progress' ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
  }, [enrollments, workshops]);
  const [activeTab, setActiveTab] = useState<"overview" | "browse" | "mycourses" | "learning">("overview");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [enrollModal, setEnrollModal] = useState<Workshop | null>(null);
  const [learningCourse, setLearningCourse] = useState<MyCourse | null>(null);
  const [activeModule, setActiveModule] = useState(0);

  const filteredWorkshops = workshops.filter(w => {
    const matchSearch = w.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchSearch;
  });

  const handleEnroll = async (w: Workshop) => {
    if (!user) {
      showToast("warning", "Sign in Required", "Please sign in to enroll.");
      return;
    }
    setEnrollModal(null);
    try {
      await enrollInWorkshop(user.id, w.id);
      await refetchEnrollments();
      showToast("success", "Enrolled!", `You have been enrolled in "${w.name}".`);
    } catch (err: unknown) {
      showToast("destructive", "Enrollment Failed", err instanceof Error ? err.message : "Unable to enroll right now.");
    }
  };

  const modules = [
    { title: "Introduction & Setup", duration: "15 min", content: "Welcome to the course! In this module, we'll set up the development environment and understand the core concepts. You'll install the required tools and create your first project." },
    { title: "Core Concepts", duration: "25 min", content: "Dive deep into the fundamental building blocks. Learn about components, props, and state management. We'll build several small examples to cement understanding." },
    { title: "Advanced Patterns", duration: "30 min", content: "Explore advanced patterns like compound components, render props, and hooks. Learn when to use each pattern for maximum code reusability." },
    { title: "State Management", duration: "35 min", content: "Master state management with Context API and external libraries. Understand when to use local vs global state and best practices for large apps." },
    { title: "API Integration", duration: "20 min", content: "Connect your application to real APIs. Learn about fetch, axios, and React Query for data fetching, caching, and synchronization." },
    { title: "Testing", duration: "25 min", content: "Write reliable tests using Jest and React Testing Library. Learn unit testing, integration testing, and snapshot testing approaches." },
    { title: "Deployment", duration: "15 min", content: "Deploy your application to production. Learn about build optimization, CI/CD pipelines, and hosting platforms." },
    { title: "Final Project", duration: "45 min", content: "Put everything together in a comprehensive final project. Build a full-featured application from scratch, applying all concepts learned." },
  ];

  return (
    <DashboardLayout title="Student Dashboard">
      {/* Tab Navigation */}
      <div className="flex gap-1 mb-6 border-b border-border overflow-x-auto">
        {[
          { key: "overview", label: "Overview" },
          { key: "browse", label: "Browse Courses" },
          { key: "mycourses", label: "My Courses" },
          { key: "learning", label: "Continue Learning" },
        ].map((tab) => (
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

      {/* ═══ OVERVIEW TAB ═══ */}
      {activeTab === "overview" && (
        <>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
            {statCards.map(({ key, label, icon: Icon }, i) => (
              <VCard key={key} hover className="p-5 cursor-pointer" onClick={() => setActiveTab(key === "enrolledWorkshops" ? "mycourses" : "overview")}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconColors[i]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold bg-success/10 text-success">
                    <TrendingUp className="h-3 w-3" />
                    {trends[i]}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold text-foreground mt-1">{stats ? (key === "averageScore" ? `${stats[key]}%` : stats[key]) : "—"}</p>
              </VCard>
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-2 mb-8">
            {/* Progress Chart */}
            <VCard className="p-0">
              <div className="px-5 pt-5 pb-2">
                <h3 className="text-base font-semibold text-foreground">My Progress</h3>
                <p className="text-sm text-muted-foreground">Score trend over weeks</p>
              </div>
              <div className="h-48 px-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={progressData}>
                    <defs>
                      <linearGradient id="studentGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
                        <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} domain={[0, 100]} />
                    <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                    <Area type="monotone" dataKey="score" stroke="hsl(var(--primary))" fill="url(#studentGrad)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </VCard>

            {/* Active Courses */}
            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Active Courses</h3>
              <div className="space-y-3">
                {myCourses.filter(c => c.status === "In Progress").map((course) => (
                  <button
                    key={course.id}
                    onClick={() => { setLearningCourse(course); setActiveTab("learning"); }}
                    className="flex w-full items-center gap-4 rounded-xl p-3 hover:bg-accent transition-all text-left group"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary shrink-0">
                      <BookOpen className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{course.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 h-1.5 rounded-full bg-secondary">
                          <div className="h-1.5 rounded-full bg-primary transition-all" style={{ width: `${course.progress}%` }} />
                        </div>
                        <span className="text-xs text-muted-foreground">{course.progress}%</span>
                      </div>
                    </div>
                    <Play className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
              <VButton variant="secondary" className="w-full mt-4" onClick={() => setActiveTab("browse")}>
                Browse More Courses
              </VButton>
            </VCard>
          </div>
        </>
      )}

      {/* ═══ BROWSE COURSES TAB ═══ */}
      {activeTab === "browse" && (
        <>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="vidya-input pl-10"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-accent"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filteredWorkshops.map((w) => {
              const isEnrolled = enrolledIds.includes(w.id);
              return (
                <VCard key={w.id} hover className="p-5 flex flex-col">
                  <div className="flex items-center justify-between mb-3">
                    <VBadge variant={w.status === "Active" ? "success" : w.status === "Upcoming" ? "warning" : "outline"}>
                      {w.status}
                    </VBadge>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Star className="h-3.5 w-3.5 fill-warning text-warning" /> 4.8
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-foreground mb-1">{w.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2 flex-1">{w.description}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> 4 weeks</span>
                    <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {w.studentsEnrolled} enrolled</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">{w.institution}</p>
                  {isEnrolled ? (
                    <VButton variant="secondary" className="w-full" onClick={() => { setActiveTab("mycourses"); }}>
                      <CheckCircle2 className="h-4 w-4" /> Enrolled
                    </VButton>
                  ) : (
                    <VButton className="w-full" onClick={() => setEnrollModal(w)}>
                      Enroll Now
                    </VButton>
                  )}
                </VCard>
              );
            })}
          </div>
        </>
      )}

      {/* ═══ MY COURSES TAB ═══ */}
      {activeTab === "mycourses" &&
        (myCourses.length === 0 ? (
          <VCard className="p-8 text-center">
            <h3 className="text-lg font-semibold text-foreground mb-2">No courses yet</h3>
            <p className="text-sm text-muted-foreground mb-5">Enroll in a workshop to see it here.</p>
            <VButton onClick={() => setActiveTab("browse")}>Browse Courses</VButton>
          </VCard>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {myCourses.map((course) => (
              <VCard key={course.id} hover className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <VBadge variant={course.status === "Completed" ? "success" : "default"}>{course.status}</VBadge>
                  <span className="text-sm font-bold text-primary">{course.progress}%</span>
                </div>
                <h3 className="text-base font-bold text-foreground mb-2">{course.name}</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  {course.completed}/{course.modules} modules completed
                </p>
                <div className="h-2 rounded-full bg-secondary mb-4">
                  <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${course.progress}%` }} />
                </div>
                <VButton
                  variant={course.status === "Completed" ? "secondary" : "primary"}
                  className="w-full"
                  onClick={() => {
                    if (course.status === "Completed") {
                      navigate("/certificates");
                    } else {
                      setLearningCourse(course);
                      setActiveTab("learning");
                    }
                  }}
                >
                  {course.status === "Completed" ? (
                    <>
                      <CheckCircle2 className="h-4 w-4" /> View Certificate
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" /> Continue Learning
                    </>
                  )}
                </VButton>
              </VCard>
            ))}
          </div>
        ))}
{/* ═══ LEARNING TAB ═══ */}
      {activeTab === "learning" && (
        <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
          {/* Module sidebar */}
          <VCard className="p-3 h-fit">
            <h3 className="text-sm font-semibold text-foreground px-3 py-2 mb-1">
              {learningCourse?.name || "React Fundamentals"}
            </h3>
            <div className="space-y-0.5">
              {modules.map((mod, i) => (
                <button
                  key={i}
                  onClick={() => setActiveModule(i)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                    activeModule === i
                      ? "bg-primary text-primary-foreground font-medium"
                      : i < (learningCourse?.completed || 3)
                      ? "text-foreground hover:bg-accent"
                      : "text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs ${
                    activeModule === i
                      ? "bg-primary-foreground/20"
                      : i < (learningCourse?.completed || 3)
                      ? "bg-success/10 text-success"
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {i < (learningCourse?.completed || 3) ? <CheckCircle2 className="h-3.5 w-3.5" /> : i + 1}
                  </span>
                  <span className="flex-1 text-left truncate">{mod.title}</span>
                  <span className={`text-xs ${activeModule === i ? "text-primary-foreground/70" : "text-muted-foreground"}`}>{mod.duration}</span>
                </button>
              ))}
            </div>
          </VCard>

          {/* Content area */}
          <VCard className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Module {activeModule + 1} of {modules.length}</p>
                <h2 className="text-xl font-bold text-foreground">{modules[activeModule].title}</h2>
              </div>
              <VBadge variant={activeModule < (learningCourse?.completed || 3) ? "success" : "default"}>
                {activeModule < (learningCourse?.completed || 3) ? "Completed" : "In Progress"}
              </VBadge>
            </div>

            <div className="prose prose-sm max-w-none">
              <p className="text-foreground leading-relaxed">{modules[activeModule].content}</p>
            </div>

            {/* Simulated video/content area */}
            <div className="mt-6 rounded-xl bg-muted/50 border border-border p-8 text-center">
              <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <FileText className="h-8 w-8 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground">Study material for this module</p>
              <VButton variant="secondary" className="mt-3" onClick={() => showToast("info", "Opening", "Reading material opened")}>
                Read Material
              </VButton>
            </div>

            <div className="flex justify-between mt-6 pt-6 border-t border-border">
              <VButton
                variant="secondary"
                disabled={activeModule === 0}
                onClick={() => setActiveModule(Math.max(0, activeModule - 1))}
              >
                Previous Module
              </VButton>
              {activeModule < modules.length - 1 ? (
                <VButton onClick={() => { setActiveModule(activeModule + 1); showToast("success", "Module Complete!"); }}>
                  Next Module
                </VButton>
              ) : (
                <VButton onClick={() => { navigate("/assessments"); showToast("success", "Course Complete!", "Time to take the assessment."); }}>
                  Take Assessment
                </VButton>
              )}
            </div>
          </VCard>
        </div>
      )}

      {/* Enrollment Modal */}
      <VModal isOpen={!!enrollModal} onClose={() => setEnrollModal(null)} title="Enroll in Workshop">
        {enrollModal && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-foreground">{enrollModal.name}</h3>
            <p className="text-sm text-muted-foreground">{enrollModal.description}</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Institution</p>
                <p className="font-medium text-foreground">{enrollModal.institution}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Duration</p>
                <p className="font-medium text-foreground">{enrollModal.startDate} - {enrollModal.endDate}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Students</p>
                <p className="font-medium text-foreground">{enrollModal.studentsEnrolled} enrolled</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Status</p>
                <p className="font-medium text-foreground">{enrollModal.status}</p>
              </div>
            </div>
            <div className="bg-primary/5 rounded-xl p-4 border border-primary/20">
              <h4 className="text-sm font-semibold text-foreground mb-2">Syllabus</h4>
              <ul className="space-y-1.5 text-sm text-muted-foreground">
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-primary" /> Introduction & Core Concepts</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-primary" /> Hands-on Projects</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-primary" /> Assessment & Certification</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-primary" /> Industry-Ready Skills</li>
              </ul>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <VButton variant="ghost" onClick={() => setEnrollModal(null)}>Cancel</VButton>
              <VButton onClick={() => handleEnroll(enrollModal)}>Confirm Enrollment</VButton>
            </div>
          </div>
        )}
      </VModal>
    </DashboardLayout>
  );
};


export default StudentDashboard;

