import streamlit as st
import uuid
import json
from langchain_core.messages import HumanMessage, AIMessage
from graph import create_graph
from config import MAX_TURNS

st.set_page_config(page_title="Gakuchika Mentor", layout="wide")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "star_score" not in st.session_state:
    st.session_state.star_score = 0
if "missing_element" not in st.session_state:
    st.session_state.missing_element = "N/A"
if "analysis_memo" not in st.session_state:
    st.session_state.analysis_memo = "入力を待機中..."
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "final_data" not in st.session_state:
    st.session_state.final_data = None
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# --- UIレイアウト（メイン部）---
st.header("🎯 就活エピソード深掘りAIメンター")

col_chat, col_sidebar = st.columns([2, 1])

with col_chat:
    st.subheader("💬 メンタリング対話")
    
    # 履歴の表示
    for msg in st.session_state.messages:
        with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
            st.write(msg.content)

    # ユーザー入力
    if prompt := st.chat_input("エピソードを入力してください..."):
        # 1. ユーザー発言を表示
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        # 2. グラフの実行
        inputs = {
            "messages": st.session_state.messages,
            "star_score": st.session_state.star_score,
            "missing_element": st.session_state.missing_element,
            "analysis_memo": st.session_state.analysis_memo,
            "final_data": None,
            "turn_count": st.session_state.turn_count
        }
        
        # グラフを実行
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_state = create_graph().invoke(inputs, config)
        
        # 3. 状態を更新
        st.session_state.star_score = final_state.get("star_score", 0)
        st.session_state.missing_element = final_state.get("missing_element", "N/A")
        st.session_state.analysis_memo = final_state.get("analysis_memo", "")
        st.session_state.final_data = final_state.get("final_data")
        st.session_state.turn_count = final_state.get("turn_count", 0)
        
        # 4. メンターの返答を表示
        if len(final_state["messages"]) > len(st.session_state.messages) - 1:
            new_msg = final_state["messages"][-1]
            st.session_state.messages.append(new_msg)
            with st.chat_message("assistant"):
                st.write(new_msg.content)
            
        st.rerun()

with col_sidebar:
    st.subheader("📊 分析結果")
    st.metric("現在のスコア", f"{st.session_state.star_score} / 100")
    st.text(f"不足要素: {st.session_state.missing_element}")
    st.caption(f"ターン数: {st.session_state.turn_count} / {MAX_TURNS}")
    
    if st.button("履歴をリセット", key="reset_btn"):
        st.session_state.messages = []
        st.session_state.star_score = 0
        st.session_state.missing_element = "N/A"
        st.session_state.turn_count = 0
        st.session_state.final_data = None
        st.rerun()

# --- エピソード完成時のサマリー表示 ---
if st.session_state.final_data is not None:
    st.divider()
    st.success("✅ エピソード構造化が完了しました！")
    
    with st.expander("📋 詳細サマリー", expanded=True):
        final_data = st.session_state.final_data
        
        # タイトルと基本情報
        st.subheader(f"📌 {final_data.title}")
        
        st.markdown("**【状況(Situation)】**")
        st.write(final_data.situation)
        st.markdown("**【課題と動機(Task)】**")
        st.write(final_data.task)
        st.markdown("**【取組内容(Actions)】**")
        st.write(final_data.action_log)
        st.markdown("**【結果(Result)】**")
        st.write(final_data.result)
        st.markdown("**【学び(Learning)】**")
        st.write(final_data.learning)

        # 300字要約
        st.markdown("---")
        st.subheader("**✒️ エピソード要約(300字)**")
        st.write(final_data.summary)

        # 強みと面接フレーズの抽出
        st.markdown("---")
        st.subheader("🌟 抽出されたポイント")
        if final_data.raw_highlights:
            st.markdown("**具体的な固有名詞・数値・発言:**")
            for highlight in final_data.raw_highlights:
                st.write(f"• {highlight}")
        
        # データエクスポート
        st.markdown("---")
        json_str = final_data.model_dump_json(indent=2)
        st.download_button(
            label="📥 データをJSONでダウンロード",
            data=json_str,
            file_name="episode.json",
            mime="application/json"
        )