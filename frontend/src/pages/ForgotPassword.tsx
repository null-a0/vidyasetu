import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, ArrowRight, ArrowLeft } from "lucide-react";
import { useTranslation } from "react-i18next";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import { useVToast } from "@/components/ui-custom/VToast";
import { forgotPassword } from "@/services/api";

const ForgotPassword = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useVToast();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email) {
      showToast("warning", t("auth.errors.missingFieldsTitle"), t("auth.errors.missingFieldsBody"));
      return;
    }
    setIsLoading(true);
    try {
      await forgotPassword(email);
      setSubmitted(true);
    } catch (err: unknown) {
      showToast("error", t("auth.forgot.failedTitle"), err instanceof Error ? err.message : t("auth.forgot.failedBody"));
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

        <h1 className="text-3xl font-extrabold text-foreground mb-2">{t("auth.forgot.title")}</h1>
        <p className="text-muted-foreground mb-8">{t("auth.forgot.subtitle")}</p>

        {submitted ? (
          <p className="text-sm text-foreground" role="status">
            {t("auth.forgot.sentBody")}
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <VInput id="email" label={t("auth.fields.email")} type="email" placeholder={t("auth.fields.emailPlaceholder")} value={email} onChange={(e) => setEmail(e.target.value)} />
            <VButton type="submit" isLoading={isLoading} className="w-full" size="lg">
              {t("auth.forgot.button")}
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </form>
        )}
      </motion.div>
    </div>
  );
};

export default ForgotPassword;
