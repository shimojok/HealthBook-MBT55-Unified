"""
HealthBook-MBT55-Unified Streamlit Dashboard
200項目問診・日英バイリンガル対応・全レイヤー統合表示
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS
from src.integration.full_pipeline import FullPipeline, PipelineResult
from dashboard.i18n.translator import I18nManager

st.set_page_config(
    page_title="HealthBook-MBT55 Unified",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────
# 200項目問診（日本語）
# ─────────────────────────────
HEALTHBOOK_200_JA = {
    "消化器系": {
        "口腔・咽喉": ["口渇", "口内炎ができやすい", "歯ぐきから出血しやすい", "喉がつかえる感じ"],
        "食道・胃": ["胃もたれ", "胸やけ", "げっぷが多い", "空腹時に胃が痛む", "食後に腹痛", "吐き気", "朝食欠食"],
        "腸": ["便秘", "下痢", "腹部膨満感", "過敏性腸症候群", "ガスが溜まりやすい", "食後に眠くなる", "消化不良", "食欲不振"],
        "肝・胆": ["脂っこいものが苦手", "酒に弱い", "二日酔いしやすい", "右肋骨下の張り", "苦味を感じやすい"],
    },
    "代謝・内分泌系": {
        "糖代謝": ["甘いもの依存", "低血糖症状（手の震え・冷や汗）", "食後急激な眠気", "喉が渇きやすい"],
        "エネルギー": ["午後眠気", "冷え", "むくみ", "朝起きられない", "疲れやすい", "脱力感", "運動不足"],
        "体重": ["肥満傾向", "痩せすぎ", "体重変動が激しい"],
    },
    "免疫・炎症系": {
        "炎症": ["慢性的な炎症", "関節痛", "筋肉痛", "原因不明の微熱", "自己免疫疾患の診断あり"],
        "アレルギー": ["アレルギー性鼻炎", "花粉症", "食物アレルギー", "化学物質過敏症", "アトピー性皮膚炎"],
        "皮膚": ["肌荒れ", "敏感肌", "吹き出物", "湿疹", "じんましん", "皮膚の色素沈着"],
    },
    "神経・精神系": {
        "認知": ["集中力低下", "記憶力低下", "判断力低下", "ブレインフォグ"],
        "気分": ["気分落込", "不安感", "イライラ", "パニック", "うつ傾向", "やる気が出ない"],
        "睡眠": ["不眠", "寝つきが悪い", "中途覚醒", "悪夢をよく見る", "寝汗"],
    },
    "循環器・呼吸器系": {
        "心・血管": ["動悸", "息切れ", "胸の圧迫感", "手足のしびれ", "冷え性", "高血圧"],
        "呼吸": ["慢性の咳", "喘息", "痰がからむ", "鼻づまり"],
    },
    "運動器系": {
        "骨・関節": ["関節のこわばり", "腰痛", "肩こり", "変形性関節症"],
        "筋肉": ["筋肉の張り", "こむら返り", "筋力低下"],
    },
    "泌尿・生殖系": {
        "泌尿": ["頻尿", "夜間頻尿", "残尿感", "尿の切れが悪い"],
        "生殖・ホルモン": ["月経不順", "月経痛", "PMS", "更年期症状", "性欲減退", "不妊"],
    },
    "その他": {
        "感覚器": ["目の疲れ", "耳鳴り", "めまい", "立ちくらみ", "ドライアイ"],
        "全身": ["慢性疲労", "微熱が続く", "寝汗", "体重減少", "リンパの腫れ"],
    },
}

# ─────────────────────────────
# 200項目問診（英語・簡易版）
# ─────────────────────────────
HEALTHBOOK_200_EN = {
    "Digestive": {
        "Oral": ["Dry mouth", "Mouth ulcers", "Bleeding gums", "Throat tightness"],
        "Stomach": ["Indigestion", "Heartburn", "Burping", "Hunger pain", "Post-meal pain", "Nausea", "Skipping breakfast"],
        "Intestine": ["Constipation", "Diarrhea", "Bloating", "IBS", "Gas", "Post-meal drowsiness", "Poor digestion", "Low appetite"],
        "Liver/Gall": ["Fatty food intolerance", "Alcohol sensitivity", "Hangover prone", "Right rib tightness", "Bitter taste"],
    },
    "Metabolic": {
        "Sugar": ["Sugar craving", "Hypoglycemia symptoms", "Post-meal crash", "Excessive thirst"],
        "Energy": ["Afternoon drowsiness", "Cold sensitivity", "Edema", "Hard to wake up", "Fatigue", "Weakness", "Lack of exercise"],
        "Weight": ["Obesity tendency", "Underweight", "Weight fluctuation"],
    },
    "Immune/Inflammatory": {
        "Inflammation": ["Chronic inflammation", "Joint pain", "Muscle pain", "Low-grade fever", "Autoimmune diagnosis"],
        "Allergy": ["Allergic rhinitis", "Hay fever", "Food allergy", "Chemical sensitivity", "Atopic dermatitis"],
        "Skin": ["Skin issues", "Sensitive skin", "Acne", "Eczema", "Hives", "Hyperpigmentation"],
    },
    "Neuro/Psychiatric": {
        "Cognitive": ["Poor concentration", "Memory loss", "Poor judgment", "Brain fog"],
        "Mood": ["Low mood", "Anxiety", "Irritability", "Panic", "Depression tendency", "Low motivation"],
        "Sleep": ["Insomnia", "Trouble falling asleep", "Mid-sleep waking", "Nightmares", "Night sweats"],
    },
    "Cardio/Respiratory": {
        "Heart": ["Palpitations", "Shortness of breath", "Chest tightness", "Numbness", "Cold extremities", "Hypertension"],
        "Respiratory": ["Chronic cough", "Asthma", "Phlegm", "Nasal congestion"],
    },
    "Musculoskeletal": {
        "Bone/Joint": ["Joint stiffness", "Lower back pain", "Shoulder stiffness", "Osteoarthritis"],
        "Muscle": ["Muscle tension", "Leg cramps", "Muscle weakness"],
    },
    "Uro/Reproductive": {
        "Urinary": ["Frequent urination", "Nocturia", "Residual urine", "Weak stream"],
        "Reproductive": ["Irregular periods", "Menstrual pain", "PMS", "Menopause symptoms", "Low libido", "Infertility"],
    },
    "Other": {
        "Sensory": ["Eye fatigue", "Tinnitus", "Dizziness", "Lightheadedness", "Dry eye"],
        "Whole body": ["Chronic fatigue", "Persistent low fever", "Night sweats", "Weight loss", "Swollen lymph nodes"],
    },
}


def flatten_symptoms(symptom_dict):
    """ネストされた症状辞書をフラットなリストに変換"""
    result = {}
    for category, subcategories in symptom_dict.items():
        for sub, symptoms in subcategories.items():
            for symptom in symptoms:
                result[symptom] = {"category": category, "subcategory": sub}
    return result


def init_session_state():
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "questionnaire_answers" not in st.session_state:
        st.session_state.questionnaire_answers = {}
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"


def get_i18n():
    return I18nManager(st.session_state.language)


def render_sidebar():
    i18n = get_i18n()
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80.png?text=MBT55", width=150)
        st.title("🏥 HealthBook-MBT55")

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
        st.markdown("### 📋 メニュー")

        menu_options = [
            "home",
            "health_assessment",
            "metabolic_analysis",
            "probiotics",
            "kampo_library",
            "disease_risk",
            "simulation",
            "reports",
        ]
        menu_labels = [i18n.t(f"nav.{x}") for x in menu_options]

        selected_label = st.radio(
            "メニュー選択",
            options=menu_labels,
            label_visibility="collapsed",
        )
        selected_index = menu_labels.index(selected_label)
        st.session_state.current_page = menu_options[selected_index]


def render_home():
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
    i18n = get_i18n()
    language = Language.JA if st.session_state.language == "ja" else Language.EN

    st.title(i18n.t("nav.health_assessment"))

    # 200項目問診データの選択
    if st.session_state.language == "ja":
        health_data = HEALTHBOOK_200_JA
    else:
        health_data = HEALTHBOOK_200_EN

    flat_symptoms = flatten_symptoms(health_data)

    tab1, tab2, tab3, tab4 = st.tabs([
        i18n.t("nav.questionnaire"),
        "📊 フェノタイピング結果",
        "🦠 菌株推奨",
        "⚠️ 疾病リスク",
    ])

    with tab1:
        st.subheader("200項目健康問診")
        st.caption("当てはまる症状にチェックを入れてください。「すべて選択」で全チェックも可能です。")

        # 全選択/全解除ボタン
        col_select_all, col_clear_all, _ = st.columns([1, 1, 4])
        with col_select_all:
            if st.button("✅ すべて選択", use_container_width=True):
                for key in st.session_state:
                    if key.startswith("symptom_"):
                        st.session_state[key] = True
                st.rerun()
        with col_clear_all:
            if st.button("🔄 すべて解除", use_container_width=True):
                for key in st.session_state:
                    if key.startswith("symptom_"):
                        st.session_state[key] = False
                st.rerun()

        st.divider()

        # カテゴリ別に症状を表示
        answers = {}
        symptom_index = 0
        for category, subcategories in health_data.items():
            st.markdown(f"### {category}")
            for sub, symptoms in subcategories.items():
                st.markdown(f"**{sub}**")
                cols = st.columns(3)
                for i, symptom in enumerate(symptoms):
                    with cols[i % 3]:
                        key = f"symptom_{symptom_index}"
                        checked = st.checkbox(
                            symptom,
                            value=st.session_state.get(key, False),
                            key=key,
                        )
                        answers[symptom] = checked
                        symptom_index += 1

        st.divider()

        if st.button("🔍 解析を実行する", type="primary", use_container_width=True):
            with st.spinner("MBT55代謝経路を解析中..."):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
                st.session_state.questionnaire_answers = answers
            st.success("✅ 解析が完了しました！下のタブで結果を確認してください。")

    with tab2:
        if st.session_state.pipeline_result:
            result: PipelineResult = st.session_state.pipeline_result
            defs = PATH_DEFINITIONS.get(language, {})

            st.subheader("📊 PATH_01〜05 代謝経路活性スコア")

            # レーダーチャート
            import plotly.graph_objects as go
            categories = []
            values = []
            for pid, ps in result.phenotype.scores.items():
                path_def = defs.get(pid, {})
                categories.append(path_def.get("short", pid.value))
                values.append(ps.score)

            if categories and values:
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

            # 全体ステータス
            st.markdown(f"### 総合判定: **{result.phenotype.overall_status}**")

            st.divider()

            # 各PATHスコア詳細
            for pid, ps in result.phenotype.scores.items():
                path_def = defs.get(pid, {})
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                with col1:
                    st.write(f"**{path_def.get('name', pid.value)}**")
                with col2:
                    st.metric(label="Score", value=f"{ps.score:.0f}%")
                with col3:
                    color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                    st.markdown(
                        f"<span style='color:{color};font-weight:bold;font-size:18px'>{ps.level}</span>",
                        unsafe_allow_html=True,
                    )
                with col4:
                    desc = path_def.get("high_meaning", "") if ps.score >= 50 else path_def.get("low_meaning", "")
                    st.caption(desc)
        else:
            st.info("「解析を実行する」ボタンを押すと、ここに結果が表示されます。")

    with tab3:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            screening = result.probiotic_screening

            st.subheader("🦠 推奨MBT55メタ株")

            if screening and screening.recommended_strains:
                for strain in screening.recommended_strains:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.metric(label="優先度", value=f"P{strain.priority}")
                        with col2:
                            st.markdown(f"### {strain.name}")
                            st.write(strain.reason)
                            opt = strain.optimal_conditions
                            if isinstance(opt, dict):
                                st.caption(
                                    f"⏱ Stage {strain.cascade_stage} | "
                                    f"🌡 Temp: {opt.get('temp', 'N/A')}°C | "
                                    f"📊 pH: {opt.get('ph', 'N/A')}"
                                )
                            if strain.compatible_substrates:
                                st.caption(f"🧪 適合基質: {', '.join(strain.compatible_substrates)}")
                        st.divider()

            # 複合提案
            if screening and screening.combination_proposal:
                st.info(screening.combination_proposal)

            # 期待効果
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for effect in result.expected_effects:
                    st.markdown(f"✅ {effect}")
        else:
            st.info("「解析を実行する」ボタンを押すと、ここに結果が表示されます。")

    with tab4:
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result

            st.subheader("⚠️ 疾病リスク評価（137疾病マトリックス）")
            if result.disease_risks:
                for disease, risk in result.disease_risks.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{disease}**")
                    with col2:
                        color = "green" if risk < 30 else "orange" if risk < 60 else "red"
                        st.markdown(
                            f"<span style='color:{color};font-size:18px;font-weight:bold'>{risk:.1f}%</span>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("顕著な疾病リスクは検出されませんでした。")

            # 推奨漢方
            if result.recommended_kampo:
                st.divider()
                st.subheader("💊 推奨漢方・生薬")
                for kampo in result.recommended_kampo:
                    st.markdown(f"- {kampo}")
        else:
            st.info("「解析を実行する」ボタンを押すと、ここに結果が表示されます。")


def render_metabolic_analysis():
    i18n = get_i18n()
    st.title("🧬 代謝解析")
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        st.subheader("代謝物予測")
        if result.metabolite_predictions:
            for pred in result.metabolite_predictions:
                with st.expander(f"🔬 {pred.get('substrate', 'Unknown')}"):
                    st.json(pred)
        else:
            st.info("代謝物予測はありません")
    else:
        st.info("まず健康アセスメントを実行してください。")


def render_probiotics():
    i18n = get_i18n()
    st.title("🦠 プロバイオティクス")
    st.info("MBT55メタ株ライブラリー - 開発中")


def render_kampo_library():
    i18n = get_i18n()
    st.title("💊 漢方ライブラリー")
    st.info("294漢方処方ライブラリー - 開発中")


def render_disease_risk():
    i18n = get_i18n()
    st.title("⚠️ 疾病リスク")
    st.info("137疾病マトリックス詳細 - 開発中")


def render_simulation():
    i18n = get_i18n()
    st.title("🔬 シミュレーション")
    st.info("3段階カスケードシミュレータ - 開発中")


def render_reports():
    i18n = get_i18n()
    st.title("📄 レポート")
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        st.download_button(
            label="📥 JSONレポートをダウンロード",
            data=str(result.to_dict()),
            file_name="healthbook_mbt55_report.json",
            mime="application/json",
        )
        st.subheader("統合解析サマリー")
        try:
            st.text(result.format_for_display())
        except Exception:
            st.json(result.to_dict())
    else:
        st.info("まず健康アセスメントを実行してください。")


def main():
    init_session_state()
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