import streamlit as st
from PIL import Image
import os
from io import BytesIO
from xhtml2pdf import pisa
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Persona Builder Card", layout="centered")

# Template selector
style_option = st.sidebar.selectbox("Pilih Template Card", ["Default", "Elegant Dark", "Playful", "Minimal Light"])

# Define different style templates
styles = {
    "Default": """
        .card {
            background-color: #f9fafb;
            color: #111827;
            border-radius: 1rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
            padding: 2rem;
        }
    """,
    "Elegant Dark": """
        .card {
            background-color: #1f2937;
            color: #f3f4f6;
            border-radius: 1rem;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            padding: 2rem;
        }
    """,
    "Playful": """
        .card {
            background-color: #fff7ed;
            color: #7c2d12;
            border: 3px dashed #fb923c;
            border-radius: 1rem;
            padding: 2rem;
            font-family: Comic Sans MS, cursive;
        }
    """,
    "Minimal Light": """
        .card {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            padding: 1.5rem;
        }
    """
}

st.markdown(f"""
    <style>
    {styles[style_option]}
    .card img {{
        border-radius: 1rem;
        border: 2px solid #e5e7eb;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Persona Builder Card")

# Inisialisasi koneksi ke Google Sheets
def init_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("persona_builder_db").sheet1
    return sheet

sheet = init_gsheet()

# Simpan data ke Sheet
def simpan_ke_sheet(data_dict):
    values = [
        data_dict["fan_name"],
        data_dict["name"],
        data_dict["age"],
        data_dict["occupation"],
        data_dict["race"],
        data_dict["nationality"],
        data_dict["strength"],
        data_dict["weakness"],
        data_dict["psychology"],
        data_dict["hobby"],
        data_dict["siblings"]
    ]
    sheet.append_row(values)

# Cari data berdasarkan Fan Name
def cari_persona(fan_name):
    df = pd.DataFrame(sheet.get_all_records())
    if fan_name in df['fan_name'].values:
        data = df[df['fan_name'] == fan_name].iloc[0].to_dict()
        return data
    return None

# Search existing personas
st.sidebar.markdown("### 🔍 Cari Character")
search_query = st.sidebar.text_input("Masukkan nama")
if search_query:
    match = cari_persona(search_query)
    if match:
        st.sidebar.success("Character ditemukan!")
        st.sidebar.json(match)
        st.subheader("🪪 Persona Card Ditemukan")
        st.markdown(f"""
        <div class='card'>
        <h2>{match['name']}</h2>
        <p><strong>Fan Name (App):</strong> {match['fan_name']}</p>
        <p><strong>Usia:</strong> {match['age']}</p>
        <p><strong>Occupation:</strong> {match['occupation']}</p>
        <p><strong>Race:</strong> {match['race']}</p>
        <p><strong>Nationality:</strong> {match['nationality']}</p>
        <p><strong>Strength:</strong> {match['strength']}</p>
        <p><strong>Weakness:</strong> {match['weakness']}</p>
        <p><strong>Kondisi Psikologi:</strong> {match['psychology']}</p>
        <p><strong>Hobby:</strong> {match['hobby']}</p>
        <p><strong>Keluarga (Siblings):</strong> {match['siblings']}</p>
        </div>
        """, unsafe_allow_html=True)

        def convert_html_to_pdf(source_html):
            result = BytesIO()
            pisa_status = pisa.CreatePDF(source_html, dest=result)
            if not pisa_status.err:
                return result.getvalue()
            return None

        pdf_html = f"""
        <h1>{match['name']}</h1>
        <p><strong>Fan Name:</strong> {match['fan_name']}</p>
        <p><strong>Age:</strong> {match['age']}</p>
        <p><strong>Occupation:</strong> {match['occupation']}</p>
        <p><strong>Race:</strong> {match['race']}</p>
        <p><strong>Nationality:</strong> {match['nationality']}</p>
        <p><strong>Strength:</strong> {match['strength']}</p>
        <p><strong>Weakness:</strong> {match['weakness']}</p>
        <p><strong>Psychology:</strong> {match['psychology']}</p>
        <p><strong>Hobby:</strong> {match['hobby']}</p>
        <p><strong>Siblings:</strong> {match['siblings']}</p>
        """

        pdf_data = convert_html_to_pdf(pdf_html)
        if pdf_data:
            st.download_button(
                label="📄 Download Card as PDF",
                data=pdf_data,
                file_name=f"persona_{match['fan_name']}.pdf",
                mime="application/pdf"
            )
    else:
        st.sidebar.warning("Character tidak ditemukan.")

with st.form("persona_form"):
    fan_name = st.text_input("Nama Fan Dalam App")
    name = st.text_input("Nama Lengkap")
    age = st.number_input("Usia", min_value=0, max_value=150, step=1)
    occupation = st.text_input("Occupation")
    race = st.text_input("Race")
    nationality = st.text_input("Nationality")
    strength = st.text_area("Strength")
    weakness = st.text_area("Weakness")
    psychology = st.text_area("Kondisi Psikologi")
    hobby = st.text_input("Hobby")
    siblings = st.text_input("Keluarga (Siblings)")
    photo = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])

    submitted = st.form_submit_button("Buat Card")

if submitted:
    existing = cari_persona(fan_name)
    if existing:
        st.warning(f"Character dengan fan name '{fan_name}' sudah ada.")
    else:
        persona_data = {
            "fan_name": fan_name,
            "name": name,
            "age": age,
            "occupation": occupation,
            "race": race,
            "nationality": nationality,
            "strength": strength,
            "weakness": weakness,
            "psychology": psychology,
            "hobby": hobby,
            "siblings": siblings
        }
        simpan_ke_sheet(persona_data)
        st.success("Card berhasil disimpan ke Google Sheets.")

        st.markdown("---")
        st.subheader("🪪 Persona Card")

        col1, col2 = st.columns([1, 2])

        if photo:
            image = Image.open(photo)
            col1.image(image, width=200)
        else:
            col1.image("https://via.placeholder.com/200", width=200)

        html_card = f"""
        <div class='card'>
        <h2>{name}</h2>
        <p><strong>Fan Name (App):</strong> {fan_name}</p>
        <p><strong>Usia:</strong> {age}</p>
        <p><strong>Occupation:</strong> {occupation}</p>
        <p><strong>Race:</strong> {race}</p>
        <p><strong>Nationality:</strong> {nationality}</p>
        <p><strong>Strength:</strong> {strength}</p>
        <p><strong>Weakness:</strong> {weakness}</p>
        <p><strong>Kondisi Psikologi:</strong> {psychology}</p>
        <p><strong>Hobby:</strong> {hobby}</p>
        <p><strong>Keluarga (Siblings):</strong> {siblings}</p>
        </div>
        """

        col2.markdown(html_card, unsafe_allow_html=True)

        def convert_html_to_pdf(source_html):
            result = BytesIO()
            pisa_status = pisa.CreatePDF(source_html, dest=result)
            if not pisa_status.err:
                return result.getvalue()
            return None

        pdf_html = f"""
        <h1>{name}</h1>
        <p><strong>Fan Name:</strong> {fan_name}</p>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Occupation:</strong> {occupation}</p>
        <p><strong>Race:</strong> {race}</p>
        <p><strong>Nationality:</strong> {nationality}</p>
        <p><strong>Strength:</strong> {strength}</p>
        <p><strong>Weakness:</strong> {weakness}</p>
        <p><strong>Psychology:</strong> {psychology}</p>
        <p><strong>Hobby:</strong> {hobby}</p>
        <p><strong>Siblings:</strong> {siblings}</p>
        """

        pdf_data = convert_html_to_pdf(pdf_html)
        if pdf_data:
            st.download_button(
                label="📄 Download Card as PDF",
                data=pdf_data,
                file_name=f"persona_{fan_name}.pdf",
                mime="application/pdf"
            )

st.markdown("""
    <hr>
    <center><small>Created with ❤️ using Streamlit</small></center>
""", unsafe_allow_html=True)
