import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Download, Award, Send, Plus, Trophy, Sparkles, CheckCircle2 } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import VTable from '@/components/ui-custom/VTable';
import VButton from '@/components/ui-custom/VButton';
import VBadge from '@/components/ui-custom/VBadge';
import VCard from '@/components/ui-custom/VCard';
import VModal from '@/components/ui-custom/VModal';
import VSelect from '@/components/ui-custom/VSelect';
import { useVToast } from '@/components/ui-custom/VToast';
import {
  fetchCertificateDownload,
  fetchCertificates,
  fetchWorkshops,
  fetchStudents,
  generateCertificate,
  recommendCertificate,
} from '@/services/api';
import { useRole } from '@/hooks/useRole';
import { useAuth } from '@/hooks/useAuth';
import type { Certificate } from '@/mock/mockData';
import { useEffect, useState } from 'react';

const adminColumns = (onDownload: (certificate: Certificate) => void, downloadingId: string | null) => [
  { key: 'certificateId', header: 'Certificate ID' },
  { key: 'studentName', header: 'Student' },
  { key: 'workshop', header: 'Workshop' },
  { key: 'completionDate', header: 'Completed' },
  {
    key: 'status',
    header: 'Status',
    render: (r: Certificate) => <VBadge variant={r.status === 'Issued' ? 'success' : 'warning'}>{r.status}</VBadge>,
  },
  {
    key: 'actions',
    header: 'Actions',
    render: (r: Certificate) =>
      r.status === 'Issued' ? (
        <VButton variant="secondary" size="sm" onClick={() => onDownload(r)} disabled={downloadingId === r.id}>
          <Download className="h-3.5 w-3.5" /> Download
        </VButton>
      ) : (
        <span className="text-sm text-muted-foreground">-</span>
      ),
  },
];

const educatorColumns = (
  onRecommend: (certificate: Certificate) => void,
  onDownload: (certificate: Certificate) => void,
  downloadingId: string | null
) => [
  { key: 'certificateId', header: 'Certificate ID' },
  { key: 'studentName', header: 'Student' },
  { key: 'workshop', header: 'Workshop' },
  {
    key: 'status',
    header: 'Status',
    render: (r: Certificate) => <VBadge variant={r.status === 'Issued' ? 'success' : 'warning'}>{r.status}</VBadge>,
  },
  {
    key: 'actions',
    header: 'Actions',
    render: (r: Certificate) =>
      r.status === 'Pending' ? (
        <VButton variant="primary" size="sm" onClick={() => onRecommend(r)}>
          <Send className="h-3.5 w-3.5" /> Recommend
        </VButton>
      ) : (
        <VButton variant="secondary" size="sm" onClick={() => onDownload(r)} disabled={downloadingId === r.id}>
          <Download className="h-3.5 w-3.5" /> Download
        </VButton>
      ),
  },
];

const StudentCertificates = ({
  certificates,
  onDownload,
}: {
  certificates: Certificate[];
  onDownload: (certificate: Certificate) => void;
}) => {
  const myCerts = certificates.filter((c) => c.status === 'Issued');

  if (myCerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10">
          <Trophy className="h-10 w-10 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-3">Your Trophy Case Awaits!</h2>
        <p className="text-muted-foreground max-w-md mb-6 leading-relaxed">
          You haven't earned any certificates yet - complete a workshop and ace the assessments to earn your first certificate.
        </p>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <VButton onClick={() => (window.location.href = '/workshops')}>
            <Sparkles className="h-4 w-4" /> Browse Workshops
          </VButton>
          <VButton variant="secondary" onClick={() => (window.location.href = '/assessments')}>
            View Assessments
          </VButton>
        </div>
        <div className="mt-10 vidya-card p-6 max-w-sm w-full">
          <p className="text-sm italic text-muted-foreground leading-relaxed">
            "The beautiful thing about learning is that nobody can take it away from you."
          </p>
          <p className="text-xs text-primary font-semibold mt-3">- B.B. King</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {myCerts.map((cert) => (
          <VCard key={cert.id} hover className="p-5 relative overflow-hidden">
            <div className="absolute top-0 right-0 h-24 w-24 bg-primary/5 rounded-bl-[60px]" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                  <Award className="h-5 w-5 text-primary" />
                </div>
                <VBadge variant="success">
                  <CheckCircle2 className="h-3 w-3 mr-1" /> Verified
                </VBadge>
              </div>
              <h3 className="text-base font-bold text-foreground mb-1">{cert.workshop}</h3>
              <p className="text-xs text-muted-foreground mb-1">ID: {cert.certificateId}</p>
              <p className="text-xs text-muted-foreground mb-4">Completed: {cert.completionDate}</p>
              <VButton variant="secondary" size="sm" className="w-full" onClick={() => onDownload(cert)}>
                <Download className="h-3.5 w-3.5" /> Download Certificate
              </VButton>
            </div>
          </VCard>
        ))}
      </div>
    </div>
  );
};

