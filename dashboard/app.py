"""
HealthBook-MBT55-Unified Streamlit Dashboard
v13.0 — ナビゲーション・問診結果反映 根本修正版
"""
import streamlit as st
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── 外部モジュールを安全にインポート ─────────────────────────────
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
        JA = "ja"
        EN = "en"
    PATH_DEFINITIONS = {}
    META_STRAIN_DEFINITIONS = {}
    def get_pathway_database(): return None
    class FullPipeline:
        def __init__(self, **kw): pass
        def run(self, a): return None

st.set_page_config(
    page_title="HealthBook-MBT55 Unified",
    page_icon="🏥",
    layout="wide",
)

# ── ページID定数 ──────────────────────────────────────────────────
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
        "home_title":           "🏥 HealthBook-MBT55 Unified",
        "home_desc":            "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。\n\n200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、\n最適な漢方・生薬・MBT55菌株セットを提案します。",
        "home_btn":             "🔴 健康アセスメントを開始する（200項目問診）",
        "home_pathways":        "代謝経路",
        "home_strains":         "MBT55メタ株",
        "home_diseases":        "疾病マトリックス",
        "home_quickstart":      "🚀 クイックスタート",
        "assess_title":         "📋 健康アセスメント",
        "assess_desc":          "該当する症状をカテゴリごとに選択し、最後に「解析を実行する」を押してください。",
        "assess_run":           "🔍 解析を実行する",
        "assess_complete":      "✅ 解析完了！「📊 結果」タブをクリックしてください。",
        "assess_no_data":       "問診に回答し「解析を実行する」を押してください。",
        "assess_tab1":          "📝 問診入力",
        "assess_tab2":          "📊 結果",
        "assess_tab3":          "🦠 菌株推奨",
        "assess_tab4":          "⚠️ 疾病リスク",
        "assess_items":         "全{count}項目",
        "assess_cat_count":     "（{count}項目）",
        "assess_select_all":    "✅ すべて選択",
        "assess_clear_all":     "🔄 すべて解除",
        "assess_spinner":       "MBT55代謝経路を解析中...",
        "assess_overall":       "総合判定",
        "assess_score_title":   "📊 解析結果サマリー",
        "assess_strains_title": "🦠 推奨MBT55メタ株",
        "assess_effects_title": "✨ 期待効果",
        "assess_disease_title": "⚠️ 疾病リスク評価",
        "error_no_json":        "⚠️ データファイルが見つかりません",
        "error_bad_structure":  "データ構造が不正です",
        "error_module":         "⚠️ モジュールのロードに失敗",
        "error_module_hint":    "src/ ディレクトリが正しく配置されているか確認してください。",
        "metabolic_title":      "🧬 代謝解析",
        "metabolic_select":     "🔍 基質を選択",
        "metabolic_effect":     "効果",
        "metabolic_all":        "📋 全登録基質",
        "metabolic_no_module":  "代謝解析モジュールが読み込めていません。",
        "metabolic_no_db":      "代謝経路データベースを取得できませんでした。",
        "probiotics_title":     "🦠 プロバイオティクス",
        "probiotics_no_data":   "プロバイオティクスデータがありません。",
        "probiotics_func":      "機能",
        "probiotics_species":   "菌種",
        "probiotics_produces":  "生成物",
        "kampo_title":          "💊 漢方ライブラリー",
        "kampo_subtitle":       "📚 漢方処方ライブラリー（{count}処方）",
        "kampo_search":         "🔍 処方名・生薬で検索",
        "kampo_count":          "表示: {f} / {t} 処方",
        "kampo_no_data":        "漢方ライブラリーデータがありません。",
        "kampo_unknown":        "不明",
        "kampo_animal":         "🦌 動物性生薬ライブラリー",
        "kampo_animal_no_data": "動物性生薬データがありません。",
        "disease_title":        "⚠️ 疾病リスク",
        "disease_subtitle":     "📊 137疾病マトリックス（{count}疾病）",
        "disease_search":       "🔍 疾病名・コードで検索",
        "disease_count":        "表示: {f} / {t} 疾病",
        "disease_no_data":      "疾病マトリックスデータがありません。",
        "disease_personal":     "🔍 あなたの疾病リスク評価",
        "disease_unknown":      "不明",
        "sim_title":            "🔬 シミュレーション",
        "sim_cascade":          "### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |",
        "reports_title":        "📄 レポート",
        "reports_dl":           "📥 JSONダウンロード",
        "reports_summary":      "📊 統合解析サマリー",
        "reports_no_data":      "まず「健康アセスメント」から解析を実行してください。",
    },
    "en": {
        "home_title":           "🏥 HealthBook-MBT55 Unified",
        "home_desc":            "Next-generation healthcare platform integrating **full metabolic pathway analysis**, **phenotyping**, and **MBT Probiotics screening**.\n\nEvaluates metabolic pathway activity (PATH_01–05) from a 200-item questionnaire and recommends optimal Kampo herbs and MBT55 strain sets.",
        "home_btn":             "🔴 Start Health Assessment (200-Item Questionnaire)",
        "home_pathways":        "Pathways",
        "home_strains":         "MBT55 Meta-Strains",
        "home_diseases":        "Disease Matrix",
        "home_quickstart":      "🚀 Quick Start",
        "assess_title":         "📋 Health Assessment",
        "assess_desc":          "Select your symptoms by category, then click 'Run Analysis'.",
        "assess_run":           "🔍 Run Analysis",
        "assess_complete":      "✅ Analysis complete! Click the '📊 Results' tab.",
        "assess_no_data":       "Please complete the questionnaire and click 'Run Analysis'.",
        "assess_tab1":          "📝 Questionnaire",
        "assess_tab2":          "📊 Results",
        "assess_tab3":          "🦠 Strains",
        "assess_tab4":          "⚠️ Disease Risk",
        "assess_items":         "Total {count} questions",
        "assess_cat_count":     "({count} items)",
        "assess_select_all":    "✅ Select All",
        "assess_clear_all":     "🔄 Clear All",
        "assess_spinner":       "Analyzing MBT55 metabolic pathways...",
        "assess_overall":       "Overall Assessment",
        "assess_score_title":   "📊 Analysis Summary",
        "assess_strains_title": "🦠 Recommended MBT55 Meta-Strains",
        "assess_effects_title": "✨ Expected Effects",
        "assess_disease_title": "⚠️ Disease Risk Assessment",
        "error_no_json":        "⚠️ Data file not found",
        "error_bad_structure":  "Invalid data structure",
        "error_module":         "⚠️ Failed to load modules",
        "error_module_hint":    "Please check that the src/ directory is correctly placed.",
        "metabolic_title":      "🧬 Metabolic Analysis",
        "metabolic_select":     "🔍 Select Substrate",
        "metabolic_effect":     "Effects",
        "metabolic_all":        "📋 All Registered Substrates",
        "metabolic_no_module":  "Metabolic analysis module could not be loaded.",
        "metabolic_no_db":      "Could not retrieve the metabolic pathway database.",
        "probiotics_title":     "🦠 Probiotics",
        "probiotics_no_data":   "No probiotics data available.",
        "probiotics_func":      "Function",
        "probiotics_species":   "Species",
        "probiotics_produces":  "Produces",
        "kampo_title":          "💊 Kampo Library",
        "kampo_subtitle":       "📚 Kampo Formula Library ({count} formulas)",
        "kampo_search":         "🔍 Search by formula or herb name",
        "kampo_count":          "Showing: {f} / {t} formulas",
        "kampo_no_data":        "No Kampo library data available.",
        "kampo_unknown":        "Unknown",
        "kampo_animal":         "🦌 Animal-Derived Herb Library",
        "kampo_animal_no_data": "No animal-derived herb data available.",
        "disease_title":        "⚠️ Disease Risk",
        "disease_subtitle":     "📊 137 Disease Matrix ({count} diseases)",
        "disease_search":       "🔍 Search by disease name or code",
        "disease_count":        "Showing: {f} / {t} diseases",
        "disease_no_data":      "No disease matrix data available.",
        "disease_personal":     "🔍 Your Disease Risk Assessment",
        "disease_unknown":      "Unknown",
        "sim_title":            "🔬 Simulation",
        "sim_cascade":          "### 3-Stage Enzyme Cascade\n| Stage | Time | Temp | Oxygen |\n|-------|------|------|--------|\n| 1 | 0-6h | 38°C | Aerobic |\n| 2 | 6-24h | 42°C | Micro-aerobic |\n| 3 | 24-72h | 35°C | Anaerobic |",
        "reports_title":        "📄 Reports",
        "reports_dl":           "📥 Download JSON",
        "reports_summary":      "📊 Integrated Analysis Summary",
        "reports_no_data":      "Please run the Health Assessment first.",
    },
}

