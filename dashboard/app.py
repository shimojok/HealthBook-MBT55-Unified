"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v5.0 — 全ボタン動作・全画面表示・堅牢パス解決・日英対応
"""
import streamlit as st
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
from src.integration.full_pipeline import FullPipeline
from src.layer2_metabolism.pathway_database import get_pathway_database

st.set_page_config(page_title="HealthBook-MBT55 Unified", page_icon="🏥", layout="wide")

# ── 定数 ──
PAGE_HOME = "home"
PAGE_ASSESS = "health_assessment"
PAGE_METABOLIC = "metabolic_analysis"
PAGE_PROBIOTICS = "probiotics"
PAGE_KAMPO = "kampo_library"
PAGE_DISEASE = "disease_risk"
PAGE_SIMULATION = "simulation"
PAGE_REPORTS = "reports"

MENU_JA = {
    "🏠 ホーム": PAGE_HOME,
    "📋 健康アセスメント": PAGE_ASSESS,
    "🧬 代謝解析": PAGE_METABOLIC,
    "🦠 プロバイオティクス": PAGE_PROBIOTICS,
    "💊 漢方ライブラリー": PAGE_KAMPO,
    "⚠️ 疾病リスク": PAGE_DISEASE,
    "🔬 シミュレーション": PAGE_SIMULATION,
    "📄 レポート": PAGE_REPORTS,
}
MENU_EN = {
    "🏠 Home": PAGE_HOME,
    "📋 Health Assessment": PAGE_ASSESS,
    "🧬 Metabolic Analysis": PAGE_METABOLIC,
    "🦠 Probiotics": PAGE_PROBIOTICS,
    "💊 Kampo Library": PAGE_KAMPO,
    "⚠️ Disease Risk": PAGE_DISEASE,
    "🔬 Simulation": PAGE_SIMULATION,
    "📄 Reports": PAGE_REPORTS,
}

T = {
    "ja": {
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_desc": "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。\n\n200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、\n最適な漢方・生薬・MBT55菌株セットを提案します。",
        "home_start_btn": "🔴 健康アセスメントを開始する（200項目問診）",
        "assess_title": "📋 健康アセスメント",
        "assess_select_all": "✅ すべて選択",
        "assess_clear_all": "🔄 すべて解除",
        "assess_run_btn": "🔍 解析を実行する",
        "assess_complete": "✅ 解析が完了しました！タブを切り替えて結果を確認してください。",
        "assess_no_data": "「解析を実行する」ボタンを押すと、ここに結果が表示されます。",
        "error_no_json": "⚠️ 問診データファイルが見つかりません。",
        "metabolic_title": "🧬 代謝解析",
        "probiotics_title": "🦠 プロバイオティクス",
        "kampo_title": "💊 漢方ライブラリー",
        "disease_title": "⚠️ 疾病リスク",
        "simulation_title": "🔬 シミュレーション",
        "reports_title": "📄 レポート",
        "reports_no_data": "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_desc": "Next-generation healthcare platform integrating **full metabolic pathway analysis**,\n**phenotyping**, and **MBT Probiotics screening**.",
        "home_start_btn": "🔴 Start Health Assessment (200-Item Questionnaire)",
        "assess_title": "📋 Health Assessment",
        "assess_select_all": "✅ Select All",
        "assess_clear_all": "🔄 Clear All",
        "assess_run_btn": "🔍 Run Analysis",
        "assess_complete": "✅ Analysis complete!",
        "assess_no_data": "Click 'Run Analysis' to see results here.",
        "error_no_json": "⚠️ Questionnaire data file not found.",
        "metabolic_title": "🧬 Metabolic Analysis",
        "probiotics_title": "🦠 Probiotics",
        "kampo_title": "💊 Kampo Library",
        "disease_title": "⚠️ Disease Risk",
        "simulation_title": "🔬 Simulation",
        "reports_title": "📄 Reports",
        "reports_no_data": "Please run the Health Assessment first.",
    },
}

def txt(key: str) -> str:
    return T.get(st.session_state.get("language", "ja"), T["ja"]).get(key, key)

# ── セッション ──
def init_session():
    for k, v in {"language": "ja", "current_page": PAGE_HOME, "pipeline_result": None}.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── データ読み込み（複数パス試行） ──
@st.cache_data
def load_questionnaire(lang: str):
    base = Path(__file__).parent.parent
    candidates = [
        base / "data" / "questionnaires" / f"healthbook_200_{lang}.json",
        Path("data") / "questionnaires" / f"healthbook_200_{lang}.json",
        Path("/mount/src/healthbook-mbt55-unified/data") / "questionnaires" / f"healthbook_200_{lang}.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

def flatten_symptoms(data):
    result = {}
    if isinstance(data, dict):
        for cat, items in data.items():
            if isinstance(items, dict):
                for sub, symptoms in items.items():
                    if isinstance(symptoms, list):
                        for s in symptoms:
                            result[s] = cat
            elif isinstance(items, list):
                for s in items:
                    result[s] = cat
    return result

# ── サイドバー ──
def render_sidebar():
    menu = MENU_JA if st.session_state.language == "ja" else MENU_EN
    labels = list(menu.keys())
    pages = list(menu.values())

    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English")
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        st.divider()
        try:
            idx = pages.index(st.session_state.current_page)
        except ValueError:
            idx = 0
        sel = st.radio("メニュー", options=labels, index=idx, label_visibility="collapsed", key="main_nav")
        new_page = menu[sel]
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.rerun()

# ── ページ描画 ──
def render_home():
    st.title(txt("home_title"))
    st.markdown(txt("home_desc"))
    c1, c2, c3 = st.columns(3)
    c1.metric("代謝経路 / Pathways", "20+")
    c2.metric("MBT55メタ株 / Strains", "5")
    c3.metric("疾病マトリックス / Diseases", "137")
    st.divider()
    st.subheader("🚀 クイックスタート")
    if st.button(txt("home_start_btn"), type="primary", use_container_width=True):
        st.session_state.current_page = PAGE_ASSESS
        st.rerun()

def render_health_assessment():
    language = Language.JA if st.session_state.language == "ja" else Language.EN
    st.title(txt("assess_title"))
    q_data = load_questionnaire(st.session_state.language)
    if q_data is None:
        st.error(txt("error_no_json"))
        st.info("HealthBook-AI リポジトリから data/questionnaires/ にJSONファイルをコピーしてください。")
        return
    flat = flatten_symptoms(q_data)
    all_symptoms = list(flat.keys())
    categories = {}
    for s, cat in flat.items():
        categories.setdefault(cat, []).append(s)
    t1, t2, t3, t4 = st.tabs(["📝 問診入力", "📊 結果", "🦠 菌株推奨", "⚠️ 疾病リスク"])
    with t1:
        st.subheader("200項目健康問診")
        ca, cb, _ = st.columns([1,1,4])
        if ca.button(txt("assess_select_all"), use_container_width=True):
            for s in all_symptoms: st.session_state[f"s_{s}"] = True
            st.rerun()
        if cb.button(txt("assess_clear_all"), use_container_width=True):
            for s in all_symptoms: st.session_state[f"s_{s}"] = False
            st.rerun()
        st.divider()
        answers = {}
        for cat, symptoms in categories.items():
            st.markdown(f"### {cat}")
            cols = st.columns(3)
            for i, s in enumerate(symptoms):
                with cols[i % 3]:
                    val = st.checkbox(s, value=st.session_state.get(f"s_{s}", False), key=f"s_{s}")
                    answers[s] = val
        st.divider()
        if st.button(txt("assess_run_btn"), type="primary", use_container_width=True):
            with st.spinner("MBT55代謝経路を解析中..."):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
            st.success(txt("assess_complete"))
    with t2:
        result = st.session_state.pipeline_result
        if result and result.phenotype and result.phenotype.scores:
            defs = PATH_DEFINITIONS.get(language, {})
            st.subheader("📊 PATH_01〜05 スコア")
            import plotly.graph_objects as go
            cats_l, vals_l = [], []
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                cats_l.append(d.get("short", pid.value))
                vals_l.append(ps.score)
            if cats_l:
                fig = go.Figure(data=go.Scatterpolar(r=vals_l, theta=cats_l, fill='toself',
                    line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**総合判定: {result.phenotype.overall_status}**")
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3 = st.columns([3,1,1])
                x1.write(f"**{d.get('name', pid.value)}**")
                x2.metric("Score", f"{ps.score:.0f}%")
                color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info(txt("assess_no_data"))
    with t3:
        result = st.session_state.pipeline_result
        if result and result.probiotic_screening and result.probiotic_screening.recommended_strains:
            st.subheader("🦠 推奨MBT55メタ株")
            for strain in result.probiotic_screening.recommended_strains:
                st.markdown(f"### P{strain.priority}: {strain.name}")
                st.write(strain.reason)
                st.divider()
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for e in result.expected_effects: st.markdown(f"✅ {e}")
        else:
            st.info(txt("assess_no_data"))
    with t4:
        result = st.session_state.pipeline_result
        if result and result.disease_risks:
            st.subheader("⚠️ 疾病リスク")
            for d, r in result.disease_risks.items(): st.metric(label=d, value=f"{r:.1f}%")
        else:
            st.info(txt("assess_no_data"))

def render_metabolic_analysis():
    st.title(txt("metabolic_title"))
    db = get_pathway_database()
    substrates = db.list_all_substrates()
    if substrates:
        sel = st.selectbox("🔍 基質を選択", substrates)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                    st.write(f"効果: {', '.join(p['human_effects'])}")
                    st.divider()
        st.subheader("📋 全登録基質")
        st.write(", ".join(substrates))
    else:
        st.warning("代謝経路データがありません。")

def render_probiotics():
    st.title(txt("probiotics_title"))
    lang = Language.JA if st.session_state.language == "ja" else Language.EN
    for sid, d in META_STRAIN_DEFINITIONS.get(lang, {}).items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(f"機能: {d['functional_unit']} | 菌種: {d['key_species']} | 生成物: {d['produces']}")

def render_kampo_library():
    st.title(txt("kampo_title"))
    st.info("294漢方処方ライブラリー - 準備中")

def render_disease_risk():
    st.title(txt("disease_title"))
    st.info("137疾病マトリックス - 準備中")

def render_simulation():
    st.title(txt("simulation_title"))
    st.markdown("### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |")
    st.latex(r"\frac{dH_2}{dt} \approx 0")

def render_reports():
    st.title(txt("reports_title"))
    result = st.session_state.pipeline_result
    if result:
        st.download_button("📥 JSONダウンロード", json.dumps(result.to_dict(), ensure_ascii=False, indent=2), "report.json", "application/json")
        st.text(result.format_for_display())
    else:
        st.info(txt("reports_no_data"))

# ── メイン ──
RENDERERS = {
    PAGE_HOME: render_home, PAGE_ASSESS: render_health_assessment,
    PAGE_METABOLIC: render_metabolic_analysis, PAGE_PROBIOTICS: render_probiotics,
    PAGE_KAMPO: render_kampo_library, PAGE_DISEASE: render_disease_risk,
    PAGE_SIMULATION: render_simulation, PAGE_REPORTS: render_reports,
}

def main():
    init_session()
    render_sidebar()
    RENDERERS.get(st.session_state.current_page, render_home)()

if __name__ == "__main__":
    main()