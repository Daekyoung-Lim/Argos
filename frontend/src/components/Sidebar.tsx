import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const employeeLinks = [
    { to: "/assets", label: "내 자산 목록", icon: "📋" },
];

const adminLinks = [
    { to: "/admin", label: "자산 조회 챗봇", icon: "💬" },
];

export default function Sidebar() {
    const { user } = useAuth();
    const links = user?.role === "Admin" ? adminLinks : employeeLinks;

    return (
        <aside style={styles.sidebar}>
            <nav style={styles.nav}>
                {links.map((link) => (
                    <NavLink
                        key={link.to}
                        to={link.to}
                        style={({ isActive }) => ({
                            ...styles.link,
                            background: isActive ? "var(--color-accent-light)" : "transparent",
                            color: isActive ? "var(--color-accent)" : "var(--color-text-secondary)",
                            borderLeft: `3px solid ${isActive ? "var(--color-accent)" : "transparent"}`,
                        })}
                    >
                        <span style={{ fontSize: 16 }}>{link.icon}</span>
                        <span>{link.label}</span>
                    </NavLink>
                ))}
            </nav>
            {user?.department && (
                <div style={styles.dept}>
                    <span style={{ fontSize: 10, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                        소속 부서
                    </span>
                    <span style={{ fontSize: 12, color: "var(--color-text-primary)", marginTop: 2 }}>
                        {user.department.dept_name}
                    </span>
                </div>
            )}
        </aside>
    );
}

const styles: Record<string, React.CSSProperties> = {
    sidebar: {
        width: 220,
        background: "var(--color-bg-secondary)",
        borderRight: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        flexShrink: 0,
    },
    nav: { display: "flex", flexDirection: "column", gap: 2, padding: "16px 0" },
    link: {
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 20px",
        fontSize: 13,
        fontWeight: 500,
        textDecoration: "none",
        transition: "all 0.15s ease",
    },
    dept: {
        padding: "16px 20px",
        borderTop: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
    },
};
