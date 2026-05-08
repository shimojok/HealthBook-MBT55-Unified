"""
HealthBook-MBT55-Unified Streamlit Dashboard
日英バイリンガル対応・全レイヤー統合表示
"""

import streamlit as st
import sys
from pathlib import Path

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS
from src.integration.full_pipeline import FullPipeline, PipelineResult
from dashboard.i18n.translator import I18nManager


# ページ設定
st.set_page_config(
    page_title="HealthBook-MBT55 Unified",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """セッション状態の初期化"""
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "questionnaire_answers" not in st.session_state:
        st.session_state.questionnaire_answers = {}
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"


def get_i18n() -> I18nManager:
    """翻訳マネージャー取得"""
    return I18nManager(st.session_state.language)


def render_sidebar():
    """サイドバーメニュー"""
    i18n = get_i18n()
    
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80.png?text=MBT55", width=150)
        st.title("🏥 HealthBook-MBT55")
        
        # 言語切替
        lang = st.selectbox(
            "🌐 Language / 言語",
            options=["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English",
            key="lang_selector",
        )
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.divider()
        
        # ナビゲーション
        st.session_state.current_page = st.radio(
            i18n.t("nav.menu"),
            options=[
                "home",
                "health_assessment",
                "metabolic_analysis",
                "probiotics",
                "kampo_library",
                "disease_risk",
                "simulation",
                "reports",
            ],
            format_func=lambda x: i18n.t(f"nav.{x}"),
        )


def render_home():
    """ホーム画面"""
    i18n = get_i18n()
    
    st.title(i18n.t("home.title"))
    st.markdown(i18n.t("home.description"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label=i18n.t("home.pathways"), value="10+", delta="20 target")
    with col2:
        st.metric(label=i18n.t("home.strains"), value="5 Meta", delta="55 units")
    with col3:
        st.metric(label=i18n.t("home.diseases"), value="137", delta="Matrix")
    
    st.divider()
    
    st.subheader(i18n.t("home.quick_start"))
    if st.button(i18n.t("home.start_assessment"), type="primary", use_container_width=True):
        st.session_state.current_page = "health_assessment"
        st.rerun()


def render_health_assessment():
    """健康アセスメント画面"""
    i18n = get_i18n()
    language = Language.JA if st.session_state.language == "ja" else Language.EN
    
    st.title(i18n.t("nav.health_assessment"))
    
    tab1, tab2, tab3 = st.tabs([
        i18n.t("nav.questionnaire"),
        i18n.t("nav.phenotyping"),
        i18n.t("nav.path_scores"),
    ])
    
    with tab1:
        st.subheader(i18n.t("questionnaire.title"))
        
        # 簡易問診フォーム
        symptoms = [
            "甘いもの依存", "午後眠気", "冷え", "疲れやすい", "肌荒れ",
            "炎症", "アレルギー", "関節痛", "集中力低下", "不眠",
            "便秘", "むくみ", "朝食欠食", "胃もたれ", "食欲不振",
            "腹部膨満感", "酒に弱い", "気分落込", "敏感肌", "慢性疲労",
        ] if st.session_state.language == "ja" else [
            "Sugar craving", "Afternoon drowsiness", "Cold sensitivity", "Fatigue", "Skin issues",
            "Inflammation", "Allergies", "Joint pain", "Poor concentration", "Insomnia",
            "Constipation", "Edema", "Skipping breakfast", "Indigestion", "Poor appetite",
            "Bloating", "Alcohol sensitivity", "Low mood", "Sensitive skin", "Chronic fatigue",
        ]
        
        answers = {}
        cols = st.columns(2)
        for i, symptom in enumerate(symptoms):
            with cols[i % 2]:
                answers[symptom] = st.checkbox(symptom, key=f"q_{i}")
        
        if st.button(i18n.t("questionnaire.submit"), type="primary"):
            with st.spinner(i18n.t("questionnaire.analyzing")):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
                st.session_state.questionnaire_answers = answers
            st.success(i18n.t("questionnaire.complete"))
    
    with tab2:
        if st.session_state.pipeline_result:
            result: PipelineResult = st.session_state.pipeline_result
            st.subheader(i18n.t("phenotyping.results"))
            
            # レーダーチャート
            import plotly.graph_objects as go
            
            defs = PATH_DEFINITIONS[language]
            categories = []
            values = []
            for pid, ps in result.phenotype.scores.items():
                categories.append(defs[pid]["short"])
                values.append(ps.score)
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='PATH Score',
                line=dict(color='#00B4D8', width=2),
                fillcolor='rgba(0, 180, 216, 0.25)',
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100]),
                ),
                showlegend=False,
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # スコア詳細
            for pid, ps in result.phenotype.scores.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{defs[pid]['name']}**")
                with col2:
                    st.metric(label="Score", value=f"{ps.score:.0f}%")
                with col3:
                    color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                    st.markdown(f"<span style='color:{color}'>{ps.level}</span>", unsafe_allow_html=True)
        else:
            st.info(i18n.t("questionnaire.no_data"))
    
    with tab3:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            st.subheader(i18n.t("path_scores.detail"))
            st.text(result.format_for_display())


def render_metabolic_analysis():
    """代謝解析画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.metabolic_analysis"))
    
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        
        st.subheader(i18n.t("metabolic.predictions"))
        for pred in result.metabolite_predictions:
            with st.expander(f"🔬 {pred.get('substrate', 'Unknown')}"):
                st.json(pred)
    else:
        st.info(i18n.t("questionnaire.no_data"))


def render_probiotics():
    """プロバイオティクス画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.probiotics"))
    
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        screening = result.probiotic_screening
        
        st.subheader(i18n.t("probiotics.recommendations"))
        
        for strain in screening.recommended_strains:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(
                        label=i18n.t("probiotics.priority"),
                        value=f"#{strain.priority}",
                    )
                with col2:
                    st.markdown(f"### {strain.name}")
                    st.write(strain.reason)
                    st.caption(
                        f"Stage {strain.cascade_stage} | "
                        f"Temp: {strain.optimal_conditions.get('temp', 'N/A')}°C"
                    )
                    st.divider()
    else:
        st.info(i18n.t("questionnaire.no_data"))


def render_kampo_library():
    """漢方ライブラリー画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.kampo_library"))
    st.info("Kampo Library - Full integration in progress")


def render_disease_risk():
    """疾病リスク画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.disease_risk"))
    
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        
        st.subheader(i18n.t("disease.assessment"))
        for disease, risk in result.disease_risks.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{disease}**")
            with col2:
                color = "green" if risk < 30 else "orange" if risk < 60 else "red"
                st.markdown(
                    f"<span style='color:{color};font-size:20px;font-weight:bold'>{risk:.1f}%</span>",
                    unsafe_allow_html=True,
                )
    else:
        st.info(i18n.t("questionnaire.no_data"))


def render_simulation():
    """シミュレーション画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.simulation"))
    st.info("Cascade Simulator - Coming soon")


def render_reports():
    """レポート画面"""
    i18n = get_i18n()
    st.title(i18n.t("nav.reports"))
    
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        
        st.download_button(
            label=i18n.t("reports.download_json"),
            data=str(result.to_dict()),
            file_name="healthbook_mbt55_report.json",
            mime="application/json",
        )
        
        st.subheader(i18n.t("reports.summary"))
        st.text(result.format_for_display())
    else:
        st.info(i18n.t("questionnaire.no_data"))


def main():
    """メイン関数"""
    init_session_state()
    render_sidebar()
    
    # ページルーティング
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