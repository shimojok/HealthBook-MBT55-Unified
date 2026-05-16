import streamlit as st
import sys
import json
from pathlib import Path

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Language, PATH_DEFINITIONS, META_STRAIN_DEFINITIONS
from src.integration.full_pipeline import FullPipeline

st.set_page_config(page_title="HealthBook MBT55", layout="wide")

# 1. データ読み込み（最速化）
@st.cache_data
def load_q_data(lang):
    qfile = f"data/questionnaires/questionnaire_200_{'jp' if lang=='ja' else 'en'}.json"
    p = Path(__file__).parent.parent / qfile
    if not p.exists(): p = Path(".") / qfile
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", {})
    # 選択肢を「カテゴリ名：症状」の形式でリスト化
    labels = [f"[{v.get('category','問診')}] {v['question']}" for k, v in questions.items()]
    mapping = {f"[{v.get('category','問診')}] {v['question']}": v['question'] for k, v in questions.items()}
    return questions, labels, mapping

# 2. セッション初期化
if "navigation" not in st.session_state: st.session_state.navigation = "Home"
if "result" not in st.session_state: st.session_state.result = None
if "lang" not in st.session_state: st.session_state.lang = "ja"

# 3. サイドバー・ナビゲーション
with st.sidebar:
    st.title("🏥 MBT55 Dashboard")
    st.session_state.lang = st.selectbox("Language", ["ja", "en"])
    st.divider()
    
    # ページ選択（ボタン式）
    if st.button("🏠 ホーム", use_container_width=True): st.session_state.navigation = "Home"
    if st.button("📋 健康アセスメント", use_container_width=True): st.session_state.navigation = "Assess"
    
    st.divider()
    # 【重要】問診の入力をサイドバーに配置することで、メイン画面のフリーズを防ぎます
    if st.session_state.navigation == "Assess":
        st.subheader("📝 問診入力")
        questions, labels, mapping = load_q_data(st.session_state.lang)
        selected = st.multiselect("該当する症状を選んでください", options=labels)
        
        if st.button("🔍 解析を実行する", type="primary", use_container_width=True):
            answers = {q_text: (f"[{questions[qid].get('category','')}] {q_text}" in selected) 
                       for qid, qdata in questions.items() for q_text in [qdata['question']]}
            
            with st.spinner("解析中..."):
                lang_enum = Language.JA if st.session_state.lang == "ja" else Language.EN
                try:
                    st.session_state.result = FullPipeline(language=lang_enum).run(answers)
                    st.success("解析完了！")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# 4. メイン画面の描画
if st.session_state.navigation == "Home":
    st.title("🏥 HealthBook-MBT55 Unified")
    st.markdown("左メニューの「健康アセスメント」から問診を行ってください。")
    if st.button("アセスメントを始める"):
        st.session_state.navigation = "Assess"
        st.rerun()

elif st.session_state.navigation == "Assess":
    st.title("📋 解析結果表示エリア")
    
    if st.session_state.result:
        res = st.session_state.result
        # 結果をタブで表示
        t1, t2, t3 = st.tabs(["📊 代謝スコア", "🦠 推奨菌株", "⚠️ 疾病リスク"])
        
        with t1:
            st.subheader("代謝経路活性状態")
            for pid, ps in res.phenotype.scores.items():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{pid.value}**")
                col2.write(f"{ps.score}% ({ps.level})")
        
        with t2:
            st.subheader("推奨MBT55菌株")
            for s in res.probiotic_screening.recommended_strains:
                st.info(f"**{s.name}**\n\n{s.reason}")
                
        with t3:
            st.subheader("疾病リスク（予測値）")
            for d, r in res.disease_risks.items():
                st.write(f"{d}: {r:.1f}%")
    else:
        st.warning("👈 左サイドバーで症状を選択し、「解析を実行する」ボタンを押してください。")
        st.info("症状を選択するまで、この画面は待機状態になります。")
