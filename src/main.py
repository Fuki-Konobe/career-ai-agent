from dotenv import load_dotenv
load_dotenv()
import os
import uuid
from langchain_core.messages import HumanMessage
from graph import create_graph
from config import SCORE_THRESHOLD



def main():
    app = create_graph()
    
    # セッション管理用の設定
    config = {"configurable": {"thread_id": "session_1"}}

    print("\n========================================")
    print("   就活エピソード深掘りAIエージェント")
    print("========================================\n")
    
    print("AIメンター: あなたが学生時代に最も力を入れたことは何ですか？")
    user_input = input("あなた: ")
    
    # 初回の入力
    inputs = {"messages": [HumanMessage(content=user_input)]}

    while True:
        # 改行のみ、または空白のみの入力は無視する
        if not user_input.strip():
            user_input = input("あなた: ")
            continue
        # グラフの実行（スコア閾値未満ならmentoringで停止、閾値以上ならextractionとsaveまで実行）
        for event in app.stream(inputs, config=config):
            for node_name, output in event.items():
                if node_name == "analysis":
                    score = output.get('star_score', 0)
                    print(f"\n[AI分析中...] 現在の充実度: {score}/100")
                
                if node_name == "mentoring":
                    # AIの質問を表示
                    last_msg = output["messages"][-1].content
                    print(f"\nAIメンター: {last_msg}")
                
                if node_name == "save":
                    # save ノードが実行されたら、extraction→save が完了
                    print("\n【エピソード構造化と保存が完了しました】")

        # 状態を確認
        state = app.get_state(config)
        final_score = state.values.get("star_score", 0)
        
        # スコアが閾値以上なら、extractionとsaveを実行
        if final_score >= SCORE_THRESHOLD:
            print("\n========================================")
            print(f"目標スコアに達しました！素晴らしいエピソードです。({final_score}/100)")
            print("========================================\n")
            
            # Noneを渡してグラフを再開 → extraction/saveまで自動実行
            for event in app.stream(None, config=config):
                for node_name, output in event.items():
                    if node_name == "save":
                        print("【エピソード構造化と保存が完了しました】\n")
            break

        # スコア < 閾値 なら、ユーザーの次の回答を入力
        user_response = input("\nあなた(回答): ")
        inputs = {"messages": [HumanMessage(content=user_response)]}


if __name__ == "__main__":
    main()