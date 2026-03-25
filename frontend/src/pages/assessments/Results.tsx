import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Award, Download, ArrowRight, CheckCircle2, XCircle, Trophy, Star, MessageSquare } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";

const leaderboardData = [
  { rank: 1, name: "Priya Patel", score: 92, time: "8:30" },
  { rank: 2, name: "Aarav Sharma", score: 85, time: "9:15" },
  { rank: 3, name: "Vikram Singh", score: 78, time: "9:45" },
  { rank: 4, name: "Ananya Iyer", score: 72, time: "9:50" },
  { rank: 5, name: "Rohan Gupta", score: 65, time: "10:00" },
];

const Results = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const role = useRole();
  const [animatedScore, setAnimatedScore] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");

  const score = state?.score ?? 0;
  const total = state?.total ?? 0;
  const answers = state?.answers ?? {};
  const questions = state?.questions ?? [];
  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  const passed = percentage >= 60;

  // Animated score reveal
  useEffect(() => {
    if (!state) return;
    const duration = 1500;
    const steps = 30;
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
            setTimeout(() => setFeedbackModal(true), 1500);
          }
        }, 500);
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
        {/* Score Card */}
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
          <VCard className="p-8 mb-8 text-center relative overflow-hidden">
            <div className="absolute inset-0 vidya-gradient-soft" />
            <div className="relative">
              <div className="mx-auto mb-6 relative h-40 w-40">
                <svg className="h-40 w-40 -rotate-90" viewBox="0 0 160 160">
                  <circle cx="80" cy="80" r="70" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                  <circle cx="80" cy="80" r="70" fill="none" stroke={passed ? "hsl(var(--success))" : "hsl(var(--destructive))"} strokeWidth="8" strokeDasharray={`${2 * Math.PI * 70}`} strokeDashoffset={`${2 * Math.PI * 70 * (1 - animatedScore / 100)}`} strokeLinecap="round" className="transition-all duration-300" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-extrabold text-foreground">{animatedScore}%</span>
                  <span className="text-sm text-muted-foreground">{score}/{total}</span>
                </div>
              </div>
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.5 }}>
                <VBadge variant={passed ? "success" : "destructive"} className="text-base px-4 py-1.5">
                  {passed ? <><CheckCircle2 className="h-4 w-4 mr-1" /> Passed!</> : <><XCircle className="h-4 w-4 mr-1" /> Failed</>}
                </VBadge>
                <p className="mt-3 text-sm text-muted-foreground">
                  {passed ? "Congratulations! You've passed the assessment." : "Don't give up! Review and try again."}
                </p>
              </motion.div>
            </div>
          </VCard>
        </motion.div>

        {/* Leaderboard */}
        {showLeaderboard && passed && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <VCard className="p-6 mb-8">
              <div className="flex items-center gap-2 mb-4">
                <Trophy className="h-5 w-5 text-warning" />
                <h3 className="text-lg font-semibold text-foreground">Leaderboard</h3>
              </div>
              <div className="space-y-2">
                {leaderboardData.map((entry) => {
                  const isYou = entry.name === "Aarav Sharma";
                  return (
                    <div key={entry.rank} className={`flex items-center gap-4 rounded-xl px-4 py-3 transition-all ${isYou ? "bg-primary/10 ring-1 ring-primary/30" : "hover:bg-accent"}`}>
                      <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${
                        entry.rank === 1 ? "bg-warning/10 text-warning" : entry.rank === 2 ? "bg-muted text-muted-foreground" : entry.rank === 3 ? "bg-warning/5 text-warning/70" : "bg-muted text-muted-foreground"
                      }`}>
                        {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">{entry.name} {isYou && <span className="text-xs text-primary">(You)</span>}</p>
                      </div>
                      <span className="text-sm font-bold text-foreground">{entry.score}%</span>
                      <span className="text-xs text-muted-foreground">{entry.time}</span>
                    </div>
                  );
                })}
              </div>
            </VCard>
          </motion.div>
        )}

        {/* Question Review */}
        {showDetails && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="space-y-4 mb-8">
            <h3 className="text-lg font-semibold text-foreground">Question Review</h3>
            {questions.map((q: any, idx: number) => {
              const userAnswer = answers[q.id];
              const isCorrect = userAnswer === q.correctIndex;
              return (
                <VCard key={q.id} className={`p-5 border-l-4 ${isCorrect ? "border-l-success" : "border-l-destructive"}`}>
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${isCorrect ? "bg-success/10" : "bg-destructive/10"}`}>
                      {isCorrect ? <CheckCircle2 className="h-4 w-4 text-success" /> : <XCircle className="h-4 w-4 text-destructive" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-foreground mb-2">{idx + 1}. {q.text}</p>
                      <p className="text-sm"><span className="text-muted-foreground">Your answer: </span><span className={isCorrect ? "text-success font-medium" : "text-destructive font-medium"}>{q.options[userAnswer] || "Not answered"}</span></p>
                      {!isCorrect && <p className="text-sm mt-1"><span className="text-muted-foreground">Correct: </span><span className="text-success font-medium">{q.options[q.correctIndex]}</span></p>}
                    </div>
                  </div>
                </VCard>
              );
            })}
          </motion.div>
        )}

        {/* Actions */}
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
            <VButton variant="secondary" onClick={() => navigate("/assessments/attempt")}>Retry Assessment</VButton>
          )}
        </div>
      </div>

      {/* Feedback/Survey Modal */}
      <VModal isOpen={feedbackModal} onClose={() => setFeedbackModal(false)} title="How was your experience?" className="max-w-md">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Help us improve! Rate the assessment and share your thoughts.</p>
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5].map(s => (
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
