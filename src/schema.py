from pydantic import BaseModel, Field
from typing import List

class GakuchikaAnalysis(BaseModel):
    """STAR-L形式での分析結果の構造化データ"""
    s_contents: List[str] = Field(description="本文から抜粋した状況(Situation)の内容を含む文章のリスト。言及なければ空リスト")
    t_contents: List[str] = Field(description="本文から抜粋した課題(Task)の内容を含む文章のリスト。言及なければ空リスト")
    a_contents: List[str] = Field(description="本文から抜粋した行動と工夫(Action)の内容を含む文章のリスト）。言及なければ空リスト")
    r_contents: List[str] = Field(description="本文から抜粋した結果(Result)の内容を含む文章のリスト）。言及なければ空リスト")
    l_contents: List[str] = Field(description="本文から抜粋した学び(Learning)の内容を含む文章のリスト）。言及なければ空リスト")
    s_score: int = Field(description="状況(Situation)の具体性スコア(0-20)")
    t_score: int = Field(description="課題と動機(Task)の深さスコア(0-20)")
    a_score: int = Field(description="行動と工夫(Action)の主体性スコア(0-20)")
    r_score: int = Field(description="結果(Result)の客観性スコア(0-20)")
    l_score: int = Field(description="学び(Learning)の再現性スコア(0-20)")
    total_score: int = Field(description="S,T,A,R,Lの合計スコア(0-100)")
    missing_element: str = Field(description="エピソードの土台となる要素（S, T）が１２点以下の場合は、その要素のみを指定。その他の場合はS, T, A, R, L の中で最も不足している要素の記号")
    feedback_reason: str = Field(description="スコアの理由と、不足要素についてなぜ深掘りが必要なのかの分析メモ。土台構築のため閾値未満でSまたはTを優先して指定した場合は、その理由を詳述すること")


class EpisodeModel(BaseModel):
    # 基本情報
    title: str = Field(..., description="エピソードのタイトル")
    
    # STAR-Lの各要素を詳細化
    situation: str = Field(..., min_length=100, description="【非損失】前提条件、組織の規模、自身の役割、当時の状況を100文字以上で詳細に記述")
    task: str = Field(..., min_length=80, description="【非損失】直面した課題の深さと、それに取り組んだ個人的な動機・葛藤を詳細に記述")
    
    # Actionは特に粒度が重要なため、リスト形式で具体的手法を分離
    actions: List[str] = Field(..., description="実行した具体的なアクションのリスト。各項目は『どのような意図で』『具体的にどう動いたか』を含むこと")
    action_log: str = Field(..., min_length=200, description="【非損失】試行錯誤のプロセス、壁にぶつかった際の思考、周囲との調整内容を、会話から漏らさず200文字以上で詳述")
    
    result: str = Field(..., description="定量的・定性的な成果。具体的な数値や、周囲からのフィードバックをそのまま記述")
    learning: str = Field(..., description="この経験から得た再現性のある学び。単なる感想ではなく、社会でどう転用できるかまで記述")

    # 蓄積用メタデータ
    raw_highlights: List[str] = Field(..., description="会話の中から抽出した、特に価値のある生の具体的発言や固有名詞のリスト")

    # エピソードの要約
    summary: str = Field(..., min_length=250, max_length=300, description="エピソード全体の要約。面接官が一目で理解できるよう、STAR-Lの要素を織り交ぜて簡潔にまとめること") 