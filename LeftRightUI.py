# ライブラリをインポート
import streamlit as st
from streamlit_chat import message
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories.streamlit import StreamlitChatMessageHistory

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import pytz
#現在時刻
global now
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

# read system prompt text
with open(fname, 'r') as f:
    templete = fname.read()

from langchain_openai import ChatOpenAI
# initializing chat model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=0,
    api_key= st.secrets.openai_api_key
)

from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import HumanMessagePromptTemplate

prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="You are a helpful assistant"),
        MessagesPlaceholder("history"),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)
history = [
        HumanMessage(content="hi! my name is 太郎"),
        AIMessage(content="hello 太郎"),
        ]

prompt = prompt_template.invoke(
   {
       "history": history,
       "question": "Call me my name."
   }
)
print(prompt.messages)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but don't know current events",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
# 会話のテンプレートを作成
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
])
#会話の読み込みを行う関数を定義
#@st.cache_resource
#def load_conversation():
    #llm = ChatOpenAI(
        #model_name="gpt-4-0125-preview",
        #temperature=0
    #)
    #memory = ConversationBufferMemory(return_messages=True)
    #conversation = ConversationChain(
        #memory=memory,
        #prompt=prompt,
        #llm=llm)
    #return conversation
# デコレータを使わない会話履歴読み込み
def load_conversation():
    if not hasattr(st.session_state, "conversation"):
        llm = ChatOpenAI(
            model_name="gpt-4-0125-preview",
            temperature=0
        )
        memory = ConversationBufferMemory(return_messages=True)
        st.session_state.conversation = ConversationChain(
            memory=memory,
            prompt=prompt,
            llm=llm)
    return st.session_state.conversation
# 質問と回答を保存するための空のリストを作成
if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []
# 送信ボタンがクリックされた後の処理を行う関数を定義
def on_input_change():
    user_message = st.session_state.user_message
    conversation = load_conversation()
    answer = conversation.predict(input=user_message)
    st.session_state.generated.append(answer)
    #with st.spinner("入力中。。。"):
            # 任意時間入力中のスピナーを長引かせたい場合はこちら！
            #time.sleep(1)
    st.session_state.past.append(user_message)
    st.session_state.user_message = ""
    Human_Agent = "Human" 
    AI_Agent = "AI" 
    doc_ref = db.collection(user_number).document(str(now))
    doc_ref.set({
        Human_Agent: user_message,
        AI_Agent: answer
    })
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
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
