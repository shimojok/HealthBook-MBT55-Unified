"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v3 - 全ボタン動作保証
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

MENU_JA = [
    ("🏠 ホーム", PAGE_HOME),
    ("📋 健康アセスメント", PAGE_ASSESS),
    ("🧬 代謝解析", PAGE_METABOLIC),
    ("🦠 プロバイオティクス", PAGE_PROBIOTICS),
    ("💊 漢方ライブラリー", PAGE_KAMPO),
    ("⚠️ 疾病リスク", PAGE_DISEASE),
    ("🔬 シミュレーション", PAGE_SIMULATION),
    ("📄 レポート", PAGE_REPORTS),
]
MENU_EN = [
    ("🏠 Home", PAGE_HOME),
    ("📋 Health Assessment", PAGE_ASSESS),
    ("🧬 Metabolic Analysis", PAGE_METABOLIC),
    ("🦠 Probiotics", PAGE_PROBIOTICS),
    ("💊 Kampo Library", PAGE_KAMPO),
    ("⚠️ Disease Risk", PAGE_DISEASE),
    ("🔬 Simulation", PAGE_SIMULATION),
    ("📄 Reports", PAGE_REPORTS),
]


def init_session():
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGE_HOME


def go_page(page):
    st.session_state.current_page = page


@st.cache_data
def load_questionnaire(lang):
    """200項目問診JSONを読み込む"""
    base = Path(__file__).parent.parent
    filename = "healthbook_200_ja.json" if lang == "ja" else "healthbook_200_en.json"
    path = base / "data" / "questionnaires" / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_symptoms(data):
    result = {}
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
    labels = [m[0] for m in menu]
    pages = [m[1] for m in menu]

    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")

        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English")
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()

        st.divider()

        # 現在のページをradioのデフォルト値に
        try:
            idx = pages.index(st.session_state.current_page)
        except ValueError:
            idx = 0

        selected = st.radio(
            "メニュー",
            options=labels,
            index=idx,
            label_visibility="collapsed",
            key="menu_radio",
            on_change=None,  # on_changeは使わない
        )
        # 選択されたラベルに対応するページに遷移
        chosen_page = pages[labels.index(selected)]
        if st.session_state.current_page != chosen_page:
            go_page(chosen_page)
            st.rerun()


# ── ホーム ──
def render_home():
    st.title("🏥 HealthBook-MBT55 Unified")

    if st.session_state.language == "ja":
        st.markdown("""
        **全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した次世代ヘルスケアプラットフォーム。
        200項目問診から代謝経路活性状態（PATH_01〜05）を評価し、最適な漢方・MBT55菌株を提案します。
        """)
    else:
        st.markdown("""
        Next-generation healthcare platform integrating **full metabolic pathway analysis**,
        **phenotyping**, and **MBT Probiotics screening**.
        """)

    c1, c2, c3 = st.columns(3)
    c1.metric("代謝経路", "20+")
    c2.metric("メタ株", "5")
    c3.metric("疾病", "137")

    st.divider()
    st.subheader("🚀 クイックスタート")

    # ★ 赤ボタン ★
    if st.button("🔴 健康アセスメントを開始する", type="primary", use_container_width=True):
        go_page(PAGE_ASSESS)
        st.rerun()


