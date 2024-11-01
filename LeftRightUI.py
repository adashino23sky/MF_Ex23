# ライブラリをインポート
# streamlit
import streamlit as st
from streamlit_chat import message

# 
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
    template = fname.read()

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
# セッションIDをuser_idで管理
session_id = {}.format(user_id)

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
    elif st.session_state.state == 4:
        ()

def input_id():
    st.write("idを入力してください")
    st.session_state.user_id = st.input("IDを入力")
    st.session_state.state = 2

def chat_page():
    st.write("idを入力してください")
    st.session_state.user_id = st.input("IDを入力")
    st.session_state.state = 2

def chat_ended():
    chat_container = st.container(height=600) # st.containerでブロックを定義
    st.write("お疲れ様でした、下のURLを押してアンケートへ進んでください")
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])
    new_tab_js = ()
    st.markdown(new_tab_js, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

elif page==2:
    st.chat_input("", on_submit=chat_input_change())
# 送信ボタンがクリックされた後の処理を行う関数を定義

with page2:
    chat_container = st.container(height=600) # st.containerでブロックを定義
    st.session_state.prompt = st.chat_input("入力してね", on_submit=chat_input_change())
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

def chat_input_change(user_input):
    if len(message) == 10:
        end()
    st.spinner("待機中…")
    time.sleep(3)
    answer = chain_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": user_id}})
    st.session_state.message["user"].append(user_input)
    st.session_state.message["user"].append(answer)
    def data_to_fb(user_id, user_msg, ai_msg):
    doc_ref = db.collection(user_id).document(str(now))
    doc_ref.set({
        Human: user_message,
        AI_Agent: answer
    })
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("Agent"):
        st.write(answer)
    if len(message) == 10:
        st.session_state.page = 3
        break
    st.chat_input

with page3:
    st.write("終了しました、下のボタンを押してください")
    st.button("", on_click=page_to_4())

def page_to_2():
    st.session_state.page = "page2"
def page_to_3():
    st.session_state.page = "page3"

def redirect_to_url(url):
    new_tab_js = f"""<script>window.open("{url}", "_blank");</script>"""
    st.markdown(new_tab_js, unsafe_allow_html=True)
'''
'''
# Use Firebase
## connect and authenticate firebase
from google.cloud import firestore

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestore-key.json")

# Create a reference to the Google post.
doc_ref = db.collection("posts").document("Google")

# Then get the data at that reference.
doc = doc_ref.get()

# チャット履歴更新
def _init_messages():
if prompt := st.chat_input("Hit me up with your queries!"):  
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = hoge # id入力時 
    if "user_message" := st.chat_input(user_message):
        st.session_state.messages.append({"role": "user", "content": user_message})
    db = firestore.Client()
    doc_ref = db.collection(user_id).document(now)
    doc_ref.set({
    'user': user_content,
    'agent': agent_content
    })
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def init_message():
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(full_response)

if __name__ == '__main__':
    init_messages()

    # 過去のメッセージを表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # ユーザーの入力受付
    if user_input := st.chat_input("input your message"):
        # メッセージを保管
        st.session_state.messages.append({"role": "user", "content": user_input})
        db = firestore.Client()
        doc_ref = db.collection(user_id).document(now)
        doc_ref.set({
        'user': user_content,
        'agent': agent_content
        })
        stop(3)
        answer_message = llm(HumanPrompt = user_input)
        load_conversation(user_input, answer_message)
        st.session_state.messages.append({"role": "Agent", "content": answer_message})

# Let's see what we got!
 if "user" not in st.session_state:
        st.session_state.user = CHATBOT_USER

    if "chats_ref" not in st.session_state:
        db = firestore.Client(project=GCP_PROJECT)
        user_ref = db.collection("users").document(st.session_state.user)
        st.session_state.chats_ref = user_ref.collection("chats")

    if "titles" not in st.session_state:
        st.session_state.titles = [
                doc.to_dict()["title"]
                for doc in st.session_state.chats_ref.order_by("created").stream()
                ]
st.write("input your id: ", user_id)
st.write("input your conversation: ", )
st.session_state.user_info 

db = firestore.Client()
doc_ref = db.collection(user_id).document(now)
doc_ref.set({
    'user': user_content,
    'agent': agent_content
})

def send_message():
    

# Then query to list all users
users_ref = db.collection('users')
for doc in users_ref.stream():
    print('{} => {}'.format(doc.id, doc.to_dict()))
## store data to firebase
##
