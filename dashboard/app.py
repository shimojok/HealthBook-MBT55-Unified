"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版 v2：全ボタン動作・全画面表示・セッション競合解消
"""

import streamlit as st
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
from src.integration.full_pipeline import FullPipeline
from src.layer2_metabolism.pathway_database import get_pathway_database
from dashboard.i18n.translator import I18nManager

st.set_page_config(
    page_title="HealthBook-MBT55 Unified",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────── 問診データ読み込み ────────────
@st.cache_data
def load_questionnaire(lang: str):
    filename = "healthbook_200_ja.json" if lang == "ja" else "healthbook_200_en.json"
    path = Path(__file__).parent.parent / "data" / "questionnaires" / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def flatten_symptoms(data):
    result = {}
    if isinstance(data, dict):
        for category, items in data.items():
            if isinstance(items, dict):
                for sub, symptoms in items.items():
                    if isinstance(symptoms, list):
                        for s in symptoms:
                            result[s] = category
            elif isinstance(items, list):
                for s in items:
                    result[s] = category
    return result


# ──────────── セッション状態 ────────────
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


def init_session_state():
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGE_HOME


def switch_page(page: str):
    """安全にページを切り替える"""
    st.session_state.current_page = page


def get_menu():
    return MENU_JA if st.session_state.language == "ja" else MENU_EN


# ──────────── サイドバー ────────────
def render_sidebar():
    menu = get_menu()
    labels = list(menu.keys())
    pages = list(menu.values())

    # 現在のページに対応するラベルを初期値に
    try:
        current_idx = pages.index(st.session_state.current_page)
    except ValueError:
        current_idx = 0

    with st.sidebar:
        st.image("https://via.placeholder.com/150x80.png?text=MBT55", width=150)
        st.title("🏥 HealthBook-MBT55")

        lang = st.selectbox(
            "🌐 Language / 言語",
            options=["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English",
        )
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()

        st.divider()
        st.markdown("### 📋 メニュー")

        # ラジオボタンでページ切り替え（キーを固定してウィジェットID安定化）
        selected_label = st.radio(
            "メニュー選択",
            options=labels,
            index=current_idx,
            label_visibility="collapsed",
            key="nav_radio",
        )
        switch_page(menu[selected_label])


# ──────────── 各画面 ────────────
def render_home():
    st.title("🏥 HealthBook-MBT55 Unified")

    if st.session_state.language == "ja":
        st.markdown("""
        **全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した
        次世代ヘルスケアプラットフォーム。

        200項目問診から、あなたの代謝経路活性状態（PATH_01〜05）を評価し、
        最適な漢方・生薬・MBT55菌株セットを提案します。
        """)
    else:
        st.markdown("""
        Next-generation healthcare platform integrating **full metabolic pathway analysis**,
        **phenotyping**, and **MBT Probiotics screening**.

        From a 200-item questionnaire, we assess your metabolic pathway activity (PATH_01-05)
        and recommend optimal Kampo, herbs, and MBT55 strain sets.
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="代謝経路 / Pathways", value="20+")
    with col2:
        st.metric(label="MBT55メタ株 / Strains", value="5")
    with col3:
        st.metric(label="疾病マトリックス / Diseases", value="137")

    st.divider()
    st.subheader("🚀 クイックスタート / Quick Start")

    if st.button("健康アセスメントを開始する", type="primary", use_container_width=True, key="btn_start_ja"):
        switch_page(PAGE_ASSESS)
        st.rerun()


