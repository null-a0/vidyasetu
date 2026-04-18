import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, ArrowRight, ArrowLeft } from "lucide-react";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/mock/mockData";

const roleOptions = [
  { value: "admin", label: "Platform Admin" },
  { value: "institution_admin", label: "Institutional Admin" },
  { value: "educator", label: "Educator" },
  { value: "student", label: "Student" },
  { value: "technical_support", label: "Technical Support" },
];

const roleDashboardMap: Record<UserRole, string> = {
  admin: "/dashboard/admin",
  institution_admin: "/dashboard/institution",
  educator: "/dashboard/educator",
  student: "/dashboard/student",
  technical_support: "/dashboard/technical_support",
};

const Login = () => {
  const [email, setEmail] = useState("admin@vidyasetu.edu");
  const [password, setPassword] = useState("admin123");
  const [role, setRole] = useState<UserRole>("admin");
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const user = await login(email, password, role);
      if (user) {
        const redirect = roleDashboardMap[user.role as UserRole] ?? "/dashboard";
        navigate(redirect);
      }
    } catch {
      // error handled by useAuth
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left decorative panel - hidden on mobile */}
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
            Welcome to VidyaSetu
          </h2>
          <p className="text-primary-foreground/70 text-lg leading-relaxed">
            Empowering institutions, educators, and students with modern skill development tools.
          </p>
        </motion.div>
      </div>

      {/* Right login form */}
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

          <h1 className="text-3xl font-extrabold text-foreground mb-2">Sign in</h1>
          <p className="text-muted-foreground mb-8">Enter your credentials to access your dashboard</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <VInput id="email" label="Email" type="email" placeholder="user@vidyasetu.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            <VInput id="password" label="Password" type="password" placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" value={password} onChange={(e) => setPassword(e.target.value)} />
            <VSelect id="role" label="Sign in as" options={roleOptions} value={role} onChange={(e) => setRole(e.target.value as UserRole)} />

            {error && <p className="text-sm text-destructive text-center">{error}</p>}

            <VButton type="submit" isLoading={isLoading} className="w-full" size="lg">
              Sign in
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Don't have an account?{" "}
            <button onClick={() => navigate("/signup")} className="text-primary font-semibold hover:underline">
              Sign up
            </button>
          </p>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            Demo: Use seeded credentials from backend
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;

