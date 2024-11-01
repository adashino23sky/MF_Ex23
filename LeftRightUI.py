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

# 会話履歴保存・操作のクラス作成、会話はグローバル変数内に保存するよー
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""
    messages: List[BaseMessage] = Field(default_factory=list)
    def add_messages(self, messages: List[BaseMessage]) -> None: # 履歴追加
        """Add a list of messages to the store"""
        self.messages.extend(messages) 
    def clear(self) -> None: # 履歴削除
        self.messages = []

# 毎回送信するプロンプト設定、システムプロンプトとメッセージ履歴をあわせて送信する
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# プロンプトとモデルを紐付け、langchain特有のパイプライン処理？
chain = prompt | llm

# 履歴管理
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_by_session_id,
    input_messages_key="input",
    history_messages_key="history",
)

# user_idセッションにuser_inputを入力した結果を表示
chain_with_history.invoke(
    {"input": user_input},
    config={"configurable": {"session_id": }}
))


# 会話履歴を格納
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


history = StreamlitChatMessageHistory(key="chat_messages")

history.add_user_message("hi!")
history.add_ai_message("whats up?")

# AIの発言を履歴に入力
history.add_messages([AIMessage(content=user_input)])

# userの発言をチャットに入力
history.add_messages([HumanMessage(content=user_input)])

def input_id():
    st.write("idを入力してください")
    st.session_state.user_id = st.input("IDを入力")
    st.session_state.state = 2

def chat_page():
    chat_container = st.container(height=600) # st.containerでブロックを定義
    if not "messages" in st.session_state:
        break
    else:
        for message in st.session_state.messages:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
    st.session_state.user_input = st.chat_input("入力してね", on_submit=chat_input_change())

def chat_ended():
    # チャット履歴を表示
    chat_container = st.container(height=600) # st.containerでブロックを定義
    for message in st.session_state.messages:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
    st.write("お疲れ様でした、下のURLを押してアンケートへ進んでください")
    new_tab_js = ()
    st.markdown(new_tab_js, unsafe_allow_html=True)

def chat_input_change():
    # 待機させる
    st.spinner("待機中…")
    time.sleep(3)
    # 生成
    answer = chain_with_history.invoke(
        {"input": st.session_state.user_input},
        config={"configurable": {"session_id": st.session_state.user_id}})
    # 保存
    st.session_state.message["User"].append(st.session_state.user_input)
    st.session_state.message["Agent"].append(answer)
    # 加工してfbに保存
    def data_to_fb(user_id, user_msg, ai_msg):
    doc_ref = db.collection(user_id).document(str(now))
    doc_ref.set({
        Human: user_message,
        AI_Agent: answer
    })
    # 一定数会話したら終了画面へ
    if st.session_state.talk ==5:
        st.session_state.state = 3


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)

history = StreamlitChatMessageHistory(key="chat_messages")

history.add_user_message("hi!")
history.add_ai_message("whats up?")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{systemprompt}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,  # Always return the instance created earlier
    input_messages_key="question",
    history_messages_key="history",
)

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