def render_health_assessment():
    language = Language.JA if st.session_state.language == "ja" else Language.EN

    st.title("📋 健康アセスメント")

    q_data = load_questionnaire(st.session_state.language)
    if not q_data:
        st.error("問診データが読み込めません。")
        return

    flat = flatten_symptoms(q_data)
    all_symptoms = list(flat.keys())

    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 問診入力",
        "📊 フェノタイピング結果",
        "🦠 菌株推奨",
        "⚠️ 疾病リスク",
    ])

    with tab1:
        st.subheader("200項目健康問診")
        st.caption("当てはまる症状にチェックを入れてください")

        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("✅ すべて選択", use_container_width=True):
                for s in all_symptoms:
                    st.session_state[f"q_{s}"] = True
                st.rerun()
        with col2:
            if st.button("🔄 すべて解除", use_container_width=True):
                for s in all_symptoms:
                    st.session_state[f"q_{s}"] = False
                st.rerun()

        st.divider()

        categories = {}
        for symptom, cat in flat.items():
            categories.setdefault(cat, []).append(symptom)

        answers = {}
        for cat, symptoms in categories.items():
            st.markdown(f"### {cat}")
            cols = st.columns(3)
            for i, symptom in enumerate(symptoms):
                with cols[i % 3]:
                    checked = st.checkbox(
                        symptom,
                        value=st.session_state.get(f"q_{symptom}", False),
                        key=f"q_{symptom}",
                    )
                    answers[symptom] = checked

        st.divider()

        if st.button("🔍 解析を実行する", type="primary", use_container_width=True):
            with st.spinner("MBT55代謝経路を解析中..."):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
            st.success("✅ 解析が完了しました！タブを切り替えて結果を確認してください。")

    # タブ2〜4：結果表示（前回と同じなので簡略化）
    with tab2:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            defs = PATH_DEFINITIONS.get(language, {})

            st.subheader("📊 PATH_01〜05 代謝経路活性スコア")

            import plotly.graph_objects as go
            cats, vals = [], []
            for pid, ps in result.phenotype.scores.items():
                pd_ = defs.get(pid, {})
                cats.append(pd_.get("short", pid.value))
                vals.append(ps.score)

            if cats:
                fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself',
                    line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**総合判定: {result.phenotype.overall_status}**")

            for pid, ps in result.phenotype.scores.items():
                pd_ = defs.get(pid, {})
                c1, c2, c3 = st.columns([3,1,1])
                with c1:
                    st.write(f"**{pd_.get('name', pid.value)}**")
                with c2:
                    st.metric("Score", f"{ps.score:.0f}%")
                with c3:
                    color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info("解析を実行すると結果が表示されます")

    with tab3:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            screening = result.probiotic_screening
            st.subheader("🦠 推奨MBT55メタ株")
            if screening and screening.recommended_strains:
                for strain in screening.recommended_strains:
                    c1, c2 = st.columns([1,4])
                    with c1:
                        st.metric("優先度", f"P{strain.priority}")
                    with c2:
                        st.markdown(f"### {strain.name}")
                        st.write(strain.reason)
                    st.divider()
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for e in result.expected_effects:
                    st.markdown(f"✅ {e}")
        else:
            st.info("解析を実行すると結果が表示されます")

    with tab4:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            st.subheader("⚠️ 疾病リスク評価")
            if result.disease_risks:
                for disease, risk in result.disease_risks.items():
                    st.metric(label=disease, value=f"{risk:.1f}%")
            else:
                st.info("顕著な疾病リスクは検出されませんでした")
        else:
            st.info("解析を実行すると結果が表示されます")


def render_metabolic_analysis():
    st.title("🧬 代謝解析")
    db = get_pathway_database()
    substrates = db.list_all_substrates()

    selected = st.selectbox("基質を選択", options=substrates)
    if selected:
        pred = db.predict_metabolites(selected)
        if pred.get("found"):
            for p in pred["predictions"]:
                with st.expander(f"🔬 {p['substrate']} → {p['final_metabolite']}"):
                    st.write(f"**効果:** {', '.join(p['human_effects'])}")
                    st.write(f"**標的:** {', '.join(p['disease_targets'])}")

    st.divider()
    st.subheader("全基質一覧")
    st.write(", ".join(substrates))


def render_probiotics():
    st.title("🦠 プロバイオティクス")
    meta_defs = META_STRAIN_DEFINITIONS[Language.JA if st.session_state.language == "ja" else Language.EN]
    for sid, defn in meta_defs.items():
        with st.expander(f"🔹 {defn['name']}"):
            st.write(f"**機能:** {defn['functional_unit']}")
            st.write(f"**主要菌種:** {defn['key_species']}")
            st.write(f"**生成物:** {defn['produces']}")


def render_kampo_library():
    st.title("💊 漢方ライブラリー")
    st.info("294漢方処方ライブラリー - 連携準備中")


def render_disease_risk():
    st.title("⚠️ 疾病リスク")
    st.info("137疾病マトリックス詳細 - 連携準備中")


def render_simulation():
    st.title("🔬 シミュレーション")
    st.markdown("### 3段階酵素カスケード")
    st.markdown("| Stage | Time | Temp | Oxygen |")
    st.markdown("|-------|------|------|--------|")
    st.markdown("| 1 | 0-6h | 38°C | 好気 |")
    st.markdown("| 2 | 6-24h | 42°C | 微好気 |")
    st.markdown("| 3 | 24-72h | 35°C | 嫌気 |")
    st.latex(r"\frac{dH_2}{dt} = \delta E - \epsilon (X_m + X_s) H_2 \approx 0")


def render_reports():
    st.title("📄 レポート")
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        st.download_button(
            "📥 JSONレポートをダウンロード",
            data=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            file_name="healthbook_mbt55_report.json",
            mime="application/json",
        )
        st.subheader("統合解析サマリー")
        st.text(result.format_for_display())
    else:
        st.info("まず健康アセスメントを実行してください")


# ──────────── メイン ────────────
def main():
    init_session_state()
    render_sidebar()

    pages = {
        PAGE_HOME: render_home,
        PAGE_ASSESS: render_health_assessment,
        PAGE_METABOLIC: render_metabolic_analysis,
        PAGE_PROBIOTICS: render_probiotics,
        PAGE_KAMPO: render_kampo_library,
        PAGE_DISEASE: render_disease_risk,
        PAGE_SIMULATION: render_simulation,
        PAGE_REPORTS: render_reports,
    }

    page_func = pages.get(st.session_state.current_page, render_home)
    page_func()


if __name__ == "__main__":
    main()