def tx(key: str, **kw) -> str:
    """翻訳ヘルパー。変数名 t と絶対に被らないよう tx に統一。"""
    text = TXT.get(st.session_state.get("lang", "ja"), TXT["ja"]).get(key, key)
    if kw:
        try:
            return text.format(**kw)
        except (KeyError, ValueError):
            return text
    return text

# ── JSONローダー（複数パス・複数ファイル名に対応）─────────────────
_SEARCH_ROOTS = [
    Path(__file__).parent.parent,
    Path("."),
    Path("/mount/src/healthbook-mbt55-unified"),
]
_QFILE_NAMES = {
    "ja": ["questionnaire_200_jp.json", "healthbook_200_ja.json",
           "questionnaire_200_ja.json", "healthbook_200_jp.json"],
    "en": ["questionnaire_200_en.json", "healthbook_200_en.json"],
}

@st.cache_data
def _load_json_cached(path_str: str):
    with open(path_str, "r", encoding="utf-8") as f:
        return json.load(f)

def load_json(rel_path: str):
    for root in _SEARCH_ROOTS:
        p = root / rel_path
        if p.exists():
            return _load_json_cached(str(p.resolve()))
    return None

def load_questionnaire(lang: str):
    for fname in _QFILE_NAMES.get(lang, []):
        data = load_json(f"data/questionnaires/{fname}")
        if data is not None:
            return data
    return None

