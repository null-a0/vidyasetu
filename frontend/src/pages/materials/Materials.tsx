import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Upload, Eye, Trash2, Download, FileText, Presentation, Search } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VDrawer from "@/components/ui-custom/VDrawer";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { fetchMaterials } from "@/services/api";
import type { Material } from "@/mock/mockData";

const fileIcons: Record<string, React.ElementType> = { PDF: FileText, PPTX: Presentation, DOC: FileText, TXT: FileText };

const MaterialsPage = () => {
  const role = useRole();
  const { showToast } = useVToast();
  const { data: initialMaterials = [] } = useQuery({ queryKey: ["materials"], queryFn: fetchMaterials });
  const [materials, setMaterials] = useState<Material[]>([]);
  const [search, setSearch] = useState("");
  const [uploadModal, setUploadModal] = useState(false);
  const [viewDrawer, setViewDrawer] = useState(false);
  const [selected, setSelected] = useState<Material | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [formTitle, setFormTitle] = useState("");
  const [formWorkshop, setFormWorkshop] = useState("");
  const [formType, setFormType] = useState("PDF");

  const all = materials.length > 0 ? materials : initialMaterials;
  const filtered = all.filter(m => m.title.toLowerCase().includes(search.toLowerCase()) || m.workshop.toLowerCase().includes(search.toLowerCase()));
  const canUpload = role !== "student";

  const columns = [
    { key: "title", header: "Title", render: (r: Material) => {
      const Icon = fileIcons[r.fileType] || FileText;
      return <div className="flex items-center gap-2"><Icon className="h-4 w-4 text-primary" /><span>{r.title}</span></div>;
    }},
    { key: "workshop", header: "Workshop" },
    { key: "fileType", header: "Type", render: (r: Material) => <VBadge variant="outline">{r.fileType}</VBadge> },
    { key: "uploadDate", header: "Uploaded" },
    { key: "actions", header: "Actions", render: (r: Material) => (
      <div className="flex gap-1">
        <button onClick={() => { setSelected(r); setViewDrawer(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors"><Eye className="h-4 w-4" /></button>
        <button onClick={() => showToast("success", "Downloaded", `${r.title} downloaded`)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-info transition-colors"><Download className="h-4 w-4" /></button>
        {canUpload && <button onClick={() => { setSelected(r); setDeleteDialog(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"><Trash2 className="h-4 w-4" /></button>}
      </div>
    )},
  ];

  return (
    <DashboardLayout title="Study Materials">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search materials..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        {canUpload && <VButton onClick={() => { setFormTitle(""); setFormWorkshop(""); setFormType("PDF"); setUploadModal(true); }}><Upload className="h-4 w-4" /> Upload Material</VButton>}
      </div>
      <VTable columns={columns} data={filtered} />

      <VModal isOpen={uploadModal} onClose={() => setUploadModal(false)} title="Upload Material">
        <div className="space-y-4">
          <VInput label="Title" placeholder="Material title" value={formTitle} onChange={e => setFormTitle(e.target.value)} />
          <VInput label="Workshop" placeholder="Workshop name" value={formWorkshop} onChange={e => setFormWorkshop(e.target.value)} />
          <VSelect label="File Type" value={formType} onChange={e => setFormType(e.target.value)} options={[
            { value: "PDF", label: "PDF Document" }, { value: "PPTX", label: "Presentation" }, { value: "DOC", label: "Document" }, { value: "TXT", label: "Text File" },
          ]} />
          <VInput label="File" type="file" />
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setUploadModal(false)}>Cancel</VButton><VButton onClick={() => {
            const nm: Material = { id: Date.now().toString(), title: formTitle, workshop: formWorkshop, fileType: formType, uploadDate: new Date().toISOString().split("T")[0] };
            setMaterials([nm, ...all]); setUploadModal(false); showToast("success", "Material Uploaded", `"${formTitle}" added successfully`);
          }} disabled={!formTitle}>Upload</VButton></div>
        </div>
      </VModal>

      <VDrawer isOpen={viewDrawer} onClose={() => setViewDrawer(false)} title={selected?.title || ""}>
        {selected && (
          <div className="space-y-6">
            <div className="rounded-xl bg-muted/50 border border-border p-8 text-center">
              {(() => { const Icon = fileIcons[selected.fileType] || FileText; return <Icon className="h-16 w-16 text-primary mx-auto mb-3" />; })()}
              <p className="text-sm text-muted-foreground">Preview not available</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><p className="text-xs text-muted-foreground mb-1">Workshop</p><p className="text-sm font-medium text-foreground">{selected.workshop}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Type</p><VBadge variant="outline">{selected.fileType}</VBadge></div>
              <div><p className="text-xs text-muted-foreground mb-1">Uploaded</p><p className="text-sm text-foreground">{selected.uploadDate}</p></div>
            </div>
            <VButton className="w-full" onClick={() => { showToast("success", "Downloaded", `${selected.title} downloaded`); }}><Download className="h-4 w-4" /> Download</VButton>
          </div>
        )}
      </VDrawer>

      <VConfirmDialog isOpen={deleteDialog} onClose={() => setDeleteDialog(false)} onConfirm={() => {
        setMaterials(all.filter(m => m.id !== selected?.id)); setDeleteDialog(false); showToast("success", "Material Deleted");
      }} title="Delete Material" message={`Delete "${selected?.title}"?`} />
    </DashboardLayout>
  );
};

export default MaterialsPage;
