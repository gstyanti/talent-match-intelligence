# ==========================================================
# 💼 AI Talent Match Dashboard - Final Version
# ==========================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from openai import OpenAI

# --- CONFIGURATIONS ---
st.set_page_config(page_title="AI Talent Match Dashboard", layout="wide")
st.title("💼 AI Talent Match Dashboard")

# --- CONNECT TO SUPABASE ---
supabase_conf = st.secrets["connections"]["supabase"]
conn_str = (
    f"postgresql+psycopg2://{supabase_conf['user']}:"
    f"{supabase_conf['password']}@{supabase_conf['host']}:"
    f"{supabase_conf['port']}/{supabase_conf['database']}"
)
engine = create_engine(conn_str)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        # Coba ambil dari Supabase
        query = "SELECT * FROM talent.match_results;"
        df = pd.read_sql(query, engine)
        st.success("✅ Data berhasil dimuat dari Supabase!")
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data dari Supabase: {e}")
        # fallback ke file lokal
        st.warning("⚠️ Memuat data dari file lokal 'match_results.csv'...")
        df = pd.read_csv("match_results.csv")
        return df

# --- MAIN APP ---
st.sidebar.header("🧭 Dashboard Control")

df = load_data()

if df.empty:
    st.warning("⚠️ Data kosong. Pastikan tabel `talent.match_results` berisi data.")
    st.stop()

# --- Sidebar filters ---
role = st.sidebar.selectbox("Pilih Department", sorted(df["name_department"].unique()))
level = st.sidebar.selectbox("Pilih Job Title", sorted(df["name_position"].unique()))

filtered = df[(df["name_department"] == role) & (df["name_position"] == level)]

st.subheader(f"📊 Analisis Hasil Match Rate untuk {role} — {level}")

# --- Visual 1: Distribution Plot ---
fig, ax = plt.subplots(figsize=(6, 3))
sns.histplot(filtered["final_match_rate"], bins=10, kde=True, ax=ax, color="skyblue")
ax.set_title("Distribusi Final Match Rate")
st.pyplot(fig)

# --- Visual 2: Top 10 Candidates ---
top_candidates = filtered.nlargest(
    10, "final_match_rate"
)[["employee_id", "fullname", "final_match_rate", "match_category"]]
st.subheader("🏅 Top 10 Kandidat Berdasarkan Match Rate")
st.dataframe(top_candidates)

# --- AI Insight Generator ---
st.markdown("### 🤖 Insight AI Talent Analysis")

client = OpenAI(
    api_key=st.secrets["openai"]["api_key"], 
    base_url="https://openrouter.ai/api/v1"
)

prompt = f"""
Kamu adalah HR Data Analyst.
Analisislah 3 insight utama berdasarkan data kandidat berikut:
{top_candidates.to_string(index=False)}
Fokus pada pola performa dan potensi kandidat unggulan.
"""

if st.button("✨ Generate Insight AI"):
    with st.spinner("Sedang menganalisis dengan AI..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Kamu adalah HR Data Analyst profesional."},
                {"role": "user", "content": prompt},
            ],
        )
        st.success("✅ Analisis selesai!")
        st.markdown(response.choices[0].message.content)

st.markdown("---")
st.caption("Built by [Gusti Ayu Putu Febriyanti] — Rakamin Case Study 2025")
