import { useState, useRef, useEffect, type FormEvent } from "react";
import apiClient from "../../api/client";
import Header from "../../components/Header";
import Sidebar from "../../components/Sidebar";
import DataTable, { type Column } from "../../components/DataTable";

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    logId?: number;
    columns?: string[];
    rows?: unknown[][];
    totalRows?: number;
    sql?: string;
}

export default function AdminDashboard() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [activeResult, setActiveResult] = useState<ChatMessage | null>(null);
    const [exporting, setExporting] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendQuery = async (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg: ChatMessage = { role: "user", content: input };
        setMessages((m) => [...m, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const res = await apiClient.post("/admin/chat", { query: input });
            const data = res.data;
            const assistantMsg: ChatMessage = {
                role: "assistant",
                content: data.summary || `${data.total_rows}개의 결과를 찾았습니다.`,
                logId: data.log_id,
                columns: data.columns,
                rows: data.rows,
                totalRows: data.total_rows,
                sql: data.generated_sql,
            };
            setMessages((m) => [...m, assistantMsg]);
            setActiveResult(assistantMsg);
        } catch {
            setMessages((m) => [
                ...m,
                { role: "assistant", content: "❌ 쿼리를 처리할 수 없습니다. 다시 시도해 주세요." },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const exportToExcel = async (logId: number) => {
        setExporting(true);
        try {
            const res = await apiClient.get(`/admin/chat/export/${logId}`);
            window.open(res.data.download_url, "_blank");
        } catch {
            alert("Excel 내보내기에 실패했습니다.");
        } finally {
            setExporting(false);
        }
    };

    const resultColumns: Column<Record<string, unknown>>[] = activeResult?.columns?.map((col) => ({
        key: col as keyof Record<string, unknown>,
        header: col,
    })) ?? [];

    const resultData: Record<string, unknown>[] = activeResult?.rows?.map((row) => {
        const obj: Record<string, unknown> = {};
        activeResult.columns?.forEach((col, i) => { obj[col] = (row as unknown[])[i]; });
        return obj;
    }) ?? [];

    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-content">
                <Header />
                <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
                    {/* Left: Chat */}
                    <div style={{ width: 380, borderRight: "1px solid var(--color-border)", display: "flex", flexDirection: "column", flexShrink: 0 }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--color-border)" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>자산 조회 챗봇</h2>
                            <p style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 2 }}>자연어로 자산을 조회하세요</p>
                        </div>
                        <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 12 }}>
                            {messages.length === 0 && (
                                <div style={{ color: "var(--color-text-secondary)", fontSize: 13, textAlign: "center", marginTop: 40 }}>
                                    <div style={{ fontSize: 32, marginBottom: 8 }}>💬</div>
                                    <p>예시: "실사를 완료하지 않은 직원 목록을 보여줘"</p>
                                </div>
                            )}
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    onClick={() => msg.role === "assistant" && msg.columns && setActiveResult(msg)}
                                    style={{
                                        alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                                        maxWidth: "85%",
                                        background: msg.role === "user" ? "var(--color-accent)" : "var(--color-bg-card)",
                                        color: msg.role === "user" ? "#fff" : "var(--color-text-primary)",
                                        borderRadius: "var(--radius-md)",
                                        padding: "10px 14px",
                                        fontSize: 13,
                                        border: msg.role === "assistant" ? "1px solid var(--color-border)" : "none",
                                        cursor: msg.role === "assistant" && msg.columns ? "pointer" : "default",
                                    }}
                                >
                                    <p>{msg.content}</p>
                                    {msg.role === "assistant" && msg.totalRows !== undefined && (
                                        <p style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 4 }}>
                                            총 {msg.totalRows}건 · 클릭하여 결과 보기
                                        </p>
                                    )}
                                </div>
                            ))}
                            {loading && (
                                <div style={{ alignSelf: "flex-start", background: "var(--color-bg-card)", borderRadius: "var(--radius-md)", padding: "10px 14px", border: "1px solid var(--color-border)", fontSize: 13, color: "var(--color-text-secondary)" }}>
                                    SQL 생성 및 실행 중...
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>
                        <form onSubmit={sendQuery} style={{ padding: "12px 16px", borderTop: "1px solid var(--color-border)", display: "flex", gap: 8 }}>
                            <input
                                id="admin-chat-input"
                                className="input"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="자산 현황을 질문하세요..."
                                disabled={loading}
                                style={{ flex: 1 }}
                            />
                            <button id="admin-send-btn" className="btn btn-primary" type="submit" disabled={loading || !input.trim()}>
                                전송
                            </button>
                        </form>
                    </div>

                    {/* Right: Result Table */}
                    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
                        <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--color-border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <h2 style={{ fontSize: 15, fontWeight: 600 }}>조회 결과</h2>
                                {activeResult && (
                                    <p style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 2 }}>
                                        총 {activeResult.totalRows}건
                                    </p>
                                )}
                            </div>
                            {activeResult?.logId && (
                                <button
                                    id="export-excel-btn"
                                    className="btn btn-secondary"
                                    onClick={() => exportToExcel(activeResult.logId!)}
                                    disabled={exporting}
                                    style={{ fontSize: 12 }}
                                >
                                    {exporting ? "내보내는 중..." : "📥 Excel 내보내기"}
                                </button>
                            )}
                        </div>
                        <div style={{ flex: 1, overflow: "auto", padding: 24 }}>
                            {activeResult?.sql && (
                                <div style={{ marginBottom: 16, background: "var(--color-bg-secondary)", borderRadius: "var(--radius-sm)", padding: "10px 14px", fontSize: 11, color: "var(--color-text-secondary)", fontFamily: "monospace", overflowX: "auto" }}>
                                    <span style={{ color: "var(--color-accent)", fontWeight: 600 }}>SQL: </span>
                                    {activeResult.sql}
                                </div>
                            )}
                            {!activeResult ? (
                                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60%", color: "var(--color-text-secondary)" }}>
                                    <div style={{ fontSize: 48, marginBottom: 12 }}>📊</div>
                                    <p style={{ fontSize: 13 }}>챗봇에서 질의하면 결과가 여기에 표시됩니다.</p>
                                </div>
                            ) : (
                                <DataTable columns={resultColumns} data={resultData} emptyMessage="조회 결과가 없습니다." />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
