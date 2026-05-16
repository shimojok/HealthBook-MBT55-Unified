"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v11.0 — オリジナルUI完全復元・解析実行バグ修正版
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
HOME = "home"
ASSESS = "health_assessment"
METABOLIC = "metabolic_analysis"
PROBIOTICS = "probiotics"
KAMPO = "kampo_library"
DISEASE = "disease_risk"
SIM = "simulation"
REPORTS = "reports"

MENU = {
    "ja": [
        ("🏠 ホーム", HOME),
        ("📋 健康アセスメント", ASSESS),
        ("🧬 代謝解析", METABOLIC),
        ("🦠 プロバイオティクス", PROBIOTICS),
        ("💊 漢方ライブラリー", KAMPO),
        ("⚠️ 疾病リスク", DISEASE),
        ("🔬 シミュレーション", SIM),
        ("📄 レポート", REPORTS),
    ],
    "en": [
        ("🏠 Home", HOME),
        ("📋 Health Assessment", ASSESS),
        ("🧬 Metabolic Analysis", METABOLIC),
        ("🦠 Probiotics", PROBIOTICS),
        ("💊 Kampo Library", KAMPO),
        ("⚠️ Disease Risk", DISEASE),
        ("🔬 Simulation", SIM),
        ("📄 Reports", REPORTS),
    ],
}

TXT = {
    "ja": {
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_desc": "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。\n\n200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、\n最適な漢方・生薬・MBT55菌株セットを提案します。",
        "home_btn": "🔴 健康アセスメントを開始する（200項目問診）",
        "home_pathways_metric": "代謝経路",
        "home_strains_metric": "MBT55メタ株",
        "home_diseases_metric": "疾病マトリックス",
        "home_quickstart": "🚀 クイックスタート",
        "assess_title": "📋 健康アセスメント",
        "assess_desc": "該当する症状をカテゴリごとに選択してください。",
        "assess_run": "🔍 解析を実行する",
        "assess_complete": "✅ 解析が完了しました！結果を表示します。",
        "assess_no_data": "問診に回答し「解析を実行する」ボタンを押してください。",
        "assess_tab1": "📝 問診入力",
        "assess_tab2": "📊 結果",
        "assess_tab3": "🦠 菌株推奨",
        "assess_tab4": "⚠️ 疾病リスク",
        "assess_total_items": "全{count}項目健康問診",
        "assess_category_count": "（{count}項目）",
        "assess_spinner": "MBT55代謝経路を解析中...",
        "assess_overall": "総合判定",
        "assess_results_summary": "📊 解析結果サマリー",
        "assess_results_detail_hint": "👉 詳細は各タブをご覧ください",
        "assess_strains_title": "🦠 推奨MBT55メタ株",
        "assess_effects_title": "✨ 期待効果",
        "error_no_json": "⚠️ データファイルが見つかりません。",
        "error_invalid_structure": "データ構造が不正です。",
        "metabolic_title": "🧬 代謝解析",
        "metabolic_select": "🔍 基質を選択",
        "metabolic_all_substrates": "📋 全登録基質",
        "probiotics_title": "🦠 プロバイオティクス",
        "kampo_title": "💊 漢方ライブラリー",
        "kampo_subtitle": "📚 漢方処方ライブラリー（{count}処方）",
        "kampo_search": "🔍 処方名・生薬で検索",
        "kampo_display_count": "表示: {filtered} / {total} 処方",
        "disease_title": "⚠️ 疾病リスク",
        "disease_subtitle": "📊 137疾病マトリックス（{count}疾病）",
        "disease_search": "🔍 疾病名・コードで検索",
        "disease_display_count": "表示: {filtered} / {total} 疾病",
        "sim_title": "🔬 シミュレーション",
        "sim_cascade_table": "### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |",
        "reports_title": "📄 レポート",
        "reports_download_btn": "📥 JSONダウンロード",
        "reports_summary": "📊 統合解析サマリー",
        "reports_no_data": "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_desc": "Next-generation healthcare platform integrating **full metabolic pathway analysis**...",
        "home_btn": "🔴 Start Health Assessment (200-Item Questionnaire)",
        "home_pathways_metric": "Pathways",
        "home_strains_metric": "MBT55 Meta-Strains",
        "home_diseases_metric": "Disease Matrix",
        "home_quickstart": "🚀 Quick Start",
        "assess_title": "📋 Health Assessment",
        "assess_desc": "Please select your symptoms for each category.",
        "assess_run": "🔍 Run Analysis",
        "assess_complete": "✅ Analysis complete!",
        "assess_no_data": "Please complete the questionnaire and click 'Run Analysis'.",
        "assess_tab1": "📝 Questionnaire",
        "assess_tab2": "📊 Results",
        "assess_tab3": "🦠 Strains",
        "assess_tab4": "⚠️ Disease Risk",
        "assess_total_items": "Total {count} Health Questions",
        "assess_category_count": "({count} items)",
        "assess_spinner": "Analyzing MBT55 metabolic pathways...",
        "assess_overall": "Overall Assessment",
        "assess_results_summary": "📊 Analysis Summary",
        "assess_results_detail_hint": "👉 See details in each tab",
        "assess_strains_title": "🦠 Recommended MBT55 Meta-Strains",
        "assess_effects_title": "✨ Expected Effects",
        "error_no_json": "⚠️ Data file not found.",
        "error_invalid_structure": "Invalid data structure.",
        "metabolic_title": "🧬 Metabolic Analysis",
        "metabolic_select": "🔍 Select Substrate",
        "metabolic_all_substrates": "📋 All Registered Substrates",
        "probiotics_title": "🦠 Probiotics",
        "kampo_title": "💊 Kampo Library",
        "kampo_subtitle": "📚 Kampo Formula Library ({count} formulas)",
        "kampo_search": "🔍 Search by formula or herb name",
        "kampo_display_count": "Showing: {filtered} / {total} formulas",
        "disease_title": "⚠️ Disease Risk",
        "disease_subtitle": "📊 137 Disease Matrix ({count} diseases)",
        "disease_search": "🔍 Search by disease name or code",
        "disease_display_count": "Showing: {filtered} / {total} diseases",
        "sim_title": "🔬 Simulation",
        "sim_cascade_table": "### 3-Stage Enzyme Cascade...",
        "reports_title": "📄 Reports",
        "reports_download_btn": "📥 Download JSON",
        "reports_summary": "📊 Integrated Analysis Summary",
        "reports_no_data": "Please run the Health Assessment first.",
    },
}

