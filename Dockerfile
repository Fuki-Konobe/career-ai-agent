# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Streamlitのデフォルトポート
EXPOSE 8501

# 実行コマンド（ホットリロードを有効にする設定を含む）
CMD ["streamlit", "run", "src/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]