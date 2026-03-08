import { useState, useRef, type ChangeEvent, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiClient from "../../api/client";
import Header from "../../components/Header";
import Sidebar from "../../components/Sidebar";

interface AuditResult {
    is_verified: boolean;
    audit_id: number;
    asset_code: string;
    photo_url?: string;
    details: {
        ocr_asset_code?: string;
        code_match: boolean;
        detected_address?: string;
        distance_meters?: number;
        location_match: boolean;
        photo_taken_at?: string;
        time_match: boolean;
    };
    verification_msg: string;
}

export default function AuditPage() {
    const { assetCode } = useParams<{ assetCode: string }>();
    const navigate = useNavigate();
    const fileRef = useRef<HTMLInputElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [condition, setCondition] = useState("양호");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AuditResult | null>(null);
    const [error, setError] = useState("");

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files?.[0];
        if (!f) return;
        setFile(f);
        setPreview(URL.createObjectURL(f));
        setResult(null);
        setError("");
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!file || !assetCode) return;
        setLoading(true);
        setError("");
        try {
            const formData = new FormData();
            formData.append("image", file);
            formData.append("asset_code", assetCode);
            formData.append("asset_condition", condition);
            const res = await apiClient.post("/audit/submit", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResult(res.data);
        } catch (err: unknown) {
            const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
            setError(msg || "실사 제출 중 오류가 발생했습니다.");
        } finally {
            setLoading(false);
        }
    };

    const CheckItem = ({ ok, label }: { ok: boolean; label: string }) => (
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: 16 }}>{ok ? "✅" : "❌"}</span>
            <span style={{ fontSize: 13, color: ok ? "var(--color-success)" : "var(--color-danger)" }}>{label}</span>
        </div>
    );

    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-content">
                <Header />
                <div className="page-body">
                    <button className="btn btn-secondary" onClick={() => navigate("/assets")} style={{ marginBottom: 20, fontSize: 12 }}>
                        ← 자산 목록으로
                    </button>
                    <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>자산 자기실사</h1>
                    <p style={{ color: "var(--color-text-secondary)", marginBottom: 24, fontSize: 13 }}>
                        자산코드: <strong style={{ color: "var(--color-accent)" }}>{assetCode}</strong>
                    </p>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                        {/* Upload Form */}
                        <div className="card">
                            <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 20 }}>사진 업로드</h2>
                            {error && <div className="alert alert-danger">{error}</div>}
                            <form onSubmit={handleSubmit}>
                                <div
                                    onClick={() => fileRef.current?.click()}
                                    style={{
                                        border: "2px dashed var(--color-border)",
                                        borderRadius: "var(--radius-md)",
                                        padding: 32,
                                        textAlign: "center",
                                        cursor: "pointer",
                                        marginBottom: 16,
                                        background: preview ? "transparent" : "var(--color-bg-secondary)",
                                        transition: "border-color 0.2s",
                                    }}
                                >
                                    {preview ? (
                                        <img src={preview} alt="Preview" style={{ maxWidth: "100%", maxHeight: 240, borderRadius: 8 }} />
                                    ) : (
                                        <>
                                            <div style={{ fontSize: 32, marginBottom: 8 }}>📷</div>
                                            <p style={{ color: "var(--color-text-secondary)", fontSize: 13 }}>
                                                자산 스티커 사진을 클릭하여 선택하세요
                                            </p>
                                        </>
                                    )}
                                </div>
                                <input id="audit-file-input" ref={fileRef} type="file" accept="image/*" onChange={handleFileChange} style={{ display: "none" }} />

                                <div className="form-group">
                                    <label htmlFor="condition-select">자산 상태</label>
                                    <select
                                        id="condition-select"
                                        className="input"
                                        value={condition}
                                        onChange={(e) => setCondition(e.target.value)}
                                    >
                                        <option value="양호">양호</option>
                                        <option value="불량">불량</option>
                                        <option value="수리필요">수리필요</option>
                                    </select>
                                </div>

                                <button
                                    id="audit-submit-btn"
                                    className="btn btn-primary"
                                    type="submit"
                                    disabled={!file || loading}
                                    style={{ width: "100%", justifyContent: "center" }}
                                >
                                    {loading ? "실사 처리 중..." : "실사 제출"}
                                </button>
                            </form>
                        </div>

                        {/* Result */}
                        <div className="card">
                            <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 20 }}>실사 결과</h2>
                            {!result && (
                                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 200, color: "var(--color-text-secondary)", fontSize: 13 }}>
                                    {loading ? <><div className="spinner" /><p style={{ marginTop: 16 }}>AI가 사진을 분석 중입니다...</p></> : <p>사진을 제출하면 결과가 여기에 표시됩니다.</p>}
                                </div>
                            )}
                            {result && (
                                <>
                                    <div style={{
                                        background: result.is_verified ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)",
                                        border: `1px solid ${result.is_verified ? "var(--color-success)" : "var(--color-danger)"}`,
                                        borderRadius: "var(--radius-md)",
                                        padding: 16,
                                        marginBottom: 20,
                                        textAlign: "center",
                                    }}>
                                        <div style={{ fontSize: 36, marginBottom: 4 }}>{result.is_verified ? "✅" : "❌"}</div>
                                        <div style={{ fontWeight: 700, fontSize: 16, color: result.is_verified ? "var(--color-success)" : "var(--color-danger)" }}>
                                            {result.is_verified ? "실사 완료" : "실사 실패"}
                                        </div>
                                        <p style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 4 }}>{result.verification_msg}</p>
                                    </div>

                                    <div style={{ marginBottom: 16 }}>
                                        <p style={{ fontSize: 11, color: "var(--color-text-secondary)", marginBottom: 8, fontWeight: 600, textTransform: "uppercase" }}>검증 조건</p>
                                        <CheckItem ok={result.details.code_match} label={`코드 일치: ${result.details.ocr_asset_code ?? "추출 실패"}`} />
                                        <CheckItem ok={result.details.location_match} label={`위치 확인: ${result.details.distance_meters != null ? `${Math.round(result.details.distance_meters)}m 이내` : "GPS 없음"}`} />
                                        <CheckItem ok={result.details.time_match} label={`시간 확인: ${result.details.photo_taken_at ? new Date(result.details.photo_taken_at).toLocaleString("ko-KR") : "메타데이터 없음"}`} />
                                    </div>

                                    {result.is_verified && (
                                        <button className="btn btn-secondary" onClick={() => navigate("/assets")} style={{ width: "100%", justifyContent: "center" }}>
                                            자산 목록으로 돌아가기
                                        </button>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
