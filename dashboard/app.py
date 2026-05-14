"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v11.1 — 赤ボタン on_click コールバックとサイドバー同期修正版
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
        "assess_desc": "以下の200項目の問診に回答してください。",
        "assess_select_all": "✅ すべて選択",
        "assess_clear_all": "🔄 すべて解除",
        "assess_run": "🔍 解析を実行する",
        "assess_complete": "✅ 解析が完了しました！",
        "assess_no_data": "「解析を実行する」ボタンを押すと、ここに結果が表示されます。",
        "assess_tab1": "📝 問診入力",
        "assess_tab2": "📊 結果",
        "assess_tab3": "🦠 菌株推奨",
        "assess_tab4": "⚠️ 疾病リスク",
        "assess_total_items": "全{count}項目健康問診",
        "assess_category_count": "（{count}項目）",
        "assess_spinner": "MBT55代謝経路を解析中...",
        "assess_overall": "総合判定",
        "assess_results_summary": "📊 解析結果サマリー",
        "assess_results_detail_hint": "👉 詳細は「📊 結果」「🦠 菌株推奨」「⚠️ 疾病リスク」タブをご覧ください",
        "assess_strains_title": "🦠 推奨MBT55メタ株",
        "assess_effects_title": "✨ 期待効果",
        "error_no_json": "⚠️ データファイルが見つかりません。",
        "error_no_json_hint": "data フォルダにJSONファイルを配置してください。",
        "error_invalid_structure": "データ構造が不正です。",
        "metabolic_title": "🧬 代謝解析",
        "metabolic_select": "🔍 基質を選択",
        "metabolic_all_substrates": "📋 全登録基質",
        "probiotics_title": "🦠 プロバイオティクス",
        "kampo_title": "💊 漢方ライブラリー",
        "kampo_subtitle": "📚 漢方処方ライブラリー（{count}処方）",
        "kampo_search": "🔍 処方名・生薬で検索",
        "kampo_display_count": "表示: {filtered} / {total} 処方",
        "kampo_overflow": "上位20件を表示中。検索で絞り込んでください。（全{total}件）",
        "kampo_animal": "🦌 動物性生薬ライブラリー",
        "kampo_animal_count": "**{count}件**の動物性生薬",
        "disease_title": "⚠️ 疾病リスク",
        "disease_subtitle": "📊 137疾病マトリックス（{count}疾病）",
        "disease_search": "🔍 疾病名・コードで検索",
        "disease_display_count": "表示: {filtered} / {total} 疾病",
        "disease_overflow": "上位20件を表示中。検索で絞り込んでください。（全{total}件）",
        "disease_personal": "🔍 あなたの疾病リスク評価",
        "sim_title": "🔬 シミュレーション",
        "sim_cascade_table": "### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |",
        "reports_title": "📄 レポート",
        "reports_download_btn": "📥 JSONダウンロード",
        "reports_summary": "📊 統合解析サマリー",
        "reports_no_data": "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_desc": "Next-generation healthcare platform integrating **full metabolic pathway analysis**,\n**phenotyping**, and **MBT Probiotics screening**.",
        "home_btn": "🔴 Start Health Assessment (200-Item Questionnaire)",
        "home_pathways_metric": "Pathways",
        "home_strains_metric": "MBT55 Meta-Strains",
        "home_diseases_metric": "Disease Matrix",
        "home_quickstart": "🚀 Quick Start",
        "assess_title": "📋 Health Assessment",
        "assess_desc": "Answer the 200-item questionnaire below.",
        "assess_select_all": "✅ Select All",
        "assess_clear_all": "🔄 Clear All",
        "assess_run": "🔍 Run Analysis",
        "assess_complete": "✅ Analysis complete!",
        "assess_no_data": "Click 'Run Analysis' to see results here.",
        "assess_tab1": "📝 Questionnaire",
        "assess_tab2": "📊 Results",
        "assess_tab3": "🦠 Strains",
        "assess_tab4": "⚠️ Disease Risk",
        "assess_total_items": "Total {count} Health Questions",
        "assess_category_count": "({count} items)",
        "assess_spinner": "Analyzing MBT55 metabolic pathways...",
        "assess_overall": "Overall Assessment",
        "assess_results_summary": "📊 Analysis Summary",
        "assess_results_detail_hint": "👉 See '📊 Results' '🦠 Strains' '⚠️ Disease Risk' tabs for details",
        "assess_strains_title": "🦠 Recommended MBT55 Meta-Strains",
        "assess_effects_title": "✨ Expected Effects",
        "error_no_json": "⚠️ Data file not found.",
        "error_no_json_hint": "Please place JSON files in the data folder.",
        "error_invalid_structure": "Invalid data structure.",
        "metabolic_title": "🧬 Metabolic Analysis",
        "metabolic_select": "🔍 Select Substrate",
        "metabolic_all_substrates": "📋 All Registered Substrates",
        "probiotics_title": "🦠 Probiotics",
        "kampo_title": "💊 Kampo Library",
        "kampo_subtitle": "📚 Kampo Formula Library ({count} formulas)",
        "kampo_search": "🔍 Search by formula or herb name",
        "kampo_display_count": "Showing: {filtered} / {total} formulas",
        "kampo_overflow": "Showing top 20. Use search to filter. (Total: {total})",
        "kampo_animal": "🦌 Animal-Derived Library",
        "kampo_animal_count": "**{count} items** of animal-derived herbs",
        "disease_title": "⚠️ Disease Risk",
        "disease_subtitle": "📊 137 Disease Matrix ({count} diseases)",
        "disease_search": "🔍 Search by disease name or code",
        "disease_display_count": "Showing: {filtered} / {total} diseases",
        "disease_overflow": "Showing top 20. Use search to filter. (Total: {total})",
        "disease_personal": "🔍 Your Disease Risk Assessment",
        "sim_title": "🔬 Simulation",
        "sim_cascade_table": "### 3-Stage Enzyme Cascade\n| Stage | Time | Temp | Oxygen |\n|-------|------|------|--------|\n| 1 | 0-6h | 38°C | Aerobic |\n| 2 | 6-24h | 42°C | Microaerophilic |\n| 3 | 24-72h | 35°C | Anaerobic |",
        "reports_title": "📄 Reports",
        "reports_download_btn": "📥 Download JSON",
        "reports_summary": "📊 Integrated Analysis Summary",
        "reports_no_data": "Please run the Health Assessment first.",
    },
}

