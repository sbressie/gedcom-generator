
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="GEDCOM Generator", layout="centered")
st.title("👪 GEDCOM Family Tree Generator")
submitter = st.text_input("Submitter Email (Gmail)", key="submitter_email")

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b %Y").upper()
    except:
        return None

def create_individual(idx, label):
    st.subheader(f"{label} Information")
    name = st.text_input(f"{label} Full Name", key=f"name_{idx}")
    gender = st.selectbox(f"{label} Gender", ["M", "F"], key=f"gender_{idx}")
    birth = st.date_input(f"{label} Birth Date", key=f"birth_{idx}", min_value=datetime(1500, 1, 1))
    birth_place = st.text_input(f"{label} Birthplace", key=f"birthplace_{idx}")
    death = st.date_input(f"{label} Death Date (optional)", value=None, key=f"death_{idx}", min_value=datetime(1500, 1, 1))
    return {
        "id": f"@I{idx}@",
        "name": name,
        "gender": gender,
        "birth": birth,
        "birth_place": birth_place,
        "death": death if death else None
    }

def create_gedcom(data, marriage_date, divorce_date):
    gedcom = "0 HEAD\n"
    gedcom += "1 SOUR StreamlitGED\n2 VERS 1.0\n"
    gedcom += "1 GEDC\n2 VERS 5.5\n2 FORM LINEAGE-LINKED\n"
    gedcom += "1 CHAR ANSEL\n1 SUBM @SUB1@\n"

    for person in data:
        # Append FAMS or FAMC based on role
        person_fam_tags = ""
        if person["id"] == "@I1@" or person["id"] == "@I2@":
            person_fam_tags += "1 FAMS @F1@\n"
        elif person["id"] in [d["id"] for d in data[2:]]:
            person_fam_tags += "1 FAMC @F1@\n"

        first, *last = person['name'].split()
        surname = last[-1] if last else "Unknown"
        given = first + " " + " ".join(last[:-1]) if last else first
        gedcom += f"0 {person['id']} INDI\n"
        gedcom += f"1 NAME {given} /{surname}/\n"
        gedcom += f"1 SEX {person['gender']}\n"
        gedcom += "1 BIRT\n"
        gedcom += f"2 DATE {format_date(str(person['birth']))}\n"
        gedcom += f"2 PLAC {person['birth_place']}\n"
        if person['death']:
            gedcom += "1 DEAT\n"
            gedcom += f"2 DATE {format_date(str(person['death']))}\n"
        gedcom += person_fam_tags + "\n"

    if len(data) >= 2:
        gedcom += "0 @F1@ FAM\n"
        gedcom += f"1 HUSB {data[0]['id']}\n"
        gedcom += f"1 WIFE {data[1]['id']}\n"
        for i in range(2, len(data)):
            gedcom += f"1 CHIL {data[i]['id']}\n"
        if marriage_date:
            gedcom += "1 MARR\n"
            gedcom += f"2 DATE {format_date(str(marriage_date))}\n"
        if divorce_date:
            gedcom += "1 DIV\n"
            gedcom += f"2 DATE {format_date(str(divorce_date))}\n"

    gedcom += f"0 @SUB1@ SUBM\n1 NAME {submitter if submitter else 'Unknown User'}\n0 TRLR\n"
    return gedcom.replace("\n", "\n")

# Collect family member inputs
members = []
labels = [
    "Husband", "Wife", "Child 1", "Child 2", "Child 3",
    "Sibling 1", "Sibling 2", "Grandparent 1", "Grandparent 2"
]
for idx, label in enumerate(labels, start=1):
    with st.expander(f"{label} Info", expanded=(idx <= 2)):
        if st.checkbox(f"Include {label}", value=(idx <= 2), key=f"include_{idx}"):
            members.append(create_individual(idx, label))

st.markdown("---")
marriage_date = st.date_input("Marriage Date (optional)", value=None, key="marriage_date", min_value=datetime(1500, 1, 1))
divorce_date = st.date_input("Divorce Date (optional)", value=None, key="divorce_date", min_value=datetime(1500, 1, 1))

# Generate GEDCOM file
if members and st.button("Generate GEDCOM File"):
    gedcom_text = create_gedcom(members, marriage_date, divorce_date)
    st.success("GEDCOM file generated!")
    st.download_button("Download GEDCOM File", gedcom_text, file_name="family_tree.ged", mime="text/plain")
