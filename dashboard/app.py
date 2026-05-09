"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全版：全代謝経路解析 + フェノタイピング + MBT Probiotics + M3-BioSynergy連携
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

# ─────────────────────────────
# 200項目問診データ読み込み
# ─────────────────────────────
@st.cache_data
def load_questionnaire(lang: str):
    if lang == "ja":
        path = Path(__file__).parent.parent / "data" / "questionnaires" / "healthbook_200_ja.json"
    else:
        path = Path(__file__).parent.parent / "data" / "questionnaires" / "healthbook_200_en.json"
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


def init_session_state():
    defaults = {
        "language": "ja",
        "pipeline_result": None,
        "current_page": "home",
        "sidebar_menu": "🏠 ホーム",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_i18n():
    return I18nManager(st.session_state.language)


# サイドバーメニュー定義（日本語/英語）
MENU_JA = {
    "🏠 ホーム": "home",
    "📋 健康アセスメント": "health_assessment",
    "🧬 代謝解析": "metabolic_analysis",
    "🦠 プロバイオティクス": "probiotics",
    "💊 漢方ライブラリー": "kampo_library",
    "⚠️ 疾病リスク": "disease_risk",
    "🔬 シミュレーション": "simulation",
    "📄 レポート": "reports",
}
MENU_EN = {
    "🏠 Home": "home",
    "📋 Health Assessment": "health_assessment",
    "🧬 Metabolic Analysis": "metabolic_analysis",
    "🦠 Probiotics": "probiotics",
    "💊 Kampo Library": "kampo_library",
    "⚠️ Disease Risk": "disease_risk",
    "🔬 Simulation": "simulation",
    "📄 Reports": "reports",
}


def render_sidebar():
    menu = MENU_JA if st.session_state.language == "ja" else MENU_EN

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

        selected = st.radio(
            "メニュー",
            options=list(menu.keys()),
            format_func=lambda x: x,
            label_visibility="collapsed",
            key="sidebar_menu",
        )
        st.session_state.current_page = menu[selected]


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
        st.metric(label="MBT55メタ株 / Meta-Strains", value="5")
    with col3:
        st.metric(label="疾病マトリックス / Diseases", value="137")

    st.divider()
    st.subheader("🚀 クイックスタート / Quick Start")

    if st.button("健康アセスメントを開始する / Start Health Assessment", type="primary", use_container_width=True):
        st.session_state.current_page = "health_assessment"
        st.session_state.sidebar_menu = "📋 健康アセスメント" if st.session_state.language == "ja" else "📋 Health Assessment"
        st.rerun()


def render_health_assessment():
    language = Language.JA if st.session_state.language == "ja" else Language.EN
    i18n = get_i18n()

    st.title("📋 健康アセスメント / Health Assessment")

    # 問診データ読み込み
    q_data = load_questionnaire(st.session_state.language)
    if not q_data:
        st.error("問診データが読み込めません。data/questionnaires/healthbook_200_ja.json を確認してください。")
        return

    flat = flatten_symptoms(q_data)
    all_symptoms = list(flat.keys())

    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 問診入力" if st.session_state.language == "ja" else "📝 Questionnaire",
        "📊 フェノタイピング結果" if st.session_state.language == "ja" else "📊 Phenotyping",
        "🦠 菌株推奨" if st.session_state.language == "ja" else "🦠 Strains",
        "⚠️ 疾病リスク" if st.session_state.language == "ja" else "⚠️ Disease Risk",
    ])

    with tab1:
        st.subheader("200項目健康問診 / 200-Item Health Questionnaire")
        st.caption("当てはまる症状にチェックを入れてください / Check all applicable symptoms")

        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("✅ すべて選択 / Select All", use_container_width=True):
                for s in all_symptoms:
                    st.session_state[f"q_{s}"] = True
                st.rerun()
        with col2:
            if st.button("🔄 すべて解除 / Clear All", use_container_width=True):
                for s in all_symptoms:
                    st.session_state[f"q_{s}"] = False
                st.rerun()

        st.divider()

        answers = {}
        # カテゴリごとに表示
        categories = {}
        for symptom, cat in flat.items():
            categories.setdefault(cat, []).append(symptom)

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

        if st.button("🔍 解析を実行する / Run Analysis", type="primary", use_container_width=True):
            with st.spinner("MBT55代謝経路を解析中... / Analyzing MBT55 metabolic pathways..."):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
            st.success("✅ 解析が完了しました！ / Analysis complete!")

    with tab2:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            defs = PATH_DEFINITIONS.get(language, {})

            st.subheader("📊 PATH_01〜05 代謝経路活性スコア / Metabolic Pathway Activity Scores")

            # レーダーチャート
            import plotly.graph_objects as go
            categories_chart = []
            values_chart = []
            for pid, ps in result.phenotype.scores.items():
                path_def = defs.get(pid, {})
                categories_chart.append(path_def.get("short", pid.value))
                values_chart.append(ps.score)

            if categories_chart:
                fig = go.Figure(data=go.Scatterpolar(
                    r=values_chart,
                    theta=categories_chart,
                    fill='toself',
                    line=dict(color='#00B4D8', width=2),
                    fillcolor='rgba(0, 180, 216, 0.25)',
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(range=[0, 100])),
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**総合判定 / Overall: {result.phenotype.overall_status}**")

            for pid, ps in result.phenotype.scores.items():
                path_def = defs.get(pid, {})
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{path_def.get('name', pid.value)}**")
                with col2:
                    st.metric(label="Score", value=f"{ps.score:.0f}%")
                with col3:
                    color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info("解析を実行すると結果が表示されます / Run analysis to see results")

    with tab3:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            screening = result.probiotic_screening

            st.subheader("🦠 推奨MBT55メタ株 / Recommended MBT55 Meta-Strains")

            if screening and screening.recommended_strains:
                for strain in screening.recommended_strains:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.metric(label="優先度", value=f"P{strain.priority}")
                    with col2:
                        st.markdown(f"### {strain.name}")
                        st.write(strain.reason)
                        opt = strain.optimal_conditions
                        if isinstance(opt, dict):
                            st.caption(f"⏱ Stage {strain.cascade_stage} | 🌡 {opt.get('temp', 'N/A')}°C | pH {opt.get('ph', 'N/A')}")
                        if strain.compatible_substrates:
                            st.caption(f"🧪 適合基質: {', '.join(strain.compatible_substrates)}")
                    st.divider()

                if screening.combination_proposal:
                    st.info(screening.combination_proposal)
            else:
                st.info("不足している代謝経路はありません / No deficient pathways detected")

            if result.expected_effects:
                st.subheader("✨ 期待効果 / Expected Effects")
                for effect in result.expected_effects:
                    st.markdown(f"✅ {effect}")

            if result.recommended_kampo:
                st.subheader("💊 推奨漢方・生薬 / Recommended Kampo & Herbs")
                for k in result.recommended_kampo:
                    st.markdown(f"- {k}")
        else:
            st.info("解析を実行すると結果が表示されます / Run analysis to see results")

    with tab4:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            st.subheader("⚠️ 疾病リスク評価 / Disease Risk Assessment")
            if result.disease_risks:
                for disease, risk in result.disease_risks.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{disease}**")
                    with col2:
                        color = "green" if risk < 30 else "orange" if risk < 60 else "red"
                        st.markdown(f"<span style='color:{color};font-size:18px;font-weight:bold'>{risk:.1f}%</span>", unsafe_allow_html=True)
            else:
                st.info("顕著な疾病リスクは検出されませんでした / No significant disease risks detected")
        else:
            st.info("解析を実行すると結果が表示されます / Run analysis to see results")


def render_metabolic_analysis():
    st.title("🧬 代謝解析 / Metabolic Analysis")

    db = get_pathway_database()
    substrates = db.list_all_substrates()

    st.subheader("生薬・ポリフェノール → 活性代謝物 経路検索")
    selected = st.selectbox("基質を選択 / Select substrate", options=substrates)

    if selected:
        prediction = db.predict_metabolites(selected)
        if prediction.get("found"):
            for pred in prediction["predictions"]:
                with st.expander(f"🔬 {pred['substrate']} → {pred['final_metabolite']}"):
                    st.markdown(f"**最終代謝物 / Final Metabolite:** {pred['final_metabolite']}")
                    st.markdown(f"**ヒト効果 / Human Effects:** {', '.join(pred['human_effects'])}")
                    st.markdown(f"**標的疾病 / Disease Targets:** {', '.join(pred['disease_targets'])}")
                    st.markdown(f"**代謝通貨 / Hypercycle Currency:** {pred['hypercycle_currency']}")
                    if "cascade_summary" in pred:
                        st.markdown("**3段階カスケード / 3-Stage Cascade:**")
                        for stage, detail in pred["cascade_summary"].items():
                            st.caption(f"- {stage}: {detail['action']} ({', '.join(detail['key_players'])})")
        else:
            st.warning(f"経路が見つかりません / Pathway not found: {selected}")

    st.divider()
    st.subheader("全登録基質一覧 / All Registered Substrates")
    st.write(", ".join(substrates))


def render_probiotics():
    st.title("🦠 プロバイオティクス / MBT Probiotics")

    meta_defs = META_STRAIN_DEFINITIONS[
        Language.JA if st.session_state.language == "ja" else Language.EN
    ]

    st.subheader("5つのMBT55メタ株 / 5 MBT55 Meta-Strains")

    for strain_id, definition in meta_defs.items():
        with st.expander(f"🔹 {definition['name']}"):
            st.markdown(f"**機能ユニット / Functional Unit:** {definition['functional_unit']}")
            st.markdown(f"**主要菌種 / Key Species:** {definition['key_species']}")
            st.markdown(f"**生成物 / Produces:** {definition['produces']}")
            st.markdown(f"**標的PATH / Target PATH:** {definition['target_path']}")


def render_kampo_library():
    st.title("💊 漢方ライブラリー / Kampo Library")

    kampo_path = Path(__file__).parent.parent / "data" / "kampo" / "kampo_294_library.json"
    if kampo_path.exists():
        with open(kampo_path, "r", encoding="utf-8") as f:
            kampo_data = json.load(f)
        st.subheader(f"登録漢方処方数 / Registered Formulas: {len(kampo_data) if isinstance(kampo_data, list) else 'N/A'}")
        st.json(kampo_data[:3] if isinstance(kampo_data, list) else kampo_data)
    else:
        st.info("漢方ライブラリーデータがありません / Kampo library data not found")


def render_disease_risk():
    st.title("⚠️ 疾病リスク / Disease Risk")

    disease_path = Path(__file__).parent.parent / "data" / "diseases" / "disease_matrix_137.json"
    if disease_path.exists():
        with open(disease_path, "r", encoding="utf-8") as f:
            disease_data = json.load(f)
        st.subheader("137疾病マトリックス / 137 Disease Matrix")
        st.json(disease_data[:5] if isinstance(disease_data, list) else list(disease_data.keys())[:5])
    else:
        st.info("疾病マトリックスデータがありません / Disease matrix data not found")

    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        st.subheader("あなたの疾病リスク評価 / Your Disease Risk Assessment")
        if result.disease_risks:
            for disease, risk in result.disease_risks.items():
                st.metric(label=disease, value=f"{risk:.1f}%")
        else:
            st.info("顕著なリスクは検出されませんでした")


def render_simulation():
    st.title("🔬 シミュレーション / Simulation")

    st.subheader("3段階酵素カスケード / 3-Stage Enzyme Cascade")
    st.markdown("""
    | Stage | Time | Temp | Oxygen | Key Action |
    |-------|------|------|--------|------------|
    | **Stage 1** | 0-6h | 38°C | Aerobic | 高速加水分解: タンパク質→ペプチド, 多糖→オリゴ糖 |
    | **Stage 2** | 6-24h | 42°C | Microaerophilic | 代謝変換: 脱糖, アグリコン露出 |
    | **Stage 3** | 24-72h | 35°C | Anaerobic | 深部合成: 新規ステロイド, フルボ酸キレート |
    """)

    st.subheader("MBT55 ハイパーサイクル / Hypercycle")
    st.latex(r"\frac{dH_2}{dt} = \delta E - \epsilon (X_m + X_s) H_2 \approx 0")
    st.caption("電子散逸均衡: dH₂/dt≈0 → 腐敗ゼロの数学的証明")


def render_reports():
    st.title("📄 レポート / Reports")

    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result

        st.download_button(
            label="📥 JSONレポートをダウンロード / Download JSON Report",
            data=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            file_name="healthbook_mbt55_report.json",
            mime="application/json",
        )

        st.subheader("📊 統合解析サマリー / Integrated Analysis Summary")
        try:
            st.text(result.format_for_display())
        except Exception:
            st.json(result.to_dict())
    else:
        st.info("まず健康アセスメントを実行してください / Run health assessment first")


def main():
    init_session_state()

    # サイドバーと現在ページの同期
    menu = MENU_JA if st.session_state.language == "ja" else MENU_EN
    reverse_menu = {v: k for k, v in menu.items()}
    if st.session_state.sidebar_menu not in menu:
        st.session_state.sidebar_menu = reverse_menu.get(st.session_state.current_page, list(menu.keys())[0])
    st.session_state.current_page = menu.get(st.session_state.sidebar_menu, "home")

    render_sidebar()

    pages = {
        "home": render_home,
        "health_assessment": render_health_assessment,
        "metabolic_analysis": render_metabolic_analysis,
        "probiotics": render_probiotics,
        "kampo_library": render_kampo_library,
        "disease_risk": render_disease_risk,
        "simulation": render_simulation,
        "reports": render_reports,
    }

    page_func = pages.get(st.session_state.current_page, render_home)
    page_func()


if __name__ == "__main__":
    main()