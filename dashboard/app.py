"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v11.9 — 高速キャッシュ・描画負荷ゼロ版
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

# ── ページID ──
HOME, ASSESS, METABOLIC, PROBIOTICS, KAMPO, DISEASE, SIM, REPORTS = (
    "home", "health_assessment", "metabolic_analysis", "probiotics", "kampo_library", "disease_risk", "simulation", "reports"
)

# テキスト定義
TXT = {
    "ja": {
        "assess_title": "📋 健康アセスメント",
        "assess_run": "🔍 解析を実行する",
        "assess_complete": "✅ 解析完了！「📊 結果」タブをご覧ください。",
        "assess_tab1": "📝 問診入力", "assess_tab2": "📊 結果", "assess_tab3": "🦠 菌株推奨", "assess_tab4": "⚠️ 疾病リスク",
        "assess_spinner": "MBT55代謝解析中...",
    },
    "en": {
        "assess_title": "📋 Health Assessment",
        "assess_run": "🔍 Run Analysis",
        "assess_complete": "✅ Done! See Results tab.",
        "assess_tab1": "📝 Input", "assess_tab2": "📊 Results", "assess_tab3": "🦠 Strains", "assess_tab4": "⚠️ Risks",
        "assess_spinner": "Analyzing...",
    }
}

def t(key):
    return TXT.get(st.session_state.get("lang", "ja"), TXT["ja"]).get(key, key)

@st.cache_data
def get_questionnaire_data(lang):
    """問診データを高速に読み込み、選択肢リストをキャッシュする"""
    qfile = f"data/questionnaires/questionnaire_200_{'jp' if lang=='ja' else 'en'}.json"
    for base in [Path(__file__).parent.parent, Path(".")]:
        p = base / qfile
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = data.get("questions", {})
                all_labels = []
                mapping = {}
                for qid, qdata in questions.items():
                    label = f"[{qdata.get('category', '')}] {qdata['question']}"
                    all_labels.append(label)
                    mapping[label] = qdata["question"]
                return questions, all_labels, mapping
    return {}, [], {}

def init():
    if "navigation" not in st.session_state: st.session_state.navigation = HOME
    if "lang" not in st.session_state: st.session_state.lang = "ja"
    if "result" not in st.session_state: st.session_state.result = None

def sidebar():
    with st.sidebar:
        st.title("🏥 HealthBook")
        st.session_state.lang = st.selectbox("🌐 Language", ["ja", "en"], index=0 if st.session_state.lang == "ja" else 1)
        st.divider()
        pages = [("🏠 ホーム", HOME), ("📋 健康アセスメント", ASSESS), ("🧬 代謝解析", METABOLIC), ("🦠 プロバイオティクス", PROBIOTICS), ("💊 漢方", KAMPO), ("⚠️ 疾病リスク", DISEASE), ("🔬 シミュレーション", SIM), ("📄 レポート", REPORTS)]
        for label, pid in pages:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.navigation == pid else "secondary"):
                st.session_state.navigation = pid
                st.rerun()

def assessment():
    st.title(t("assess_title"))
    questions, all_labels, mapping = get_questionnaire_data(st.session_state.lang)
    
    if not questions:
        st.error("Questionnaire data not found.")
        return

    # タブを最優先で描画
    tab1, tab2, tab3, tab4 = st.tabs([t("assess_tab1"), t("assess_tab2"), t("assess_tab3"), t("assess_tab4")])

    with tab1:
        st.write("該当する症状を検索・選択してください。")
        # keyを固定して再描画時の負荷を軽減
        chosen_labels = st.multiselect("症状の選択", options=all_labels, key="symptom_sel")
        
        st.divider()
        if st.button(t("assess_run"), type="primary", use_container_width=True):
            answers = {qtext: (f"[{qdata.get('category','')}] {qtext}" in chosen_labels) 
                       for qtext, qdata in questions.items()}
            try:
                with st.spinner(t("assess_spinner")):
                    lang_enum = Language.JA if st.session_state.lang == "ja" else Language.EN
                    st.session_state.result = FullPipeline(language=lang_enum).run(answers)
                st.success(t("assess_complete"))
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        res = st.session_state.result
        if res and res.phenotype:
            st.subheader("📊 代謝経路活性")
            for pid, ps in res.phenotype.scores.items():
                st.write(f"**{pid.value}**: {ps.score}% ({ps.level})")
        else: st.info("解析を実行してください。")

    with tab3:
        res = st.session_state.result
        if res and res.probiotic_screening:
            for s in res.probiotic_screening.recommended_strains:
                st.write(f"🦠 **{s.name}**: {s.reason}")
        else: st.info("解析を実行してください。")

    with tab4:
        res = st.session_state.result
        if res and res.disease_risks:
            for d, r in res.disease_risks.items():
                st.write(f"⚠️ {d}: {r:.1f}%")
        else: st.info("解析を実行してください。")

# --- 他のページ関数 ---
def home():
    st.title("🏥 HealthBook-MBT55")
    if st.button("🔴 健康アセスメントを開始する", type="primary"):
        st.session_state.navigation = ASSESS
        st.rerun()

def main():
    init()
    sidebar()
    p = st.session_state.navigation
    if p == HOME: home()
    elif p == ASSESS: assessment()
    else: st.title("Coming Soon...")

if __name__ == "__main__":
    main()