# ── session_state 初期化 ──────────────────────────────────────────
def init():
    defs = {
        "lang":       "ja",
        "navigation": HOME,
        "result":     None,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
#  ★ ナビゲーション修正の核心
#
#  on_click コールバックで navigation を書き換えるだけでは
#  Streamlit が再描画してもサイドバーの st.radio が古い index を
#  キャッシュし続けてページが切り替わらないことがある。
#
#  解決策: st.query_params を使って「行き先」を URL パラメータに
#  書き込み、スクリプト最上流の init() で読み取る方式に統一する。
#  これにより on_click → query_params 書き換え → 自動 rerun の
#  確実なフローが保証される。
# ══════════════════════════════════════════════════════════════════
def go(page: str):
    """ページ遷移。どこから呼んでも確実に動作する。"""
    st.session_state.navigation = page
    st.query_params["page"] = page   # URL パラメータにも書き込む

def sync_navigation():
    """URL パラメータと session_state を同期する（init の後に呼ぶ）。"""
    qp = st.query_params.get("page", None)
    if qp and qp != st.session_state.navigation:
        st.session_state.navigation = qp

# ── サイドバー ────────────────────────────────────────────────────
def sidebar():
    lang  = st.session_state.lang
    menu  = MENU[lang]
    labels = [m[0] for m in menu]
    ids    = [m[1] for m in menu]

    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")

        # 言語切替
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

        # ナビゲーション
        try:
            cur_idx = ids.index(st.session_state.navigation)
        except ValueError:
            cur_idx = 0

        chosen = st.radio(
            "Menu",
            labels,
            index=cur_idx,
            label_visibility="collapsed",
            key="nav_radio",
        )
        chosen_page = ids[labels.index(chosen)]
        if chosen_page != st.session_state.navigation:
            go(chosen_page)
            st.rerun()

# ══════════════════════════════════════════════════════════════════
#  ページ: ホーム
# ══════════════════════════════════════════════════════════════════
def page_home():
    st.title(tx("home_title"))
    st.markdown(tx("home_desc"))

    if not MODULES_LOADED:
        st.error(f"{tx('error_module')}: {_IMPORT_ERROR}")
        st.info(tx("error_module_hint"))

    c1, c2, c3 = st.columns(3)
    c1.metric(tx("home_pathways"), "20+")
    c2.metric(tx("home_strains"),  "5")
    c3.metric(tx("home_diseases"), "137")

    st.divider()
    st.subheader(tx("home_quickstart"))

    # ★ on_click で go() を呼び、その後 st.rerun() が走る
    if st.button(
        tx("home_btn"),
        type="primary",
        use_container_width=True,
        key="start_btn",
    ):
        go(ASSESS)
        st.rerun()   # ← ここが決定的。on_click だけでは再描画が保証されない

# ══════════════════════════════════════════════════════════════════
#  ページ: 健康アセスメント
# ══════════════════════════════════════════════════════════════════
def page_assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN

    st.title(tx("assess_title"))
    st.markdown(tx("assess_desc"))

    # データ読み込み
    data = load_questionnaire(st.session_state.lang)
    if data is None:
        st.error(tx("error_no_json"))
        tried = ", ".join(_QFILE_NAMES[st.session_state.lang])
        st.code(f"Searched filenames: {tried}")
        return

    questions = data.get("questions", {})
    if not questions:
        st.error(tx("error_bad_structure"))
        return

    # カテゴリ分類
    cats: dict[str, list] = {}
    for qid, qdata in questions.items():
        cat = qdata.get("category", "Other")
        cats.setdefault(cat, []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    # ── タブを先に定義 ──────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        tx("assess_tab1"), tx("assess_tab2"),
        tx("assess_tab3"), tx("assess_tab4"),
    ])

    # ════════════════════════════════════════════════════════════
    #  tab1: 問診入力
    #
    #  ★ st.form を使わない。
    #     各チェックボックスを key="ck_{qid}" で session_state に
    #     直接保存。解析ボタン押下時に全 key を読み取る。
    #     expanded=True で全カテゴリを常時描画し、
    #     「未展開 → 値が False になる」バグを完全排除。
    # ════════════════════════════════════════════════════════════
    with tab1:
        st.write(tx("assess_items", count=len(questions)))

        # 一括操作
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button(tx("assess_select_all"), key="btn_sel_all", use_container_width=True):
            for qid in questions:
                st.session_state[f"ck_{qid}"] = True
            st.rerun()
        if cb.button(tx("assess_clear_all"), key="btn_clr_all", use_container_width=True):
            for qid in questions:
                st.session_state[f"ck_{qid}"] = False
            st.rerun()

        st.divider()

        for cat_name in cat_order:
            qlist = cats.get(cat_name, [])
            if not qlist:
                continue
            with st.expander(
                f"■ {cat_name} {tx('assess_cat_count', count=len(qlist))}",
                expanded=True,   # ★ False にすると未展開の値が取れない
            ):
                cols = st.columns(2)
                for i, q in enumerate(qlist):
                    key = f"ck_{q['id']}"
                    with cols[i % 2]:
                        st.checkbox(
                            q["question"],
                            value=st.session_state.get(key, False),
                            key=key,
                        )

        st.divider()

        # ════════════════════════════════════════════════════
        #  解析ボタン（フォーム外・タブ内に単独配置）
        #  押下 → answers 収集 → pipeline 実行 →
        #  session_state.result に保存 → st.rerun() で全タブ更新
        # ════════════════════════════════════════════════════
        if st.button(
            tx("assess_run"),
            type="primary",
            use_container_width=True,
            key="btn_run",
        ):
            if not MODULES_LOADED:
                st.error(f"{tx('error_module')}: {_IMPORT_ERROR}")
            else:
                # ★ session_state から全回答を確実に収集
                answers = {
                    qdata["question"]: bool(st.session_state.get(f"ck_{qid}", False))
                    for qid, qdata in questions.items()
                }

                with st.spinner(tx("assess_spinner")):
                    try:
                        result = FullPipeline(language=language).run(answers)
                        st.session_state.result = result
                        st.success(tx("assess_complete"))
                        st.rerun()   # ★ tab2〜4 を最新結果で再描画
                    except Exception as exc:
                        import traceback
                        st.error(f"Error: {exc}")
                        st.code(traceback.format_exc())

    # ── tab2: PATHスコア・レーダーチャート ──────────────────────
    with tab2:
        result = st.session_state.result
        if result and result.phenotype and result.phenotype.scores:
            path_defs = PATH_DEFINITIONS.get(language, {})
            st.subheader(tx("assess_score_title"))

            try:
                import plotly.graph_objects as go
                labels_r, values_r = [], []
                for pid, ps in result.phenotype.scores.items():
                    pd_info = path_defs.get(pid, {})
                    lbl = pd_info.get(
                        "short",
                        pid.value if hasattr(pid, "value") else str(pid),
                    )
                    labels_r.append(lbl)
                    values_r.append(ps.score)

                if labels_r:
                    fig = go.Figure(go.Scatterpolar(
                        r=values_r, theta=labels_r, fill="toself",
                        line=dict(color="#00B4D8", width=2),
                        fillcolor="rgba(0,180,216,0.25)",
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(range=[0, 100])),
                        showlegend=False, height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as chart_e:
                st.warning(f"Chart render error: {chart_e}")

            st.markdown(
                f"**{tx('assess_overall')}: {result.phenotype.overall_status}**"
            )
            st.divider()

            for pid, ps in result.phenotype.scores.items():
                pd_info = path_defs.get(pid, {})
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(
                    f"**{pd_info.get('name', str(pid))}**"
                    f"\n*{pd_info.get('desc', '')}*"
                )
                c2.metric("Score", f"{ps.score:.0f}%")
                color = (
                    "green" if ps.score >= 70
                    else "orange" if ps.score >= 40
                    else "red"
                )
                c3.markdown(
                    f"<span style='color:{color};font-weight:bold'>"
                    f"{ps.level}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info(tx("assess_no_data"))

    # ── tab3: 菌株推奨 ───────────────────────────────────────────
    with tab3:
        result = st.session_state.result
        screening = getattr(result, "probiotic_screening", None) if result else None
        strains   = getattr(screening, "recommended_strains", None) if screening else None

        if strains:
            st.subheader(tx("assess_strains_title"))
            for s in strains:
                st.markdown(f"### P{s.priority}: {s.name}")
                st.write(s.reason)
                st.divider()
            effects = getattr(result, "expected_effects", None)
            if effects:
                st.subheader(tx("assess_effects_title"))
                for e in effects:
                    st.markdown(f"✅ {e}")
        else:
            st.info(tx("assess_no_data"))

    # ── tab4: 疾病リスク ─────────────────────────────────────────
    with tab4:
        result = st.session_state.result
        risks  = getattr(result, "disease_risks", None) if result else None

        if risks:
            st.subheader(tx("assess_disease_title"))
            for dname, rval in risks.items():
                st.metric(label=dname, value=f"{rval:.1f}%")
        else:
            st.info(tx("assess_no_data"))

# ══════════════════════════════════════════════════════════════════
#  ページ: 代謝解析
# ══════════════════════════════════════════════════════════════════
def page_metabolic():
    st.title(tx("metabolic_title"))
    if not MODULES_LOADED:
        st.error(tx("metabolic_no_module"))
        return
    db = get_pathway_database()
    if db is None:
        st.warning(tx("metabolic_no_db"))
        return
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox(tx("metabolic_select"), subs)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(
                        f"### {p['substrate']} → **{p['final_metabolite']}**"
                    )
                    st.write(f"{tx('metabolic_effect')}: {', '.join(p['human_effects'])}")
                    st.divider()
        st.subheader(tx("metabolic_all"))
        st.write(", ".join(subs))

# ══════════════════════════════════════════════════════════════════
#  ページ: プロバイオティクス
# ══════════════════════════════════════════════════════════════════
def page_probiotics():
    st.title(tx("probiotics_title"))
    lang = Language.JA if st.session_state.lang == "ja" else Language.EN
    strain_defs = META_STRAIN_DEFINITIONS.get(lang, {})
    if not strain_defs:
        st.info(tx("probiotics_no_data"))
        return
    for _sid, d in strain_defs.items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(
                f"{tx('probiotics_func')}: {d['functional_unit']} | "
                f"{tx('probiotics_species')}: {d['key_species']} | "
                f"{tx('probiotics_produces')}: {d['produces']}"
            )

# ══════════════════════════════════════════════════════════════════
#  ページ: 漢方ライブラリー
# ══════════════════════════════════════════════════════════════════
def page_kampo():
    st.title(tx("kampo_title"))
    kampo_data = (
        load_json("data/kampo/kampo_metabolic_library.json")
        or load_json("data/kampo/kampo_294_library.json")
    )
    if kampo_data and isinstance(kampo_data, list):
        st.subheader(tx("kampo_subtitle", count=len(kampo_data)))
        search = st.text_input(tx("kampo_search"), key="kampo_search_in")
        filtered = (
            [k for k in kampo_data if search.lower() in str(k).lower()]
            if search else kampo_data
        )
        st.write(tx("kampo_count", f=len(filtered), t=len(kampo_data)))
        for item in filtered[:20]:
            name = item.get("name", item.get("formula_name", tx("kampo_unknown")))
            with st.expander(f"💊 {name}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(f"… {len(filtered) - 20} more")
    else:
        st.warning(tx("kampo_no_data"))

    st.divider()
    st.subheader(tx("kampo_animal"))
    animal_data = (
        load_json("data/kampo/animal_metabolic_library.json")
        or load_json("data/kampo/animal_derived_library.json")
    )
    if animal_data and isinstance(animal_data, list):
        for item in animal_data:
            name = item.get("name_ja", item.get("name", tx("kampo_unknown")))
            with st.expander(f"🦌 {name}"):
                st.json(item)
    else:
        st.info(tx("kampo_animal_no_data"))

# ══════════════════════════════════════════════════════════════════
#  ページ: 疾病リスク
# ══════════════════════════════════════════════════════════════════
def page_disease():
    st.title(tx("disease_title"))
    disease_data = (
        load_json("data/diseases/disease_matrix_137.json")
        or load_json("data/diseases/disease_matrix.json")
    )
    if disease_data and isinstance(disease_data, list):
        st.subheader(tx("disease_subtitle", count=len(disease_data)))
        search = st.text_input(tx("disease_search"), key="disease_search_in")
        filtered = (
            [d for d in disease_data if search.lower() in str(d).lower()]
            if search else disease_data
        )
        st.write(tx("disease_count", f=len(filtered), t=len(disease_data)))
        for item in filtered[:20]:
            name = item.get("name", item.get("disease_name", tx("disease_unknown")))
            with st.expander(f"⚠️ {name}"):
                st.json(item)
        if len(filtered) > 20:
            st.info(f"… {len(filtered) - 20} more")
    else:
        st.warning(tx("disease_no_data"))

    result = st.session_state.result
    risks  = getattr(result, "disease_risks", None) if result else None
    if risks:
        st.divider()
        st.subheader(tx("disease_personal"))
        for dname, rval in risks.items():
            st.metric(label=dname, value=f"{rval:.1f}%")

# ══════════════════════════════════════════════════════════════════
#  ページ: シミュレーション
# ══════════════════════════════════════════════════════════════════
def page_sim():
    st.title(tx("sim_title"))
    st.markdown(tx("sim_cascade"))
    st.latex(r"\frac{dH_2}{dt} \approx 0")

# ══════════════════════════════════════════════════════════════════
#  ページ: レポート
# ══════════════════════════════════════════════════════════════════
def page_reports():
    st.title(tx("reports_title"))
    result = st.session_state.result
    if result:
        st.download_button(
            tx("reports_dl"),
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            "report.json",
            "application/json",
        )
        st.subheader(tx("reports_summary"))
        st.text(result.format_for_display())
    else:
        st.info(tx("reports_no_data"))

# ══════════════════════════════════════════════════════════════════
#  エントリポイント
# ══════════════════════════════════════════════════════════════════
PAGES = {
    HOME:       page_home,
    ASSESS:     page_assessment,
    METABOLIC:  page_metabolic,
    PROBIOTICS: page_probiotics,
    KAMPO:      page_kampo,
    DISEASE:    page_disease,
    SIM:        page_sim,
    REPORTS:    page_reports,
}

def main():
    init()
    sync_navigation()   # URL パラメータ → session_state を同期
    sidebar()
    PAGES.get(st.session_state.navigation, page_home)()

if __name__ == "__main__":
    main()
