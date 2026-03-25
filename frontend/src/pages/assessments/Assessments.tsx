import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Play, Eye, ClipboardList, Trophy, BarChart3, Clock } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { fetchAssessments } from "@/services/api";
import type { Assessment } from "@/mock/mockData";

type QuestionType = "MCQ" | "MSQ" | "Integer";

interface QuestionItem {
  text: string;
  type: QuestionType;
  options: string[];
  correct: number;
  marks: number;
}

const mockLeaderboard = [
  { rank: 1, name: "Priya Patel", score: 92, time: "8:30", correct: 5, incorrect: 0, accuracy: 100, questions: [
    { q: "What is React?", selected: "A library", correct: "A library", isCorrect: true, marks: 10 },
    { q: "Which hook manages state?", selected: "useState", correct: "useState", isCorrect: true, marks: 10 },
    { q: "JSX stands for?", selected: "JavaScript XML", correct: "JavaScript XML", isCorrect: true, marks: 10 },
    { q: "Virtual DOM purpose?", selected: "Performance optimization", correct: "Performance optimization", isCorrect: true, marks: 10 },
    { q: "useEffect runs when?", selected: "After render", correct: "After render", isCorrect: true, marks: 10 },
  ]},
  { rank: 2, name: "Aarav Sharma", score: 85, time: "9:15", correct: 4, incorrect: 1, accuracy: 80, questions: [
    { q: "What is React?", selected: "A library", correct: "A library", isCorrect: true, marks: 10 },
    { q: "Which hook manages state?", selected: "useState", correct: "useState", isCorrect: true, marks: 10 },
    { q: "JSX stands for?", selected: "Java Syntax Extension", correct: "JavaScript XML", isCorrect: false, marks: 0 },
    { q: "Virtual DOM purpose?", selected: "Performance optimization", correct: "Performance optimization", isCorrect: true, marks: 10 },
    { q: "useEffect runs when?", selected: "After render", correct: "After render", isCorrect: true, marks: 10 },
  ]},
  { rank: 3, name: "Vikram Singh", score: 78, time: "9:45", correct: 4, incorrect: 1, accuracy: 80, questions: [
    { q: "What is React?", selected: "A library", correct: "A library", isCorrect: true, marks: 10 },
    { q: "Which hook manages state?", selected: "useReducer", correct: "useState", isCorrect: false, marks: 0 },
    { q: "JSX stands for?", selected: "JavaScript XML", correct: "JavaScript XML", isCorrect: true, marks: 10 },
    { q: "Virtual DOM purpose?", selected: "Performance optimization", correct: "Performance optimization", isCorrect: true, marks: 10 },
    { q: "useEffect runs when?", selected: "After render", correct: "After render", isCorrect: true, marks: 10 },
  ]},
  { rank: 4, name: "Ananya Iyer", score: 72, time: "9:50", correct: 3, incorrect: 2, accuracy: 60, questions: [
    { q: "What is React?", selected: "A framework", correct: "A library", isCorrect: false, marks: 0 },
    { q: "Which hook manages state?", selected: "useState", correct: "useState", isCorrect: true, marks: 10 },
    { q: "JSX stands for?", selected: "JavaScript XML", correct: "JavaScript XML", isCorrect: true, marks: 10 },
    { q: "Virtual DOM purpose?", selected: "CSS rendering", correct: "Performance optimization", isCorrect: false, marks: 0 },
    { q: "useEffect runs when?", selected: "After render", correct: "After render", isCorrect: true, marks: 10 },
  ]},
  { rank: 5, name: "Rohan Gupta", score: 65, time: "10:00", correct: 3, incorrect: 2, accuracy: 60, questions: [
    { q: "What is React?", selected: "A library", correct: "A library", isCorrect: true, marks: 10 },
    { q: "Which hook manages state?", selected: "useState", correct: "useState", isCorrect: true, marks: 10 },
    { q: "JSX stands for?", selected: "JSON XML", correct: "JavaScript XML", isCorrect: false, marks: 0 },
    { q: "Virtual DOM purpose?", selected: "Browser API", correct: "Performance optimization", isCorrect: false, marks: 0 },
    { q: "useEffect runs when?", selected: "After render", correct: "After render", isCorrect: true, marks: 10 },
  ]},
];

