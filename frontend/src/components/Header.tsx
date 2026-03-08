import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Header() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <header style={styles.header}>
            <div style={styles.brand}>
                <span style={styles.brandName}>ARGOS</span>
                <span style={styles.brandSub}>자산 관리</span>
            </div>
            <div style={styles.userInfo}>
                {user && (
                    <>
                        <span style={styles.name}>{user.name}</span>
                        <span
                            className={`badge ${user.role === "Admin" ? "badge-info" : "badge-success"}`}
                        >
                            {user.role === "Admin" ? "관리자" : "직원"}
                        </span>
                    </>
                )}
                <button
                    id="logout-btn"
                    className="btn btn-secondary"
                    onClick={handleLogout}
                    style={{ padding: "6px 14px", fontSize: 12 }}
                >
                    로그아웃
                </button>
            </div>
        </header>
    );
}

const styles: Record<string, React.CSSProperties> = {
    header: {
        height: 56,
        background: "var(--color-bg-secondary)",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
        flexShrink: 0,
    },
    brand: { display: "flex", alignItems: "baseline", gap: 8 },
    brandName: { fontWeight: 700, fontSize: 18, color: "var(--color-accent)", letterSpacing: 3 },
    brandSub: { fontSize: 11, color: "var(--color-text-secondary)" },
    userInfo: { display: "flex", alignItems: "center", gap: 12 },
    name: { fontWeight: 500, fontSize: 13 },
};
