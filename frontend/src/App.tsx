import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { VToastProvider } from "@/components/ui-custom/VToast";
import { AuthProvider } from "@/hooks/useAuth";
import AppRoutes from "@/routes/AppRoutes";
import "./index.css";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <ThemeProvider>
        <VToastProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </VToastProvider>
      </ThemeProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