const AssessmentsPage = () => {
  const navigate = useNavigate();
  const role = useRole();
  const { showToast } = useVToast();
  const { data: initial = [] } = useQuery({ queryKey: ["assessments"], queryFn: fetchAssessments });
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [createModal, setCreateModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [selected, setSelected] = useState<Assessment | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formWorkshop, setFormWorkshop] = useState("");
  const [formTotal, setFormTotal] = useState("100");
  const [formPassing, setFormPassing] = useState("40");
  const [formStatus, setFormStatus] = useState("Draft");
  const [formDuration, setFormDuration] = useState("30");

  // Question builder state
  const [questionModal, setQuestionModal] = useState(false);
  const [questions, setQuestions] = useState<QuestionItem[]>([
    { text: "What is React?", type: "MCQ", options: ["A library", "A framework", "A language", "A database"], correct: 0, marks: 10 },
  ]);
  const [qText, setQText] = useState("");
  const [qType, setQType] = useState<QuestionType>("MCQ");
  const [qOptions, setQOptions] = useState(["", "", "", ""]);
  const [qCorrect, setQCorrect] = useState(0);
  const [qMarks, setQMarks] = useState("10");

  // Leaderboard & Student Performance
  const [leaderboardModal, setLeaderboardModal] = useState(false);
  const [studentPerfModal, setStudentPerfModal] = useState(false);
  const [selectedStudentIndex, setSelectedStudentIndex] = useState<number | null>(null);
  const [perfTab, setPerfTab] = useState<"basic" | "detailed">("basic");

  const all = assessments.length > 0 ? assessments : initial;
  const canManage = role !== "student";
  const isStudent = role === "student";

  const selectedStudent = selectedStudentIndex !== null ? mockLeaderboard[selectedStudentIndex] : null;

  const openStudentPerf = (index: number) => {
    setSelectedStudentIndex(index);
    setPerfTab("basic");
    setStudentPerfModal(true);
  };

  return (
    <DashboardLayout title="Assessments">
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">{all.length} assessments</p>
        <div className="flex gap-2">
          {canManage && (
            <>
              <VButton variant="secondary" onClick={() => setLeaderboardModal(true)}>
                <Trophy className="h-4 w-4" /> Leaderboard
              </VButton>
              <VButton onClick={() => { setFormTitle(""); setFormWorkshop(""); setFormTotal("100"); setFormPassing("40"); setFormStatus("Draft"); setFormDuration("30"); setCreateModal(true); }}>
                <Plus className="h-4 w-4" /> Create Assessment
              </VButton>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {all.map((a) => (
          <VCard key={a.id} hover className="p-5 flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <VBadge variant={a.status === "Published" ? "success" : "outline"}>{a.status}</VBadge>
              <div className="flex items-center gap-2">
                {a.duration && (
                  <span className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" /> {a.duration}m
                  </span>
                )}
                <span className="text-xs text-muted-foreground">{a.totalMarks} marks</span>
              </div>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary shrink-0">
                <ClipboardList className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">{a.title}</h3>
                <p className="text-xs text-muted-foreground">{a.workshop}</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mb-4 flex-1">Passing: {a.passingMarks}/{a.totalMarks} marks</p>
            <div className="flex gap-2">
              {isStudent && a.status === "Published" ? (
                <VButton className="flex-1" onClick={() => navigate("/assessments/attempt")}>
                  <Play className="h-4 w-4" /> Take Test
                </VButton>
              ) : canManage ? (
                <>
                  <VButton variant="secondary" size="sm" onClick={() => { setSelected(a); setQuestionModal(true); }}>
                    <Eye className="h-3.5 w-3.5" /> Questions
                  </VButton>
                  <VButton variant="secondary" size="sm" onClick={() => { setSelected(a); setFormTitle(a.title); setFormWorkshop(a.workshop); setFormTotal(String(a.totalMarks)); setFormPassing(String(a.passingMarks)); setFormStatus(a.status); setFormDuration(String(a.duration || 30)); setEditModal(true); }}>
                    <Pencil className="h-3.5 w-3.5" /> Edit
                  </VButton>
                  <VButton variant="secondary" size="sm" onClick={() => { setLeaderboardModal(true); }}>
                    <BarChart3 className="h-3.5 w-3.5" /> Stats
                  </VButton>
                  <VButton variant="destructive" size="sm" onClick={() => { setSelected(a); setDeleteDialog(true); }}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </VButton>
                </>
              ) : (
                <VButton variant="secondary" className="flex-1" onClick={() => showToast("info", "Assessment Details", a.title)}>
                  <Eye className="h-4 w-4" /> View
                </VButton>
              )}
            </div>
          </VCard>
        ))}
      </div>

      {/* Create Modal */}
      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Assessment">
        <div className="space-y-4">
          <VInput label="Title" placeholder="Assessment title" value={formTitle} onChange={e => setFormTitle(e.target.value)} />
          <VInput label="Workshop" placeholder="Workshop name" value={formWorkshop} onChange={e => setFormWorkshop(e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Total Marks" type="number" value={formTotal} onChange={e => setFormTotal(e.target.value)} />
            <VInput label="Passing Marks" type="number" value={formPassing} onChange={e => setFormPassing(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Duration (minutes)" type="number" value={formDuration} onChange={e => setFormDuration(e.target.value)} placeholder="e.g. 30" />
            <VSelect label="Status" value={formStatus} onChange={e => setFormStatus(e.target.value)} options={[
              { value: "Draft", label: "Draft" }, { value: "Published", label: "Published" },
            ]} />
          </div>
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton><VButton onClick={() => {
            const na: Assessment = { id: Date.now().toString(), title: formTitle, workshop: formWorkshop, totalMarks: Number(formTotal), passingMarks: Number(formPassing), status: formStatus as any, duration: Number(formDuration) };
            setAssessments([na, ...all]); setCreateModal(false); showToast("success", "Assessment Created");
          }} disabled={!formTitle}>Create</VButton></div>
        </div>
      </VModal>

      {/* Edit Modal */}
      <VModal isOpen={editModal} onClose={() => setEditModal(false)} title="Edit Assessment">
        <div className="space-y-4">
          <VInput label="Title" value={formTitle} onChange={e => setFormTitle(e.target.value)} />
          <VInput label="Workshop" value={formWorkshop} onChange={e => setFormWorkshop(e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Total Marks" type="number" value={formTotal} onChange={e => setFormTotal(e.target.value)} />
            <VInput label="Passing Marks" type="number" value={formPassing} onChange={e => setFormPassing(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Duration (minutes)" type="number" value={formDuration} onChange={e => setFormDuration(e.target.value)} />
            <VSelect label="Status" value={formStatus} onChange={e => setFormStatus(e.target.value)} options={[
              { value: "Draft", label: "Draft" }, { value: "Published", label: "Published" },
            ]} />
          </div>
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setEditModal(false)}>Cancel</VButton><VButton onClick={() => {
            setAssessments(all.map(a => a.id === selected?.id ? { ...a, title: formTitle, workshop: formWorkshop, totalMarks: Number(formTotal), passingMarks: Number(formPassing), status: formStatus as any, duration: Number(formDuration) } : a));
            setEditModal(false); showToast("success", "Assessment Updated");
          }}>Save</VButton></div>
        </div>
      </VModal>

      {/* Question Builder Modal */}
      <VModal isOpen={questionModal} onClose={() => setQuestionModal(false)} title={`Questions — ${selected?.title || ""}`} className="max-w-2xl">
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {questions.map((q, i) => (
            <VCard key={i} className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-foreground">{i + 1}. {q.text}</p>
                  <VBadge variant="outline">{q.type}</VBadge>
                  <span className="text-xs text-muted-foreground">{q.marks} marks</span>
                </div>
                <button onClick={() => { setQuestions(questions.filter((_, j) => j !== i)); showToast("info", "Question Removed"); }} className="text-muted-foreground hover:text-destructive transition-colors">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              {q.type !== "Integer" && (
                <div className="grid grid-cols-2 gap-2">
                  {q.options.map((opt, oi) => (
                    <span key={oi} className={`text-xs px-3 py-1.5 rounded-lg ${oi === q.correct ? "bg-success/10 text-success font-medium" : "bg-muted text-muted-foreground"}`}>
                      {String.fromCharCode(65 + oi)}. {opt}
                    </span>
                  ))}
                </div>
              )}
              {q.type === "Integer" && <p className="text-xs text-muted-foreground">Answer: Numerical input</p>}
            </VCard>
          ))}
        </div>
        <div className="border-t border-border pt-4 mt-4">
          <p className="text-sm font-semibold text-foreground mb-3">Add Question</p>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <VSelect label="Question Type" value={qType} onChange={e => setQType(e.target.value as QuestionType)} options={[
              { value: "MCQ", label: "MCQ (Single Choice)" },
              { value: "MSQ", label: "MSQ (Multiple Select)" },
              { value: "Integer", label: "Integer Input" },
            ]} />
            <VInput label="Marks" type="number" value={qMarks} onChange={e => setQMarks(e.target.value)} />
          </div>
          <VInput label="Question" value={qText} onChange={e => setQText(e.target.value)} placeholder="Enter question text" className="mb-3" />
          {qType !== "Integer" && (
            <div className="grid grid-cols-2 gap-2 mb-3">
              {qOptions.map((opt, i) => (
                <VInput key={i} placeholder={`Option ${String.fromCharCode(65 + i)}`} value={opt} onChange={e => { const n = [...qOptions]; n[i] = e.target.value; setQOptions(n); }} />
              ))}
            </div>
          )}
          {qType !== "Integer" && (
            <VSelect label="Correct Answer" value={String(qCorrect)} onChange={e => setQCorrect(Number(e.target.value))} options={qOptions.map((_, i) => ({ value: String(i), label: `Option ${String.fromCharCode(65 + i)}` }))} />
          )}
          <VButton className="w-full mt-3" variant="secondary" onClick={() => {
            if (!qText) { showToast("warning", "Enter question text"); return; }
            if (qType !== "Integer" && qOptions.some(o => !o)) { showToast("warning", "Fill all options"); return; }
            setQuestions([...questions, { text: qText, type: qType, options: qType === "Integer" ? [] : [...qOptions], correct: qCorrect, marks: Number(qMarks) || 10 }]);
            setQText(""); setQOptions(["", "", "", ""]); setQCorrect(0); setQMarks("10");
            showToast("success", "Question Added");
          }}>
            <Plus className="h-4 w-4" /> Add Question
          </VButton>
        </div>
      </VModal>

      {/* Leaderboard Modal — FIXED: unique state per student */}
      <VModal isOpen={leaderboardModal} onClose={() => setLeaderboardModal(false)} title="Assessment Leaderboard" className="max-w-lg">
        <div className="space-y-2">
          {mockLeaderboard.map((entry, index) => (
            <div key={entry.rank} className="flex items-center gap-4 rounded-xl px-4 py-3 hover:bg-accent transition-all cursor-pointer" onClick={() => {
              setLeaderboardModal(false);
              openStudentPerf(index);
            }}>
              <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${entry.rank <= 3 ? "bg-warning/10 text-warning" : "bg-muted text-muted-foreground"}`}>
                {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
              </span>
              <div className="flex-1"><p className="text-sm font-medium text-foreground">{entry.name}</p></div>
              <span className="text-sm font-bold text-foreground">{entry.score}%</span>
              <span className="text-xs text-muted-foreground">{entry.time}</span>
            </div>
          ))}
        </div>
      </VModal>

      {/* Student Performance Modal — FIXED: uses index-based selection, basic+detailed tabs */}
      <VModal isOpen={studentPerfModal} onClose={() => { setStudentPerfModal(false); setSelectedStudentIndex(null); }} title="Student Performance" className="max-w-2xl">
        {selectedStudent ? (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground font-bold">
                {selectedStudent.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">{selectedStudent.name}</h3>
                <p className="text-sm text-muted-foreground">Rank #{selectedStudent.rank}</p>
              </div>
            </div>

            {/* Basic / Detailed tabs */}
            <div className="flex gap-1 border-b border-border">
              {(["basic", "detailed"] as const).map(t => (
                <button key={t} onClick={() => setPerfTab(t)} className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors capitalize ${perfTab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
                  {t} Stats
                </button>
              ))}
            </div>

            {perfTab === "basic" && (
              <div className="grid grid-cols-2 gap-3">
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Score</p><p className="text-2xl font-bold text-foreground">{selectedStudent.score}%</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Rank</p><p className="text-2xl font-bold text-foreground">#{selectedStudent.rank}</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Correct</p><p className="text-2xl font-bold text-success">{selectedStudent.correct}</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Incorrect</p><p className="text-2xl font-bold text-destructive">{selectedStudent.incorrect}</p></VCard>
                <VCard className="p-4 text-center col-span-2"><p className="text-xs text-muted-foreground">Accuracy</p><p className="text-2xl font-bold text-foreground">{selectedStudent.accuracy}%</p></VCard>
              </div>
            )}

            {perfTab === "detailed" && (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {selectedStudent.questions.map((q, idx) => (
                  <div key={idx} className={`flex items-start gap-2 rounded-lg px-3 py-2.5 text-sm ${q.isCorrect ? "bg-success/5" : "bg-destructive/5"}`}>
                    {q.isCorrect ? <Eye className="h-4 w-4 text-success mt-0.5 shrink-0" /> : <Trash2 className="h-4 w-4 text-destructive mt-0.5 shrink-0" />}
                    <div className="flex-1 min-w-0">
                      <p className="text-foreground font-medium">{idx + 1}. {q.q}</p>
                      <p className={`text-xs mt-0.5 ${q.isCorrect ? "text-success" : "text-destructive"}`}>
                        Selected: {q.selected}
                      </p>
                      {!q.isCorrect && <p className="text-xs text-success mt-0.5">Correct: {q.correct}</p>}
                      <p className="text-xs text-muted-foreground mt-0.5">Marks: {q.marks}/{10}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <VButton variant="secondary" className="w-full" onClick={() => { setSelectedStudentIndex(null); setStudentPerfModal(false); setLeaderboardModal(true); }}>
              ← Back to Leaderboard
            </VButton>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground mb-3">Select a student to view detailed performance:</p>
            {mockLeaderboard.map((s, index) => (
              <button key={s.rank} onClick={() => openStudentPerf(index)} className="flex w-full items-center gap-3 rounded-xl px-4 py-3 hover:bg-accent transition-all text-left">
                <div className="h-9 w-9 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground text-xs font-bold">{s.name.split(" ").map(n => n[0]).join("").slice(0, 2)}</div>
                <div className="flex-1"><p className="text-sm font-medium text-foreground">{s.name}</p></div>
                <span className="text-sm font-bold text-foreground">{s.score}%</span>
              </button>
            ))}
          </div>
        )}
      </VModal>

      <VConfirmDialog isOpen={deleteDialog} onClose={() => setDeleteDialog(false)} onConfirm={() => {
        setAssessments(all.filter(a => a.id !== selected?.id)); setDeleteDialog(false); showToast("success", "Assessment Deleted");
      }} title="Delete Assessment" message={`Delete "${selected?.title}"?`} />
    </DashboardLayout>
  );
};

export default AssessmentsPage;
