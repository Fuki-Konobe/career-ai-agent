from typing import TypedDict, Annotated, Sequence, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from schema import EpisodeModel

class AgentState(TypedDict):
    # add_messagesにより、既存の履歴に新しい発言が自動で追加(Append)される
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # STARフレームワークの充足度
    star_score: int
    # 不足している要素（S, T, A, R, Lのいずれか）
    missing_element: str
    # 分析結果の内部メモ（面接官視点の分析）
    analysis_memo: str
    # 最終的に構造化されたデータ（最初はNone）
    final_data: Optional[EpisodeModel]
    # ターンカウント（メンタリングのループ回数）
    turn_count: int
    