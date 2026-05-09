"""
HealthBook-MBT55 Unified - 国際化辞書
全てのUIテキストを言語別に定義
"""

TEXTS = {
    "ja": {
        "app_title": "🏥 HealthBook-MBT55 Unified",
        "app_subtitle": "全代謝経路解析 × フェノタイピング × MBT Probiotics",
        "language_selector": "🌐 言語",
        "sidebar_menu_title": "📋 メニュー",
        
        # ホーム
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_description": """
**全代謝経路解析**・**フェノタイピング**・**MBT Probioticsスクリーニング**を統合した
次世代ヘルスケアプラットフォームです。

MBT55微生物群（立山連峰山麓由来、120〜2,000+菌種）が、
漢方生薬・ポリフェノール・動物性生薬をヒト有用代謝産物へ変換する全プロセスを解析します。

### 主な機能
- **200項目問診** → PATH_01〜05 代謝経路活性スコアを計算
- **MBT55メタ株推奨** → 不足する代謝経路を補完する最適菌株を提案
- **生薬・漢方推奨** → 個人の代謝状態に合わせた漢方処方を提案
- **全代謝経路検索** → 20種類以上の生薬の微生物代謝経路を表示
""",
        "home_pathways_metric": "代謝経路",
        "home_strains_metric": "MBT55メタ株",
        "home_diseases_metric": "疾病マトリックス",
        "home_quickstart": "🚀 クイックスタート",
        "home_start_button": "🔴 健康アセスメントを開始する（200項目問診）",
        "home_start_caption": "クリックすると健康アセスメント画面に移動します",
        
        # 健康アセスメント
        "assess_title": "📋 健康アセスメント",
        "assess_questionnaire_tab": "📝 問診入力",
        "assess_results_tab": "📊 フェノタイピング結果",
        "assess_strains_tab": "🦠 菌株推奨",
        "assess_disease_tab": "⚠️ 疾病リスク",
        "assess_select_all": "✅ すべて選択",
        "assess_clear_all": "🔄 すべて解除",
        "assess_run_button": "🔍 解析を実行する",
        "assess_running": "MBT55代謝経路を解析中...",
        "assess_complete": "✅ 解析が完了しました！タブを切り替えて結果を確認してください。",
        "assess_no_data": "解析を実行すると、ここに結果が表示されます。",
        "assess_overall": "総合判定",
        
        # 他画面
        "metabolic_title": "🧬 代謝解析",
        "probiotics_title": "🦠 MBTプロバイオティクス",
        "kampo_title": "💊 漢方ライブラリー",
        "disease_title": "⚠️ 疾病リスク",
        "simulation_title": "🔬 シミュレーション",
        "reports_title": "📄 レポート",
        
        "error_no_questionnaire": "⚠️ 問診データファイルが見つかりません。",
    },
    "en": {
        "app_title": "🏥 HealthBook-MBT55 Unified",
        "app_subtitle": "Full Metabolic Pathway Analysis × Phenotyping × MBT Probiotics",
        "language_selector": "🌐 Language",
        "sidebar_menu_title": "📋 Menu",
        
        "home_title": "🏥 HealthBook-MBT55 Unified",
        "home_description": """
Next-generation healthcare platform integrating **full metabolic pathway analysis**,
**phenotyping**, and **MBT Probiotics screening**.

The MBT55 microbial consortium (120-2,000+ species from Tateyama, Japan) 
transforms Kampo herbs, polyphenols, and animal-derived natural products 
into therapeutically active compounds for human health.

### Key Features
- **200-Item Questionnaire** → PATH_01-05 metabolic pathway activity scores
- **MBT55 Meta-Strain Recommendation** → Optimal strains to compensate deficient pathways
- **Kampo & Herb Recommendation** → Personalized herbal formulas
- **Pathway Search** → 20+ substrate metabolic pathway maps
""",
        "home_pathways_metric": "Pathways",
        "home_strains_metric": "MBT55 Meta-Strains",
        "home_diseases_metric": "Disease Matrix",
        "home_quickstart": "🚀 Quick Start",
        "home_start_button": "🔴 Start Health Assessment (200-Item Questionnaire)",
        "home_start_caption": "Click to navigate to the health assessment page",
        
        "assess_title": "📋 Health Assessment",
        "assess_questionnaire_tab": "📝 Questionnaire",
        "assess_results_tab": "📊 Phenotyping Results",
        "assess_strains_tab": "🦠 Strain Recommendations",
        "assess_disease_tab": "⚠️ Disease Risk",
        "assess_select_all": "✅ Select All",
        "assess_clear_all": "🔄 Clear All",
        "assess_run_button": "🔍 Run Analysis",
        "assess_running": "Analyzing MBT55 metabolic pathways...",
        "assess_complete": "✅ Analysis complete! Switch tabs to view results.",
        "assess_no_data": "Run the analysis to see results here.",
        "assess_overall": "Overall Assessment",
        
        "metabolic_title": "🧬 Metabolic Analysis",
        "probiotics_title": "🦠 MBT Probiotics",
        "kampo_title": "💊 Kampo Library",
        "disease_title": "⚠️ Disease Risk",
        "simulation_title": "🔬 Simulation",
        "reports_title": "📄 Reports",
        
        "error_no_questionnaire": "⚠️ Questionnaire data file not found.",
    }
}

def get_text(key: str, lang: str = "ja") -> str:
    """指定されたキーの翻訳テキストを取得"""
    return TEXTS.get(lang, TEXTS["ja"]).get(key, key)