import VModal from "./VModal";
import VButton from "./VButton";

interface VConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  variant?: "destructive" | "primary";
  isLoading?: boolean;
}

const VConfirmDialog = ({
  isOpen, onClose, onConfirm, title, message,
  confirmText = "Confirm", variant = "destructive", isLoading
}: VConfirmDialogProps) => (
  <VModal isOpen={isOpen} onClose={onClose} title={title} className="max-w-sm">
    <p className="text-sm text-muted-foreground mb-6">{message}</p>
    <div className="flex justify-end gap-3">
      <VButton variant="ghost" onClick={onClose}>Cancel</VButton>
      <VButton variant={variant} onClick={onConfirm} isLoading={isLoading}>{confirmText}</VButton>
    </div>
  </VModal>
);

export default VConfirmDialog;