# ── 健康アセスメント ──
def render_health_assessment():
    language = Language.JA if st.session_state.language == "ja" else Language.EN
    st.title("📋 健康アセスメント")

    q_data = load_questionnaire(st.session_state.language)
    if q_data is None:
        st.error("⚠️ 問診データファイルが見つかりません。data/questionnaires/healthbook_200_ja.json を確認してください。")
        st.info("リポジトリに data/questionnaires/ フォルダを作成し、HealthBook-AI から JSON ファイルをコピーしてください。")
        return

    flat = flatten_symptoms(q_data)
    all_symptoms = list(flat.keys())

    # カテゴリごとに整理
    categories = {}
    for s, cat in flat.items():
        categories.setdefault(cat, []).append(s)

    t1, t2, t3, t4 = st.tabs(["📝 問診入力", "📊 結果", "🦠 菌株", "⚠️ リスク"])

    with t1:
        st.subheader("200項目健康問診")
        st.caption("当てはまる症状すべてにチェックを入れてください")

        # 全選択/解除
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button("✅ すべて選択", use_container_width=True):
            for s in all_symptoms:
                st.session_state[f"s_{s}"] = True
            st.rerun()
        if cb.button("🔄 すべて解除", use_container_width=True):
            for s in all_symptoms:
                st.session_state[f"s_{s}"] = False
            st.rerun()

        st.divider()

        answers = {}
        for cat, symptoms in categories.items():
            st.markdown(f"### {cat}")
            cols = st.columns(3)
            for i, s in enumerate(symptoms):
                with cols[i % 3]:
                    key = f"s_{s}"
                    val = st.checkbox(s, value=st.session_state.get(key, False), key=key)
                    answers[s] = val

        st.divider()

        if st.button("🔍 解析を実行する", type="primary", use_container_width=True):
            with st.spinner("MBT55代謝経路を解析中..."):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
            st.success("✅ 解析完了！タブを切り替えて結果を確認してください。")

    with t2:
        result = st.session_state.pipeline_result
        if result:
            defs = PATH_DEFINITIONS.get(language, {})
            st.subheader("📊 PATH_01〜05 スコア")

            import plotly.graph_objects as go
            cats, vals = [], []
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                cats.append(d.get("short", pid.value))
                vals.append(ps.score)
            if cats:
                fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself',
                    line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**総合判定: {result.phenotype.overall_status}**")
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3 = st.columns([3, 1, 1])
                x1.write(f"**{d.get('name', pid.value)}**")
                x2.metric("Score", f"{ps.score:.0f}%")
                c = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(f"<span style='color:{c};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info("解析を実行してください")

    with t3:
        result = st.session_state.pipeline_result
        if result:
            st.subheader("🦠 推奨MBT55メタ株")
            screening = result.probiotic_screening
            if screening and screening.recommended_strains:
                for strain in screening.recommended_strains:
                    st.markdown(f"**P{strain.priority}: {strain.name}**")
                    st.write(strain.reason)
                    st.divider()
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for e in result.expected_effects:
                    st.write(f"✅ {e}")
        else:
            st.info("解析を実行してください")

    with t4:
        result = st.session_state.pipeline_result
        if result:
            st.subheader("⚠️ 疾病リスク")
            if result.disease_risks:
                for d, r in result.disease_risks.items():
                    st.metric(d, f"{r:.1f}%")
            else:
                st.info("顕著なリスクなし")
        else:
            st.info("解析を実行してください")


# ── 他画面 ──
def render_metabolic_analysis():
    st.title("🧬 代謝解析")
    db = get_pathway_database()
    substrates = db.list_all_substrates()
    sel = st.selectbox("基質を選択", substrates)
    if sel:
        pred = db.predict_metabolites(sel)
        if pred.get("found"):
            for p in pred["predictions"]:
                st.metric("最終代謝物", p["final_metabolite"])
                st.write(f"効果: {', '.join(p['human_effects'])}")
    st.divider()
    st.write(f"登録基質: {', '.join(substrates)}")


def render_probiotics():
    st.title("🦠 プロバイオティクス")
    lang = Language.JA if st.session_state.language == "ja" else Language.EN
    for sid, d in META_STRAIN_DEFINITIONS[lang].items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(f"機能: {d['functional_unit']} | 主要菌種: {d['key_species']} | 生成物: {d['produces']}")


def render_kampo_library():
    st.title("💊 漢方ライブラリー")
    st.info("294漢方処方 - 準備中")


def render_disease_risk():
    st.title("⚠️ 疾病リスク")
    st.info("137疾病マトリックス - 準備中")


def render_simulation():
    st.title("🔬 シミュレーション")
    st.markdown("### 3段階酵素カスケード")
    st.table({"Stage": [1,2,3], "時間": ["0-6h","6-24h","24-72h"], "温度": ["38°C","42°C","35°C"], "酸素": ["好気","微好気","嫌気"]})
    st.latex(r"\frac{dH_2}{dt} \approx 0")


def render_reports():
    st.title("📄 レポート")
    if st.session_state.pipeline_result:
        r = st.session_state.pipeline_result
        st.download_button("📥 JSONダウンロード", json.dumps(r.to_dict(), ensure_ascii=False, indent=2),
            "healthbook_mbt55_report.json", "application/json")
        st.text(r.format_for_display())
    else:
        st.info("解析を実行してください")


# ── メイン ──
def main():
    init_session()
    render_sidebar()

    router = {
        PAGE_HOME: render_home,
        PAGE_ASSESS: render_health_assessment,
        PAGE_METABOLIC: render_metabolic_analysis,
        PAGE_PROBIOTICS: render_probiotics,
        PAGE_KAMPO: render_kampo_library,
        PAGE_DISEASE: render_disease_risk,
        PAGE_SIMULATION: render_simulation,
        PAGE_REPORTS: render_reports,
    }
    router.get(st.session_state.current_page, render_home)()


if __name__ == "__main__":
    main()