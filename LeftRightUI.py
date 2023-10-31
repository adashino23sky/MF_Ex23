# ライブラリをインポート
import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
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

# 環境変数の読み込み
#from dotenv import load_dotenv
#load_dotenv()

#プロンプトテンプレートを作成
template = """
Instructions:
You are now going to practice debating with me. I will specify the content and setting of the debate.
Follow the prior information, the debate setting and the participants' settings to interact about the theme and reach the goal.

Theme:
Should Japan abolish nuclear power generation or not?

Debate setting:
This is a simple group work in a university class.
This debate will be held in Japanese.
Each statement should be answered in 150 characters or less in Japanese.

Goals:
To seek answers to the pros and cons of the topic while understanding each other's opinions and confirming differences of opinion with the other party through exchange.

Participants:
Two university students (you and I will act as you and me)

Preliminary information:
(1) About moral foundations
You are familiar with Haidt's five moral foundations, called Moral Foundations Theory.
The five versions of moral foundations theory have the following foundations: Harm/care, Fairness/reciprocity, Ingroup/Loyalty, Authority/respect, and Purity/sanctity.
Moral judgments are made according to each of these bases.
The following is an example of the explanation of each foundation.
Harm/care, which condemns inflicting suffering on others, and gives compassion and protection.
Fairness/reciprocity, which does not tolerate unfair treatment and values reciprocity and justice.
Ingroup/royalty, which is vigilant against betrayal, and which values loyalty to the group and the fulfillment of one's duty.
Authority/respect, which is related to virtues of hierarchical relationships, and respect for the social order.
Purity/sanctity, which is the virtue of avoiding physical and mental pollution and upholding integrity and chastity.
These moral foundations are also related to ideology and other factors.
For more information, please refer to Moral Foundation Theory, MFT, Moral Foundation Theory, and other related information.
(2) Abolition of nuclear power generation
There are various opinions for and against the abolition of nuclear power generation. Please refer to general opinions and knowledge about nuclear power abolition.

Your setting:
You are an ordinary Japanese university student.
You are polite and casual.
Please try to use plain expressions that even elementary school students can understand.
Please do not use interjections such as, um, let's see, um, well, etc. 
For your opinion, please follow these instructions.

Your opinion:
Decide your position for or against and the content of your opinion based on your own moral foundation.
Please do not speak neutrally.
If you have a good understanding of the content of moral foundation theory, the relationship between moral foundation and ideology, and consideration of Harm foundation, you may agree, disagree, or question your opponent's opinion during the discussion.
Do not address yourself to anything that the Harm foundation might not insist on.
Please refer to general opinions and knowledge about the abolition of nuclear power, taking into account your moral foundation.

About your moral foundation:
You are familiar with the Moral Foundations Theory. You are particularly more sensitive to the Harm foundation than most people, one of the key elements of the theory.
Consider what opinions you would assert with a high Harm foundation and how you would react to which of your opponents' arguments.

My Setting:
I am a student from the same college as you who will be participating in the same group work.
No other information is specified.
I will offer my opinion as I see fit.

I will initiate the conversation.
"""

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
        #model_name="gpt-4",
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
            model_name="gpt-4",
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
            #time.sleep(60)
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

# タイトルやキャプション部分のUI
st.title("ChatApp")
#st.caption("Q&A")
st.write("議論を行いましょう！")
user_number = st.text_input("学籍番号を入力してエンターを押してください")
if user_number:
    st.write(f"こんにちは、{user_number}さん！")
    # 初期済みでない場合は初期化処理を行う
    if not firebase_admin._apps:
            cred = credentials.Certificate('chatapp-509c9-firebase-adminsdk-5tvj9-9106d52707.json') 
            default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    #doc_ref = db.collection(user_number)
    #doc_ref = db.collection(u'tour').document(str(now))

# 会話履歴を表示するためのスペースを確保
chat_placeholder = st.empty()

# 会話履歴を表示
with chat_placeholder.container():
    for i in range(len(st.session_state.generated)):
        message(st.session_state.past[i],is_user=True)
        message(st.session_state.generated[i])

# 質問入力欄と送信ボタンを設置
with st.container():
    user_message = st.text_input("内容を入力して送信ボタンを押してください", key="user_message")
    st.button("送信", on_click=on_input_change)
# 質問入力欄 上とどっちが良いか    
#if user_message := st.chat_input("聞きたいことを入力してね！", key="user_message"):
#    on_input_change()


redirect_link = "https://nagoyapsychology.qualtrics.com/jfe/form/SV_cw48jqskbAosSLY"
st.markdown(f'<a href="{redirect_link}" target="_blank">5往復のチャットが終了したらこちらを押してください。</a>', unsafe_allow_html=True)
#if st.button("終了したらこちらを押してください。画面が遷移します。"):
    #redirect_to_url("https://www.google.com")


