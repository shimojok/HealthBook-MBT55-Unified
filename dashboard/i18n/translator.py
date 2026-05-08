"""
I18nManager — 日英統合翻訳マネージャー
"""

from typing import Dict


class I18nManager:
    """日英統合翻訳マネージャー"""
    
    SUPPORTED_LANGUAGES = {
        "ja": "日本語",
        "en": "English",
    }
    
    def __init__(self, lang: str = "ja"):
        self.lang = lang if lang in self.SUPPORTED_LANGUAGES else "ja"
        self.translations: Dict[str, str] = self._load_translations()
    
    def t(self, key: str, default: str = None) -> str:
        """翻訳キーから表示テキストを取得"""
        value = self.translations.get(key)
        if value is None:
            return default or key
        return value
    
    def _load_translations(self) -> Dict[str, str]:
        """言語辞書を読み込み"""
        if self.lang == "ja":
            return {
                # ナビゲーション
                "nav.menu": "📋 メニュー",
                "nav.home": "🏠 ホーム",
                "nav.health_assessment": "📋 健康アセスメント",
                "nav.questionnaire": "📝 問診入力",
                "nav.phenotyping": "📊 フェノタイピング結果",
                "nav.path_scores": "📈 PATH_01〜05スコア",
                "nav.metabolic_analysis": "🧬 代謝解析",
                "nav.probiotics": "🦠 プロバイオティクス",
                "nav.kampo_library": "💊 漢方ライブラリー",
                "nav.disease_risk": "⚠️ 疾病リスク",
                "nav.simulation": "🔬 シミュレーション",
                "nav.reports": "📄 レポート",
                "nav.settings": "⚙️ 設定",
                
                # ホーム
                "home.title": "🏥 HealthBook-MBT55 Unified",
                "home.description": (
                    "MBT55微生物群による**全代謝経路解析**と"
                    "**フェノタイピング**、**MBT Probioticsスクリーニング**を統合した"
                    "次世代ヘルスケアプラットフォーム。\n\n"
                    "200項目問診から、あなたの代謝経路活性状態（PATH_01〜05）を評価し、"
                    "最適な漢方・生薬・MBT55菌株セットを提案します。"
                ),
                "home.pathways": "代謝経路",
                "home.strains": "メタ菌株",
                "home.diseases": "疾病マトリックス",
                "home.quick_start": "🚀 クイックスタート",
                "home.start_assessment": "健康アセスメントを開始する",
                
                # 問診
                "questionnaire.title": "200項目問診（簡易版）",
                "questionnaire.submit": "解析を実行する",
                "questionnaire.analyzing": "MBT55代謝経路を解析中...",
                "questionnaire.complete": "解析が完了しました！",
                "questionnaire.no_data": "まずは問診タブで健康状態を入力してください。",
                
                # フェノタイピング
                "phenotyping.results": "フェノタイピング結果",
                "path_scores.detail": "PATH_01〜05 スコア詳細",
                
                # 代謝
                "metabolic.predictions": "代謝物予測",
                
                # プロバイオティクス
                "probiotics.recommendations": "MBT55メタ株推奨",
                "probiotics.priority": "優先度",
                
                # 疾病
                "disease.assessment": "疾病リスク評価",
                
                # レポート
                "reports.download_json": "📥 JSONレポートをダウンロード",
                "reports.summary": "📊 統合解析サマリー",
            }
        else:
            return {
                "nav.menu": "📋 Menu",
                "nav.home": "🏠 Home",
                "nav.health_assessment": "📋 Health Assessment",
                "nav.questionnaire": "📝 Questionnaire",
                "nav.phenotyping": "📊 Phenotyping Results",
                "nav.path_scores": "📈 PATH Scores",
                "nav.metabolic_analysis": "🧬 Metabolic Analysis",
                "nav.probiotics": "🦠 Probiotics",
                "nav.kampo_library": "💊 Kampo Library",
                "nav.disease_risk": "⚠️ Disease Risk",
                "nav.simulation": "🔬 Simulation",
                "nav.reports": "📄 Reports",
                "nav.settings": "⚙️ Settings",
                
                "home.title": "🏥 HealthBook-MBT55 Unified",
                "home.description": (
                    "Next-generation healthcare platform integrating **full metabolic pathway analysis**, "
                    "**phenotyping**, and **MBT Probiotics screening** with MBT55 microbial consortium.\n\n"
                    "From a 200-item questionnaire, we assess your metabolic pathway activity (PATH_01-05) "
                    "and recommend optimal Kampo, herbs, and MBT55 strain sets."
                ),
                "home.pathways": "Pathways",
                "home.strains": "Meta-Strains",
                "home.diseases": "Disease Matrix",
                "home.quick_start": "🚀 Quick Start",
                "home.start_assessment": "Start Health Assessment",
                
                "questionnaire.title": "200-Item Questionnaire (Simplified)",
                "questionnaire.submit": "Run Analysis",
                "questionnaire.analyzing": "Analyzing MBT55 metabolic pathways...",
                "questionnaire.complete": "Analysis complete!",
                "questionnaire.no_data": "Please complete the questionnaire first.",
                
                "phenotyping.results": "Phenotyping Results",
                "path_scores.detail": "PATH_01-05 Score Details",
                
                "metabolic.predictions": "Metabolite Predictions",
                
                "probiotics.recommendations": "MBT55 Meta-Strain Recommendations",
                "probiotics.priority": "Priority",
                
                "disease.assessment": "Disease Risk Assessment",
                
                "reports.download_json": "📥 Download JSON Report",
                "reports.summary": "📊 Integrated Analysis Summary",
            }