
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="GEDCOM Generator", layout="centered")
st.title("👪 GEDCOM Family Tree Generator")

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b %Y").upper()
    except:
        return None

def create_individual(idx, label):
    st.subheader(f"{label} Information")
    name = st.text_input(f"{label} Full Name", key=f"name_{idx}")
    birth = st.date_input(f"{label} Birth Date", key=f"birth_{idx}")
    birth_place = st.text_input(f"{label} Birthplace", key=f"birthplace_{idx}")
    death = st.date_input(f"{label} Death Date (optional)", value=None, key=f"death_{idx}")
    return {
        "id": f"@I{idx}@",
        "name": name,
        "birth": birth,
        "birth_place": birth_place,
        "death": death if death else None
    }

def create_gedcom(data):
    gedcom = "0 HEAD\n1 SOUR StreamlitGED\n1 GEDC\n2 VERS 5.5\n1 CHAR UTF-8\n"
    for person in data:
        gedcom += f"0 {person['id']} INDI\n"
        gedcom += f"1 NAME {person['name']}\n"
        gedcom += f"1 BIRT\n2 DATE {format_date(str(person['birth']))}\n2 PLAC {person['birth_place']}\n"
        if person['death']:
            gedcom += f"1 DEAT\n2 DATE {format_date(str(person['death']))}\n"
    if len(data) > 1:
        gedcom += f"0 @F1@ FAM\n"
        if len(data) > 1: gedcom += f"1 HUSB {data[0]['id']}\n"
        if len(data) > 2: gedcom += f"1 WIFE {data[1]['id']}\n"
        for i in range(2, len(data)):
            gedcom += f"1 CHIL {data[i]['id']}\n"
        gedcom += "1 MARR\n2 DATE 01 JAN 2000\n"
    gedcom += "0 TRLR\n"
    return gedcom.replace("\n", "\n")

# Collect input for up to 5 individuals
members = []
labels = ["Husband", "Wife", "Child 1", "Child 2", "Child 3"]
for idx, label in enumerate(labels, start=1):
    with st.expander(f"{label} Info", expanded=(idx <= 2)):
        if st.checkbox(f"Include {label}", value=(idx <= 2), key=f"include_{idx}"):
            members.append(create_individual(idx, label))

# Generate GEDCOM file
if members and st.button("Generate GEDCOM File"):
    gedcom_text = create_gedcom(members)
    st.success("GEDCOM file generated!")
    st.download_button("Download GEDCOM File", gedcom_text, file_name="family_tree.ged", mime="text/plain")
