"""
HealthBook-MBT55 Unified - Page Router
全てのページ遷移を一元管理し、セッション競合を完全に防止する
"""
import streamlit as st

# ページID定数
PAGE_HOME = "home"
PAGE_ASSESS = "health_assessment"
PAGE_METABOLIC = "metabolic_analysis"
PAGE_PROBIOTICS = "probiotics"
PAGE_KAMPO = "kampo_library"
PAGE_DISEASE = "disease_risk"
PAGE_SIMULATION = "simulation"
PAGE_REPORTS = "reports"

# メニュー定義
MENU_ITEMS_JA = [
    ("🏠 ホーム", PAGE_HOME, "ようこそ"),
    ("📋 健康アセスメント", PAGE_ASSESS, "200項目問診からPATH_01〜05を評価"),
    ("🧬 代謝解析", PAGE_METABOLIC, "生薬・ポリフェノールの代謝経路"),
    ("🦠 MBTプロバイオティクス", PAGE_PROBIOTICS, "5つのメタ株と55の機能ユニット"),
    ("💊 漢方ライブラリー", PAGE_KAMPO, "294処方と動物性生薬"),
    ("⚠️ 疾病リスク", PAGE_DISEASE, "137疾病マトリックス"),
    ("🔬 シミュレーション", PAGE_SIMULATION, "3段階カスケードとハイパーサイクル"),
    ("📄 レポート", PAGE_REPORTS, "解析結果のダウンロード"),
]

MENU_ITEMS_EN = [
    ("🏠 Home", PAGE_HOME, "Welcome"),
    ("📋 Health Assessment", PAGE_ASSESS, "200-item questionnaire to PATH_01-05"),
    ("🧬 Metabolic Analysis", PAGE_METABOLIC, "Herb & polyphenol pathways"),
    ("🦠 MBT Probiotics", PAGE_PROBIOTICS, "5 Meta-Strains & 55 Functional Units"),
    ("💊 Kampo Library", PAGE_KAMPO, "294 formulas & animal-derived herbs"),
    ("⚠️ Disease Risk", PAGE_DISEASE, "137 Disease Matrix"),
    ("🔬 Simulation", PAGE_SIMULATION, "3-Stage Cascade & Hypercycle"),
    ("📄 Reports", PAGE_REPORTS, "Download analysis results"),
]

def get_menu_items():
    """現在の言語に応じたメニュー項目を返す"""
    lang = st.session_state.get("language", "ja")
    return MENU_ITEMS_JA if lang == "ja" else MENU_ITEMS_EN

def get_current_page():
    """現在のページIDを安全に取得"""
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGE_HOME
    return st.session_state.current_page

def navigate_to(page_id: str):
    """ページ遷移を実行（セッション状態を更新してrerun）"""
    st.session_state.current_page = page_id

def get_page_title(page_id: str) -> str:
    """ページIDから表示タイトルを取得"""
    menu = get_menu_items()
    for label, pid, desc in menu:
        if pid == page_id:
            return label
    return "🏠 ホーム"