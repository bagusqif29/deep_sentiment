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


def query(payload):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

def waktu_now_jakarta():
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    jakarta_time = datetime.now(jakarta_tz)
    jakarta_time = jakarta_time.replace(microsecond=0)
    jakarta_time = jakarta_time.strftime('%Y-%m-%d %H:%M:%S')
    return jakarta_time


output = None
score = None
st.title('Sentiment Analysis with DeepLearning')

user_input = st.text_input("Enter Your Sentence :")
if user_input :
    translated_text = GoogleTranslator(source='auto', target='english').translate(user_input)
    data_l = query({"inputs": translated_text})
    data_l = data_l[0]

    output = str(data_l[0]['label'])
    score = float(data_l[0]['score'])


    if data_l[0]['score'] == data_l[1]['score']:
        output = 'Unknown'
        st.title(output)
        st.stop()

    if output == None:
        output = 'ERROR'
        st.title(output)
        st.stop()
    
if output != None:
    
    with st.spinner("Wait for it...."):
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


        print("berhasil "+str(user_input))
        print("_______________________________________________________________")
        
    st.title(output)