def t(key: str, **kwargs) -> str:
    """翻訳テキスト取得。{key} プレースホルダーを kwargs で置換。"""
    text = TXT.get(st.session_state.get("lang", "ja"), TXT["ja"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
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
    if "lang" not in st.session_state:
        st.session_state.lang = "ja"
    if "navigation" not in st.session_state:
        st.session_state.navigation = HOME
    if "result" not in st.session_state:
        st.session_state.result = None

def go(page):
    st.session_state.navigation = page

def sidebar():
    menu = MENU[st.session_state.lang]
    labels = [m[0] for m in menu]
    ids = [m[1] for m in menu]
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English", key="lang_select")
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
        st.divider()
        try:
            idx = ids.index(st.session_state.navigation)
        except ValueError:
            idx = 0
            
        # 赤ボタンからナビゲーションが切り替わった際に、ラジオボタンの状態（navキー）も同期する
        st.session_state.nav = labels[idx]
        
        sel = st.radio("メニュー", labels, label_visibility="collapsed", key="nav")
        new_page = ids[labels.index(sel)]
        if new_page != st.session_state.navigation:
            go(new_page)
            st.rerun()

# ★★★ on_click 専用コールバック (修正：ラジオボタンの状態も同期する) ★★★
def start_assessment():
    st.session_state.navigation = ASSESS
    current_menu = MENU[st.session_state.get("lang", "ja")]
    for label, page_id in current_menu:
        if page_id == ASSESS:
            st.session_state.nav = label
            break

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
    st.markdown(t("assess_desc"))
    qfile = "questionnaire_200_jp.json" if st.session_state.lang == "ja" else "questionnaire_200_en.json"
    data = load_json(f"data/questionnaires/{qfile}")
    if data is None:
        st.error(t("error_no_json"))
        st.info(t("error_no_json_hint"))
        return
    questions = data.get("questions", {})
    if not questions:
        st.error(t("error_invalid_structure"))
        return
    cats = {}
    for qid, qdata in questions.items():
        cat = qdata.get("category", "その他")
        cats.setdefault(cat, []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    t1, t2, t3, t4 = st.tabs([t("assess_tab1"), t("assess_tab2"), t("assess_tab3"), t("assess_tab4")])
    with t1:
        st.subheader(t("assess_total_items", count=len(questions)))
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button(t("assess_select_all"), use_container_width=True):
            for qid in questions: st.session_state[f"q_{qid}"] = True
            st.rerun()
        if cb.button(t("assess_clear_all"), use_container_width=True):
            for qid in questions: st.session_state[f"q_{qid}"] = False
            st.rerun()
        st.divider()
        answers = {}
        for cat_name in cat_order:
            qlist = cats.get(cat_name, [])
            if not qlist: continue
            st.markdown(f"### {cat_name} {t('assess_category_count', count=len(qlist))}")
            cols = st.columns(2)
            for i, qdata in enumerate(qlist):
                qid = qdata["id"]
                question_text = qdata["question"]
                key = f"q_{qid}"
                with cols[i % 2]:
                    val = st.checkbox(question_text, value=st.session_state.get(key, False), key=key)
                    answers[question_text] = val
            st.divider()
        if st.button(t("assess_run"), type="primary", use_container_width=True):
            with st.spinner(t("assess_spinner")):
                result = FullPipeline(language=language).run(answers)
                st.session_state.result = result
            st.success(t("assess_complete"))
    with t2:
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
                fig = go.Figure(data=go.Scatterpolar(r=vl, theta=cl, fill='toself',
                    line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**{t('assess_overall')}: {result.phenotype.overall_status}**")
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3 = st.columns([3, 1, 1])
                x1.write(f"**{d.get('name', pid.value)}**")
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
            st.subheader("⚠️ 疾病リスク評価")
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
        st.subheader(t("metabolic_all_substrates"))
        st.write(", ".join(subs))

def probiotics():
    st.title(t("probiotics_title"))
    lang = Language.JA if st.session_state.lang == "ja" else Language.EN
    for sid, d in META_STRAIN_DEFINITIONS.get(lang, {}).items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(f"機能: {d['functional_unit']} | 菌種: {d['key_species']} | 生成物: {d['produces']}")

def kampo():
    st.title(t("kampo_title"))
    kampo_data = load_json("data/kampo/kampo_metabolic_library.json")
    if kampo_data and isinstance(kampo_data, list):
        st.subheader(t("kampo_subtitle", count=len(kampo_data)))
        search = st.text_input(t("kampo_search"), key="kampo_search")
        filtered = kampo_data
        if search:
            filtered = [k for k in kampo_data if search.lower() in str(k).lower()]
        st.write(t("kampo_display_count", filtered=len(filtered), total=len(kampo_data)))
        for item in filtered[:20]:
            with st.expander(f"💊 {item.get('name', item.get('formula_name', '不明'))}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(t("kampo_overflow", total=len(filtered)))
    elif kampo_data:
        st.json(kampo_data)
    else:
        st.warning(t("error_no_json"))
    st.divider()
    st.subheader(t("kampo_animal"))
    animal_data = load_json("data/kampo/animal_metabolic_library.json")
    if animal_data and isinstance(animal_data, list):
        st.write(t("kampo_animal_count", count=len(animal_data)))
        for item in animal_data:
            with st.expander(f"🦌 {item.get('name_ja', item.get('name', '不明'))}"):
                st.json(item)
    elif animal_data:
        st.json(animal_data)
    else:
        st.info(t("error_no_json"))

def disease():
    st.title(t("disease_title"))
    disease_data = load_json("data/diseases/disease_matrix_137.json")
    if disease_data and isinstance(disease_data, list):
        st.subheader(t("disease_subtitle", count=len(disease_data)))
        search = st.text_input(t("disease_search"), key="disease_search")
        filtered = disease_data
        if search:
            filtered = [d for d in disease_data if search.lower() in str(d).lower()]
        st.write(t("disease_display_count", filtered=len(filtered), total=len(disease_data)))
        for item in filtered[:20]:
            with st.expander(f"⚠️ {item.get('name', item.get('disease_name', '不明'))}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(t("disease_overflow", total=len(filtered)))
    elif disease_data:
        st.json(disease_data)
    else:
        st.warning(t("error_no_json"))
    if st.session_state.result and st.session_state.result.disease_risks:
        st.divider()
        st.subheader(t("disease_personal"))
        for d, r in st.session_state.result.disease_risks.items():
            st.metric(label=d, value=f"{r:.1f}%")

def sim():
    st.title(t("sim_title"))
    st.markdown(t("sim_cascade_table"))
    st.latex(r"\frac{dH_2}{dt} \approx 0")

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
    pages = {HOME: home, ASSESS: assessment, METABOLIC: metabolic, PROBIOTICS: probiotics,
             KAMPO: kampo, DISEASE: disease, SIM: sim, REPORTS: reports}
    pages.get(current_page, home)()

if __name__ == "__main__":
    main()
