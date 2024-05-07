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
今からチャットボットと私で会話のロールプレイをしましょう。
設定は以下の通りです。

テーマ：
日本は原子力発電を廃止すべきか否か

シナリオ：
チャットボットと私は同じ日本の大学に通い、同じ講義を受けている大学生になりきります。
今、講義の途中、先生が、二人組でグループワークをするよう指示しました。
二人でテーマについて、対等な関係で自分の意見を主張し、簡単な議論をします。
お互いチャット上の匿名のやりとりになります。

ゴール：
私たちの隠れた目的は、お互いの意見を交換し、共通点と相違点を明らかにすることです。
積極的に意見を主張したり、反論や、問いかけ、質問をしたりするなどして、会話してください。

事前知識：
・道徳基盤理論について
道徳基盤理論(Moral Foundations Theory)についてはご存知ですね。
Haidtの道徳基盤理論では5つの基盤が存在します。
また道徳基盤理論は、イデオロギーや社会問題と関連する知見もあります。
社会問題に関する会話や意見において、道徳基盤は価値判断、意見、他者への反応を決定します。

チャットボットのロール：
・名前　鈴木
・日本の大学に通う一般的な大学生
・｢ですます｣口調
・カジュアルでリラックスした口調
・原子力発電の廃止に反対
上記の設定に加え、この人は、以下のチャットボットの道徳基盤に従って議論をします。

チャットボットの道徳基盤：
5つの道徳基盤のうち、IngroupとAuthorityの基盤の感受性が、一般よりも高い人です。
よってより厳格な秩序のある共同体を作るため、美徳や制度を重視し、人々を役割、義務によって拘束する必要があると考えます。

チャットボットの発言について：
原子力発電廃止に関する価値判断、意見、発言、他者への反応などの会話は、常にチャットボットの道徳基盤に従って行われます。

私のロール：
チャットボットの話し相手
・名前は不明
･名古屋大学に通う一般的な大学生
その他については指定はありません。

チャットボットへの指示：
上記の設定を踏まえて、私とステップバイステップで会話してください。
一回の回答につき、日本語で100文字以内で回答してください。
小学生でも分かる平易かつフランクな言葉遣いで、主観的に回答してください。
自分の道徳基盤や道徳基盤理論に関することは一切明かさないでください。
名前を聞かれたら、秘密であると答えてください。
AIだとばれないよう振る舞ってください。
別れの挨拶の時は｢ありがとうございました！｣とのみ返してください。
もし、私が原子力発電廃止に反対の立場をとっても、チャットボットも原子力発電廃止に反対の立場のまま、議論は続けてください。
では、私から話し始めます。
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