def t(key: str, **kwargs) -> str:
    text = TXT.get(st.session_state.get("lang", "ja"), TXT["ja"]).get(key, key)
    if kwargs:
        try: return text.format(**kwargs)
        except (KeyError, ValueError): return text
    return text

@st.cache_data
def load_json(filename):
    for base in [Path(__file__).parent.parent, Path("."), Path("/mount/src/healthbook-mbt55-unified")]:
        p = base / filename
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

def init():
    if "lang" not in st.session_state: st.session_state.lang = "ja"
    if "navigation" not in st.session_state: st.session_state.navigation = HOME
    if "result" not in st.session_state: st.session_state.result = None

def sidebar():
    menu = MENU[st.session_state.lang]
    labels = [m[0] for m in menu]
    ids = [m[1] for m in menu]
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"], index=0 if st.session_state.lang == "ja" else 1, key="lang_select")
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
        st.divider()
        try: idx = ids.index(st.session_state.navigation)
        except ValueError: idx = 0
        sel = st.radio("メニュー", labels, index=idx, label_visibility="collapsed")
        new_page = ids[labels.index(sel)]
        if new_page != st.session_state.navigation:
            st.session_state.navigation = new_page
            st.rerun()

def start_assessment():
    st.session_state.navigation = ASSESS

def home():
    st.title(t("home_title"))
    st.markdown(t("home_desc"))
    c1, c2, c3 = st.columns(3)
    c1.metric(t("home_pathways_metric"), "20+")
    c2.metric(t("home_strains_metric"), "5")
    c3.metric(t("home_diseases_metric"), "137")
    st.divider()
    st.subheader(t("home_quickstart"))
    st.button(t("home_btn"), type="primary", use_container_width=True, key="start_btn", on_click=start_assessment)

def assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN
    st.title(t("assess_title"))
    qfile = "questionnaire_200_jp.json" if st.session_state.lang == "ja" else "questionnaire_200_en.json"
    data = load_json(f"data/questionnaires/{qfile}")
    if data is None:
        st.error(t("error_no_json"))
        return
    questions = data.get("questions", {})
    cats = {}
    for qid, qdata in questions.items():
        cat = qdata.get("category", "その他")
        cats.setdefault(cat, []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    st.markdown(t("assess_desc"))
    t1, t2, t3, t4 = st.tabs([t("assess_tab1"), t("assess_tab2"), t("assess_tab3"), t("assess_tab4")])
    
    with t1:
        st.write(t("assess_total_items", count=len(questions)))
        # ★最重要変更点: FORMオブジェクトに包むことで「解析を実行する」ボタン押下時に200項目を完全に一括送信し、画面フリーズを解消
        with st.form(key="assessment_form"):
            form_answers = {}
            for cat_name in cat_order:
                qlist = cats.get(cat_name, [])
                if not qlist: continue
                with st.expander(f"■ {cat_name} {t('assess_category_count', count=len(qlist))}", expanded=False):
                    for q in qlist:
                        form_answers[q["question"]] = st.checkbox(q["question"], key=f"q_{q['id']}")
            
            submit = st.form_submit_button(t("assess_run"), type="primary", use_container_width=True)
            if submit:
                with st.spinner(t("assess_spinner")):
                    try:
                        # 正しい入力データ（form_answers）をパイプラインに渡して再計算を実行
                        st.session_state.result = FullPipeline(language=language).run(form_answers)
                        st.success(t("assess_complete"))
                    except Exception as e:
                        st.error(f"Execution Error: {e}")

    with t2:
        result = st.session_state.result
        if result and result.phenotype and result.phenotype.scores:
            defs = PATH_DEFINITIONS.get(language, {})
            st.subheader(t("assess_results_summary"))
            st.caption(t("assess_results_detail_hint"))
            import plotly.graph_objects as go
            cl, vl = [], []
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                cl.append(d.get("short", pid.value))
                vl.append(ps.score)
            if cl:
                fig = go.Figure(data=go.Scatterpolar(r=vl, theta=cl, fill='toself', line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**{t('assess_overall')}: {result.phenotype.overall_status}**")
            st.divider()
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3 = st.columns([3, 1, 1])
                x1.write(f"**{d.get('name', pid.value)}**\n*{d.get('desc', '')}*")
                x2.metric("Score", f"{ps.score:.0f}%")
                color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info(t("assess_no_data"))
    with t3:
        result = st.session_state.result
        if result and result.probiotic_screening and result.probiotic_screening.recommended_strains:
            st.subheader(t("assess_strains_title"))
            for strain in result.probiotic_screening.recommended_strains:
                st.markdown(f"### P{strain.priority}: {strain.name}")
                st.write(strain.reason)
                st.divider()
            if result.expected_effects:
                st.subheader(t("assess_effects_title"))
                for e in result.expected_effects: st.markdown(f"✅ {e}")
        else:
            st.info(t("assess_no_data"))
    with t4:
        result = st.session_state.result
        if result and result.disease_risks:
            st.subheader(t("disease_title"))
            for d, r in result.disease_risks.items(): st.metric(label=d, value=f"{r:.1f}%")
        else:
            st.info(t("assess_no_data"))

def metabolic():
    st.title(t("metabolic_title"))
    db = get_pathway_database()
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox(t("metabolic_select"), subs)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                    st.write(f"効果: {', '.join(p['human_effects'])}")
                    st.divider()

def probiotics():
    st.title(t("probiotics_title"))
    lang = Language.JA if st.session_state.lang == "ja" else Language.EN
    for sid, d in META_STRAIN_DEFINITIONS.get(lang, {}).items():
        with st.expander(f"🔹 {d['name']}"): st.write(f"機能: {d['functional_unit']} | 菌種: {d['key_species']} | 生成物: {d['produces']}")

def kampo():
    st.title(t("kampo_title"))
    kampo_data = load_json("data/kampo/kampo_metabolic_library.json")
    if kampo_data and isinstance(kampo_data, list):
        st.subheader(t("kampo_subtitle", count=len(kampo_data)))
        search = st.text_input(t("kampo_search"), key="kampo_search")
        filtered = [k for k in kampo_data if search.lower() in str(k).lower()] if search else kampo_data
        for item in filtered[:20]:
            with st.expander(f"💊 {item.get('name', item.get('formula_name', '不明'))}"): st.json(item)

def disease():
    st.title(t("disease_title"))
    disease_data = load_json("data/diseases/disease_matrix_137.json")
    if disease_data and isinstance(disease_data, list):
        st.subheader(t("disease_subtitle", count=len(disease_data)))
        search = st.text_input(t("disease_search"), key="disease_search")
        filtered = [d for d in disease_data if search.lower() in str(d).lower()] if search else disease_data
        for item in filtered[:20]:
            with st.expander(f"⚠️ {item.get('name', item.get('disease_name', '不明'))}"): st.json(item)

def sim():
    st.title(t("sim_title"))
    st.markdown(t("sim_cascade_table"))

def reports():
    st.title(t("reports_title"))
    result = st.session_state.result
    if result:
        st.download_button(t("reports_download_btn"), json.dumps(result.to_dict(), ensure_ascii=False, indent=2), "report.json", "application/json")
        st.subheader(t("reports_summary"))
        st.text(result.format_for_display())
    else:
        st.info(t("reports_no_data"))

def main():
    init()
    sidebar()
    current_page = st.session_state.navigation
    pages = {HOME: home, ASSESS: assessment, METABOLIC: metabolic, PROBIOTICS: probiotics, KAMPO: kampo, DISEASE: disease, SIM: sim, REPORTS: reports}
    pages.get(current_page, home)()

if __name__ == "__main__":
    main()
