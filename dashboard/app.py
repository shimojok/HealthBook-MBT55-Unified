"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v11.8 — デッドロック完全解消・標準タブ復帰版
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
        "assess_desc": "該当する症状を選択し、「🔍 解析を実行する」ボタンを押してください。結果は「📊 結果」以降のタブに表示されます。",
        "assess_run": "🔍 解析を実行する",
        "assess_complete": "✅ 解析が完了しました！右側のタブに結果が反映されています。",
        "assess_no_data": "問診に回答し、下の「解析を実行する」ボタンを押すとここに結果が表示されます。",
        "assess_tab1": "📝 問診入力",
        "assess_tab2": "📊 結果",
        "assess_tab3": "🦠 菌株推奨",
        "assess_tab4": "⚠️ 疾病リスク",
        "assess_overall": "総合判定",
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
        "disease_title": "⚠️ 疾病リスク",
        "disease_subtitle": "📊 137疾病マトリックス（{count}疾病）",
        "disease_search": "🔍 疾病名・コードで検索",
        "sim_title": "🔬 シミュレーション",
        "sim_cascade_table": "### 3段階酵素カスケード",
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
        "assess_desc": "Please choose your symptoms and click 'Run Analysis'.",
        "assess_run": "🔍 Run Analysis",
        "assess_complete": "✅ Analysis complete! Check the results tabs.",
        "assess_no_data": "Click 'Run Analysis' to see results here.",
        "assess_tab1": "📝 Questionnaire",
        "assess_tab2": "📊 Results",
        "assess_tab3": "🦠 Strains",
        "assess_tab4": "⚠️ Disease Risk",
        "assess_overall": "Overall Assessment",
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
        "disease_title": "⚠️ Disease Risk",
        "disease_subtitle": "📊 137 Disease Matrix ({count} diseases)",
        "disease_search": "🔍 Search by disease name or code",
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
    if "navigation" not in st.session_state: st.session_state.navigation = HOME
    if "result" not in st.session_state: st.session_state.result = None
    if "lang" not in st.session_state: st.session_state.lang = "ja"

def sidebar():
    lang_setting = st.session_state.lang
    menu = MENU[lang_setting]
    
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        
        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"],
            index=0 if lang_setting == "ja" else 1,
            format_func=lambda x: "日本語" if x == "ja" else "English")
        if lang != lang_setting:
            st.session_state.lang = lang
            st.rerun()
            
        st.divider()
        st.markdown("### メニューナビゲーション")
        
        # 完全に独立したボタンで安全に遷移（フリーズ防止仕様）
        for label, page_id in menu:
            is_current = (st.session_state.navigation == page_id)
            btn_type = "primary" if is_current else "secondary"
            
            if st.button(label, key=f"nav_btn_{page_id}", type=btn_type, use_container_width=True):
                st.session_state.navigation = page_id
                st.rerun()

def home():
    st.title(t("home_title"))
    st.markdown(t("home_desc"))
    c1, c2, c3 = st.columns(3)
    c1.metric(t("home_pathways_metric"), "20+")
    c2.metric(t("home_strains_metric"), "5")
    c3.metric(t("home_diseases_metric"), "137")
    st.divider()
    st.subheader(t("home_quickstart"))
    if st.button(t("home_btn"), type="primary", use_container_width=True, key="start_home_btn"):
        st.session_state.navigation = ASSESS
        st.rerun()

def assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN
    st.title(t("assess_title"))
    st.markdown(t("assess_desc"))
    
    qfile = "questionnaire_200_jp.json" if st.session_state.lang == "ja" else "questionnaire_200_en.json"
    data = load_json(f"data/questionnaires/{qfile}")
    if data is None:
        st.error(t("error_no_json"))
        return
    questions = data.get("questions", {})

    # ─── 修正の要：標準的で頑丈なタブ構造への差し戻し ───
    # 画面のデッドロック（非表示バグ）を完全に防ぐため、入力と結果をタブに並列化します。
    tab1, tab2, tab3, tab4 = st.tabs([t("assess_tab1"), t("assess_tab2"), t("assess_tab3"), t("assess_tab4")])
    
    # 📝 問診入力タブ
    with tab1:
        st.markdown("### 📋 該当する症状をすべて選んでください")
        
        all_symptom_list = []
        symptom_to_id_map = {}
        for qid, qdata in questions.items():
            q_text = qdata["question"]
            cat = qdata.get("category", "その他")
            display_label = f"[{cat}] {q_text}"
            all_symptom_list.append(display_label)
            symptom_to_id_map[display_label] = q_text

        chosen_labels = st.multiselect(
            label="症状の検索ボックス（文字入力で絞り込めます）",
            options=all_symptom_list,
            key="symptom_multiselect_box"
        )
        
        st.divider()
        
        if st.button(t("assess_run"), type="primary", use_container_width=True, key="run_pipeline_btn"):
            answers = {qdata["question"]: False for qdata in questions.values()}
            for label in chosen_labels:
                original_question = symptom_to_id_map[label]
                answers[original_question] = True

            try:
                with st.spinner(t("assess_spinner")):
                    result = FullPipeline(language=language).run(answers)
                    st.session_state.result = result
                st.success(t("assess_complete"))
                # リフレッシュせず、そのままセッションデータを下に展開
            except Exception as e:
                st.error("❌ 解析ロジック(FullPipeline)の実行中にエラーが発生しました。")
                st.exception(e)

    # 📊 結果タブ
    with tab2:
        result = st.session_state.result
        if result and result.phenotype and result.phenotype.scores:
            defs = PATH_DEFINITIONS.get(language, {})
            st.subheader("📊 PATH_01〜05 代謝経路活性スコア")
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
            
            st.markdown(f"### **{t('assess_overall')}: {result.phenotype.overall_status}**")
            st.divider()
            
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3 = st.columns([3, 1, 1])
                x1.write(f"**{d.get('name', pid.value)}**")
                x2.metric("Score", f"{ps.score:.0f}%")
                color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info(t("assess_no_data"))

    # 🦠 菌株推奨タブ
    with tab3:
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

    # ⚠️ 疾病リスクタブ
    with tab4:
        result = st.session_state.result
        if result and result.disease_risks:
            st.subheader("⚠️ 疾病リスク評価")
            for d, r in result.disease_risks.items(): 
                st.metric(label=d, value=f"{r:.1f}%")
        else:
            st.info(t("assess_no_data"))

def metabolic():
    st.title(t("metabolic_title"))
    db = get_pathway_database()
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox(t("metabolic_select"), subs, key="meta_subs_box")
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
        search = st.text_input(t("kampo_search"), key="kampo_search_box")
        filtered = [k for k in kampo_data if search.lower() in str(k).lower()] if search else kampo_data
        for item in filtered[:20]:
            with st.expander(f"💊 {item.get('name', item.get('formula_name', '不明'))}"): st.json(item)

def disease():
    st.title(t("disease_title"))
    disease_data = load_json("data/diseases/disease_matrix_137.json")
    if disease_data and isinstance(disease_data, list):
        search = st.text_input(t("disease_search"), key="disease_search_box")
        filtered = [d for d in disease_data if search.lower() in str(d).lower()] if search else disease_data
        for item in filtered[:20]:
            with st.expander(f"⚠️ {item.get('name', item.get('disease_name', '不明'))}"): st.json(item)

def sim():
    st.title(t("sim_title"))
    st.markdown("### 3段階酵素カスケード")

def reports():
    st.title(t("reports_title"))
    result = st.session_state.result
    if result:
        st.download_button(t("reports_download_btn"), json.dumps(result.to_dict(), ensure_ascii=False, indent=2), "report.json", "application/json", key="report_dl_btn")
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
