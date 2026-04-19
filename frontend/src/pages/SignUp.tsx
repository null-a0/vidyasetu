import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, ArrowRight, ArrowLeft, Eye, EyeOff } from "lucide-react";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useVToast } from "@/components/ui-custom/VToast";
import type { UserRole } from "@/mock/mockData";
import { registerUser } from "@/services/api";

const roleOptions = [
  { value: "student", label: "Student" },
  { value: "educator", label: "Educator" },
  { value: "institution_admin", label: "Institutional Admin" },
];

const SignUp = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useVToast();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) {
      showToast("warning", "Missing Fields", "Please fill in all fields.");
      return;
    }
    setIsLoading(true);
    try {
      await registerUser({ name, email, password, role });
      showToast("success", "Account Created!", "Your account has been created. Please sign in.");
      navigate("/login");
    } catch (err: unknown) {
      showToast("error", "Registration Failed", err instanceof Error ? err.message : "Unable to register at this time.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left decorative panel */}
      <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center overflow-hidden">
        <div className="absolute inset-0 vidya-gradient" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.1),transparent_50%)]" />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7 }}
          className="relative z-10 p-12 text-center max-w-lg"
        >
          <div className="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-3xl bg-white/15 backdrop-blur-sm border border-white/20 shadow-2xl">
            <GraduationCap className="h-10 w-10 text-primary-foreground" />
          </div>
          <h2 className="text-4xl font-extrabold text-primary-foreground mb-4 leading-tight">
            Join VidyaSetu
          </h2>
          <p className="text-primary-foreground/70 text-lg leading-relaxed">
            Start your journey in modern skill development. Sign up to access workshops, assessments, and certifications.
          </p>
        </motion.div>
      </div>

      {/* Right sign-up form */}
      <div className="flex flex-1 items-center justify-center px-4 sm:px-8 relative">
        <div className="absolute inset-0 overflow-hidden pointer-events-none lg:hidden">
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-primary/5 blur-[100px]" />
          <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-primary/5 blur-[100px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative w-full max-w-md"
        >
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> Back to home
          </button>

          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl vidya-gradient shadow-md">
              <GraduationCap className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-extrabold text-foreground">VidyaSetu</span>
          </div>

          <h1 className="text-3xl font-extrabold text-foreground mb-2">Create Account</h1>
          <p className="text-muted-foreground mb-8">Fill in your details to get started</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <VInput id="name" label="Full Name" placeholder="Your full name" value={name} onChange={(e) => setName(e.target.value)} />
            <VInput id="email" label="Email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            
            <div className="relative">
              <VInput 
                id="password" 
                label="Password" 
                type={showPassword ? "text" : "password"} 
                placeholder="••••••••" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[38px] text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>

            <VSelect id="role" label="I am a" options={roleOptions} value={role} onChange={(e) => setRole(e.target.value as UserRole)} />

            <VButton type="submit" isLoading={isLoading} className="w-full" size="lg">
              Sign Up
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <button onClick={() => navigate("/login")} className="text-primary font-semibold hover:underline">
              Sign in
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default SignUp;