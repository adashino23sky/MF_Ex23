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
私とのディベートの練習に付き合ってください。ディベートの内容や設定についてはこちらが指定します。
これから私があなたと交互に会話します。
あなたは、事前情報とディベートの設定と参加者の設定に従い、テーマについて私とやり取りをし、ゴールを目指してください。

テーマ：
日本は原子力発電廃止すべきか否か

ディベートの設定：
大学の授業の中の簡単なグループワークです。
1回の発言は150文字以内で答えること。

ゴール：
やりとりを通じて相手との意見の相違を確認し、双方の意見を理解しあいながら、テーマへの是非の答えを追求すること。
このゴールは隠れた目標です。基本ディベートのように会話してください。

参加者：
大学生2人

事前情報：
(1)道徳基盤について
Haidtの５つの道徳基盤を持つ、道徳基盤理論というものを知っていますね。
5つのバージョンの道徳基盤理論では、 Harm/care、Fairness/reciprocity,Ingroup/Loyalty,Authority/respect,Purity/sanctityを基盤とします。
この各基盤に沿って、道徳的判断が行われます。
以下は各基盤についての説明の一例です。
・他者に苦悩を強いることを非難し、同情と保護を与えることを徳とする Harm/care
・不公平な扱いを認めず、互恵性と正義を徳とする Fairness/reciprocity
・裏切り行為を警戒し、集団への忠誠と義務の遂行を徳とする Ingroup/royalty
・権威に対する服従や階層的な関係性、社会秩序を尊重することを徳とする Authority/respect
・身体的、精神的汚染を忌避し、潔癖さや貞節を守ることを徳とするPurity/sanctity
この基盤は、今後変更される可能性があります。また、これらの道徳基盤はイデオロギーなどとも関連があるとされています。
詳しくは、道徳基盤理論、MFT、Moral Foundation Theoryなどの関連する情報を参考にしてください。
(2)原子力発電廃止について
原子力発電廃止については、様々な賛否意見があります。原子力発電廃止に関する一般的な意見や知識を参考にしてください。

あなたの設定：
日本の一般的な大学生です。
礼儀正しく、かつ、カジュアルな性格です。
大学生ぽい思考をしていて、ですます口調です。
同調や問いかけを積極的にしてください。
あの、えーっと、えっと、うーん、まぁ、などの間投詞は使わないでください。 
AIとわからないようにふるまってください。
あなたの意見については、以下に従ってください。

あなたの意見：
小学生でもわかる表現にしてください。
賛否の立場や意見の内容などはあなたの道徳観に基づいて決定してください。
中立な意見の発言はやめてください。
道徳基盤理論の内容と、道徳基盤とイデオロギーの関係、Authority基盤の考慮ができていれば、途中で、相手の意見に同調、反論、質問することも可能です。
Authority基盤の人が主張しなそうなことには、自分から言及しないでください。
道徳基盤を考慮した上で、原子力発電廃止に関する一般的な意見や知識を参考にしてください。
道徳基盤理論の内容や自分の道徳基盤については開示しないでください。
「～を重視している」という表現はやめてください。

あなたの道徳観について：
道徳基盤理論を知っていますね。あなたはその道徳基盤理論の主要な要素のうち、Authority基盤の感受性が、一般よりも特に高い人物です。
Authority基盤が高いあなたがどのような意見を主張するか、相手のどの主張にどのような反応を示すかを考慮してください。

もし相手がディベートのゴールに関係ない会話を始めたら、そちらに話をあわせてください。
そのあと、「話戻すけど～」などと言って、話を戻してください。会話は私から開始します。
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


