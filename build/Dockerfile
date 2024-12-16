# ベースイメージとしてPython 3.11を使用
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 依存パッケージをインストールするため、requirements.txtをコピー
COPY requirements.txt .

# 依存パッケージをインストール
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY src/ ./src/

# ホットリロードを有効化するための環境変数
ENV STREAMLIT_SERVER_RUN_ON_SAVE="true"

# ポートを公開
EXPOSE ${STREAMLIT_PORT}

# CMDでshを使って環境変数を展開してからstreamlitを起動
CMD sh -c "streamlit run /app/src/app.py --server.port=$STREAMLIT_PORT --server.address=$APP_HOST --global.developmentMode=false --server.maxUploadSize=3000"
