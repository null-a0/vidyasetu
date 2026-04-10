import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Award, ArrowRight, CheckCircle2, XCircle, Trophy, Star, MessageSquare, Sparkles } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import StudentExplanationPanel from "@/components/assessments/StudentExplanationPanel";
import { createStudentAnswerExplanation, fetchAssessmentLeaderboard } from "@/services/api";
import type { BackendStudentExplanationResult } from "@/api/types";

type ResultState = {
  assessmentId?: string;
  assessmentTitle?: string;
  result?: {
    submission_id: string;
    score: number;
    total_marks: number;
    percentage: number;
    pass_fail: boolean;
    per_question: Array<{ question_id: string; earned: number; max: number }>;
  };
  answers?: Record<string, string | string[]>;
  questions?: Array<{
    id: string;
    text?: string | null;
    options: Array<{ id: string; text: string }>;
  }>;
  score?: number;
  total?: number;
};

const Results = () => {
  const location = useLocation();
  const state = (location.state ?? null) as ResultState | null;
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const role = useRole();
  const [animatedScore, setAnimatedScore] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const [explanationsByQuestion, setExplanationsByQuestion] = useState<Record<string, BackendStudentExplanationResult>>({});
  const [explanationErrorsByQuestion, setExplanationErrorsByQuestion] = useState<Record<string, string>>({});
  const [loadingExplanationForQuestion, setLoadingExplanationForQuestion] = useState<string | null>(null);

  const backendResult = state?.result;
  const score = backendResult?.score ?? state?.score ?? 0;
  const total = backendResult?.total_marks ?? state?.total ?? 0;
  const percentage = backendResult
    ? Math.round(backendResult.percentage)
    : total > 0
      ? Math.round((score / total) * 100)
      : 0;
  const passed = backendResult?.pass_fail ?? percentage >= 60;
  const answers = state?.answers ?? {};
  const questions = state?.questions ?? [];
  const perQuestionMap = Object.fromEntries((backendResult?.per_question ?? []).map((item) => [item.question_id, item]));
  const assessmentId = state?.assessmentId;
  const leaderboardQuery = useQuery({
    queryKey: ["assessmentLeaderboard", assessmentId],
    queryFn: () => fetchAssessmentLeaderboard(assessmentId ?? ""),
    enabled: Boolean(showLeaderboard && passed && assessmentId),
  });
  const leaderboardEntries = leaderboardQuery.data?.entries ?? [];
  const explanationMutation = useMutation({
    mutationFn: (payload: { submissionId: string; questionId: string }) =>
      createStudentAnswerExplanation({
        submission_id: payload.submissionId,
        question_id: payload.questionId,
      }),
    onSuccess: (data, variables) => {
      setExplanationsByQuestion((prev) => ({
        ...prev,
        [variables.questionId]: data.explanation,
      }));
      setExplanationErrorsByQuestion((prev) => {
        const next = { ...prev };
        delete next[variables.questionId];
        return next;
      });
      showToast(
        data.from_cache ? "info" : "success",
        data.from_cache ? "Loaded Cached Explanation" : "Explanation Ready",
        data.from_cache ? "Reused a previous explanation." : "Generated a new explanation.",
      );
    },
    onError: (error, variables) => {
      setExplanationErrorsByQuestion((prev) => ({
        ...prev,
        [variables.questionId]: error instanceof Error ? error.message : "Unable to generate explanation.",
      }));
      showToast(
        "destructive",
        "Explanation Failed",
        error instanceof Error ? error.message : "Unable to generate explanation.",
      );
    },
    onSettled: () => {
      setLoadingExplanationForQuestion(null);
    },
  });

  useEffect(() => {
    if (!state) return;
    const duration = 1200;
    const steps = 24;
    const increment = percentage / steps;
    let current = 0;
    const interval = setInterval(() => {
      current += increment;
      if (current >= percentage) {
        setAnimatedScore(percentage);
        clearInterval(interval);
        setTimeout(() => {
          setShowDetails(true);
          if (passed && role === "student") {
            setTimeout(() => setShowLeaderboard(true), 500);
            setTimeout(() => setFeedbackModal(true), 1200);
          }
        }, 400);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(interval);
  }, [state, percentage, passed, role]);

  if (!state) {
    return (
      <DashboardLayout title="Results">
        <div className="flex flex-col items-center justify-center py-16">
          <p className="text-muted-foreground mb-4">No results available.</p>
          <VButton onClick={() => navigate("/assessments")}>Back to Assessments</VButton>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Assessment Results">
      <div className="max-w-3xl mx-auto">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
          <VCard className="p-8 mb-8 text-center relative overflow-hidden">
            <div className="absolute inset-0 vidya-gradient-soft" />
            <div className="relative">
              <div className="mx-auto mb-6 relative h-40 w-40">
                <svg className="h-40 w-40 -rotate-90" viewBox="0 0 160 160">
                  <circle cx="80" cy="80" r="70" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke={passed ? "hsl(var(--success))" : "hsl(var(--destructive))"}
                    strokeWidth="8"
                    strokeDasharray={`${2 * Math.PI * 70}`}
                    strokeDashoffset={`${2 * Math.PI * 70 * (1 - animatedScore / 100)}`}
                    strokeLinecap="round"
                    className="transition-all duration-300"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-extrabold text-foreground">{animatedScore}%</span>
                  <span className="text-sm text-muted-foreground">{score}/{total}</span>
                </div>
              </div>
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2 }}>
                <VBadge variant={passed ? "success" : "destructive"} className="text-base px-4 py-1.5">
                  {passed ? <><CheckCircle2 className="h-4 w-4 mr-1" /> Passed!</> : <><XCircle className="h-4 w-4 mr-1" /> Failed</>}
                </VBadge>
                <p className="mt-3 text-sm text-muted-foreground">
                  {passed ? "Great work! Backend grading marked this attempt as pass." : "Keep going — backend grading marked this attempt as not passed yet."}
                </p>
              </motion.div>
            </div>
          </VCard>
        </motion.div>

        {showLeaderboard && passed && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <VCard className="p-6 mb-8">
              <div className="flex items-center gap-2 mb-4">
                <Trophy className="h-5 w-5 text-warning" />
                <h3 className="text-lg font-semibold text-foreground">Leaderboard</h3>
              </div>
              <div className="space-y-2">
                {leaderboardEntries.map((entry) => (
                  <div key={entry.rank} className="flex items-center gap-4 rounded-xl px-4 py-3 transition-all hover:bg-accent">
                    <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${
                      entry.rank === 1 ? "bg-warning/10 text-warning" : entry.rank === 2 ? "bg-muted text-muted-foreground" : entry.rank === 3 ? "bg-warning/5 text-warning/70" : "bg-muted text-muted-foreground"
                    }`}>
                      {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">{entry.student_name}</p>
                    </div>
                    <span className="text-sm font-bold text-foreground">{Math.round(entry.average_percentage)}%</span>
                    <span className="text-xs text-muted-foreground">{entry.attempts} attempts</span>
                  </div>
                ))}
                {!leaderboardEntries.length && (
                  <p className="text-sm text-muted-foreground">
                    {leaderboardQuery.isLoading ? "Loading leaderboard..." : "No leaderboard entries yet."}
                  </p>
                )}
              </div>
            </VCard>
          </motion.div>
        )}

        {showDetails && questions.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="space-y-4 mb-8">
            <h3 className="text-lg font-semibold text-foreground">Question Feedback</h3>
            {questions.map((q, idx) => {
              const selected = answers[q.id];
              const selectedIds = Array.isArray(selected) ? selected : selected ? [selected] : [];
              const userAnswer = q.options
                .filter((opt) => selectedIds.includes(opt.id))
                .map((opt) => opt.text)
                .join(", ") || "Not answered";
              const grading = perQuestionMap[q.id];
              const isCorrect = grading ? grading.earned === grading.max : false;
              const canRequestExplanation = Boolean(
                role === "student" && !isCorrect && backendResult?.submission_id,
              );
              return (
                <VCard key={q.id} className={`p-5 border-l-4 ${isCorrect ? "border-l-success" : "border-l-destructive"}`}>
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${isCorrect ? "bg-success/10" : "bg-destructive/10"}`}>
                      {isCorrect ? <CheckCircle2 className="h-4 w-4 text-success" /> : <XCircle className="h-4 w-4 text-destructive" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-foreground mb-2">{idx + 1}. {q.text}</p>
                      <p className="text-sm"><span className="text-muted-foreground">Your answer: </span><span className="text-foreground font-medium">{userAnswer}</span></p>
                      {grading && (
                        <p className="text-sm mt-1"><span className="text-muted-foreground">Marks awarded: </span><span className={isCorrect ? "text-success font-medium" : "text-destructive font-medium"}>{grading.earned}/{grading.max}</span></p>
                      )}
                      {canRequestExplanation && (
                        <div className="mt-3">
                          <VButton
                            size="sm"
                            variant="secondary"
                            isLoading={loadingExplanationForQuestion === q.id}
                            onClick={() => {
                              if (!backendResult?.submission_id) return;
                              setLoadingExplanationForQuestion(q.id);
                              explanationMutation.mutate({
                                submissionId: backendResult.submission_id,
                                questionId: q.id,
                              });
                            }}
                          >
                            <Sparkles className="h-4 w-4" /> Explain This
                          </VButton>
                          {explanationErrorsByQuestion[q.id] && (
                            <p className="text-xs text-destructive mt-2">{explanationErrorsByQuestion[q.id]}</p>
                          )}
                          {explanationsByQuestion[q.id] && (
                            <StudentExplanationPanel explanation={explanationsByQuestion[q.id]} />
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </VCard>
              );
            })}
          </motion.div>
        )}

        <div className="flex flex-col sm:flex-row gap-3">
          <VButton onClick={() => navigate("/assessments")}>
            <ArrowRight className="h-4 w-4" /> Back to Assessments
          </VButton>
          {passed && (
            <VButton variant="secondary" onClick={() => { navigate("/certificates"); showToast("success", "Certificate", "Check your certificates!"); }}>
              <Award className="h-4 w-4" /> View Certificate
            </VButton>
          )}
          {!passed && (
            <VButton variant="secondary" onClick={() => navigate(state.assessmentId ? `/assessments/attempt/${state.assessmentId}` : "/assessments")}>Retry Assessment</VButton>
          )}
        </div>
      </div>

      <VModal isOpen={feedbackModal} onClose={() => setFeedbackModal(false)} title="How was your experience?" className="max-w-md">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Help us improve! Rate the assessment and share your thoughts.</p>
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <button key={s} onClick={() => setFeedbackRating(s)} className="transition-transform hover:scale-110">
                <Star className={`h-8 w-8 ${s <= feedbackRating ? "fill-warning text-warning" : "text-muted-foreground"}`} />
              </button>
            ))}
          </div>
          <div>
            <label className="vidya-label">Comments (optional)</label>
            <textarea value={feedbackText} onChange={e => setFeedbackText(e.target.value)} rows={3} className="vidya-input resize-none" placeholder="Any suggestions or feedback..." />
          </div>
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setFeedbackModal(false)}>Skip</VButton>
            <VButton onClick={() => { setFeedbackModal(false); showToast("success", "Thank You!", "Your feedback has been submitted."); }}>
              <MessageSquare className="h-4 w-4" /> Submit Feedback
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default Results;
