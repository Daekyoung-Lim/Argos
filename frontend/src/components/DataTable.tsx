import { useState } from "react";

export interface Column<T> {
    key: keyof T;
    header: string;
    render?: (value: T[keyof T], row: T) => React.ReactNode;
}

interface DataTableProps<T> {
    columns: Column<T>[];
    data: T[];
    loading?: boolean;
    emptyMessage?: string;
}

export default function DataTable<T>({
    columns,
    data,
    loading = false,
    emptyMessage = "데이터가 없습니다.",
}: DataTableProps<T>) {
    const [sortKey, setSortKey] = useState<keyof T | null>(null);
    const [sortAsc, setSortAsc] = useState(true);

    const handleSort = (key: keyof T) => {
        if (sortKey === key) setSortAsc((a) => !a);
        else { setSortKey(key); setSortAsc(true); }
    };

    const sorted = sortKey
        ? [...data].sort((a, b) => {
            const av = a[sortKey];
            const bv = b[sortKey];
            if (av == null) return 1;
            if (bv == null) return -1;
            const cmp = String(av).localeCompare(String(bv), "ko");
            return sortAsc ? cmp : -cmp;
        })
        : data;

    if (loading) return <div className="spinner" />;

    return (
        <div style={styles.wrapper}>
            {data.length === 0 ? (
                <p style={styles.empty}>{emptyMessage}</p>
            ) : (
                <table style={styles.table}>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={String(col.key)}
                                    style={styles.th}
                                    onClick={() => handleSort(col.key)}
                                >
                                    {col.header}
                                    {sortKey === col.key ? (sortAsc ? " ▲" : " ▼") : ""}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map((row, i) => (
                            <tr key={i} style={{ background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.02)" }}>
                                {columns.map((col) => (
                                    <td key={String(col.key)} style={styles.td}>
                                        {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? "-")}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrapper: {
        overflowX: "auto",
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--color-border)",
    },
    table: {
        width: "100%",
        borderCollapse: "collapse",
        fontSize: 13,
    },
    th: {
        padding: "10px 14px",
        textAlign: "left",
        fontWeight: 600,
        fontSize: 11,
        textTransform: "uppercase" as const,
        letterSpacing: "0.5px",
        color: "var(--color-text-secondary)",
        background: "var(--color-bg-secondary)",
        borderBottom: "1px solid var(--color-border)",
        cursor: "pointer",
        userSelect: "none" as const,
        whiteSpace: "nowrap" as const,
    },
    td: {
        padding: "10px 14px",
        borderBottom: "1px solid rgba(46,53,88,0.5)",
        color: "var(--color-text-primary)",
    },
    empty: {
        padding: 32,
        textAlign: "center" as const,
        color: "var(--color-text-secondary)",
    },
};
