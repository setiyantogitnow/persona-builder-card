import streamlit as st
from PIL import Image
import os
import json
from io import BytesIO
from xhtml2pdf import pisa
from pathlib import Path

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

DB_FILE = "persona_db.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        persona_db = json.load(f)
else:
    persona_db = {}

# Search existing personas
st.sidebar.markdown("### 🔍 Cari Character")
search_query = st.sidebar.text_input("Masukkan nama")
if search_query:
    match = persona_db.get(search_query)
    if match:
        st.sidebar.success("Character ditemukan!")
        st.sidebar.json(match)
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

def convert_html_to_pdf(source_html):
    result = BytesIO()
    pisa_status = pisa.CreatePDF(source_html, dest=result)
    if not pisa_status.err:
        return result.getvalue()
    return None

if submitted:
    if not fan_name:
        st.warning("Nama Fan Dalam App wajib diisi.")
    elif fan_name in persona_db:
        st.warning(f"Character dengan nama fan '{fan_name}' sudah ada dalam database.")
    else:
        # Save image temporarily if exists
        img_path = None
        if photo:
            image = Image.open(photo)
            img_path = f"temp_{fan_name}.png"
            image.save(img_path)
        else:
            image = None

        persona_data = {
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
        persona_db[fan_name] = persona_data
        with open(DB_FILE, "w") as f:
            json.dump(persona_db, f, indent=2)

        st.success("Card berhasil dibuat dan disimpan.")
        st.markdown("---")
        st.subheader("🪪 Persona Card")

        col1, col2 = st.columns([1, 2])

        if image:
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

        # Prepare img tag for PDF
        img_tag = f'<img src="{img_path}" width="200"/>' if img_path else ""

        pdf_html = f"""
        <h1>{name}</h1>
        {img_tag}
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

        # Cleanup temporary image file
        if img_path and Path(img_path).exists():
            Path(img_path).unlink()

st.markdown("""
    <hr>
    <center><small>Created with ❤️ using Streamlit</small></center>
""", unsafe_allow_html=True)