const GenerateCertificateModal = ({
  isOpen,
  onClose,
  onIssue,
}: {
  isOpen: boolean;
  onClose: () => void;
  onIssue: (payload: { workshopId: string; studentId: string }) => Promise<void>;
}) => {
  const [workshopId, setWorkshopId] = useState('');
  const [studentId, setStudentId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setWorkshopId('');
      setStudentId('');
      setSubmitting(false);
    }
  }, [isOpen]);

  const { data: workshops = [] } = useQuery({ queryKey: ['workshops'], queryFn: fetchWorkshops, enabled: isOpen });
  const { data: students = [] } = useQuery({ queryKey: ['students'], queryFn: fetchStudents, enabled: isOpen });

  const completedWorkshops = workshops.filter((w) => w.status === 'Completed');

  return (
    <VModal isOpen={isOpen} onClose={onClose} title="Generate Certificate">
      <div className="space-y-4">
        <VSelect
          label="Workshop"
          value={workshopId}
          onChange={(e) => setWorkshopId(e.target.value)}
          options={[
            { value: '', label: 'Select completed workshop' },
            ...completedWorkshops.map((w) => ({ value: w.id, label: w.name })),
          ]}
        />
        <VSelect
          label="Student"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          options={[
            { value: '', label: 'Select student' },
            ...students.map((s) => ({ value: s.id, label: s.name })),
          ]}
        />
        <div className="flex justify-end gap-3 pt-2">
          <VButton variant="ghost" onClick={onClose} disabled={submitting}>
            Cancel
          </VButton>
          <VButton
            onClick={async () => {
              if (!workshopId || !studentId) return;
              setSubmitting(true);
              try {
                await onIssue({ workshopId, studentId });
              } finally {
                setSubmitting(false);
              }
            }}
            disabled={!workshopId || !studentId || submitting}
          >
            <Award className="h-4 w-4" /> Issue Certificate
          </VButton>
        </div>
      </div>
    </VModal>
  );
};

const Certificates = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const role = useRole();
  const { user } = useAuth();
  const [showGenerate, setShowGenerate] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const { data: certificates = [] } = useQuery({
    queryKey: ['certificates', user?.id, role],
    queryFn: () => {
      if (!user) return [];
      if (role === 'student') {
        return fetchCertificates({ studentId: user.id });
      }
      return fetchCertificates({ asStaff: true });
    },
    enabled: Boolean(user),
  });

  const downloadMutation = useMutation({ mutationFn: fetchCertificateDownload });
  const recommendMutation = useMutation({
    mutationFn: recommendCertificate,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['certificates'] });
      showToast('success', 'Recommendation Sent', 'Certificate recommendation dispatched to institution admins.');
    },
    onError: (err: unknown) => {
      showToast('destructive', 'Recommend Failed', err instanceof Error ? err.message : 'Unable to send recommendation.');
    },
  });

  const handleIssue = async (payload: { workshopId: string; studentId: string }) => {
    try {
      await generateCertificate({ workshopId: payload.workshopId, studentId: payload.studentId });
      await queryClient.invalidateQueries({ queryKey: ['certificates'] });
      showToast('success', 'Certificate Issued', 'Certificate generation started.');
      setShowGenerate(false);
    } catch (err: unknown) {
      showToast('destructive', 'Failed to Issue Certificate', err instanceof Error ? err.message : 'Unable to issue certificate.');
    }
  };

  const handleDownload = async (certificate: Certificate) => {
    try {
      setDownloadingId(certificate.id);
      const response = await downloadMutation.mutateAsync(certificate.id);
      window.open(response.download_url, '_blank', 'noopener,noreferrer');
    } catch (err: unknown) {
      showToast('destructive', 'Download Failed', err instanceof Error ? err.message : 'Unable to download certificate.');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleRecommend = (certificate: Certificate) => {
    if (!certificate.studentId || !certificate.workshopId) {
      showToast('destructive', 'Recommend Failed', 'Student/workshop mapping missing for this certificate.');
      return;
    }
    recommendMutation.mutate({
      studentId: certificate.studentId,
      workshopId: certificate.workshopId,
      note: `Recommended from educator certificates panel (${certificate.id}).`,
    });
  };

  if (role === 'student') {
    return (
      <DashboardLayout title="My Certificates">
        <StudentCertificates certificates={certificates} onDownload={handleDownload} />
      </DashboardLayout>
    );
  }

  if (role === 'educator') {
    return (
      <DashboardLayout title="Certificates">
        <p className="text-sm text-muted-foreground mb-4">
          Review and recommend students for certification. Institutions will issue the final certificate.
        </p>
        <VTable columns={educatorColumns(handleRecommend, handleDownload, downloadingId)} data={certificates} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Certificates">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <p className="text-sm text-muted-foreground">Manage and issue certificates for completed workshops.</p>
        {role === 'institution_admin' && (
          <VButton onClick={() => setShowGenerate(true)}>
            <Plus className="h-4 w-4" /> Generate Certificate
          </VButton>
        )}
      </div>
      <VTable columns={adminColumns(handleDownload, downloadingId)} data={certificates} />
      <GenerateCertificateModal isOpen={showGenerate} onClose={() => setShowGenerate(false)} onIssue={handleIssue} />
    </DashboardLayout>
  );
};

export default Certificates;
