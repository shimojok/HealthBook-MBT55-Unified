"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v12.0 — フォーム/タブ構造バグ・ファイルパス・結果反映 完全修正版
"""
import streamlit as st
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── 外部モジュールを安全にインポート ──────────────────────────
try:
    from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
    from src.integration.full_pipeline import FullPipeline
    from src.layer2_metabolism.pathway_database import get_pathway_database
    MODULES_LOADED = True
    _IMPORT_ERROR = ""
except ImportError as _e:
    MODULES_LOADED = False
    _IMPORT_ERROR = str(_e)
    class Language:
        JA = "ja"; EN = "en"
    PATH_DEFINITIONS = {}
    META_STRAIN_DEFINITIONS = {}
    def get_pathway_database(): return None
    class FullPipeline:
        def __init__(self, **kw): pass
        def run(self, a): return None

st.set_page_config(page_title="HealthBook-MBT55 Unified", page_icon="🏥", layout="wide")

# ── ページID ───────────────────────────────────────────────────
HOME       = "home"
ASSESS     = "health_assessment"
METABOLIC  = "metabolic_analysis"
PROBIOTICS = "probiotics"
KAMPO      = "kampo_library"
DISEASE    = "disease_risk"
SIM        = "simulation"
REPORTS    = "reports"

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
        "home_title":              "🏥 HealthBook-MBT55 Unified",
        "home_desc":               "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。\n\n200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、\n最適な漢方・生薬・MBT55菌株セットを提案します。",
        "home_btn":                "🔴 健康アセスメントを開始する（200項目問診）",
        "home_pathways_metric":    "代謝経路",
        "home_strains_metric":     "MBT55メタ株",
        "home_diseases_metric":    "疾病マトリックス",
        "home_quickstart":         "🚀 クイックスタート",
        "assess_title":            "📋 健康アセスメント",
        "assess_desc":             "該当する症状をカテゴリごとに選択し、最後に「解析を実行する」を押してください。",
        "assess_run":              "🔍 解析を実行する",
        "assess_complete":         "✅ 解析が完了しました！上の「結果」タブをご確認ください。",
        "assess_no_data":          "問診に回答し「解析を実行する」ボタンを押してください。",
        "assess_tab1":             "📝 問診入力",
        "assess_tab2":             "📊 結果",
        "assess_tab3":             "🦠 菌株推奨",
        "assess_tab4":             "⚠️ 疾病リスク",
        "assess_total_items":      "全{count}項目健康問診",
        "assess_category_count":   "（{count}項目）",
        "assess_select_all":       "✅ すべて選択",
        "assess_clear_all":        "🔄 すべて解除",
        "assess_spinner":          "MBT55代謝経路を解析中...",
        "assess_overall":          "総合判定",
        "assess_results_summary":  "📊 解析結果サマリー",
        "assess_strains_title":    "🦠 推奨MBT55メタ株",
        "assess_effects_title":    "✨ 期待効果",
        "assess_disease_tab":      "⚠️ 疾病リスク評価",
        "error_no_json":           "⚠️ データファイルが見つかりません。",
        "error_invalid_structure": "データ構造が不正です。",
        "module_error":            "⚠️ モジュールのロードに失敗しました",
        "module_error_hint":       "src/ ディレクトリが正しく配置されているか確認してください。",
        "metabolic_title":         "🧬 代謝解析",
        "metabolic_select":        "🔍 基質を選択",
        "metabolic_effect":        "効果",
        "metabolic_all":           "📋 全登録基質",
        "metabolic_no_module":     "代謝解析モジュールが読み込めていません。",
        "metabolic_no_db":         "代謝経路データベースを取得できませんでした。",
        "probiotics_title":        "🦠 プロバイオティクス",
        "probiotics_no_data":      "プロバイオティクスデータがありません。",
        "probiotics_func":         "機能",
        "probiotics_species":      "菌種",
        "probiotics_produces":     "生成物",
        "kampo_title":             "💊 漢方ライブラリー",
        "kampo_subtitle":          "📚 漢方処方ライブラリー（{count}処方）",
        "kampo_search":            "🔍 処方名・生薬で検索",
        "kampo_display_count":     "表示: {filtered} / {total} 処方",
        "kampo_truncated":         "上位20件を表示中。検索で絞り込んでください。（全{total}件）",
        "kampo_no_data":           "漢方ライブラリーデータがありません。",
        "kampo_animal":            "🦌 動物性生薬ライブラリー",
        "kampo_animal_no_data":    "動物性生薬データがありません。",
        "kampo_unknown":           "不明",
        "disease_title":           "⚠️ 疾病リスク",
        "disease_subtitle":        "📊 137疾病マトリックス（{count}疾病）",
        "disease_search":          "🔍 疾病名・コードで検索",
        "disease_display_count":   "表示: {filtered} / {total} 疾病",
        "disease_truncated":       "上位20件を表示中。検索で絞り込んでください。（全{total}件）",
        "disease_no_data":         "疾病マトリックスデータがありません。",
        "disease_personal":        "🔍 あなたの疾病リスク評価",
        "disease_unknown":         "不明",
        "sim_title":               "🔬 シミュレーション",
        "sim_cascade":             "### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |",
        "reports_title":           "📄 レポート",
        "reports_download_btn":    "📥 JSONダウンロード",
        "reports_summary":         "📊 統合解析サマリー",
        "reports_no_data":         "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title":              "🏥 HealthBook-MBT55 Unified",
        "home_desc":               "Next-generation healthcare platform integrating **full metabolic pathway analysis**, **phenotyping**, and **MBT Probiotics screening**.\n\nEvaluates metabolic pathway activity (PATH_01–05) from a 200-item questionnaire and recommends optimal Kampo, herbs, and MBT55 strain sets.",
        "home_btn":                "🔴 Start Health Assessment (200-Item Questionnaire)",
        "home_pathways_metric":    "Pathways",
        "home_strains_metric":     "MBT55 Meta-Strains",
        "home_diseases_metric":    "Disease Matrix",
        "home_quickstart":         "🚀 Quick Start",
        "assess_title":            "📋 Health Assessment",
        "assess_desc":             "Select your symptoms by category, then click 'Run Analysis'.",
        "assess_run":              "🔍 Run Analysis",
        "assess_complete":         "✅ Analysis complete! Check the 'Results' tab above.",
        "assess_no_data":          "Please complete the questionnaire and click 'Run Analysis'.",
        "assess_tab1":             "📝 Questionnaire",
        "assess_tab2":             "📊 Results",
        "assess_tab3":             "🦠 Strains",
        "assess_tab4":             "⚠️ Disease Risk",
        "assess_total_items":      "Total {count} Health Questions",
        "assess_category_count":   "({count} items)",
        "assess_select_all":       "✅ Select All",
        "assess_clear_all":        "🔄 Clear All",
        "assess_spinner":          "Analyzing MBT55 metabolic pathways...",
        "assess_overall":          "Overall Assessment",
        "assess_results_summary":  "📊 Analysis Summary",
        "assess_strains_title":    "🦠 Recommended MBT55 Meta-Strains",
        "assess_effects_title":    "✨ Expected Effects",
        "assess_disease_tab":      "⚠️ Disease Risk Assessment",
        "error_no_json":           "⚠️ Data file not found.",
        "error_invalid_structure": "Invalid data structure.",
        "module_error":            "⚠️ Failed to load modules",
        "module_error_hint":       "Please check that the src/ directory is correctly placed.",
        "metabolic_title":         "🧬 Metabolic Analysis",
        "metabolic_select":        "🔍 Select Substrate",
        "metabolic_effect":        "Effects",
        "metabolic_all":           "📋 All Registered Substrates",
        "metabolic_no_module":     "Metabolic analysis module could not be loaded.",
        "metabolic_no_db":         "Could not retrieve the metabolic pathway database.",
        "probiotics_title":        "🦠 Probiotics",
        "probiotics_no_data":      "No probiotics data available.",
        "probiotics_func":         "Function",
        "probiotics_species":      "Species",
        "probiotics_produces":     "Produces",
        "kampo_title":             "💊 Kampo Library",
        "kampo_subtitle":          "📚 Kampo Formula Library ({count} formulas)",
        "kampo_search":            "🔍 Search by formula or herb name",
        "kampo_display_count":     "Showing: {filtered} / {total} formulas",
        "kampo_truncated":         "Showing top 20. Refine with search. (Total: {total})",
        "kampo_no_data":           "No Kampo library data available.",
        "kampo_animal":            "🦌 Animal-Derived Herb Library",
        "kampo_animal_no_data":    "No animal-derived herb data available.",
        "kampo_unknown":           "Unknown",
        "disease_title":           "⚠️ Disease Risk",
        "disease_subtitle":        "📊 137 Disease Matrix ({count} diseases)",
        "disease_search":          "🔍 Search by disease name or code",
        "disease_display_count":   "Showing: {filtered} / {total} diseases",
        "disease_truncated":       "Showing top 20. Refine with search. (Total: {total})",
        "disease_no_data":         "No disease matrix data available.",
        "disease_personal":        "🔍 Your Disease Risk Assessment",
        "disease_unknown":         "Unknown",
        "sim_title":               "🔬 Simulation",
        "sim_cascade":             "### 3-Stage Enzyme Cascade\n| Stage | Time | Temp | Oxygen |\n|-------|------|------|--------|\n| 1 | 0-6h | 38°C | Aerobic |\n| 2 | 6-24h | 42°C | Micro-aerobic |\n| 3 | 24-72h | 35°C | Anaerobic |",
        "reports_title":           "📄 Reports",
        "reports_download_btn":    "📥 Download JSON",
        "reports_summary":         "📊 Integrated Analysis Summary",
        "reports_no_data":         "Please run the Health Assessment first.",
    },
}

def t(key: str, **kwargs) -> str:
    text = TXT.get(st.session_state.get("lang", "ja"), TXT["ja"]).get(key, key)
    if kwargs:
        try: return text.format(**kwargs)
        except (KeyError, ValueError): return text
    return text

# ── JSONファイル名の候補（READMEとコード両方の命名に対応）──────
_QFILE_CANDIDATES = {
    "ja": ["questionnaire_200_jp.json", "healthbook_200_ja.json",
           "questionnaire_200_ja.json", "healthbook_200_jp.json"],
    "en": ["questionnaire_200_en.json", "healthbook_200_en.json"],
}

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

def load_questionnaire(lang: str):
    """複数の候補ファイル名を順に試してデータを返す。"""
    for fname in _QFILE_CANDIDATES.get(lang, []):
        data = load_json(f"data/questionnaires/{fname}")
        if data is not None:
            return data
    return None

def init():
    defaults = {"lang": "ja", "navigation": HOME, "result": None, "answers": {}}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def start_assessment():
    st.session_state.navigation = ASSESS

def sidebar():
    menu   = MENU[st.session_state.lang]
    labels = [m[0] for m in menu]
    ids    = [m[1] for m in menu]
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        lang = st.selectbox(
            "🌐 言語 / Language", ["ja", "en"],
            index=0 if st.session_state.lang == "ja" else 1,
            format_func=lambda x: "日本語" if x == "ja" else "English",
            key="lang_select",
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
        st.divider()
        try: idx = ids.index(st.session_state.navigation)
        except ValueError: idx = 0
        sel = st.radio("Menu", labels, index=idx, label_visibility="collapsed", key="nav_radio")
        new_page = ids[labels.index(sel)]
        if new_page != st.session_state.navigation:
            st.session_state.navigation = new_page
            st.rerun()

# ── ホーム ────────────────────────────────────────────────────
def home():
    st.title(t("home_title"))
    st.markdown(t("home_desc"))
    if not MODULES_LOADED:
        st.error(f"{t('module_error')}: {_IMPORT_ERROR}")
        st.info(t("module_error_hint"))
    c1, c2, c3 = st.columns(3)
    c1.metric(t("home_pathways_metric"), "20+")
    c2.metric(t("home_strains_metric"),  "5")
    c3.metric(t("home_diseases_metric"), "137")
    st.divider()
    st.subheader(t("home_quickstart"))
    st.button(t("home_btn"), type="primary", use_container_width=True,
              key="start_btn", on_click=start_assessment)

# ── アセスメント ───────────────────────────────────────────────
def assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN
    st.title(t("assess_title"))
    st.markdown(t("assess_desc"))

    # ── データ読み込み（複数ファイル名候補に対応）──
    data = load_questionnaire(st.session_state.lang)
    if data is None:
        st.error(t("error_no_json"))
        st.info("Searched: " + ", ".join(
            f"data/questionnaires/{f}" for f in _QFILE_CANDIDATES[st.session_state.lang]
        ))
        return

    questions = data.get("questions", {})
    if not questions:
        st.error(t("error_invalid_structure"))
        return

    cats = {}
    for qid, qdata in questions.items():
        cat = qdata.get("category", "その他" if st.session_state.lang == "ja" else "Other")
        cats.setdefault(cat, []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    # ════════════════════════════════════════════════════════════
    # ★ 修正の核心:
    #   st.form を廃止し、session_state で個別回答を保持する。
    #   タブを先に定義し、tab1（問診）と tab2〜4（結果）を完全に分離。
    #   ボタン押下 → session_state.result を更新 → st.rerun() で
    #   全タブが同一スクリプト実行内で最新の result を参照できる。
    # ════════════════════════════════════════════════════════════

    tab1, tab2, tab3, tab4 = st.tabs([
        t("assess_tab1"), t("assess_tab2"), t("assess_tab3"), t("assess_tab4")
    ])

    # ── tab1: 問診入力 ────────────────────────────────────────
    with tab1:
        st.write(t("assess_total_items", count=len(questions)))

        # 一括操作ボタン
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button(t("assess_select_all"), use_container_width=True, key="sel_all"):
            for qid in questions:
                st.session_state[f"ans_{qid}"] = True
            st.rerun()
        if cb.button(t("assess_clear_all"), use_container_width=True, key="clr_all"):
            for qid in questions:
                st.session_state[f"ans_{qid}"] = False
            st.rerun()

        st.divider()

        # チェックボックス（expanded=True で確実に全項目を描画・値取得）
        for cat_name in cat_order:
            qlist = cats.get(cat_name, [])
            if not qlist:
                continue
            with st.expander(
                f"■ {cat_name} {t('assess_category_count', count=len(qlist))}",
                expanded=True,  # ★ False だと未展開カテゴリの値が取れないため True 固定
            ):
                cols = st.columns(2)
                for i, q in enumerate(qlist):
                    key = f"ans_{q['id']}"
                    with cols[i % 2]:
                        st.checkbox(
                            q["question"],
                            key=key,
                            value=st.session_state.get(key, False),
                        )

        st.divider()

        # ── 解析ボタン（st.form の外に配置）──────────────────
        if st.button(t("assess_run"), type="primary", use_container_width=True, key="run_btn"):
            if not MODULES_LOADED:
                st.error(f"{t('module_error')}: {_IMPORT_ERROR}")
            else:
                # ★ session_state から全回答を収集
                answers = {
                    qdata["question"]: st.session_state.get(f"ans_{qid}", False)
                    for qid, qdata in questions.items()
                }
                with st.spinner(t("assess_spinner")):
                    try:
                        result = FullPipeline(language=language).run(answers)
                        st.session_state.result  = result
                        st.session_state.answers = answers
                        st.success(t("assess_complete"))
                        # ★ rerun して全タブに結果を反映
                        st.rerun()
                    except Exception as e:
                        st.error(f"Execution Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())

    # ── tab2: 結果（PATHスコア）─────────────────────────────
    with tab2:
        result = st.session_state.result
        if result and result.phenotype and result.phenotype.scores:
            path_defs = PATH_DEFINITIONS.get(language, {})
            st.subheader(t("assess_results_summary"))
            try:
                import plotly.graph_objects as go
                cl, vl = [], []
                for pid, ps in result.phenotype.scores.items():
                    pd_info = path_defs.get(pid, {})
                    label = pd_info.get("short",
                        str(pid.value) if hasattr(pid, "value") else str(pid))
                    cl.append(label)
                    vl.append(ps.score)
                if cl:
                    fig = go.Figure(data=go.Scatterpolar(
                        r=vl, theta=cl, fill="toself",
                        line=dict(color="#00B4D8", width=2),
                        fillcolor="rgba(0,180,216,0.25)",
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(range=[0, 100])),
                        showlegend=False, height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as chart_err:
                st.warning(f"Chart error: {chart_err}")

            st.markdown(f"**{t('assess_overall')}: {result.phenotype.overall_status}**")
            st.divider()
            for pid, ps in result.phenotype.scores.items():
                pd_info = path_defs.get(pid, {})
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{pd_info.get('name', str(pid))}**\n*{pd_info.get('desc', '')}*")
                c2.metric("Score", f"{ps.score:.0f}%")
                color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                c3.markdown(
                    f"<span style='color:{color};font-weight:bold'>{ps.level}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info(t("assess_no_data"))

    # ── tab3: 菌株推奨 ────────────────────────────────────────
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
                for e in result.expected_effects:
                    st.markdown(f"✅ {e}")
        else:
            st.info(t("assess_no_data"))

    # ── tab4: 疾病リスク ──────────────────────────────────────
    with tab4:
        result = st.session_state.result
        if result and result.disease_risks:
            st.subheader(t("assess_disease_tab"))
            for disease_name, risk_val in result.disease_risks.items():
                st.metric(label=disease_name, value=f"{risk_val:.1f}%")
        else:
            st.info(t("assess_no_data"))

# ── 代謝解析 ──────────────────────────────────────────────────
def metabolic():
    st.title(t("metabolic_title"))
    if not MODULES_LOADED:
        st.error(t("metabolic_no_module"))
        return
    db = get_pathway_database()
    if db is None:
        st.warning(t("metabolic_no_db"))
        return
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox(t("metabolic_select"), subs)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                    st.write(f"{t('metabolic_effect')}: {', '.join(p['human_effects'])}")
                    st.divider()
        st.subheader(t("metabolic_all"))
        st.write(", ".join(subs))

# ── プロバイオティクス ─────────────────────────────────────────
def probiotics():
    st.title(t("probiotics_title"))
    lang = Language.JA if st.session_state.lang == "ja" else Language.EN
    strain_defs = META_STRAIN_DEFINITIONS.get(lang, {})
    if not strain_defs:
        st.info(t("probiotics_no_data"))
        return
    for sid, d in strain_defs.items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(
                f"{t('probiotics_func')}: {d['functional_unit']} | "
                f"{t('probiotics_species')}: {d['key_species']} | "
                f"{t('probiotics_produces')}: {d['produces']}"
            )

# ── 漢方ライブラリー ──────────────────────────────────────────
def kampo():
    st.title(t("kampo_title"))
    kampo_data = (
        load_json("data/kampo/kampo_metabolic_library.json") or
        load_json("data/kampo/kampo_294_library.json")
    )
    if kampo_data and isinstance(kampo_data, list):
        st.subheader(t("kampo_subtitle", count=len(kampo_data)))
        search = st.text_input(t("kampo_search"), key="kampo_search_input")
        filtered = [k for k in kampo_data if search.lower() in str(k).lower()] if search else kampo_data
        st.write(t("kampo_display_count", filtered=len(filtered), total=len(kampo_data)))
        for item in filtered[:20]:
            name = item.get("name", item.get("formula_name", t("kampo_unknown")))
            with st.expander(f"💊 {name}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(t("kampo_truncated", total=len(filtered)))
    else:
        st.warning(t("kampo_no_data"))

    st.divider()
    st.subheader(t("kampo_animal"))
    animal_data = (
        load_json("data/kampo/animal_metabolic_library.json") or
        load_json("data/kampo/animal_derived_library.json")
    )
    if animal_data and isinstance(animal_data, list):
        for item in animal_data:
            name = item.get("name_ja", item.get("name", t("kampo_unknown")))
            with st.expander(f"🦌 {name}"):
                st.json(item)
    else:
        st.info(t("kampo_animal_no_data"))

# ── 疾病リスク ─────────────────────────────────────────────────
def disease():
    st.title(t("disease_title"))
    disease_data = (
        load_json("data/diseases/disease_matrix_137.json") or
        load_json("data/diseases/disease_matrix.json")
    )
    if disease_data and isinstance(disease_data, list):
        st.subheader(t("disease_subtitle", count=len(disease_data)))
        search = st.text_input(t("disease_search"), key="disease_search_input")
        filtered = [d for d in disease_data if search.lower() in str(d).lower()] if search else disease_data
        st.write(t("disease_display_count", filtered=len(filtered), total=len(disease_data)))
        for item in filtered[:20]:
            name = item.get("name", item.get("disease_name", t("disease_unknown")))
            with st.expander(f"⚠️ {name}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(t("disease_truncated", total=len(filtered)))
    else:
        st.warning(t("disease_no_data"))

    result = st.session_state.result
    if result and result.disease_risks:
        st.divider()
        st.subheader(t("disease_personal"))
        for disease_name, risk_val in result.disease_risks.items():
            st.metric(label=disease_name, value=f"{risk_val:.1f}%")

# ── シミュレーション ───────────────────────────────────────────
def sim():
    st.title(t("sim_title"))
    st.markdown(t("sim_cascade"))
    st.latex(r"\frac{dH_2}{dt} \approx 0")

# ── レポート ──────────────────────────────────────────────────
def reports():
    st.title(t("reports_title"))
    result = st.session_state.result
    if result:
        st.download_button(
            t("reports_download_btn"),
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            "report.json",
            "application/json",
        )
        st.subheader(t("reports_summary"))
        st.text(result.format_for_display())
    else:
        st.info(t("reports_no_data"))

# ── メイン ────────────────────────────────────────────────────
def main():
    init()
    sidebar()
    pages = {
        HOME:       home,
        ASSESS:     assessment,
        METABOLIC:  metabolic,
        PROBIOTICS: probiotics,
        KAMPO:      kampo,
        DISEASE:    disease,
        SIM:        sim,
        REPORTS:    reports,
    }
    pages.get(st.session_state.navigation, home)()

if __name__ == "__main__":
    main()
