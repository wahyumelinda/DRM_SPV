import streamlit as st
import requests
import json
import pandas as pd  

st.set_page_config(page_title="SPV Approval", page_icon="⏳", layout="wide")

# URL apps script
API_URL = "https://script.google.com/macros/s/AKfycbzsuKredhurZqKVQz8XR1v7PemvrJ3yAdKRx7LHxpEwTLGMUOGzeGYbW_tZ732Wk35NKA/exec"

st.title("SPV Approval")

# Ambil semua data 
def get_all_data():
    response = requests.get(f"{API_URL}?action=get_data")
    if response.status_code == 200:
        return response.json()
    return []

# Ambil opsi SPV dari sheet Google Spreadsheet
def get_spv_list():
    response = requests.get(f"{API_URL}?action=get_options")
    if response.status_code == 200:
        options = response.json()
        return options.get("SPV", [])
    return []

# Inisialisasi semua data
all_data = get_all_data()

# Jika data berhasil diambil
if all_data:
    # Konversi ke DataFrame
    df = pd.DataFrame(all_data, columns=[
        "ID", "BU", "Line", "Produk", "Mesin", "Tanggal",
        "Mulai", "Selesai", "Masalah", "Tindakan", "Deskripsi",
        "Quantity", "PIC", "Kondisi", "Alasan", "SPV", "Last Update SPV", 
        "Approve", "Reason", "SM", "Last Update SM"
    ])

    # Pastikan kolom yang digunakan benar
    if "ID" in df.columns and "Kondisi" in df.columns:
        # Selectbox untuk memilih filter data
        filter_option = st.selectbox(
            "Pilih Data yang Ingin Ditampilkan",
            ["Data Keseluruhan", "On Progress / Kosong", "Close & Done"]
        )

        # **Filter dataframe berdasarkan pilihan**
        if filter_option == "On Progress / Kosong":
            df_filtered = df[df["Kondisi"].astype(str).isin(["On Progress", ""])]
        elif filter_option == "Close & Done":
            df_filtered = df[df["Kondisi"].astype(str).isin(["Close", "Done"])]
        else:
            df_filtered = df  # Tampilkan semua data jika pilih "Data Keseluruhan"

        # **Tampilkan data setelah difilter**
        st.subheader(f"Tabel Data - {filter_option}")
        st.dataframe(df_filtered)

        # **Ambil daftar ID berdasarkan hasil filter**
        id_list = df_filtered["ID"].astype(str).tolist()

        # **Pilihan ID dari selectbox (berdasarkan hasil filter)**
        id_to_update = st.selectbox("Pilih ID untuk diupdate", id_list)

        # **Jika ID dipilih, tampilkan data terkait**
        if id_to_update:
            record = df[df["ID"] == id_to_update]
            st.write("### Data Saat Ini:")
            st.dataframe(record)

            # Pilihan kondisi
            kondisi_options = ["On Progress", "Close", "Done"]
            kondisi = st.selectbox("Pilih Kondisi", kondisi_options)

            # Alasan hanya muncul jika kondisi "On Progress"
            alasan = ""
            if kondisi == "On Progress":
                alasan = st.text_area("Alasan")

            # Pilihan SPV dari Google Sheet
            spv_list = get_spv_list()
            spv = st.selectbox("SPV", spv_list)

            # **Tombol Update Data**
            if st.button("Update Data"):
                data = {
                    "action": "update_data",
                    "ID": id_to_update,
                    "Kondisi": kondisi,
                    "Alasan": alasan,
                    "SPV": spv
                }

                response = requests.post(API_URL, data=json.dumps(data))

                if response.status_code == 200:
                    result = response.json()
                    last_update_spv = result.get("last_update_spv", "Tidak tersedia")
                    
                    st.success(f"✅ Data berhasil diperbarui! (Last Update SPV: {last_update_spv})")
                    st.session_state.form_add_reset = True
                    st.rerun()
                else:
                    st.error("❌ Gagal memperbarui data. Cek kembali input dan koneksi.")
    else:
        st.error("❌ Kolom 'ID' atau 'Kondisi' tidak ditemukan. Periksa struktur data yang diambil!")

else:
    st.error("❌ Gagal mengambil data dari Google Sheet.")
