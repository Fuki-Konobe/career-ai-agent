import streamlit as st
import uuid
from langchain_core.messages import HumanMessage, AIMessage
# あなたのグラフ定義をインポート
from graph import create_graph

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

# --- UIレイアウト ---
col_score, col_chat = st.columns([1, 2])

with col_score:
    st.header("📊 分析結果")
    st.metric("現在のスコア", f"{st.session_state.star_score} / 100")
    st.subheader(f"不足要素: {st.session_state.missing_element}")
    st.info(st.session_state.analysis_memo)
    
    if st.button("履歴をリセット"):
        st.session_state.messages = []
        st.session_state.star_score = 0
        st.rerun()

with col_chat:
    st.header("💬 メンタリング対話")
    
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
        # 初回または継続のStateを構築
        inputs = {
            "messages": st.session_state.messages,
            "star_score": st.session_state.star_score,
            "missing_element": st.session_state.missing_element,
            "analysis_memo": st.session_state.analysis_memo,
            "final_data": None
        }
        
        # グラフを実行（スレッドIDで会話履歴を管理）
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_state = create_graph().invoke(inputs, config)
        
        # 3. 分析結果の更新
        st.session_state.star_score = final_state.get("star_score", 0)
        st.session_state.missing_element = final_state.get("missing_element", "N/A")
        st.session_state.analysis_memo = final_state.get("analysis_memo", "")
        
        # 4. メンターの返答を表示
        new_msg = final_state["messages"][-1]
        st.session_state.messages.append(new_msg)
        with st.chat_message("assistant"):
            st.write(new_msg.content)
            
        st.rerun()