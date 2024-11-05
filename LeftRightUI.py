# ライブラリをインポート
# streamlit
import streamlit as st
from streamlit_chat import message

# ???
from operator import itemgetter
from typing import List

# langchain
from langchain_openai import ChatOpenAI # OpenAIの利用
from langchain_core.chat_history import BaseChatMessageHistory # 会話履歴の保存
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # プロンプトのひな形
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage # 各入出力の属性付け
from langchain_core.pydantic_v1 import BaseModel, Field # pydantic: 各オブジェクトのメタデータ宣言とか、検証とかデータ型管理が容易になるライブラリ、いる？
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
) # 動的な会話に必須
from langchain_core.runnables.history import RunnableWithMessageHistory # 動的にチャット履歴を保存

# langchain*streamlit
from langchain_community.chat_message_histories.streamlit import StreamlitChatMessageHistory

# firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 時間管理
import datetime
import pytz # タイムゾーンに直せるやつ
global now # PCから現在時刻
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

# システムプロンプトを読み込み
with open(fname, 'r') as f:
    systemprompt = fname.read()

# モデルのインスタンス生成
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=0,
    api_key= st.secrets.openai_api_key
)

# プロンプト設定
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", systemprompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input_message}"),
    ]
)
# chain設定
chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,  # Always return the instance created earlier
    input_messages_key="input_message",
    history_messages_key="history",
)

# firebaseの設定
db = firestore.Client(project=CHAT_PROJECT_TEST)

def input_id():
    st.write("idを入力してください")
    st.session_state.user_id = st.text_input("IDを入力") # ユーザID取得
    # セッションID初期化
    if not "conversation_key" in st.session_state:
        st.session_state.conversation_key = "{}_{}".format(st.session_state.user_id, now)
    st.session_state.state = 2

def chat_page():
    chat_container = st.container(height=600) # st.containerでブロックを定義
    # 会話ログ格納開始
    if not "msgs" in st.session_state:
        st.session_state.msgs = StreamlitChatMessageHistory(key="any")
    for msg in st.session_state.msgs.messages:
        with chat_container.chat_message(msg.type):
            st.markdown(msg.content)

    if user_input := st.chat_input("入力してね"):
        st.chat_message("human").write(user_input)
        st.session_state.send_time = str(now)
        st.spinner("待機中…")
        time.sleep(5)
        # As usual, new messages are added to StreamlitChatMessageHistory when the Chain is called. 
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"input_message": user_input}, config)
        st.chat_message("ai").write(response.content)
        st.session_state.display_time = str(now)
        doc_ref = db.collection(user_id).document(st.session_state.send_time)
        doc_ref.set({
            Human: user_input,
            AI_Agent: response.content
        })
        if st.session_state.talktime == 5:
            st.session_state.state = 3
        else:
            st.session_state.talktime += 1


def chat_ended():
    # チャット履歴を表示
    chat_container = st.container(height=600) # st.containerでブロックを定義
    for msg in st.session_state.msgs.messages:
        with chat_container.chat_message(msg.type):
            st.markdown(msg.content)
    '''
    for message in st.session_state.messages:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
    '''
    view_messages = st.expander("View the message contents in session state")
    with view_messages:
        view_messages.json(st.session_state.any)
    st.write("お疲れ様でした、下のURLを押してアンケートへ進んでください")
    url = "https://www.nagoya-u.ac.jp/"
    st.markdown("check out this [link](%s)" % url)

def main():
    st.title('チャットボット')
    if not "state" in st.session_state:
        st.session_state.state = 1
    if st.session_state.state == 1:
        input_id()
    elif st.session_state.state == 2:
        chat_page()
    elif st.session_state.state == 3:
        chat_ended()

if __name__ == "__main__":
    main()
