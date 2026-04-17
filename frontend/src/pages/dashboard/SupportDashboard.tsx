import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import { LifeBuoy } from "lucide-react";

const SupportDashboard = () => {
  return (
    <DashboardLayout title="Support Dashboard" subtitle="Operational tools for technical support">
      <div className="grid gap-6 md:grid-cols-2">
        <VCard className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <LifeBuoy className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">Support Console</p>
              <p className="text-xs text-muted-foreground">Audit logs, job status, reruns, rate limits, cache stats</p>
            </div>
          </div>
          <div className="mt-4">
            <VButton onClick={() => (window.location.href = "/support")}>Open Console</VButton>
          </div>
        </VCard>
      </div>
    </DashboardLayout>
  );
};

export default SupportDashboard;

