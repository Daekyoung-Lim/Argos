import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import apiClient from "../api/client";

interface Department {
    dept_id: number;
    dept_name: string;
}

export interface CurrentUser {
    user_id: number;
    employee_no: string;
    name: string;
    email: string;
    role: "Employee" | "Admin";
    department?: Department;
}

interface AuthContextType {
    user: CurrentUser | null;
    token: string | null;
    login: (employee_no: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<CurrentUser | null>(() => {
        const stored = localStorage.getItem("user");
        return stored ? JSON.parse(stored) : null;
    });
    const [token, setToken] = useState<string | null>(() =>
        localStorage.getItem("access_token")
    );

    const login = useCallback(async (employee_no: string, password: string) => {
        const response = await apiClient.post("/auth/login", { employee_no, password });
        const { access_token, user: userData } = response.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("user", JSON.stringify(userData));
        setToken(access_token);
        setUser(userData);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        setToken(null);
        setUser(null);
    }, []);

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
    return ctx;
}
