import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../../api/client";
import Header from "../../components/Header";
import Sidebar from "../../components/Sidebar";
import DataTable, { type Column } from "../../components/DataTable";

interface Asset {
    asset_id: number;
    asset_code: string;
    asset_name: string;
    category: { category_id: number; category_name: string } | null;
    registered_address: string | null;
    status: string;
    last_audit_date: string | null;
    last_condition: string | null;
}

export default function AssetListPage() {
    const navigate = useNavigate();
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        apiClient
            .get("/assets/my")
            .then((res) => setAssets(res.data.assets))
            .catch(() => setError("자산 목록을 불러오는 데 실패했습니다."))
            .finally(() => setLoading(false));
    }, []);

    const columns: Column<Asset>[] = [
        { key: "asset_code", header: "자산코드" },
        { key: "asset_name", header: "자산명" },
        {
            key: "category",
            header: "분류",
            render: (v) => (v as Asset["category"])?.category_name ?? "-",
        },
        { key: "registered_address", header: "등록 위치" },
        { key: "last_condition", header: "최종 상태" },
        {
            key: "last_audit_date",
            header: "최종 실사일",
            render: (v) => v ? new Date(v as string).toLocaleDateString("ko-KR") : "미실시",
        },
        {
            key: "asset_code",
            header: "실사",
            render: (_, row) => (
                <button
                    id={`audit-btn-${row.asset_code}`}
                    className="btn btn-primary"
                    style={{ padding: "5px 12px", fontSize: 12 }}
                    onClick={() => navigate(`/audit/${row.asset_code}`)}
                >
                    실사 시작
                </button>
            ),
        },
    ];

    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-content">
                <Header />
                <div className="page-body">
                    <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>내 자산 목록</h1>
                    <p style={{ color: "var(--color-text-secondary)", marginBottom: 24, fontSize: 13 }}>
                        배정된 자산을 확인하고 자기실사를 진행하세요.
                    </p>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <div className="card" style={{ padding: 0 }}>
                        <DataTable columns={columns} data={assets} loading={loading} emptyMessage="배정된 자산이 없습니다." />
                    </div>
                </div>
            </div>
        </div>
    );
}
