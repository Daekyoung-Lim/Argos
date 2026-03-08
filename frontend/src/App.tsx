import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import LoginPage from "./auth/LoginPage";
import AssetListPage from "./pages/employee/AssetListPage";
import AuditPage from "./pages/employee/AuditPage";
import AdminDashboard from "./pages/admin/AdminDashboard";
import "./styles/index.css";

function ProtectedRoute({
  children,
  requiredRole,
}: {
  children: JSX.Element;
  requiredRole?: "Employee" | "Admin";
}) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to={user?.role === "Admin" ? "/admin" : "/assets"} replace />;
  }
  return children;
}

function RootRedirect() {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={user?.role === "Admin" ? "/admin" : "/assets"} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<RootRedirect />} />
          <Route
            path="/assets"
            element={
              <ProtectedRoute requiredRole="Employee">
                <AssetListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/audit/:assetCode"
            element={
              <ProtectedRoute requiredRole="Employee">
                <AuditPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRole="Admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
