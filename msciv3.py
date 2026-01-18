import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="MSCI Checker - Manual Input", layout="wide")
st.title("📊 MSCI Eligibility Checker (Kriteria Sumber [1])")

# Input Pengguna
col_input1, col_input2 = st.columns(2)

with col_input1:
    ticker_symbol = st.text_input("Masukkan Kode Saham (Contoh: BREN.JK):", value="BREN.JK")

with col_input2:
    # Pengguna memasukkan persentase saham masyarakat secara manual sesuai data bursa
    free_float_pct = st.number_input("Masukkan Persentase Saham Masyarakat (%)", 
                                     min_value=0.0, max_value=100.0, value=13.0, step=0.1)

if ticker_symbol:
    try:
        # Mengambil data dari Yahoo Finance API
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        history = ticker.history(period="1y") # Data 1 tahun untuk turnover

        # 1. Total Market Cap (Kriteria: Minimal 50 Triliun [1])
        total_market_cap = info.get('marketCap', 0)
        
        # 2. Perhitungan Free Float Market Cap (Kriteria: Minimal 25 Triliun [1])
        # Rumus sesuai sumber: Total Market Cap * Porsi Saham Masyarakat
        free_float_market_cap = total_market_cap * (free_float_pct / 100)

        # 3. Perhitungan ATVR (Kriteria: Minimal 15% [1])
        # Rumus sesuai sumber: Annual Turnover / Free Float Market Cap
        annual_turnover = (history['Volume'] * history['Close']).sum()
        atvr = (annual_turnover / free_float_market_cap) if free_float_market_cap > 0 else 0

        # Menampilkan Hasil Analisis
        st.divider()
        st.subheader(f"Hasil Analisis untuk {info.get('longName', ticker_symbol)}")
        
        c1, c2, c3 = st.columns(3)

        # Cek Total Market Cap
        with c1:
            is_mc_ok = total_market_cap >= 50e12
            st.metric("Total Market Cap", f"Rp {total_market_cap/1e12:.2f} T")
            st.write("Status: " + ("✅ Lolos (>= 50T)" if is_mc_ok else "❌ Tidak Lolos"))

        # Cek Free Float Market Cap
        with c2:
            is_ff_ok = free_float_market_cap >= 25e12
            st.metric("Free Float Market Cap", f"Rp {free_float_market_cap/1e12:.2f} T")
            st.caption(f"Dihitung dari {free_float_pct}% porsi masyarakat")
            st.write("Status: " + ("✅ Lolos (>= 25T)" if is_ff_ok else "❌ Tidak Lolos"))

        # Cek ATVR (Likuiditas)
        with c3:
            is_atvr_ok = atvr >= 0.15
            st.metric("ATVR (Likuiditas)", f"{atvr*100:.2f}%")
            st.write("Status: " + ("✅ Lolos (>= 15%)" if is_atvr_ok else "❌ Tidak Lolos"))

        # Kesimpulan Berdasarkan Sumber
        st.divider()
        if is_mc_ok and is_ff_ok and is_atvr_ok:
            st.success("**KESIMPULAN:** Saham ini memenuhi tiga kriteria utama MSCI berdasarkan perhitungan sumber [1].")
            st.balloons()
        else:
            st.error("**KESIMPULAN:** Saham ini belum memenuhi kriteria kelayakan MSCI.")
            
        st.info("Catatan: Pengelola indeks juga menggunakan **metode ranking** dengan menghitung seluruh saham di bursa untuk menentukan urutan kelayakan akhir [1].")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}. Pastikan kode ticker benar.")