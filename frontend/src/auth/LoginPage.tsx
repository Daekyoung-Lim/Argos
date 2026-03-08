import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function LoginPage() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [employeeNo, setEmployeeNo] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await login(employeeNo, password);
            navigate("/");
        } catch {
            setError("사원번호 또는 비밀번호가 올바르지 않습니다.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.wrapper}>
            <div style={styles.card}>
                <div style={styles.logo}>
                    <span style={styles.logoText}>ARGOS</span>
                    <span style={styles.logoSub}>KT 자산 관리 시스템</span>
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="employee-no">사원번호</label>
                        <input
                            id="employee-no"
                            className="input"
                            type="text"
                            placeholder="사원번호를 입력하세요"
                            value={employeeNo}
                            onChange={(e) => setEmployeeNo(e.target.value)}
                            required
                            autoComplete="username"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">비밀번호</label>
                        <input
                            id="password"
                            className="input"
                            type="password"
                            placeholder="비밀번호를 입력하세요"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>
                    <button
                        id="login-btn"
                        className="btn btn-primary"
                        type="submit"
                        disabled={loading}
                        style={{ width: "100%", justifyContent: "center", marginTop: 8 }}
                    >
                        {loading ? "로그인 중..." : "로그인"}
                    </button>
                </form>
            </div>
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrapper: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0f1117 0%, #1a1d27 60%, #1e2235 100%)",
    },
    card: {
        background: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-lg)",
        padding: "40px 36px",
        width: "100%",
        maxWidth: 400,
        boxShadow: "0 8px 48px rgba(0,0,0,0.6)",
    },
    logo: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginBottom: 32,
    },
    logoText: {
        fontSize: 32,
        fontWeight: 700,
        color: "var(--color-accent)",
        letterSpacing: 6,
    },
    logoSub: {
        fontSize: 12,
        color: "var(--color-text-secondary)",
        marginTop: 4,
        letterSpacing: 1,
    },
};
