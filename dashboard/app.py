"""
HealthBook-MBT55-Unified Streamlit Dashboard
最終完全版 — 全ボタン動作・全画面連携・結果反映
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

HOME = "home"
ASSESS = "health_assessment"
METABOLIC = "metabolic_analysis"
PROBIOTICS = "probiotics"
KAMPO = "kampo_library"
DISEASE = "disease_risk"
SIM = "simulation"
REPORTS = "reports"

MENU_JA = [
    ("🏠 ホーム", HOME), ("📋 健康アセスメント", ASSESS),
    ("🧬 代謝解析", METABOLIC), ("🦠 プロバイオティクス", PROBIOTICS),
    ("💊 漢方ライブラリー", KAMPO), ("⚠️ 疾病リスク", DISEASE),
    ("🔬 シミュレーション", SIM), ("📄 レポート", REPORTS),
]
MENU_EN = [
    ("🏠 Home", HOME), ("📋 Health Assessment", ASSESS),
    ("🧬 Metabolic Analysis", METABOLIC), ("🦠 Probiotics", PROBIOTICS),
    ("💊 Kampo Library", KAMPO), ("⚠️ Disease Risk", DISEASE),
    ("🔬 Simulation", SIM), ("📄 Reports", REPORTS),
]

@st.cache_data
def load_json(filename):
    for base in [Path(__file__).parent.parent, Path("."), Path("/mount/src/healthbook-mbt55-unified")]:
        p = base / filename
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

def init():
    if "lang" not in st.session_state: st.session_state.lang = "ja"
    if "page" not in st.session_state: st.session_state.page = HOME
    if "result" not in st.session_state: st.session_state.result = None

def sidebar():
    menu = MENU_JA if st.session_state.lang == "ja" else MENU_EN
    labels = [m[0] for m in menu]
    ids = [m[1] for m in menu]
    with st.sidebar:
        st.title("🏥 HealthBook-MBT55")
        lang = st.selectbox("🌐 言語 / Language", ["ja", "en"],
            format_func=lambda x: "日本語" if x == "ja" else "English")
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()
        st.divider()
        try:
            idx = ids.index(st.session_state.page)
        except ValueError:
            idx = 0
        sel = st.radio("メニュー", labels, index=idx, label_visibility="collapsed", key="nav")
        new_page = ids[labels.index(sel)]
        if new_page != st.session_state.page:
            st.session_state.page = new_page
            st.rerun()

# ── 共通：結果表示コンポーネント ──
def show_phenotype_result(result, language):
    """PATH_01〜05スコアとレーダーチャートを表示（全画面共通）"""
    if not result or not result.phenotype or not result.phenotype.scores:
        return
    defs = PATH_DEFINITIONS.get(language, {})
    import plotly.graph_objects as go
    cl, vl = [], []
    for pid, ps in result.phenotype.scores.items():
        d = defs.get(pid, {})
        cl.append(d.get("short", pid.value))
        vl.append(ps.score)
    if cl:
        fig = go.Figure(data=go.Scatterpolar(r=vl, theta=cl, fill='toself',
            line=dict(color='#00B4D8', width=2), fillcolor='rgba(0,180,216,0.25)'))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**総合判定: {result.phenotype.overall_status}**")
    for pid, ps in result.phenotype.scores.items():
        d = defs.get(pid, {})
        x1, x2, x3 = st.columns([3,1,1])
        x1.write(f"**{d.get('name', pid.value)}**")
        x2.metric("Score", f"{ps.score:.0f}%")
        color = "green" if ps.score >= 70 else "orange" if ps.score >= 40 else "red"
        x3.markdown(f"<span style='color:{color};font-weight:bold'>{ps.level}</span>", unsafe_allow_html=True)

def show_strains_result(result):
    """推奨MBT55メタ株を表示（全画面共通）"""
    if not result or not result.probiotic_screening or not result.probiotic_screening.recommended_strains:
        return
    for strain in result.probiotic_screening.recommended_strains:
        st.markdown(f"**P{strain.priority}: {strain.name}**")
        st.write(strain.reason)
        st.divider()
    if result.expected_effects:
        st.subheader("✨ 期待効果")
        for e in result.expected_effects: st.markdown(f"✅ {e}")

def show_disease_risks(result):
    """疾病リスクを表示（全画面共通）"""
    if not result or not result.disease_risks:
        return
    for d, r in result.disease_risks.items():
        st.metric(label=d, value=f"{r:.1f}%")

# ── ホーム ──
def home():
    lang = st.session_state.lang
    T = {
        "ja": {"title": "🏥 HealthBook-MBT55 Unified", "desc": "**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した\n次世代ヘルスケアプラットフォーム。", "btn": "🔴 健康アセスメントを開始する（200項目問診）"},
        "en": {"title": "🏥 HealthBook-MBT55 Unified", "desc": "Next-generation healthcare platform.", "btn": "🔴 Start Health Assessment (200-Item Questionnaire)"}
    }
    t = T.get(lang, T["ja"])
    st.title(t["title"])
    st.markdown(t["desc"])
    c1, c2, c3 = st.columns(3)
    c1.metric("代謝経路 / Pathways", "20+")
    c2.metric("MBT55メタ株 / Strains", "5")
    c3.metric("疾病マトリックス / Diseases", "137")
    st.divider()
    st.subheader("🚀 クイックスタート")
    if st.button(t["btn"], type="primary", use_container_width=True):
        st.session_state.page = ASSESS
        st.rerun()

# ── 健康アセスメント ──
def assessment():
    language = Language.JA if st.session_state.lang == "ja" else Language.EN
    lang = st.session_state.lang
    T = {
        "ja": {"title": "📋 健康アセスメント", "select_all": "✅ すべて選択", "clear_all": "🔄 すべて解除", "run": "🔍 解析を実行する", "complete": "✅ 解析が完了しました！", "no_data": "「解析を実行する」ボタンを押すと結果が表示されます。"},
        "en": {"title": "📋 Health Assessment", "select_all": "✅ Select All", "clear_all": "🔄 Clear All", "run": "🔍 Run Analysis", "complete": "✅ Analysis complete!", "no_data": "Click 'Run Analysis' to see results."}
    }
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    qfile = "questionnaire_200_jp.json" if lang == "ja" else "questionnaire_200_en.json"
    data = load_json(f"data/questionnaires/{qfile}")
    if data is None:
        st.error("⚠️ データファイルが見つかりません。")
        return

    questions = data.get("questions", {})
    cats = {}
    for qid, qdata in questions.items():
        cats.setdefault(qdata.get("category", "その他"), []).append(qdata)
    cat_order = list(data.get("categories", {}).keys()) or list(cats.keys())

    ca, cb, _ = st.columns([1, 1, 4])
    if ca.button(t["select_all"], use_container_width=True):
        for qid in questions: st.session_state[f"q_{qid}"] = True
        st.rerun()
    if cb.button(t["clear_all"], use_container_width=True):
        for qid in questions: st.session_state[f"q_{qid}"] = False
        st.rerun()
    st.divider()

    answers = {}
    for cat_name in cat_order:
        qlist = cats.get(cat_name, [])
        if not qlist: continue
        st.markdown(f"### {cat_name}（{len(qlist)}項目）")
        cols = st.columns(2)
        for i, qdata in enumerate(qlist):
            qid = qdata["id"]
            question_text = qdata["question"]
            key = f"q_{qid}"
            with cols[i % 2]:
                val = st.checkbox(question_text, value=st.session_state.get(key, False), key=key)
                answers[question_text] = val
        st.divider()

    if st.button(t["run"], type="primary", use_container_width=True):
        with st.spinner("MBT55代謝経路を解析中..."):
            result = FullPipeline(language=language).run(answers)
            st.session_state.result = result
        st.success(t["complete"])

    result = st.session_state.result
    if result and result.phenotype and result.phenotype.scores:
        st.divider()
        st.subheader("📊 解析結果")
        show_phenotype_result(result, language)
        st.divider()
        st.subheader("🦠 推奨MBT55メタ株")
        show_strains_result(result)
        st.divider()
        st.subheader("⚠️ 疾病リスク評価")
        show_disease_risks(result)
    elif not result:
        st.info(t["no_data"])

# ── 代謝解析 ──
def metabolic():
    lang = st.session_state.lang
    T = {"ja": {"title": "🧬 代謝解析", "no_data": "まず健康アセスメントで解析を実行してください。"}, "en": {"title": "🧬 Metabolic Analysis", "no_data": "Please run the Health Assessment first."}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    db = get_pathway_database()
    subs = db.list_all_substrates()
    if subs:
        sel = st.selectbox("🔍 基質を選択", subs)
        if sel:
            pred = db.predict_metabolites(sel)
            if pred.get("found"):
                for p in pred["predictions"]:
                    st.markdown(f"### {p['substrate']} → **{p['final_metabolite']}**")
                    st.write(f"効果: {', '.join(p['human_effects'])}")
        st.subheader("📋 全登録基質")
        st.write(", ".join(subs))

    # 解析結果があれば表示
    if st.session_state.result:
        st.divider()
        st.subheader("📊 あなたのPATHスコア")
        language = Language.JA if lang == "ja" else Language.EN
        show_phenotype_result(st.session_state.result, language)
    else:
        st.info(t["no_data"])

# ── プロバイオティクス ──
def probiotics():
    lang = st.session_state.lang
    T = {"ja": {"title": "🦠 プロバイオティクス"}, "en": {"title": "🦠 Probiotics"}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    language = Language.JA if lang == "ja" else Language.EN
    for sid, d in META_STRAIN_DEFINITIONS.get(language, {}).items():
        with st.expander(f"🔹 {d['name']}"):
            st.write(f"機能: {d['functional_unit']} | 菌種: {d['key_species']} | 生成物: {d['produces']}")

    if st.session_state.result:
        st.divider()
        st.subheader("🦠 あなたへの推奨MBT55メタ株")
        show_strains_result(st.session_state.result)
    else:
        st.info("まず健康アセスメントで解析を実行してください。" if lang == "ja" else "Please run the Health Assessment first.")

# ── 漢方ライブラリー ──
def kampo():
    lang = st.session_state.lang
    T = {"ja": {"title": "💊 漢方ライブラリー"}, "en": {"title": "💊 Kampo Library"}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    kampo_data = load_json("data/kampo/kampo_metabolic_library.json")
    if kampo_data and isinstance(kampo_data, list):
        for item in kampo_data[:10]:
            with st.expander(f"💊 {item.get('name', item.get('formula_name', '不明'))}"):
                st.json(item)
    animal_data = load_json("data/kampo/animal_metabolic_library.json")
    if animal_data and isinstance(animal_data, list):
        st.subheader("🦌 動物性生薬")
        for item in animal_data:
            with st.expander(f"🦌 {item.get('name_ja', item.get('name', '不明'))}"):
                st.json(item)

    if st.session_state.result and st.session_state.result.recommended_kampo:
        st.divider()
        st.subheader("💊 あなたへの推奨漢方・生薬")
        st.write(", ".join(st.session_state.result.recommended_kampo))

# ── 疾病リスク ──
def disease():
    lang = st.session_state.lang
    T = {"ja": {"title": "⚠️ 疾病リスク"}, "en": {"title": "⚠️ Disease Risk"}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    disease_data = load_json("data/diseases/disease_matrix_137.json")
    if disease_data and isinstance(disease_data, list):
        for item in disease_data[:10]:
            with st.expander(f"⚠️ {item.get('name', item.get('disease_name', '不明'))}"):
                st.json(item)

    if st.session_state.result:
        st.divider()
        st.subheader("🔍 あなたの疾病リスク評価")
        show_disease_risks(st.session_state.result)
    else:
        st.info("まず健康アセスメントで解析を実行してください。" if lang == "ja" else "Please run the Health Assessment first.")

# ── シミュレーション ──
def sim():
    lang = st.session_state.lang
    T = {"ja": {"title": "🔬 シミュレーション"}, "en": {"title": "🔬 Simulation"}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])
    st.markdown("### 3段階酵素カスケード\n| Stage | 時間 | 温度 | 酸素 |\n|-------|------|------|------|\n| 1 | 0-6h | 38°C | 好気 |\n| 2 | 6-24h | 42°C | 微好気 |\n| 3 | 24-72h | 35°C | 嫌気 |")
    st.latex(r"\frac{dH_2}{dt} \approx 0")

    if st.session_state.result:
        st.divider()
        st.subheader("📊 あなたのPATHスコア")
        language = Language.JA if lang == "ja" else Language.EN
        show_phenotype_result(st.session_state.result, language)

# ── レポート ──
def reports():
    lang = st.session_state.lang
    T = {"ja": {"title": "📄 レポート", "no_data": "まず健康アセスメントで解析を実行してください。"}, "en": {"title": "📄 Reports", "no_data": "Please run the Health Assessment first."}}
    t = T.get(lang, T["ja"])
    st.title(t["title"])

    result = st.session_state.result
    if result:
        st.download_button("📥 JSONダウンロード", json.dumps(result.to_dict(), ensure_ascii=False, indent=2), "report.json", "application/json")
        st.divider()
        language = Language.JA if lang == "ja" else Language.EN
        st.subheader("📊 PATHスコア")
        show_phenotype_result(result, language)
        st.divider()
        st.subheader("🦠 推奨菌株")
        show_strains_result(result)
        st.divider()
        st.subheader("⚠️ 疾病リスク")
        show_disease_risks(result)
    else:
        st.info(t["no_data"])

def main():
    init()
    sidebar()
    pages = {HOME: home, ASSESS: assessment, METABOLIC: metabolic, PROBIOTICS: probiotics,
             KAMPO: kampo, DISEASE: disease, SIM: sim, REPORTS: reports}
    pages.get(st.session_state.page, home)()

if __name__ == "__main__":
    main()
