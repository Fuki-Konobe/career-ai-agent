# 🎯 Career AI Agent: 就活ガクチカ深掘りエンジン

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-blueviolet?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-green?style=flat-square)](https://www.langchain.com/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-GPT--4o-orange?style=flat-square&logo=openai)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)](https://www.docker.com/)

---

## 📋 Overview

**就職活動において、「学生時代に最も力を入れたこと」（ガクチカ）は、学生が持つ最強の武器です。**

本システムは、学生が**自分でも気づかない成長**を自覚させ、その武器を**磨き尽くす**ための **AI駆動メンター** です。

### What This System Does

```
✌️ 学生の曖昧なエピソードを入力
     ↓
⚡ GPT-4o が「面接官目線」で冷徹に採点（STAR-L形式）
     ↓
🔍 不足要素を特定し、高解像度な深掘り質問を自動生成
     ↓
🎙️ ターンベースのメンタリングループで充実度を向上
     ↓
📊 目標スコア（80/100）達成で、構造化データとして保存
```

**特徴:**

| 機能 | 説明 |
|:----:|------|
| 🧠 **厳格採点** | 推論禁止・抽象語無効化ルール により、甘い評価を徹底排除 |
| 🎯 **不足要素抽出** | STAR-L（状況・課題・行動・結果・学び）のうち、最も深掘るべき要素を自動判定 |
| 💬 **適応的メンタリング** | 不足要素に特化した質問を動的生成 |
| 📝 **構造化出力** | 会話全体から 150+ 文字の詳細エピソードを抽出 |
| 💾 **永続化** | タイムスタンプ付きJSON形式で履歴保存 |

---

## 🚀 Background & Mission

### なぜこのシステムが必要なのか？

**学生が直面する4つの課題:**

1. **解像度の低さ** → 「頑張った」「工夫した」程度で終わる
2. **主観的評価** → 自分のエピソードの強みが正確に理解できない
3. **深掘り疲弊** → メンター不足で、どこまで掘るべきか判断できない
4. **企業適合性の見落とし** → ガクチカはあっても、企業の求める能力と結びつかない

### このシステムの使命

**「ガクチカ」を「武器」に変える。**

- ✅ 短絡的な高評価を与えない設計（スコア80まで容易ではない）
- ✅ 学生が気づかない成長を言語化し、自覚させる
- ✅ 試行錯誤プロセスの「生々しさ」を引き出す
- ✅ 企業特性ごとにカスタマイズ可能な高品質ESへの道筋を提供

---

## 🏗️ System Architecture

### 全体フロー図

```mermaid
graph TD
    A["👤 ユーザー入力<br/>（ガクチカ初期版）"] -->|HumanMessage| B["🧠 analysis_node<br/>STAR-L採点エンジン"]
    
    B -->|構造化出力| C{"score ≥ 80？"}
    
    C -->|NO| D["💬 mentoring_node<br/>深掘り質問生成"]
    D -->|AIMessage| E["⏸️ インタラプト<br/>ユーザー入力待機"]
    E -->|HumanMessage| B
    
    C -->|YES| F["🔍 extraction_node<br/>EpisodeModel構造化"]
    F -->|詳細エピソード| G["💾 save_node<br/>JSON保存"]
    G -->|/episodes/.json| H["📊 履歴蓄積<br/>（JST timestamp）"]
    
    style B fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style D fill:#4ecdc4,stroke:#0b8a8a,stroke-width:2px,color:#fff
    style F fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#333
    style H fill:#ffe66d,stroke:#f59f00,stroke-width:2px,color:#333
```

### データフロー（内部状態遷移）

```mermaid
sequenceDiagram
    participant U as 学生
    participant G as LangGraph<br/>Workflow
    participant L as GPT-4o<br/>LLM
    participant S as State<br/>Management
    participant F as File System<br/>/episodes

    U->>G: ① 初回入力（ガクチカ）
    G->>L: ② system_prompt + messages
    L->>G: ③ GakuchikaAnalysis 構造化出力
    G->>S: ④ State更新<br/>(score, missing_element)
    
    alt score < 80
        G->>L: ⑤ mentoring_prompt生成
        L->>G: ⑥ 深掘り質問
        G->>U: ⑦ AIMessage表示
        U->>G: ⑧ インタラプト後、ユーザー回答
        G->>S: ⑨ messages Append
        G->>L: ⑩ Loop: analysis_nodeで再分析
    else score ≥ 80
        G->>L: ⑪ extraction_prompt
        L->>G: ⑫ EpisodeModel 構造化出力
        G->>S: ⑬ final_data 保存
        G->>F: ⑭ JSON保存
        G->>U: ⑮ 完了通知
    end
```

### ノード設計と責務分離

| ノード | 入力 | 処理 | 出力 | 特性 |
|:------:|------|------|------|------|
| **analysis** | messages + turn履歴 | STAR-L厳格採点 | `(score, missing_element, memo)` | 決定論的（temp=0.2） |
| **mentoring** | missing_element + memo | 要素特化質問生成 | `AIMessage(質問)` | 建設的なトーン |
| **extraction** | messages全体 | 詳細構造化 | `EpisodeModel` | 高密度テキスト抽出 |
| **save** | EpisodeModel | JSON保存 | ファイルシステム操作 | 副作用実行 |

---

## ⚡ Technical Excellence

### 1. 厳格採点ロジックの精密性

#### 🔒 Anti-Inference Rules（推論禁止の徹底）

本システムの最大の特徴は、**「本文に直接明記されていない行動を推論してはいけない」** という鉄則です。

**ルール1: 推論禁止**

```python
# ❌ 悪い例
ユーザー: 「ゲーム制作に取り組みました」
AI推論: 「チームマネジメントもしたんでしょう」← 書かれていない！
採点: 加点NG

# ✅ 良い例
ユーザー: 「Blenderで3Dモデルを作成し、ファシリテータを務めました」
採点: 「ファシリテータ」は具体的行動として加点
```

**ルール2: 抽象語は無効化**

```
❌ 「頑張った」「工夫した」「リーダーシップを発揮」
   → 具体的な動作・数値がない → 5点以下

✅ 「毎日5時間、Pythonを学習し、掲示板アプリを完成させた」
   → 時間数・成果物が具体的 → 加点
```

**ルール3: 文字数による足切り**

```
入力 < 150文字 → 内容品質に関わらず最大40点（充実度の問題）
```

#### 📊 採点ルーブリック（20段階）

各STAR-L要素を20点満点で評価：

| スコア帯 | 基準 | 例 |
|:-------:|------|-----|
| **18-20点** | 圧倒的な解像度 | 固有名詞・数値・独自の思考プロセス・生々しい葛藤が全て言語化 |
| **13-17点** | 優秀 | 定量的事実は明記だが、独自性・深さが一段足りない |
| **6-12点** | 平凡 | 誰にでも言える表面的事実。特筆すべき点がない |
| **1-5点** | 不十分 | 抽象語のみ。具体的動作が不明瞭 |
| **0点** | 欠落 | その要素に言及なし |

#### 🧠 Chain of Thoughtプロセス

```python
# Step 1: 抽出（一言一句変えず）
S（状況）: 「大学のゲームクリエイトプロジェクト」
T（課題）: 「VRゲームで水の豊かさを守る」
A（行動）: 「Blenderで3Dモデルを作成、ファシリテータを務めた」
R（結果）: 「ユーザーから『新鮮だった』というフィードバック」
L（学び）: （なし）

# Step 2: 各要素を20点満点で採点
# Step 3: 最も深掘るべき要素を判定
```

#### 🎯 Few-Shot Examplesの活用

プロンプトに **3つの詳細な判定事例** を含めることで、LLMの採点ブレを最小化：

```python
■ 例1：低品質・抽象的な回答（厳密な低評価）
■ 例2：事実のみで独自性が足りない回答（厳しい中評価）
■ 例3：一見優秀だが解像度がもう一歩足りない回答（頭打ちの評価）
```

**効果:**
- LLMの学習により、採点の一貫性が向上
- ドリフト（時間経過での評価ズレ）が削減

---

### 2. スキーマ設計による制約と品質保証

#### Pydantic による厳格なバリデーション

```python
class EpisodeModel(BaseModel):
    # 基本情報
    title: str
    
    # STAR-Lの各要素を詳細化
    situation: str = Field(..., min_length=100)  # ← 最小100文字を強制
    task: str = Field(..., min_length=80)        # ← 動機の深掘りを強制
    
    actions: List[str]  # ← 複数行動の分離で粒度を確保
    action_log: str = Field(..., min_length=200)  # ← 試行錯誤プロセスを保証
    
    result: str         # ← 定量的成果を記述
    learning: str       # ← 再現性のある学びを強制
    
    raw_highlights: List[str]  # ← 生の発言を保存
```

**設計の狙い:**

| フィールド | 制約 | 意図 |
|:--------:|------|------|
| `situation` | min_length=100 | 前提条件の曖昧性を排除 |
| `task` | min_length=80 | 表面的な課題記述を防止 |
| `action_log` | min_length=200 | 試行錯誤の過程を強制 |
| `raw_highlights` | List[str] | 生の発言を失わず保存 |

**バリデーション失敗時:**

extraction_nodeで失敗 → 自動的にメンタリングループに戻す（MAX_TURNS=10まで）

---

### 3. 不足要素の動的抽出と深掘り質問生成

#### 🎯 要素-質問マッピング

```python
element_focus_map = {
    "S": "当時の具体的な状況や、チームの規模・役割などの前提条件",
    "T": "なぜその課題に取り組もうと思ったのかという『個人的な動機』や『目標の難易度』",
    "A": "壁にぶつかった際に、具体的にどのような『工夫』や『あなたならではのアプローチ』をとったのか",
    "R": "その行動によって生じた具体的な変化や、周囲からの評価、定量的な成果",
    "L": "その経験を通じて得た価値観の変化や、今後どう活かせるかという『学び』"
}
```

**メンタリングプロンプトの構造:**

```python
system_prompt = f"""
あなたは採用面接官兼キャリアコンサルタント。

【内部分析データ（参照用）】
不足要素: {missing_element}
分析メモ: {analysis_memo}

【指示】
1. 肯定と指摘のバランス: 良い点を認めつつ、曖昧な点を「面接官目線で評価されない」理由と共に指摘
2. 高解像度質問: 数字、固有名詞、セリフ、具体的動作が含まれるヒントを添えた質問を1つだけ
3. トーン: 過度な称賛を避け、客観的かつ建設的に

【制約事項】
- 段落分けのみの自然な会話文（見出し・箇条書きNG）
- 1回の発言で質問は1つに絞る
"""
```

---

### 4. ターンカウント・スコア閾値管理

```python
# config.py
SCORE_THRESHOLD = 80      # 目標スコア
MAX_TURNS = 10            # メンタリングループの最大回数
```

**ロジック:**

```python
def routing_logic(state):
    turn_count = state.get("turn_count", 0)
    score = state.get("star_score", 0)
    
    # ①MAX_TURNS到達で強制終了
    if turn_count >= MAX_TURNS:
        return "extraction"  # 高い精度を保ちつつ、無限ループを防止
    
    # ②スコア80以上で自動進行
    if score >= SCORE_THRESHOLD:
        return "extraction"
    
    # ③それ以外はメンタリング継続
    return "mentoring"
```

**効果:**

- 🎯 学生に「目標までの進捗」を可視化
- ⏱️ セッション時間の可予測性（通常 5-15分）
- 🛡️ コンテキスト窓超過リスクの軽減（トークン節約）

---

### 5. LangGraphによるステートフルワークフロー管理

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

def create_graph():
    workflow = StateGraph(AgentState)
    
    # ノード登録
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("mentoring", mentoring_node)
    workflow.add_node("extraction", extraction_node)
    workflow.add_node("save", save_node)
    
    # 条件付き分岐
    workflow.add_conditional_edges(
        "analysis",
        routing_logic,
        {"mentoring": "mentoring", "extraction": "extraction"}
    )
    
    # 永続化（SQLite Checkpointer）
    memory = MemorySaver()
    
    # インタラプト設定：mentoringの直後に停止してユーザー入力待機
    return workflow.compile(
        checkpointer=memory,
        interrupt_after=["mentoring"]
    )
```

**メリット:**

| 機能 | 効果 |
|:---:|------|
| **Checkpointer** | セッション再開時に全会話履歴を復元 |
| **interrupt_after** | ユーザーのタイミングで入力可能（UI友好的） |
| **Annotated State** | `add_messages` により自動的にメッセージを Append |

---

## 🔮 Future Outlook & Technology Roadmap

### 現在の実装における技術的負債

#### 🚨 Critical Issue: 客観的評価パイプラインの欠落

**現状:**

```
出力の品質評価 → 主観的フィードバックのみ
                ↓
            改良の効果が測定不可
                ↓
         システム全体の最適化停止
```

**問題の具体例:**

- ❌ プロンプト改良後、採点精度が向上したのか判断できない
- ❌ Few-Shot examples の効果を定量的に測定できない
- ❌ 学生の「成長実感度」を数値化できない
- ❌ エピソード抽出の「誤り率」が不明

---

### Phase 2: 定量的評価フレームワークの構築

**目的:** 出力品質を客観的に測定し、プロンプト改良の効果を定量化

**修正の方向性:**

1. **採点精度の検証**
   - 企業の実際の選考結果（フィードバック）をground truthとして収集
   - analysis_node の出力スコアとの乖離を F1スコア, Precision, Recall で計測
   - プロンプト改良ごとに精度の推移を記録・可視化

2. **構造化データの品質メトリクス**
   - テキスト密度：action_log の字数増加（200字 → 1000字）を追跡
   - 具体性スコア：Named Entity 検出率（固有名詞の出現率）を定量化
   - 矛盾検出：S→T→A→R→L の因果関係の一貫性をチェック
   - 学習実装度：learning フィールドの「転用可能性」を評価

3. **A/Bテストの実施**
   - 同一エピソードに対して複数プロンプト戦略を実験
     - prompt_v1（現在）：基本ルーブリック
     - prompt_v2：より詳細なFew-shot例を追加
     - prompt_v3：CoT（思考ステップ）を明示化
   - スコアの一貫性・精度を比較し、最適戦略を決定

**利用技術:** MLflow（実験管理）, Prometheus（メトリクス収集）, Grafana（可視化）

---

### Phase 3: スケーラビリティと多企業対応

**目的:** 単一の「汎用ガクチカ」ではなく、企業特性に最適化されたES自動生成

**修正の方向性:**

構造化された EpisodeModel データと企業の Job Description（職務記述書）を照合し、各企業に最適化した ES を自動生成します。

**具体的な機能:**

1. **企業プロフィール分析**
   - 企業の JD をテキスト化・ベクトル化
   - 求められるスキル（技術力、リーダーシップ、データ分析など）を抽出

2. **要素マッピングと重要度スコア計算**
   - EpisodeModel の各 STAR-L要素を企業のニーズと照合
   - relevance_score（関連度）を計算
   - 例：
     - SIer企業 → R（結果）や L（学び）を強調（定量的成果、スケーラビリティ思考）
     - スタートアップ → A（行動）を強調（試行錯誤、自律性）
     - コンサル企業 → T（課題分析）や A（解決策立案）を強調

3. **カスタマイズES生成**
   - 重要度スコアに基づいて STAR-L要素を再配置・削稿
   - 各企業向けに異なる複数バージョンの ES を自動出力

**利用技術:** RAG（企業JDのベクトル化・検索）, Semantic Search, LLM（再構成）

---

### Phase 4: マルチモーダル・リアルタイムフィードバック

**目的:** テキスト入力のみから、音声・ビジュアルを活用した高い学習効果を実現

**修正の方向性:**

1. **音声入力対応**
   - Whisper API を使用して音声をテキストに自動変換
   - 音声の「ポーズ」「イントネーション」「話速」から、エピソード表現の真正性・自信度を推定
   - 抽象語の連発（「えっと」「あの」「まあ」など）を自動検出 → 即座に掘り下げ質問を生成

2. **リアルタイムスコア可視化**
   - ターンごとのスコア推移をグラフで表示
   - 学生の「充実度向上」の実感を促進
   - 例：Turn 1 → 35/100（Sが不十分）→ Turn 5 → 71/100（Aが充実）

3. **インタラクティブなフィードバック**
   - AI の指摘内容を「なぜそこが弱いのか」を複数角度から説明
   - 学生の改善案に対する即座な評価・採点（メンタリング→分析→可視化 の高速化）

**利用技術:** OpenAI Whisper, Plotly（グラフ可視化）, WebSocket（リアルタイム通信）

---

### Phase 5: 分散型SLM導入とエッジ化

**現在の課題:**

- ⏱️ OpenAI API 呼び出し遅延（500ms-1s/リクエスト）
- 💰 トークンコストの累積（月額$500+を想定、スケール時は深刻）
- 🔒 プライバシー懸念（会話データが外部サーバーに送信）

**修正の方向性:**

1. **ローカルSLM（Small Language Model）の導入**
   - Mistral 7B, Llama 2-13B などのSLMを Docker コンテナ内で実行
   - ollama / llama.cpp を用いたの高速ローカル推論
   - 完全オンプレミス化によりプライバシーを保証

2. **パフォーマンス最適化**
   - API遅延の排除 → 即座のメンタリングフィードバック
   - スケーラビリティの向上 → 同時複数ユーザーの対応可能
   - 運用コスト削減

3. **精度補完戦略**
   - SLMの推論精度は GPT-4o 比で 2-3% 低下の可能性
   - 以下で補完：
     - Few-shot例の更なる充実化
     - RAG（Retrieval-Augmented Generation）による参考事例の検索・挿入
     - 社内フィードバックループによるファインチューニング

**利用技術:** Llama 2 / Mistral, ollama, LoRA（パラメータ効率化チューニング）

---

**ロードマップ:**

| Phase | 時期 | 主要機能 | 技術スタック |
|:-----:|------|---------|-----------|
| **現在** | ✅ | 厳格採点 + メンタリング | GPT-4o + LangGraph |
| **Phase 2** | Q2-Q3 | 定量的評価パイプライン | MLflow + Prometheus |
| **Phase 3** | Q3-Q4 | 企業特性別ES生成 | RAG（企業JDベクトル化） |
| **Phase 4** | Q4-Q1 | 音声入力 + UI可視化 | Whisper + Plotly |
| **Phase 5** | Q1-Q2 | エッジLLM展開 | Llama 2 / ollama |

---

## 🔧 Setup & Getting Started

### 前提条件

- Docker & Docker Compose
- OpenAI API キー（`OPENAI_API_KEY`）
- Python 3.11+（ローカル実行時）

### 方法1: Docker Compose（推奨・3分で起動）

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-name/career-ai-agent.git
cd career-ai-agent

# 2. 環境変数を設定
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Docker Composeで起動
docker-compose up -d

# 4. ブラウザで開く
open http://localhost:8501
```

**docker-compose.yml の仕様:**

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"  # Streamlit
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./episodes:/app/episodes  # 出力ファイルのマウント
    command: streamlit run src/ui.py --server.port=8501 --server.address=0.0.0.0
```

### 方法2: ローカル実行

```bash
# 1. 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. 環境変数を設定
export OPENAI_API_KEY="sk-..."

# 4. CLIモードで実行
python src/main.py

# または Streamlit UI で実行
streamlit run src/ui.py
```

### 方法3: GitHub Codespaces（クラウド実行）

```bash
# 1. Codespaces を起動
# 2. ターミナルで実行
python -m pip install -r requirements.txt
streamlit run src/ui.py
```

---

## 📂 Project Structure

```
.
├── README.md                           # このファイル
├── requirements.txt                    # Python 依存関係
├── docker-compose.yml                  # Docker Compose 設定
├── Dockerfile                          # Docker イメージ定義
│
├── src/
│   ├── __init__.py
│   ├── config.py                       # SCORE_THRESHOLD, MAX_TURNS
│   ├── state.py                        # AgentState （LangGraph State）
│   ├── schema.py                       # GakuchikaAnalysis, EpisodeModel
│   ├── nodes.py                        # 4ノード実装（analysis/mentoring/extraction/save）
│   ├── graph.py                        # LangGraph Workflow
│   ├── main.py                         # CLI エントリーポイント
│   └── ui.py                           # Streamlit UI
│
└── episodes/
    ├── 20260407_163415_学生団体の再設計.json
    ├── 20260414_151223_大学でのゲーム制作.json
    └── ...                             # タイムスタンプ付き EpisodeModel JSON
```

---

## 📊 Example Usage

### CLI 実行例

```bash
$ python src/main.py

========================================
   就活エピソード深掘りAIエージェント
========================================

AIメンター: あなたが学生時代に最も力を入れたことは何ですか？
あなた: 学生団体の代表として、ほぼ解散状態だった団体を再構築する取り組みに力を入れました。

[AI分析中...] 現在の充実度: 35/100 (ターン: 1/10)

AIメンター: その団体再構築の具体的な状況を教えていただけますか？
例えば、その団体は何人のメンバーで、初期状態はどんな課題を抱えていたのでしょうか？

あなた: 元々20人程度いたメンバーが、運営陣の卒業で実質2人まで減少していました。
ビジョンやミッションが不明確で、新入生の勧誘もできていない状態でした。

[AI分析中...] 現在の充実度: 48/100 (ターン: 2/10)

AIメンター: ビジョンやミッション の再設計について、あなた自身はどのように考え、
メンバーに何を語りかけたのでしょうか？具体的なセリフやエピソードがあれば教えてください。

あなた: 最初、メンバーからの質問に答えられない経験がありました。
「結局、この団体は何をやりたいんですか？」と聞かれた時の戸惑いを感じました。
そこから、自分たちが何を成し遂げたいのか、メンバーの個性や価値観を
1on1対話で聴きながら、ビジョンを言語化していきました。

[AI分析中...] 現在の充実度: 61/100 (ターン: 3/10)

AIメンター: 素晴らしい自己認識ですね。では、そのビジョン共有の後、
メンバーの成長やチーム活動で、具体的に成果として表れたことはありますか？

あなた: 企業との合同新歓イベントを企画・実行して、100名の新入生を集めることができました。
また、P2Mというプロジェクトマネジメント手法を導入して、メンバーがプロジェクトリーダーとして
意思決定できる環境を整備しました。そのプロセスで12人のメンバーを集めることに成功しました。

[AI分析中...] 現在の充実度: 74/100 (ターン: 4/10)

AIメンター: イベント成功やメンバー増加という成果は素晴らしい。
では、この経験を通じて、あなた自身の考え方や姿勢でどのような変化がありましたか？
「リーダーとして学んだこと」を掘り下げていただけますか？

あなた: リーダーとして、自分のビジョンを明確に言語化することの大切さを学びました。
また、メンバーの多様な価値観を理解し、その価値観とチームのミッションを結びつける力が
身についたと感じます。プロジェクト単位だけでなく、プログラム全体でのマネジメント視点を
持つようになったことで、メンバーのリーダーシップ育成に重点を置くようになりました。

[AI分析中...] 現在の充実度: 83/100 (ターン: 5/10)

========================================
【エピソード構造化と保存が完了しました】
========================================

✅ 出力: /app/episodes/20260422_172812_学生団体の再構築とイベント成功.json
```

### 出力 JSON 例

```json
{
  "title": "学生団体の再構築とイベント成功",
  "situation": "学生団体の代表として、ほとんど解散状態にあった団体を再構築する必要があった。団体のビジョンやミッションを再設計し、もともと学生だったメンバーを中心に声をかけ、1人1人の声を聴きながら、団体が与えられるものとメンバーが求めるものを結びつける作業を行った。",
  "task": "団体の再構築を通じて、メンバーを集め、団体としての活動を再開することが課題であった。特に、団体のビジョンを明確にし、メンバーのモチベーションを高めることが重要であった。",
  "actions": [
    "ビジョンやミッションを再設計し、メンバーに共有した。",
    "1on1の対話を通じて、メンバーの声を聴き、彼らの求めるものを把握した。",
    "企業との合同新歓イベントを企画し、実行した。",
    "P2Mのメソッドを用いてプロジェクト制で管理し、メンバーのリーダーシップを育成した。"
  ],
  "action_log": "初めて自分の想いや考え方を明確に言語化することの難しさを痛感した。メンバーからの質問に答えられなかった経験を通じて、リーダーとしての自分の考えに共感させるためには、明確にビジョンを語る必要があることを学んだ。また、メンバーが求めているものや価値観を把握する力を身に付けた。プロジェクト制での管理を通じて、プログラム単位でのマネジメント力を向上させた。特に、プロジェクトリーダーのメンターとしての立ち位置で進行を行い、メンバーのリーダーシップや企画力を醸成することを目指した。",
  "result": "12人のメンバーを集めることに成功し、企業との合同新歓イベントでは100名の新入生を集めることができた。団体としての活動が再開され、メンバーの成長も促進された。",
  "learning": "リーダーとしてのビジョンを明確に語ることの重要性を学び、メンバーの価値観を把握する力を身に付けた。プロジェクトを超えたプログラム単位でのマネジメント力を向上させ、メンバーのリーダーシップや企画力を育成することができた。",
  "raw_highlights": [
    "考えや理想はわかりました。じゃあ結局何をやりたいんですか？",
    "P2Mのメソッドを踏襲したプロジェクト制で管理",
    "プロジェクトリーダーのメンターとしての立ち位置で進行"
  ]
}
```

---

## 📄 License

MIT License

---

## 🎯 最後に

このプロジェクトは、「学生のガクチカを武器に変える」という使命で開発されています。

このシステムで、あなたのガクチカが磨き上げられ、
企業に選ばれるエピソードへと変わることを願っています。

**「武器を持つこと」と「武器を使いこなすこと」は全く異なります。**

このシステムは、後者への伴走者です。

---