import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Eye, CheckCircle2, Search, XCircle } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VCard from "@/components/ui-custom/VCard";
import { useVToast } from "@/components/ui-custom/VToast";
import { fetchSubmissions } from "@/services/api";
import type { Submission } from "@/mock/mockData";

const mockQuestionBreakdown = [
  { q: "What is the correct way to create a React component?", studentAnswer: "function App() {}", correctAnswer: "function App() {}", isCorrect: true, marksAwarded: 20, maxMarks: 20 },
  { q: "Which hook is used for side effects?", studentAnswer: "useEffect", correctAnswer: "useEffect", isCorrect: true, marksAwarded: 20, maxMarks: 20 },
  { q: "What does JSX stand for?", studentAnswer: "JavaScript XML", correctAnswer: "JavaScript XML", isCorrect: true, marksAwarded: 20, maxMarks: 20 },
  { q: "Which method is used to update state?", studentAnswer: "setState()", correctAnswer: "useState setter", isCorrect: false, marksAwarded: 0, maxMarks: 20 },
  { q: "What is the virtual DOM?", studentAnswer: "A browser API", correctAnswer: "A lightweight JS representation of the DOM", isCorrect: false, marksAwarded: 0, maxMarks: 20 },
];

const SubmissionsPage = () => {
  const { showToast } = useVToast();
  const { data: submissions = [], isLoading, isError, error, refetch } = useQuery({ queryKey: ["submissions"], queryFn: fetchSubmissions });

  const tableEmptyText = isLoading
    ? "Loading submissions..."
    : isError
    ? (error instanceof Error ? error.message : "Failed to load submissions.")
    : "No submissions found.";
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [selected, setSelected] = useState<Submission | null>(null);
  const [viewModal, setViewModal] = useState(false);

  const filtered = submissions.filter(s => {
    const matchSearch = s.studentName.toLowerCase().includes(search.toLowerCase()) || s.assessment.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || s.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const columns = [
    { key: "studentName", header: "Student" },
    { key: "assessment", header: "Assessment" },
    { key: "score", header: "Score", render: (r: Submission) => <span className="font-medium text-foreground">{r.status === "Pending" ? "—" : r.score}</span> },
    { key: "status", header: "Status", render: (r: Submission) => (
      <VBadge variant={r.status === "Graded" ? "success" : r.status === "Pending" ? "warning" : "destructive"}>
        {r.status}
      </VBadge>
    )},
    { key: "submittedAt", header: "Submitted" },
    { key: "actions", header: "Actions", render: (r: Submission) => (
      <div className="flex gap-1">
        <button onClick={() => { setSelected(r); setViewModal(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors">
          <Eye className="h-4 w-4" />
        </button>
        {r.status === "Pending" && (
          <button onClick={() => showToast("success", "Graded", `${r.studentName}'s submission has been graded`)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-success/10 hover:text-success transition-colors">
            <CheckCircle2 className="h-4 w-4" />
          </button>
        )}
      </div>
    )},
  ];

  // Adjust breakdown based on selected submission score
  const getBreakdown = () => {
    if (!selected) return mockQuestionBreakdown;
    if (selected.score > 80) {
      return mockQuestionBreakdown.map((q, i) => i < 4 ? { ...q, isCorrect: true, marksAwarded: q.maxMarks, studentAnswer: q.correctAnswer } : q);
    }
    return mockQuestionBreakdown;
  };

  return (
    <DashboardLayout title="Submissions">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search submissions..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        <div className="flex gap-2">
          {["All", "Graded", "Pending", "Late"].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)} className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${statusFilter === s ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}>
              {s}
            </button>
          ))}
        </div>
      </div>
      {isError && (
        <div className="mb-4">
          <VButton variant="secondary" onClick={() => refetch()}>Retry</VButton>
        </div>
      )}
      <VTable columns={columns} data={filtered} emptyText={tableEmptyText} />

      <VModal isOpen={viewModal} onClose={() => setViewModal(false)} title="Submission Details" className="max-w-2xl">
        {selected && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div><p className="text-xs text-muted-foreground mb-1">Student</p><p className="text-sm font-medium text-foreground">{selected.studentName}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Assessment</p><p className="text-sm font-medium text-foreground">{selected.assessment}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Score</p><p className="text-2xl font-bold text-foreground">{selected.status === "Pending" ? "—" : selected.score}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Status</p><VBadge variant={selected.status === "Graded" ? "success" : "warning"}>{selected.status}</VBadge></div>
              <div className="col-span-2"><p className="text-xs text-muted-foreground mb-1">Submitted At</p><p className="text-sm text-foreground">{selected.submittedAt}</p></div>
            </div>

            {/* Full question-level breakdown for graded submissions */}
            {selected.status === "Graded" && (
              <div className="border-t border-border pt-4">
                <h4 className="text-sm font-semibold text-foreground mb-3">Question-Level Breakdown</h4>
                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {getBreakdown().map((item, idx) => (
                    <VCard key={idx} className={`p-3 border-l-4 ${item.isCorrect ? "border-l-success" : "border-l-destructive"}`}>
                      <div className="flex items-start gap-2">
                        {item.isCorrect ? <CheckCircle2 className="h-4 w-4 text-success mt-0.5 shrink-0" /> : <XCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-foreground font-medium">{idx + 1}. {item.q}</p>
                          <div className="mt-1 grid grid-cols-2 gap-x-4">
                            <p className={`text-xs ${item.isCorrect ? "text-success" : "text-destructive"}`}>
                              Student: {item.studentAnswer}
                            </p>
                            {!item.isCorrect && (
                              <p className="text-xs text-success">Correct: {item.correctAnswer}</p>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">Marks: {item.marksAwarded}/{item.maxMarks}</p>
                        </div>
                      </div>
                    </VCard>
                  ))}
                </div>
                <div className="mt-3 flex justify-between items-center rounded-xl bg-muted p-3">
                  <span className="text-sm font-medium text-foreground">Total Marks</span>
                  <span className="text-lg font-bold text-foreground">
                    {getBreakdown().reduce((s, q) => s + q.marksAwarded, 0)}/{getBreakdown().reduce((s, q) => s + q.maxMarks, 0)}
                  </span>
                </div>
              </div>
            )}

            {selected.status === "Pending" && (
              <VButton className="w-full" onClick={() => { setViewModal(false); showToast("success", "Graded", `${selected.studentName}'s submission graded`); }}>
                <CheckCircle2 className="h-4 w-4" /> Grade Submission
              </VButton>
            )}
          </div>
        )}
      </VModal>
    </DashboardLayout>
  );
};

export default SubmissionsPage;
