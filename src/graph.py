from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import analysis_node, extraction_node, save_node, mentoring_node
from config import SCORE_THRESHOLD, MAX_TURNS

def create_graph():
    workflow = StateGraph(AgentState)

    # ノードの登録
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("mentoring", mentoring_node)
    workflow.add_node("extraction", extraction_node)
    workflow.add_node("save", save_node)

    # 開始ノードの設定
    workflow.set_entry_point("analysis")

    # 条件付き分岐: スコアが閾値未満ならメンタリング継続、閾値以上なら構造化へ進む
    # ただし、ターン数が MAX_TURNS に到達したら強制的に extraction へ遷移
    def routing_logic(state):
        turn_count = state.get("turn_count", 0)
        if turn_count >= MAX_TURNS:
            return "extraction"
        if state["star_score"] >= SCORE_THRESHOLD:
            return "extraction"
        return "mentoring"
    
    workflow.add_conditional_edges(
        "analysis",
        routing_logic,
        {
            "mentoring": "mentoring",
            "extraction": "extraction"
        }
    )

    # extractionからsaveへ遷移
    workflow.add_edge("extraction", "save")

    # saveの後は終了
    workflow.add_edge("save", END)

    # メンタリングから分析へ戻るループ（ターンカウント をインクリメント）
    def increment_turn(state):
        return {"turn_count": state.get("turn_count", 0) + 1}
    
    workflow.add_node("increment_turn", increment_turn)
    workflow.add_edge("mentoring", "increment_turn")
    workflow.add_edge("increment_turn", "analysis")

    # SQLite による永続化
    memory = MemorySaver()

    # mentoringノードが終わったタイミングで実行を一時停止し、ユーザーの入力を待つ
    return workflow.compile(
        checkpointer=memory,
        interrupt_after=["mentoring"]
    )