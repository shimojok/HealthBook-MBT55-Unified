"""
HealthBook-MBT55-Unified Streamlit Dashboard
完全リライト版 — ページ遷移完全解決・全機能統合
"""
import streamlit as st
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
from src.core.page_router import (
    get_menu_items, get_current_page, navigate_to,
    PAGE_HOME, PAGE_ASSESS, PAGE_METABOLIC, PAGE_PROBIOTICS,
    PAGE_KAMPO, PAGE_DISEASE, PAGE_SIMULATION, PAGE_REPORTS,
)
from src.core.i18n_dict import get_text
from src.integration.full_pipeline import FullPipeline
from src.layer2_metabolism.pathway_database import get_pathway_database

st.set_page_config(page_title="HealthBook-MBT55 Unified", page_icon="🏥", layout="wide")

# ── セッション初期化 ──
def init_session():
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGE_HOME

init_session()
LANG = st.session_state.language
T = lambda key: get_text(key, LANG)

# ── 問診データ ──
@st.cache_data
def load_questionnaire(lang: str):
    base = Path(__file__).parent.parent
    filename = f"healthbook_200_{lang}.json"
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
    menu = get_menu_items()
    labels = [m[0] for m in menu]
    page_ids = [m[1] for m in menu]
    
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        st.caption(T("app_subtitle"))
        
        lang = st.selectbox(
            T("language_selector"),
            ["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English"
        )
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.divider()
        st.markdown(f"### {T('sidebar_menu_title')}")
        
        current = get_current_page()
        current_label = labels[0]
        for i, pid in enumerate(page_ids):
            if pid == current:
                current_label = labels[i]
                break
        
        selected = st.radio(
            "nav",
            options=labels,
            index=labels.index(current_label),
            label_visibility="collapsed",
            key=f"nav_{st.session_state.language}"
        )
        
        new_page = page_ids[labels.index(selected)]
        if new_page != current:
            navigate_to(new_page)
            st.rerun()

# ── ホーム ──
def render_home():
    st.title(T("home_title"))
    st.markdown(T("home_description"))
    
    col1, col2, col3 = st.columns(3)
    col1.metric(T("home_pathways_metric"), "20+", delta="10 base + 10 planned")
    col2.metric(T("home_strains_metric"), "5", delta="From 55 functional units")
    col3.metric(T("home_diseases_metric"), "137", delta="Full matrix")
    
    st.divider()
    st.subheader(T("home_quickstart"))
    st.caption(T("home_start_caption"))
    
    # ★★★ 最重要：赤ボタン ★★★
    if st.button(T("home_start_button"), type="primary", use_container_width=True, key="home_start_btn"):
        navigate_to(PAGE_ASSESS)
        st.rerun()

# ── 健康アセスメント ──
def render_health_assessment():
    language = Language.JA if LANG == "ja" else Language.EN
    st.title(T("assess_title"))
    
    q_data = load_questionnaire(LANG)
    if q_data is None:
        st.error(T("error_no_questionnaire"))
        st.info("HealthBook-AIリポジトリから data/questionnaires/healthbook_200_ja.json をコピーしてください。")
        st.info("または、以下のリンクからファイルを確認: https://github.com/shimojok/HealthBook-AI")
        return
    
    flat = flatten_symptoms(q_data)
    all_symptoms = list(flat.keys())
    categories = {}
    for s, cat in flat.items():
        categories.setdefault(cat, []).append(s)
    
    t1, t2, t3, t4 = st.tabs([
        T("assess_questionnaire_tab"),
        T("assess_results_tab"),
        T("assess_strains_tab"),
        T("assess_disease_tab"),
    ])
    
    with t1:
        st.subheader("200項目健康問診" if LANG == "ja" else "200-Item Health Questionnaire")
        st.caption("当てはまる症状すべてにチェックを入れてください" if LANG == "ja" else "Check all symptoms that apply to you")
        
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button(T("assess_select_all"), use_container_width=True, key="select_all"):
            for s in all_symptoms:
                st.session_state[f"qs_{s}"] = True
            st.rerun()
        if cb.button(T("assess_clear_all"), use_container_width=True, key="clear_all"):
            for s in all_symptoms:
                st.session_state[f"qs_{s}"] = False
            st.rerun()
        
        st.divider()
        
        answers = {}
        for cat, symptoms in categories.items():
            st.markdown(f"### {cat}")
            cols = st.columns(3)
            for i, s in enumerate(symptoms):
                with cols[i % 3]:
                    key = f"qs_{s}"
                    val = st.checkbox(s, value=st.session_state.get(key, False), key=key)
                    answers[s] = val
        
        st.divider()
        
        if st.button(T("assess_run_button"), type="primary", use_container_width=True, key="run_analysis"):
            with st.spinner(T("assess_running")):
                pipeline = FullPipeline(language=language)
                result = pipeline.run(answers)
                st.session_state.pipeline_result = result
            st.success(T("assess_complete"))
    
    with t2:
        result = st.session_state.pipeline_result
        if result and result.phenotype and result.phenotype.scores:
            defs = PATH_DEFINITIONS.get(language, {})
            st.subheader("📊 PATH_01〜05 代謝経路活性スコア")
            
            import plotly.graph_objects as go
            cats_l, vals_l = [], []
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                cats_l.append(d.get("short", pid.value))
                vals_l.append(ps.score)
            
            if cats_l:
                fig = go.Figure(data=go.Scatterpolar(
                    r=vals_l, theta=cats_l, fill='toself',
                    line=dict(color='#00B4D8', width=2),
                    fillcolor='rgba(0,180,216,0.25)'
                ))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"### {T('assess_overall')}: **{result.phenotype.overall_status}**")
            st.divider()
            
            for pid, ps in result.phenotype.scores.items():
                d = defs.get(pid, {})
                x1, x2, x3, x4 = st.columns([2, 1, 1, 2])
                x1.write(f"**{d.get('name', pid.value)}**")
                x2.metric("Score", f"{ps.score:.0f}%")
                c = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
                x3.markdown(f"<span style='color:{c};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)
                x4.caption(d.get("high_meaning", "") if ps.score >= 50 else d.get("low_meaning", ""))
        else:
            st.info(T("assess_no_data"))
    
    with t3:
        result = st.session_state.pipeline_result
        if result and result.probiotic_screening:
            screening = result.probiotic_screening
            st.subheader("🦠 推奨MBT55メタ株")
            
            if screening.recommended_strains:
                for strain in screening.recommended_strains:
                    st.markdown(f"### P{strain.priority}: {strain.name}")
                    st.write(strain.reason)
                    if strain.compatible_substrates:
                        st.caption(f"🧪 適合基質: {', '.join(strain.compatible_substrates)}")
                    st.divider()
                
                if screening.combination_proposal:
                    st.info(screening.combination_proposal)
            
            if result.expected_effects:
                st.subheader("✨ 期待効果")
                for e in result.expected_effects:
                    st.markdown(f"✅ {e}")
            
            if result.recommended_kampo:
                st.subheader("💊 推奨漢方・生薬")
                st.write(", ".join(result.recommended_kampo))
        else:
            st.info(T("assess_no_data"))
    
    with t4:
        result = st.session_state.pipeline_result
        if result and result.disease_risks:
            st.subheader("⚠️ 137疾病リスク評価")
            for disease, risk in result.disease_risks.items():
                st.metric(label=disease, value=f"{risk:.1f}%")
        else:
            st.info(T("assess_no_data"))

# ── 代謝解析 ──
def render_metabolic_analysis():
    st.title(T("metabolic_title"))
    db = get_pathway_database()
    substrates = db.list_all_substrates()
    
    if substrates:
        sel = st.selectbox("🔍 基質（生薬・ポリフェノール）を選択してください", substrates)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    with st.container():
                        st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                        st.write(f"**ヒト効果**: {', '.join(p['human_effects'])}")
                        st.write(f"**標的疾病**: {', '.join(p['disease_targets'])}")
                        st.write(f"**代謝通貨**: {p['hypercycle_currency']}")
                        if "cascade_summary" in p:
                            st.caption("**3段階カスケード**:")
                            for stage, detail in p["cascade_summary"].items():
                                st.caption(f"  - {stage}: {detail['action']} (菌: {', '.join(detail['key_players'])})")
                        st.divider()
        
        st.subheader("📋 全登録基質一覧")
        st.write(", ".join(substrates))
    else:
        st.warning("代謝経路データが読み込めません。data/pathways/master_pathways.json を確認してください。")

# ── プロバイオティクス ──
def render_probiotics():
    st.title(T("probiotics_title"))
    lang = Language.JA if LANG == "ja" else Language.EN
    meta_defs = META_STRAIN_DEFINITIONS.get(lang, {})
    
    st.markdown("""
    MBT55の**55の機能的ユニット**を、臨床応用のために**5つのメタ株**に集約しています。
    各メタ株は、特定の代謝経路（PATH_01〜05）に対応し、固有の代謝通貨を生成します。
    """ if LANG == "ja" else """
    The **55 functional units** of MBT55 are consolidated into **5 Meta-Strains** for clinical application.
    Each Meta-Strain corresponds to a specific metabolic pathway (PATH_01-05) and produces unique metabolic currencies.
    """)
    
    for sid, d in meta_defs.items():
        with st.expander(f"🔹 {d['name']} ({sid})"):
            st.markdown(f"**機能ユニット / Functional Unit:** {d['functional_unit']}")
            st.markdown(f"**主要菌種 / Key Species:** {d['key_species']}")
            st.markdown(f"**生成物 / Produces:** {d['produces']}")
            st.markdown(f"**標的PATH / Target PATH:** {d['target_path']}")

# ── 漢方ライブラリー ──
def render_kampo_library():
    st.title(T("kampo_title"))
    
    kampo_path = Path(__file__).parent.parent / "data" / "kampo" / "kampo_294_library.json"
    animal_path = Path(__file__).parent.parent / "data" / "kampo" / "animal_derived_library.json"
    
    if kampo_path.exists():
        with open(kampo_path, "r", encoding="utf-8") as f:
            kampo_data = json.load(f)
        st.subheader(f"📚 294漢方処方ライブラリー（{len(kampo_data) if isinstance(kampo_data, list) else 'loaded'}）")
        if isinstance(kampo_data, list) and len(kampo_data) > 0:
            st.json(kampo_data[:2])
    else:
        st.info("294漢方処方データがありません。")
    
    if animal_path.exists():
        with open(animal_path, "r", encoding="utf-8") as f:
            animal_data = json.load(f)
        st.subheader(f"🦌 動物性生薬ライブラリー（{len(animal_data) if isinstance(animal_data, list) else 'loaded'}）")
        if isinstance(animal_data, list) and len(animal_data) > 0:
            st.json(animal_data[:2])
    else:
        st.info("動物性生薬データがありません。")

# ── 疾病リスク ──
def render_disease_risk():
    st.title(T("disease_title"))
    
    disease_path = Path(__file__).parent.parent / "data" / "diseases" / "disease_matrix_137.json"
    if disease_path.exists():
        with open(disease_path, "r", encoding="utf-8") as f:
            disease_data = json.load(f)
        st.subheader("📊 137疾病マトリックス")
        st.json(disease_data if isinstance(disease_data, dict) else {"count": len(disease_data)})
    else:
        st.info("疾病マトリックスデータがありません。")
    
    if st.session_state.pipeline_result and st.session_state.pipeline_result.disease_risks:
        st.subheader("🔍 あなたの疾病リスク評価")
        for d, r in st.session_state.pipeline_result.disease_risks.items():
            st.metric(label=d, value=f"{r:.1f}%")

# ── シミュレーション ──
def render_simulation():
    st.title(T("simulation_title"))
    
    st.markdown("""
    ## 3段階酵素カスケード
    
    MBT55は、温度と酸素濃度を段階的に変化させることで、生薬成分を効率的に活性代謝物へ変換します。
    このプロセスは「3段階酵素カスケード」と呼ばれ、MBT55の代謝能力の中核を成します。
    
    | 段階 | 時間 | 温度 | 酸素 | 主な働き |
    |------|------|------|------|----------|
    | **Stage 1** | 0-6h | 38°C | 好気 | **高速加水分解**: タンパク質→ペプチド、多糖→オリゴ糖に分解 |
    | **Stage 2** | 6-24h | 42°C | 微好気 | **代謝変換**: 配糖体の脱糖、アグリコン（活性体）の露出 |
    | **Stage 3** | 24-72h | 35°C | 嫌気 | **深部合成**: 新規ステロイド・フルボ酸キレートの生成 |
    
    **42°Cの意図的熱ストレス**: Stage 2の42°Cは、菌群に熱ストレスを与え、防御物質（二次代謝産物）の産生を促進するための意図的な設定です。
    """ if LANG == "ja" else """
    ## 3-Stage Enzyme Cascade
    
    MBT55 converts herbal components into active metabolites through progressive changes in temperature and oxygen levels.
    
    | Stage | Time | Temp | Oxygen | Key Action |
    |-------|------|------|--------|------------|
    | **Stage 1** | 0-6h | 38°C | Aerobic | High-speed hydrolysis: proteins→peptides, polysaccharides→oligosaccharides |
    | **Stage 2** | 6-24h | 42°C | Microaerophilic | Metabolic transformation: deglycosylation, aglycone exposure |
    | **Stage 3** | 24-72h | 35°C | Anaerobic | Deep synthesis: novel steroids, fulvic acid chelation |
    """)
    
    st.divider()
    
    st.markdown("""
    ## ハイパーサイクルと電子散逸理論
    
    MBT55の安定性は、以下の数式で数学的に証明されています。
    """)
    st.latex(r"\frac{dH_2}{dt} = \delta E - \epsilon (X_m + X_s) H_2 \approx 0")
    
    st.markdown("""
    **解説**: 
    - $H_2$（水素）の生成速度と消費速度が均衡することで、水素の蓄積がゼロになります。
    - 水素の蓄積ゼロ = 電子滞留ゼロ = **腐敗・悪臭が発生しない** という数学的証明です。
    - これは、MBT55が多経路の電子受容体（O₂, NO₃⁻, SO₄²⁻, Fe³⁺）を持つことで実現されています。
    
    ### 3つの代謝通貨
    
    | 通貨 | 種類 | 機能 |
    |------|------|------|
    | **乳酸** | 界面通貨 | 拡散速度が速く、嫌気層深部でMn・Fe還元を駆動。腸内で酪酸へ変換。 |
    | **キノン化合物** | 電子通貨 | 微生物間の電子伝達を加速。ミトコンドリア電子伝達系を補完。 |
    | **フルボ酸** | ミネラル通貨 | 微量元素をキレート保持。植物や人間への栄養受け渡しを媒介。 |
    """ if LANG == "ja" else """
    ## Hypercycle and Electron Dissipation Theory
    
    The stability of MBT55 is mathematically proven by:
    
    **Explanation**:
    - When H₂ production and consumption rates are balanced, hydrogen accumulation becomes zero.
    - Zero H₂ accumulation = zero electron stagnation = **no putrefaction or malodor**.
    - This is achieved through MBT55's multi-pathway electron acceptors (O₂, NO₃⁻, SO₄²⁻, Fe³⁺).
    
    ### Three Metabolic Currencies
    
    | Currency | Type | Function |
    |----------|------|----------|
    | **Lactate** | Interface Currency | Rapid diffusion, drives Mn/Fe reduction in deep anaerobic layers |
    | **Quinones** | Electron Currency | Accelerates inter-species electron transfer, complements mitochondrial ETC |
    | **Fulvic Acid** | Mineral Currency | Chelates trace elements, mediates nutrient delivery |
    """)

# ── レポート ──
def render_reports():
    st.title(T("reports_title"))
    
    result = st.session_state.pipeline_result
    if result:
        st.download_button(
            label="📥 JSONレポートをダウンロード",
            data=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            file_name="healthbook_mbt55_report.json",
            mime="application/json",
            type="primary",
        )
        st.divider()
        st.subheader("📊 統合解析サマリー")
        st.text(result.format_for_display())
    else:
        st.info("まず「健康アセスメント」から解析を実行してください。" if LANG == "ja" else "Please run the Health Assessment first.")

# ── メインルーター ──
ROUTER = {
    PAGE_HOME: render_home,
    PAGE_ASSESS: render_health_assessment,
    PAGE_METABOLIC: render_metabolic_analysis,
    PAGE_PROBIOTICS: render_probiotics,
    PAGE_KAMPO: render_kampo_library,
    PAGE_DISEASE: render_disease_risk,
    PAGE_SIMULATION: render_simulation,
    PAGE_REPORTS: render_reports,
}

def main():
    render_sidebar()
    current = get_current_page()
    render_func = ROUTER.get(current, render_home)
    render_func()

if __name__ == "__main__":
    main()