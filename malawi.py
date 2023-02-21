import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#library gsheet
import gspread as gs
# library progress
import time
from annotated_text import annotated_text
import re
import webbrowser
from datetime import date
from datetime import datetime
import plotly.express as px

# setting page nya jadi gede
st.set_page_config(layout="wide")
# judul dan sub bagiannya
bag1, bag2 = st.columns([4,1])
with bag1:
    st.markdown("<h1 style='text-align: center; color: black;'>Dashboard Absensi Kelompok Malawi Version 1.0</h1>", unsafe_allow_html=True)
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1, text=progress_text)    
    sub1, sub2 = st.columns(2)
    with sub1 :
        current_dateTime = date.today()
        st.write(":blue[Tanggal Sekarang adalah:]", current_dateTime, "_waktu setempat_")
    with sub2: 
        st.markdown("<h6 style='text-align: right; '> Powered By: GrMi </h6>", unsafe_allow_html=True)
with bag2:
    image = Image.open('note.png')
    st.image(image)

# declare data dan looping
SHEET_ID = '1QphUIDEVnGOacEiLD5H72KGXlCkbhKNr-RZVvJWnt8U'
SHEET_NAME = 'main_page'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

def get_data() -> pd.DataFrame:
    return pd.read_csv(url)

df = pd.read_csv(url)
# pembagian tab dan dashboard data
tab1, tab2, tab3 = st.tabs(["Main Page", "Hasil Pencarian", "Contact Us"])
with tab1:
    st.write("Entry Absen Terbaru (_*silahkan refresh halaman untuk update_)")
    df = df.sort_values(by="Timestamp", ascending=False)
    terbaru15 = df.head(10)
    st.table(terbaru15)

    # create two column chart
    fig_col1, fig_col2 = st.columns(2)
    with fig_col1 :
        st.markdown("<h4 style='text-align: center; color: red;'>Barplot Jenis Kehadiran keseluruhan</h4>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center; color: black; '>Mulai 2023-02-19</h6>", unsafe_allow_html=True)
        fig = px.bar(data_frame=df, x='Kehadiran ', color = 'Kehadiran ')
        st.write(fig)
        with st.expander("Insight:"):
            cn = df['Kehadiran '].value_counts()
            cn["column_total"] = cn.sum(numeric_only=True, axis=0)
            hadir = cn["Hadir"]
            izin = cn["Izin"]
            sakit = cn["Sakit"]
            total = cn["column_total"]
            st.write("Kehadiran Kelompok Malawi sampai pada:", current_dateTime, ".", "Hadir:", round(hadir/total*100,2), "%",
                    "Izin:", round(izin/total*100, 2), "% dan sakit:", round(sakit/total*100,2), "%.")
    with fig_col2 :
        f1 = st.selectbox('Pilih Jenis Kehadiran', {'Semua', 'Hadir', 'Izin', 'Sakit'})
        w1, w2 = st.columns(2)
        with w1:
            rm= st.date_input("Range mulai", date(2023,1,1))
        with w2:
            ra= st.date_input("Range akhir", current_dateTime)
        halo = "{}".format(f1)
        df.loc[:, "Timestamp"] = pd.to_datetime(df.loc[:,"Timestamp"], infer_datetime_format=True)  
        df["tanggal"] = pd.to_datetime(df["Timestamp"]).dt.date

        filter = df.loc[df["tanggal"] <= ra]
        filter = filter.loc[filter["tanggal"] >= rm]

        st.write("Plotting kehadiran dengan filter range", rm, "-", ra)
        if halo == 'Hadir':
            filter = filter.loc[filter["Kehadiran "]=="Hadir"]
        elif halo == 'Izin':
            filter = filter.loc[filter["Kehadiran "]=="Izin"]
        elif halo == 'Sakit':
            filter = filter.loc[filter["Kehadiran "]=="Sakit"]
        else:
            filter = filter
        gb = px.bar(data_frame=filter, x='Kehadiran ', color = 'Kehadiran ')
        st.write(gb)
    # selanjutnya akan membahas time series dari data 
    annotated_text(("Plot Detail Per Pengajian", "Time series"))
    df2 = df.groupby(['tanggal', 'Kehadiran ']
                    ).size().unstack(fill_value=0).reset_index()
    hj = df2.set_index('tanggal')
    st.area_chart(hj)
# pencarian cepat
with st.sidebar:
    st.subheader(':blue[Pencarian Cepat]')
    tgl = st.date_input("Pilihan tanggal", 
                  current_dateTime)
    radio = st.radio("Set Filter Tanggal", ("Yes", "No"))
    nama = st.text_input("Masukkan nama")
    if st.button('Temukan'):
            st.write("Silahkan pergi ke Tab Hasil Pencarian")
            with tab2:
                 if radio == "Yes":
                     st.write("Berikut ditampilkan berdasar perintah", tgl, "dan", nama)
                 else:
                     st.write("Berikut ditampilkan berdasar perintah", nama)
                 pencarian = df
                 pencarian['find'] = pencarian.iloc[:, 2].str.findall(nama, flags=re.IGNORECASE)
                 pencarian['similar'] = pencarian["find"].str.len()
                 pencarian = pencarian.loc[pencarian["similar"] >0 ]
                 if radio == "No":
                     pencarian = pencarian
                 else:
                    pencarian = pencarian.loc[pencarian["tanggal"] == tgl]
                 pencarian = pencarian.iloc[:, :6]
                 st.table(pencarian)
    else:
        st.write('Belum diminta')
    
    with st.expander("Ketahui Lebih Labjut"):
        st.write("Silahkan isi tanggal, klik _Yes_ untuk mengaktifkan tanggal, isi pencarian nama, dan klik _Temukan_")
        st.write("Secara default, tanggal akan aktif dan diset hari ini dan mencari semua nama")
with tab3:
    b1, b2 = st.columns([1, 3])
    with b1:
        ludy = Image.open('profile.jpg')
        st.image(ludy)
    with b2:
        st.write("_If you find a mistake or provide any suggestion, please contact us !_")
        st.write("_Waiting you at version 2......_")
        if st.button('_Whatsapp_'):
            webbrowser.open_new_tab('https://wa.me/+6285735949780')
        if st.button('E-mail'):
            webbrowser.open_new_tab('mailto:fewesgalih@gmail.com?Subject=Dashboard%20Malawi%20Version%201')
        if st.button('Github'):
            webbrowser.open_new_tab('https://github.com/ludyhasby')