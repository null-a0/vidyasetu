import { useState, useEffect, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, ArrowRight, ArrowLeft } from "lucide-react";
import { useTranslation } from "react-i18next";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import { useVToast } from "@/components/ui-custom/VToast";
import { resetPassword } from "@/services/api";

const MIN_PASSWORD_LENGTH = 8;

// The token is delivered in the URL fragment (never sent to the server or
// logged by proxies); read it once and clear it from the address bar.
const readTokenFromFragment = (): string => {
  const hash = window.location.hash.replace(/^#/, "");
  const token = new URLSearchParams(hash).get("token") ?? "";
  if (token) {
    window.history.replaceState(null, "", window.location.pathname);
  }
  return token;
};

const ResetPassword = () => {
  const { t } = useTranslation();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { showToast } = useVToast();

  useEffect(() => {
    setToken(readTokenFromFragment());
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!password || !confirm) {
      showToast("warning", t("auth.errors.missingFieldsTitle"), t("auth.errors.missingFieldsBody"));
      return;
    }
    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(t("auth.reset.tooShort", { count: MIN_PASSWORD_LENGTH }));
      return;
    }
    if (password !== confirm) {
      setError(t("auth.reset.mismatch"));
      return;
    }
    setIsLoading(true);
    try {
      await resetPassword(token, password);
      setDone(true);
      showToast("success", t("auth.reset.successTitle"), t("auth.reset.successBody"));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : t("auth.reset.failedBody"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 sm:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        <button
          onClick={() => navigate("/login")}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> {t("auth.forgot.backToLogin")}
        </button>

        <div className="flex items-center gap-2.5 mb-8">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl vidya-gradient shadow-md">
            <GraduationCap className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-extrabold text-foreground">{t("common.appName")}</span>
        </div>

        <h1 className="text-3xl font-extrabold text-foreground mb-2">{t("auth.reset.title")}</h1>
        <p className="text-muted-foreground mb-8">{t("auth.reset.subtitle")}</p>

        {done ? (
          <div className="space-y-5">
            <p className="text-sm text-foreground" role="status">{t("auth.reset.successBody")}</p>
            <VButton onClick={() => navigate("/login")} className="w-full" size="lg">
              {t("auth.forgot.backToLogin")}
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </div>
        ) : !token ? (
          <div className="space-y-5">
            <p className="text-sm text-destructive" role="alert">{t("auth.reset.missingToken")}</p>
            <VButton onClick={() => navigate("/forgot-password")} className="w-full" size="lg">
              {t("auth.reset.requestNewLink")}
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <VInput id="password" label={t("auth.reset.newPassword")} type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
            <VInput id="confirm" label={t("auth.reset.confirmPassword")} type="password" placeholder="••••••••" value={confirm} onChange={(e) => setConfirm(e.target.value)} />

            {error && <p className="text-sm text-destructive text-center" role="alert">{error}</p>}

            <VButton type="submit" isLoading={isLoading} className="w-full" size="lg">
              {t("auth.reset.button")}
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </form>
        )}
      </motion.div>
    </div>
  );
};

export default ResetPassword;
