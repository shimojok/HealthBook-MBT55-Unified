"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v10.1 — バグ修正版
"""
import streamlit as st
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── 外部モジュールを安全にインポート ──
try:
    from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
    from src.integration.full_pipeline import FullPipeline
    from src.layer2_metabolism.pathway_database import get_pathway_database
    MODULES_LOADED = True
except ImportError as _e:
    MODULES_LOADED = False
    _IMPORT_ERROR = str(_e)
    # ダミー定義（UI表示のみ）
    class Language:
        JA = "ja"
        EN = "en"
    PATH_DEFINITIONS = {}
    META_STRAIN_DEFINITIONS = {}
    def get_pathway_database(): return None
    class FullPipeline:
        def __init__(self, **kwargs): pass
        def run(self, answers): return None

st.set_page_config(page_title="HealthBook-MBT55 Unified", page_icon="🏥", layout="wide")

# ── ページID ──
HOME      = "home"
ASSESS    = "health_assessment"
METABOLIC = "metabolic_analysis"
PROBIOTICS = "probiotics"
KAMPO     = "kampo_library"
DISEASE   = "disease_risk"
SIM       = "simulation"
REPORTS   = "reports"

MENU = {
    "ja": [
        ("🏠 ホーム",            HOME),
        ("📋 健康アセスメント",   ASSESS),
        ("🧬 代謝解析",          METABOLIC),
        ("🦠 プロバイオティクス", PROBIOTICS),
        ("💊 漢方ライブラリー",   KAMPO),
        ("⚠️ 疾病リスク",        DISEASE),
        ("🔬 シミュレーション",   SIM),
        ("📄 レポート",          REPORTS),
    ],
    "en": [
        ("🏠 Home",              HOME),
        ("📋 Health Assessment", ASSESS),
        ("🧬 Metabolic Analysis",METABOLIC),
        ("🦠 Probiotics",        PROBIOTICS),
        ("💊 Kampo Library",     KAMPO),
        ("⚠️ Disease Risk",      DISEASE),
        ("🔬 Simulation",        SIM),
        ("📄 Reports",           REPORTS),
    ],
}

TXT = {
    "ja": {
        "home_title":      "🏥 HealthBook-MBT55 Unified",
        "home_desc":       "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。\n\n200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、\n最適な漢方・生薬・MBT55菌株セットを提案します。",
        "home_btn":        "🔴 健康アセスメントを開始する（200項目問診）",
        "assess_title":    "📋 健康アセスメント",
        "assess_desc":     "以下の200項目の問診に回答してください。",
        "assess_select_all": "✅ すべて選択",
        "assess_clear_all":  "🔄 すべて解除",
        "assess_run":      "🔍 解析を実行する",
        "assess_complete": "✅ 解析が完了しました！",
        "assess_no_data":  "「解析を実行する」ボタンを押すと、ここに結果が表示されます。",
        "error_no_json":   "⚠️ データファイルが見つかりません。",
        "metabolic_title": "🧬 代謝解析",
        "probiotics_title":"🦠 プロバイオティクス",
        "kampo_title":     "💊 漢方ライブラリー",
        "kampo_animal":    "🦌 動物性生薬ライブラリー",
        "disease_title":   "⚠️ 疾病リスク",
        "disease_personal":"🔍 あなたの疾病リスク評価",
        "sim_title":       "🔬 シミュレーション",
        "reports_title":   "📄 レポート",
        "reports_no_data": "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title":      "🏥 HealthBook-MBT55 Unified",
        "home_desc":       "Next-generation healthcare platform integrating **full metabolic pathway analysis**,\n**phenotyping**, and **MBT Probiotics screening**.",
        "home_btn":        "🔴 Start Health Assessment (200-Item Questionnaire)",
        "assess_title":    "📋 Health Assessment",
        "assess_desc":     "Answer the 200-item questionnaire below.",
        "assess_select_all": "✅ Select All",
        "assess_clear_all":  "🔄 Clear All",
        "assess_run":      "🔍 Run Analysis",
        "assess_complete": "✅ Analysis complete!",
        "assess_no_data":  "Click 'Run Analysis' to see results here.",
        "error_no_json":   "⚠️ Data file not found.",
        "metabolic_title": "🧬 Metabolic Analysis",
        "probiotics_title":"🦠 Probiotics",
        "kampo_title":     "💊 Kampo Library",
        "kampo_animal":    "🦌 Animal-Derived Library",
        "disease_title":   "⚠️ Disease Risk",
        "disease_personal":"🔍 Your Disease Risk Assessment",
        "sim_title":       "🔬 Simulation",
        "reports_title":   "📄 Reports",
        "reports_no_data": "Please run the Health Assessment first.",
    },
}

# ── 翻訳ヘルパー（"t" は assessment() 内のタブ変数と衝突しないよう tx に統一）──
def tx(key):
    return TXT[st.session_state.get("lang", "ja")].get(key, key)

@st.cache_data
def load_json(filename):
    for base in [
        Path(__file__).parent.parent,
        Path("."),
        Path("/mount/src/healthbook-mbt55-unified"),
    ]:
        p = base / filename
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

def init():
    defaults = {
        "lang":       "ja",
        "navigation": HOME,
        "result":     None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def navigate_to(page):
    """ページ遷移。呼び出し後は必ず st.rerun() する。"""
    st.session_state.navigation = page
    st.rerun()

def sidebar():
    lang = st.session_state.lang
    menu = MENU[lang]
    labels = [m[0] for m in menu]
    ids    = [m[1] for m in menu]

    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")

        # ── 言語切替 ──
        # key を "lang" と別にして session_state の直接書き換えを避ける
        new_lang = st.selectbox(
            "🌐 言語 / Language",
            ["ja", "en"],
            index=0 if lang == "ja" else 1,
            format_func=lambda x: "日本語" if x == "ja" else "English",
            key="lang_select",
        )
        if new_lang != lang:
            st.session_state.lang = new_lang
            st.rerun()

        st.divider()

        # ── ナビゲーション ──
        try:
            current_idx = ids.index(st.session_state.navigation)
        except ValueError:
            current_idx = 0

        selected_label = st.radio(
            "メニュー",
            labels,
            index=current_idx,
            label_visibility="collapsed",
            key="nav_radio",          # "nav" → "nav_radio" に変更（競合回避）
        )
        new_page = ids[labels.index(selected_label)]
        if new_page != st.session_state.navigation:
            navigate_to(new_page)     # 内部で st.rerun() を呼ぶ

def page_home():
    st.title(tx("home_title"))
    st.markdown(tx("home_desc"))

    if not MODULES_LOADED:
        st.error(f"⚠️ モジュールのロードに失敗しました: {_IMPORT_ERROR}")
        st.info("src/ ディレクトリが正しく配置されているか確認してください。")

    c1, c2, c3 = st.columns(3)
    c1.metric("代謝経路 / Pathways",    "20+")
    c2.metric("MBT55メタ株 / Strains",   "5")
    c3.metric("疾病マトリックス / Diseases", "137")
    st.divider()
    st.subheader("🚀 クイックスタート")
    if st.button(tx("home_btn"), type="primary", use_container_width=True, key="start_btn"):
        navigate_to(ASSESS)

def page_assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN
    st.title(tx("assess_title"))
    st.markdown(tx("assess_desc"))

    qfile = "questionnaire_200_jp.json" if st.session_state.lang == "ja" else "questionnaire_200_en.json"
    data = load_json(f"data/questionnaires/{qfile}")
    if data is None:
        st.error(tx("error_no_json"))
        st.info(f"data/questionnaires/{qfile} を配置してください。")
        return

    questions = data.get("questions", {})
    if not questions:
        st.error("問診データの構造が不正です。")
        return

    cats = {}
    for qid, qdata in questions.items():
        cat = qdata.get("category", "その他")
        cats.setdefault(cat, []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    # ── タブ変数を tab1〜tab4 に変更（グローバル tx() との名前衝突を排除）──
    tab1, tab2, tab3, tab4 = st.tabs(["📝 問診入力", "📊 結果", "🦠 菌株推奨", "⚠️ 疾病リスク"])

    with tab1:
        st.subheader(f"全{len(questions)}項目健康問診")
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button(tx("assess_select_all"), use_container_width=True, key="select_all_btn"):
            for qid in questions:
                st.session_state[f"q_{qid}"] = True
            st.rerun()
        if cb.button(tx("assess_clear_all"), use_container_width=True, key="clear_all_btn"):
            for qid in questions:
                st.session_state[f"q_{qid}"] = False
            st.rerun()
        st.divider()

        answers = {}
        for cat_name in cat_order:
            qlist = cats.get(cat_name, [])
            if not qlist:
                continue
            st.markdown(f"### {cat_name}（{len(qlist)}項目）")
            cols = st.columns(2)
            for i, qdata in enumerate(qlist):
                qid   = qdata["id"]
                qtext = qdata["question"]
                key   = f"q_{qid}"
                with cols[i % 2]:
                    val = st.checkbox(qtext, value=st.session_state.get(key, False), key=key)
                    answers[qtext] = val
            st.divider()

        if st.button(tx("assess_run"), type="primary", use_container_width=True, key="run_btn"):
            if not MODULES_LOADED:
                st.error(f"解析モジュールが読み込めていません: {_IMPORT_ERROR}")
            else:
                with st.spinner("MBT55代謝経路を解析中..."):
                    result = FullPipeline(language=language).run(answers)
                    st.session_state.result = result
                st.success(tx("assess_complete"))

    with tab2:
        result = st.session_state.result
        if result and result.phenotype and result.phenotype.scores:
            path_defs = PATH_DEFINITIONS.get(language, {})
            st.subheader("📊 PATH_01〜05 代謝経路活性スコア")
            import plotly.graph_objects as go_plotly
            cl, vl = [], []
            for pid, ps in result.phenotype.scores.items():
                pd_info = path_defs.get(pid, {})
                cl.append(pd_info.get("short", pid.value))
                vl.append(ps.score)
            if cl:
                fig = go_plotly.Figure(data=go_plotly.Scatterpolar(
                    r=vl, theta=cl, fill='toself',
                    line=dict(color='#00B4D8', width=2),
                    fillcolor='rgba(0,180,216,0.25)',
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(range=[0, 100])),
                    showlegend=False, height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**総合判定: {result.phenotype.overall_status}**")
            for pid, ps in result.phenotype.scores.items():
                pd_info = path_defs.get(pid, {})
                x1, x2, x3 = st.columns([3, 1, 1])
                x1.write(f"**{pd_info.get('name', pid.value)}**")
                x2.metric("Score", f"{ps.score:.0f}%")
                color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(
                    f"<span style='color:{color};font-weight:bold'>{ps.level}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info(tx("assess_no_data"))

    with tab3:
        result = st.session_state.result
        if result and result.probiotic_screening and result.probiotic_screening.recommended_strains:
            st.subheader("🦠 推奨MBT55メタ株")
            for strain in result.probiotic_screening.recommended_strains:
                st.markdown(f"### P{strain.priority}: {strain.name}")
                st.write(strain.reason)
                st.divider()
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for e in result.expected_effects:
                    st.markdown(f"✅ {e}")
        else:
            st.info(tx("assess_no_data"))

    with tab4:
        result = st.session_state.result
        if result and result.disease_risks:
            st.subheader("⚠️ 疾病リスク評価")
            for disease_name, risk_val in result.disease_risks.items():
                st.metric(label=disease_name, value=f"{risk_val:.1f}%")
        else:
            st.info(tx("assess_no_data"))

def page_metabolic():
    st.title(tx("metabolic_title"))
    if not MODULES_LOADED:
        st.error("代謝解析モジュールが読み込めていません。")
        return
    db = get_pathway_database()
    if db is None:
        st.warning("代謝経路データベースを取得できませんでした。")
        return
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox("🔍 基質を選択", subs)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                    st.write(f"効果: {', '.join(p['human_effects'])}")
                    st.divider()
        st.subheader("📋 全登録基質")
        st.write(", ".join(subs))

def page_probiotics():
    st.title(tx("probiotics_title"))
    lang = Language.JA if st.session_state.lang == "ja" else Language.EN
    strain_defs = META_STRAIN_DEFINITIONS.get(lang, {})
    if not strain_defs:
        st.info("プロバイオティクスデータがありません。")
        return
    for sid, strain_info in strain_defs.items():
        with st.expander(f"🔹 {strain_info['name']}"):
            st.write(
                f"機能: {strain_info['functional_unit']} | "
                f"菌種: {strain_info['key_species']} | "
                f"生成物: {strain_info['produces']}"
            )

def page_kampo():
    st.title(tx("kampo_title"))

    kampo_data = load_json("data/kampo/kampo_metabolic_library.json")
    if kampo_data:
        if isinstance(kampo_data, list):
            st.subheader(f"📚 漢方処方ライブラリー（{len(kampo_data)}処方）")
            search = st.text_input("🔍 処方名・生薬で検索", key="kampo_search")
            filtered = kampo_data
            if search:
                filtered = [k for k in kampo_data if search.lower() in str(k).lower()]
            st.write(f"表示: {len(filtered)} / {len(kampo_data)} 処方")
            for item in filtered[:20]:
                name = item.get("name", item.get("formula_name", "不明"))
                with st.expander(f"💊 {name}"):
                    st.json(item)
            if len(filtered) > 20:
                st.info(f"上位20件を表示中。検索で絞り込んでください。（全{len(filtered)}件）")
        else:
            st.json(kampo_data)
    else:
        st.warning("漢方ライブラリーデータがありません。data/kampo/kampo_metabolic_library.json を配置してください。")

    st.divider()

    st.subheader(tx("kampo_animal"))
    animal_data = load_json("data/kampo/animal_metabolic_library.json")
    if animal_data:
        if isinstance(animal_data, list):
            st.write(f"**{len(animal_data)}件**の動物性生薬")
            for item in animal_data:
                name = item.get("name_ja", item.get("name", "不明"))
                with st.expander(f"🦌 {name}"):
                    st.json(item)
        else:
            st.json(animal_data)
    else:
        st.info("動物性生薬データがありません。data/kampo/animal_metabolic_library.json を配置してください。")

def page_disease():
    st.title(tx("disease_title"))

    disease_data = load_json("data/diseases/disease_matrix_137.json")
    if disease_data:
        if isinstance(disease_data, list):
            st.subheader(f"📊 137疾病マトリックス（{len(disease_data)}疾病）")
            search = st.text_input("🔍 疾病名・コードで検索", key="disease_search")
            filtered = disease_data
            if search:
                filtered = [item for item in disease_data if search.lower() in str(item).lower()]
            st.write(f"表示: {len(filtered)} / {len(disease_data)} 疾病")
            for item in filtered[:20]:
                name = item.get("name", item.get("disease_name", "不明"))
                with st.expander(f"⚠️ {name}"):
                    st.json(item)
            if len(filtered) > 20:
                st.info(f"上位20件を表示中。検索で絞り込んでください。（全{len(filtered)}件）")
        else:
            st.json(disease_data)
    else:
        st.warning("疾病マトリックスデータがありません。data/diseases/disease_matrix_137.json を配置してください。")

    if st.session_state.result and st.session_state.result.disease_risks:
        st.divider()
        st.subheader(tx("disease_personal"))
        for disease_name, risk_val in st.session_state.result.disease_risks.items():
            st.metric(label=disease_name, value=f"{risk_val:.1f}%")

def page_sim():
    st.title(tx("sim_title"))
    st.markdown(
        "### 3段階酵素カスケード\n"
        "| Stage | 時間 | 温度 | 酸素 |\n"
        "|-------|------|------|------|\n"
        "| 1 | 0-6h | 38°C | 好気 |\n"
        "| 2 | 6-24h | 42°C | 微好気 |\n"
        "| 3 | 24-72h | 35°C | 嫌気 |"
    )
    st.latex(r"\frac{dH_2}{dt} \approx 0")

def page_reports():
    st.title(tx("reports_title"))
    result = st.session_state.result
    if result:
        st.download_button(
            "📥 JSONダウンロード",
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            "report.json",
            "application/json",
        )
        st.text(result.format_for_display())
    else:
        st.info(tx("reports_no_data"))

def main():
    init()
    sidebar()

    pages = {
        HOME:       page_home,
        ASSESS:     page_assessment,
        METABOLIC:  page_metabolic,
        PROBIOTICS: page_probiotics,
        KAMPO:      page_kampo,
        DISEASE:    page_disease,
        SIM:        page_sim,
        REPORTS:    page_reports,
    }
    pages.get(st.session_state.navigation, page_home)()

if __name__ == "__main__":
    main()
