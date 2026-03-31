import { useState, useEffect } from "react";
import { User, Mail, Building2, GraduationCap, Camera, Save, Shield } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VInput from "@/components/ui-custom/VInput";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import { fetchInstitutions, updateUser } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

const ProfilePage = () => {
  const { user, refreshUser } = useAuth();
  const role = user?.role ?? null;
  const { showToast } = useVToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [bio, setBio] = useState("");
  const [institution, setInstitution] = useState("");
  const [institutionName, setInstitutionName] = useState("");
  const [department, setDepartment] = useState("");
  const [avatarInitials, setAvatarInitials] = useState("VS");

  // Institution admin extra fields
  const [instName, setInstName] = useState("");
  const [instAddress, setInstAddress] = useState("");
  const [instCode, setInstCode] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const institutionsQuery = useQuery({
    queryKey: ["institutions"],
    queryFn: fetchInstitutions,
  });

  useEffect(() => {
    if (!user) return;
    setName(user.name || "");
    setEmail(user.email || "");
    setInstitution(user.institution_id || "");
    const instNameLookup = institutionsQuery.data?.find((i) => i.id === user.institution_id)?.name;
    setInstitutionName(instNameLookup || user.institution_id || "");
    setAvatarInitials((user.name || "VS")
      .split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2));
    setPhone(user.phone || "+91 98765 43210");
    setInstName(instNameLookup || user.institution_id || "IIT Delhi");
    setInstAddress("Hauz Khas, New Delhi, 110016");
    setInstCode("IITD-2026");
  }, [user, institutionsQuery.data]);

  const handleSave = async () => {
    if (!user) return;
    setIsSaving(true);
    try {
      await updateUser(user.id, { name, phone, institution_id: institution || undefined });
      await refreshUser();
      showToast("success", "Profile Updated", "Your changes have been saved.");
    } catch (err: unknown) {
      showToast("destructive", "Save Failed", err instanceof Error ? err.message : "Unable to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <DashboardLayout title="Profile">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Avatar & Header */}
        <VCard className="p-6">
          <p className="text-xs text-muted-foreground mb-4">Fallback: profile image upload endpoint is not available yet.</p>
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <div className="relative group">
              <div className="h-24 w-24 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground text-2xl font-bold">
                {avatarInitials}
              </div>
              <button
                onClick={() => showToast("info", "Upload", "Profile image upload simulated")}
                className="absolute bottom-0 right-0 h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg hover:opacity-90 transition-opacity"
              >
                <Camera className="h-4 w-4" />
              </button>
            </div>
            <div className="text-center sm:text-left">
              <h2 className="text-xl font-bold text-foreground">{name}</h2>
              <p className="text-sm text-muted-foreground">{email}</p>
              <VBadge variant="default" className="mt-2">
                <Shield className="h-3 w-3 mr-1" />
              {role === "admin"
                ? "Platform Admin"
                : role === "institution_admin"
                  ? "Institute Admin"
                  : role === "educator"
                    ? "Educator"
                    : "Student"}
              </VBadge>
            </div>
          </div>
        </VCard>

        {/* Personal Details */}
        <VCard className="p-6">
          <h3 className="text-base font-semibold text-foreground mb-4 flex items-center gap-2">
            <User className="h-4 w-4 text-primary" /> Personal Information
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <VInput label="Full Name" value={name} onChange={e => setName(e.target.value)} />
            <VInput label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} />
            <VInput label="Phone" value={phone} onChange={e => setPhone(e.target.value)} />
            {(role === "educator" || role === "student") && (
              <VInput label="Department" value={department} onChange={e => setDepartment(e.target.value)} />
            )}
          </div>
          <div className="mt-4">
            <label className="vidya-label">Bio</label>
            <textarea
              value={bio}
              onChange={e => setBio(e.target.value)}
              rows={3}
              className="vidya-input resize-none"
              placeholder="Tell us about yourself..."
            />
          </div>
        </VCard>

        {/* Role-specific section */}
        {role === "institution_admin" ? (
          <VCard className="p-6">
            <h3 className="text-base font-semibold text-foreground mb-4 flex items-center gap-2">
              <Building2 className="h-4 w-4 text-primary" /> Institution Details
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <VInput label="Institution Name" value={instName} onChange={e => setInstName(e.target.value)} />
              <VInput label="Institution Code" value={instCode} onChange={e => setInstCode(e.target.value)} />
            </div>
            <div className="mt-4">
              <label className="vidya-label">Address</label>
              <textarea
                value={instAddress}
                onChange={e => setInstAddress(e.target.value)}
                rows={2}
                className="vidya-input resize-none"
              />
            </div>
          </VCard>
        ) : (role === "educator" || role === "student") ? (
          <VCard className="p-6">
            <h3 className="text-base font-semibold text-foreground mb-4 flex items-center gap-2">
              <GraduationCap className="h-4 w-4 text-primary" /> Academic Details
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <VInput label="Institution" value={institutionName} disabled />
              <VInput label="Department" value={department} onChange={e => setDepartment(e.target.value)} />
            </div>
          </VCard>
        ) : null}

        {/* Save */}
        <div className="flex justify-end">
        <VButton size="lg" isLoading={isSaving} onClick={handleSave}>
            <Save className="h-4 w-4" /> Save Changes
          </VButton>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ProfilePage;
