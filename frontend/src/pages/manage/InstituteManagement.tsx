import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Eye, Search, Building2 } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import { fetchInstitutions, fetchUsers, fetchWorkshops } from "@/services/api";
import type { BackendInstitution, BackendUser } from "@/api/types";

interface InstituteRow {
  id: string;
  name: string;
  code: string;
  location: string;
  workshops: number;
  educators: number;
  students: number;
  status: "Active" | "Pending";
}

const InstituteManagement = () => {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<InstituteRow | null>(null);
  const [viewModal, setViewModal] = useState(false);

  const {
    data: institutions = [],
    isLoading: instLoading,
    isError: instError,
    error: instErr,
    refetch: refetchInst,
  } = useQuery({ queryKey: ["institutions"], queryFn: fetchInstitutions });

  const {
    data: usersPage,
    isLoading: usersLoading,
    isError: usersError,
    error: usersErr,
    refetch: refetchUsers,
  } = useQuery({ queryKey: ["users", "admin"], queryFn: () => fetchUsers({ limit: 500 }) });

  const {
    data: workshops = [],
    isLoading: workshopsLoading,
    isError: workshopsError,
    error: workshopsErr,
    refetch: refetchWorkshops,
  } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });

  const rows = useMemo<InstituteRow[]>(() => {
    const users = (usersPage?.items ?? []) as BackendUser[];

    const educatorCountByInst: Record<string, number> = {};
    const studentCountByInst: Record<string, number> = {};
    for (const u of users) {
      const instId = u.institution_id ?? "";
      if (!instId) continue;
      if (u.role === "educator") educatorCountByInst[instId] = (educatorCountByInst[instId] ?? 0) + 1;
      if (u.role === "student") studentCountByInst[instId] = (studentCountByInst[instId] ?? 0) + 1;
    }

    // Workshops are already adapted to show institution name. Build counts by institution name.
    const workshopsByInstName: Record<string, number> = {};
    for (const w of workshops) {
      const name = w.institution ?? "";
      if (!name) continue;
      workshopsByInstName[name] = (workshopsByInstName[name] ?? 0) + 1;
    }

    return (institutions as BackendInstitution[]).map((i) => ({
      id: i.id,
      name: i.name,
      code: `INST-${i.id.slice(0, 8).toUpperCase()}`,
      location: i.address ?? "—",
      workshops: workshopsByInstName[i.name] ?? 0,
      educators: educatorCountByInst[i.id] ?? 0,
      students: studentCountByInst[i.id] ?? 0,
      status: "Active",
    }));
  }, [institutions, usersPage, workshops]);

  const filtered = rows.filter((i) =>
    i.name.toLowerCase().includes(search.toLowerCase()) || i.code.toLowerCase().includes(search.toLowerCase())
  );

  const loading = instLoading || usersLoading || workshopsLoading;
  const errorMsg =
    (instError && (instErr instanceof Error ? instErr.message : "Failed to load institutions.")) ||
    (usersError && (usersErr instanceof Error ? usersErr.message : "Failed to load users.")) ||
    (workshopsError && (workshopsErr instanceof Error ? workshopsErr.message : "Failed to load workshops.")) ||
    null;

  const emptyText = loading
    ? "Loading institutes..."
    : errorMsg
    ? errorMsg
    : "No institutes found.";

  const columns = [
    {
      key: "name",
      header: "Institute",
      render: (r: InstituteRow) => (
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Building2 className="h-4 w-4 text-primary" />
          </div>
          <span className="font-medium text-foreground">{r.name}</span>
        </div>
      ),
    },
    { key: "code", header: "Code" },
    { key: "location", header: "Location" },
    { key: "workshops", header: "Workshops" },
    { key: "educators", header: "Educators" },
    { key: "students", header: "Students" },
    {
      key: "status",
      header: "Status",
      render: (r: InstituteRow) => (
        <VBadge variant={r.status === "Active" ? "success" : "warning"}>{r.status}</VBadge>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (r: InstituteRow) => (
        <button
          onClick={() => {
            setSelected(r);
            setViewModal(true);
          }}
          className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
        >
          <Eye className="h-4 w-4" />
        </button>
      ),
    },
  ];

  const totalWorkshops = rows.reduce((s, i) => s + i.workshops, 0);
  const totalStudents = rows.reduce((s, i) => s + i.students, 0);

  return (
    <DashboardLayout title="Institute Management">
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search institutes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="vidya-input pl-10"
          />
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3 mb-6">
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Institutes</p>
          <p className="text-2xl font-bold text-foreground">{rows.length}</p>
        </VCard>
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Workshops</p>
          <p className="text-2xl font-bold text-foreground">{totalWorkshops}</p>
        </VCard>
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Students</p>
          <p className="text-2xl font-bold text-foreground">{totalStudents.toLocaleString()}</p>
        </VCard>
      </div>

      {errorMsg && (
        <div className="mb-4">
          <button
            className="text-sm text-primary underline"
            onClick={() => {
              refetchInst();
              refetchUsers();
              refetchWorkshops();
            }}
          >
            Retry
          </button>
        </div>
      )}

      <div className="overflow-x-auto">
        <VTable columns={columns} data={filtered} emptyText={emptyText} />
      </div>

      <VModal isOpen={viewModal} onClose={() => setViewModal(false)} title="Institute Details">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-primary/10 flex items-center justify-center">
                <Building2 className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">{selected.name}</h3>
                <p className="text-sm text-muted-foreground">{selected.code}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Location</p>
                <p className="text-sm font-medium text-foreground">{selected.location}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Status</p>
                <VBadge variant="success">{selected.status}</VBadge>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Workshops</p>
                <p className="text-lg font-bold text-foreground">{selected.workshops}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Educators</p>
                <p className="text-lg font-bold text-foreground">{selected.educators}</p>
              </div>
              <div className="rounded-xl bg-muted p-3 col-span-2">
                <p className="text-xs text-muted-foreground">Students</p>
                <p className="text-lg font-bold text-foreground">{selected.students}</p>
              </div>
            </div>
          </div>
        )}
      </VModal>
    </DashboardLayout>
  );
};

export default InstituteManagement;