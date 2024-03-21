import streamlit as st
from flask import request
from deep_translator import GoogleTranslator
import pytz
import requests
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, false, text
from datetime import datetime
import time
import toml
from langdetect import detect
import geocoder
import pycountry
from typing import Optional
import socket


st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)


if 'input' not in st.session_state:
    st.session_state.input = ''
    st.session_state.title = ''
    st.session_state.err = False

DATABASE_URL = st.secrets['config']['DATABASE_URL']

API_TOKEN = st.secrets['config']['API_TOKEN']

#for text classficication
api_url = st.secrets['config']['api_url']
headers = {"Authorization": f"Bearer {API_TOKEN}"}
def query(payload):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

#for text to gen
headers2 = {"Authorization": f"Bearer {API_TOKEN}"}
api_text_to_gen = st.secrets['config']['API_URL_text_gen']
def query2(payload):
    response = requests.post(api_text_to_gen, headers=headers2, json=payload)
    return response.json()






def get_ip_address():
    api_ip = st.secrets['config']['api_ip']
    response = requests.get(api_ip)
    if response.status_code == 200:
        return response.json()['ip_address']
    else:
        return 'Error: Unable to reach API'
        
#get location using geocoder        
def get_location_g():
    try:
        client_ip = get_ip_address()
        g = geocoder.ip(client_ip)
        list = [g.latlng[0], g.latlng[1], g.city]
        return list
    except Exception as e:
        return str(e)
    
def detect_language(text):
    # Mendeteksi kode bahasa
    language_code = detect(text)
    
    # Mengubah kode bahasa menjadi nama bahasa lengkap
    language = pycountry.languages.get(alpha_2=language_code)
    
    if language is None:
        temp = detect(text)
        return f'{temp}, Unknown Language'
    else:
        return language.name




def waktu_now_jakarta():
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    jakarta_time = datetime.now(jakarta_tz)
    jakarta_time = jakarta_time.replace(microsecond=0)
    jakarta_time = jakarta_time.strftime('%Y-%m-%d %H:%M:%S')
    return jakarta_time



def process():
    user_input = st.session_state['input']

    if user_input == None or user_input == '':
        return 0
        
        
    try:
        temp.empty()
        temp2.empty()

        translated_text = GoogleTranslator(source='auto', target='english').translate(user_input)
        data_l = query({"inputs": translated_text})
        # st.write('data_l =',data_l)

    
        if data_l[0]:
            data_l2 = data_l[0]
            output = str(data_l2[0]['label'])
            score = float(data_l2[0]['score'])

            if data_l2[0]['score'] == data_l2[1]['score']:
                output = 'Neutral'

        if output != None and output != '':
            pl.markdown("<h2 style='text-align:center;'>Wait for it....</h2>", unsafe_allow_html=True)
            #make db
            engine = create_engine(DATABASE_URL)
            conn = engine.connect()
            meta = MetaData()
            data = Table(
                'data', meta,
                Column('id', Integer, primary_key = True, autoincrement=True),
                Column('text', String),
                Column('text_translated', String),
                Column('origin_language', String),
                Column('sentiment', String),
                Column('score', Float),
                Column('ip_user', String),
                Column('latitude', String),
                Column('longitude', String),
                Column('city', String),
                Column('time', DateTime),
                
            )
            meta.create_all(engine)

            lang_source = str(detect_language(user_input))
            ip = get_ip_address()
            getloc = get_location_g()
            long = getloc[1]
            lat = getloc[0]
            city = getloc[2]

            waktu = waktu_now_jakarta()
            stmt = text("INSERT INTO data (text, text_translated, origin_language, sentiment, score, ip_user, latitude, longitude, city, time) VALUES (:user_input, :translated_text, :os, :output, :score, :ip, :lat, :long, :city, :waktu)")
            
            params = {'user_input': user_input, 'translated_text': translated_text, 'os':lang_source, 'output': output, 'score': score, 'ip':ip, 'lat':lat, 'long':long, 'city':city, 'waktu': waktu}
            conn.execute(stmt, params)
            conn.commit()
            # st.text("STMT",stmt)

    except Exception as e:
        st.session_state.err = True

    st.session_state.title = output
        # st.session_state['input'] = ''
    
def process_text_to_gen():
    user_input = st.session_state['input']
    data = query2({"inputs": user_input})
    st.header(data)


def contoh():
    st.write(st.session_state['input'])


st.markdown('<h1 style="text-align:center;">Sentiment Analysis using DeepLearning</h1>', unsafe_allow_html=True)
st.subheader('', divider='violet')

temp = st.empty()
temp2 = st.empty()
pl = st.empty()


form = temp.form(key='form', clear_on_submit=True, border=True)
user_input = form.text_input("", key='input', autocomplete='thanks god!', max_chars=250, placeholder="Insert Here")


submitted = form.form_submit_button(use_container_width=True, disabled=st.session_state['err'], label="Analyze", type="primary", on_click=process)

# title = temp2.title(st.session_state['title'])




a = "<h1 style='background-color:#198754; text-align:center;'>POSITIVE</h1>"
b = "<h1 style='background-color:#dc3545; text-align:center;'>NEGATIVE</h1>"
c = "<h1 style='text-align:center;'>ERROR, Please refresh page.</h1>"
d = "<h1 style='background-color:#20c997; text-align:center;'>NEUTRAL</h1>"

if st.session_state.title == "POSITIVE":
    form.text("Text : "+user_input)
    temp2.markdown(a, unsafe_allow_html=True)
elif st.session_state.title == "NEGATIVE":
    form.text("Text : "+user_input)
    temp2.markdown(b, unsafe_allow_html=True)
elif st.session_state.title == "NEUTRAL":
    form.text("Text : "+user_input)
    temp2.markdown(d, unsafe_allow_html=True)
elif st.session_state.err == True: 
    st.session_state.err = False 
    temp2.markdown(c, unsafe_allow_html=True)

st.subheader('', divider='violet')
# st.session_state



