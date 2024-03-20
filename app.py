import streamlit as st
from deep_translator import GoogleTranslator
import pytz
import requests
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, text
from datetime import datetime
import time
import toml

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)




API_TOKEN = st.secrets['config']['API_TOKEN']
api_url = st.secrets['config']['api_url']
DATABASE_URL = st.secrets['config']['DATABASE_URL']
headers = {"Authorization": f"Bearer {API_TOKEN}"}


if 'input' not in st.session_state:
    st.session_state.input = ''
    st.session_state.title = ''

def query(payload):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

def waktu_now_jakarta():
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    jakarta_time = datetime.now(jakarta_tz)
    jakarta_time = jakarta_time.replace(microsecond=0)
    jakarta_time = jakarta_time.strftime('%Y-%m-%d %H:%M:%S')
    return jakarta_time

def process():
    user_input = st.session_state['input']
    temp.empty()
    temp2.empty()

    translated_text = GoogleTranslator(source='auto', target='english').translate(st.session_state['input'])
    data_l = query({"inputs": translated_text})
    if data_l:
        data_l2 = data_l[0]
    else:
        st.title("ERROR!")
        st.stop()

    output = str(data_l2[0]['label'])
    score = float(data_l2[0]['score'])

    if data_l2[0]['score'] == data_l2[1]['score']:
        output = 'Unknown'
        st.title(output)
        st.stop()
    
    if output != None:
        pl.text("Wait for it....")
        #make db
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        meta = MetaData()
        data = Table(
            'data', meta,
            Column('id', Integer, primary_key = True, autoincrement=True),
            Column('text', String),
            Column('text_translated', String),
            Column('sentiment', String),
            Column('score', Float),
            Column('time', DateTime)
        )
        meta.create_all(engine)


        waktu = waktu_now_jakarta()
        stmt = text("INSERT INTO data (text, text_translated, sentiment, score, time) VALUES (:user_input, :translated_text, :output, :score, :waktu)")
        params = {'user_input': user_input, 'translated_text': translated_text, 'output': output, 'score': score, 'waktu': waktu}
        conn.execute(stmt, params)
        conn.commit()

        st.session_state.title = output
        st.session_state['input'] = ''



def contoh():
    st.write(st.session_state['input'])


st.title('Sentiment Analysis with hhhhDeepLearning')

temp = st.empty()
temp2 = st.empty()
pl = st.empty()


user_input = temp.text_input("Enter Your Sentence :", on_change=process, key='input')
# title = temp2.title(st.session_state['title'])

a = "<h1 style='background-color:#198754; text-align:center;'>POSITIVE</h1>"
b = "<h1 style='background-color:#dc3545; text-align:center;'>NEGATIVE</h1>"
c = "<h1 style='background-color:#ffc107; text-align:center;'>ERROR!</h1>"

if st.session_state.title == "POSITIVE":
    temp2.markdown(a, unsafe_allow_html=True)

elif st.session_state.title == "NEGATIVE":
    temp2.markdown(b, unsafe_allow_html=True)
elif st.session_state.title != '':
    temp2.markdown(c, unsafe_allow_html=True)

# st.session_state



