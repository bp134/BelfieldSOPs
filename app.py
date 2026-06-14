import streamlit as st
import json
import os

# Set up page configurations
st.set_page_config(page_title="Belfield Pharmacy SOP Editor", layout="wide")
st.title("🏥 Belfield Pharmacy — SOP Master Editor")

JSON_FILE = "belfield_sops.json"

# Define the correct master file path at the top
JSON_FILE = "fixed_sop_data.json"

# Helper function to load JSON data
def load_data():
    if not os.path.exists(JSON_FILE):
        # Fallback template if file doesn't exist yet
        return {"pharmacy_profile": {"name": "Belfield Pharmacy", "location": "Rochdale"}, "sops": []}
    with open(JSON_FILE, "r", encoding="utf-8") as f: # Changed to match JSON_FILE variable
        return json.load(f)

# Helper function to save JSON data
def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    st.success("💾 Master JSON successfully updated!")

# Load master data into session state
if "sop_data" not in st.session_state:
    st.session_state.sop_data = load_data()

data = st.session_state.sop_data

# Sidebar for global configurations and navigation
st.sidebar.header("Global Settings")
data["pharmacy_profile"]["name"] = st.sidebar.text_input("Pharmacy Name", data["pharmacy_profile"]["name"])
data["pharmacy_profile"]["location"] = st.sidebar.text_input("Location", data["pharmacy_profile"]["location"])

st.sidebar.markdown("---")
st.sidebar.header("Navigation")

# Dropdown list to pick which SOP to edit
sop_titles = [f"{sop.get('id', 'N/A')} - {sop.get('title', 'Untitled')}" for sop in data.get("sops", [])]
if sop_titles:
    selected_sop_label = st.sidebar.selectbox("Select an SOP to Edit", sop_titles)
    selected_index = sop_titles.index(selected_sop_label)
    current_sop = data["sops"][selected_index]
else:
    st.warning("No SOPs found in the dataset.")
    current_sop = None

import streamlit as st
import json
import os
from jinja2 import Template
from weasyprint import HTML

st.set_page_config(page_title="Belfield Pharmacy SOP Studio", layout="wide")
st.title("🏥 Belfield Pharmacy — Master SOP Studio")

# List of files to read and compile
DATA_FILES = ["profile_and_rp.json", "dispensing_sops.json", "advanced_and_appendices.json"]

def load_all_data():
    master_data = {"pharmacy_profile": {"name": "Belfield Pharmacy", "location": "Rochdale"}, "sops": []}
    for file_name in DATA_FILES:
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                content = json.load(f)
                if "pharmacy_profile" in content:
                    master_data["pharmacy_profile"] = content["pharmacy_profile"]
                if "sops" in content:
                    master_data["sops"].extend(content["sops"])
    return master_data

def save_all_data(master_data):
    # Split back out into original structural files to avoid memory blocks
    f1 = {"pharmacy_profile": master_data["pharmacy_profile"], "sops": master_data["sops"][:5]}
    f2 = {"sops": master_data["sops"][5:14]}
    f3 = {"sops": master_data["sops"][14:]}
    
    payloads = [f1, f2, f3]
    for file_name, data in zip(DATA_FILES, payloads):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def compile_pdf(data):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {
            size: A4; margin: 25mm 20mm;
            @top-right { content: "Belfield Pharmacy Master SOP Manual"; font-family: sans-serif; font-size: 8pt; color: #666; }
            @bottom-right { content: "Page " counter(page); font-family: sans-serif; font-size: 9pt; }
        }
        body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
        .cover { page-break-after: always; text-align: center; padding-top: 100px; }
        .cover h1 { font-size: 32pt; color: #005A9C; }
        .sop-block { page-break-after: always; }
        h1.sop-title { color: #005A9C; border-bottom: 2px solid #005A9C; font-size: 18pt; margin-top: 30px; }
        .meta-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 10pt; }
        .meta-table td { border: 1px solid #ddd; padding: 6px; background: #f9f9f9; }
        .step-list { padding-left: 20px; }
        .step-list li { margin-bottom: 6px; }
    </style>
    </head>
    <body>
        <div class="cover">
            <h1>{{ data.pharmacy_profile.name }}</h1>
            <h2>Standard Operating Procedures Manual</h2>
            <p><strong>Location:</strong> {{ data.pharmacy_profile.location }}</p>
        </div>
        {% for sop in data.sops %}
        <div class="sop-block">
            <h1 class="sop-title">{{ sop.id }} — {{ sop.title }}</h1>
            <table class="meta-table">
                <tr>
                    <td><strong>Version:</strong> {{ sop.metadata.version }}</td>
                    <td><strong>Effective:</strong> {{ sop.metadata.effective_from }}</td>
                    <td><strong>Review Date:</strong> {{ sop.metadata.review_date }}</td>
                </tr>
            </table>
            {% for section in sop.sections %}
                <h3>{{ section.heading }}</h3>
                {% if section.content %}<p>{{ section.content }}</p>{% endif %}
                {% if section.steps %}
                    <ol class="step-list">
                    {% for step in section.steps %}<li>{{ step }}</li>{% endfor %}
                    </ol>
                {% endif %}
            {% endfor %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return HTML(string=Template(html_template).render(data=data)).write_pdf()

if "sop_data" not in st.session_state:
    st.session_state.sop_data = load_all_data()

data = st.session_state.sop_data

# Sidebar Elements
st.sidebar.header("⚙️ Global Settings")
data["pharmacy_profile"]["name"] = st.sidebar.text_input("Pharmacy Name", data["pharmacy_profile"]["name"], key="sidebar_pharmacy_name")
data["pharmacy_profile"]["location"] = st.sidebar.text_input("Pharmacy Location", data["pharmacy_profile"]["location"], key="sidebar_pharmacy_location")

st.sidebar.markdown("---")
st.sidebar.header("📁 Navigation")
sop_titles = [f"{sop.get('id', 'N/A')} - {sop.get('title', 'Untitled')}" for sop in data.get("sops", [])]

if sop_titles:
    selected_sop_label = st.sidebar.selectbox("Select an SOP to Edit", sop_titles, key="sidebar_sop_selectbox")
    selected_index = sop_titles.index(selected_sop_label)
    current_sop = data["sops"][selected_index]
else:
    current_sop = None

st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Changes", use_container_width=True):
    save_all_data(data)
    st.sidebar.success("Saved successfully!")

try:
    pdf_bytes = compile_pdf(data)
    st.sidebar.download_button("📥 Download PDF Manual", data=pdf_bytes, file_name="Belfield_SOP_Manual.pdf", mime="application/pdf", type="primary", use_container_width=True)
except Exception as e:
    st.sidebar.error(f"Compiler Notice: {e}")

# Editing Panel
if current_sop:
    st.header(f"✏️ Editing Pane: {current_sop.get('id')}")
    col1, col2 = st.columns(2)
    with col1: current_sop["id"] = st.text_input("SOP ID", current_sop.get("id"))
    with col2: current_sop["title"] = st.text_input("SOP Title", current_sop.get("title"))
    
    st.markdown("---")
    if "sections" in current_sop:
        for s_idx, section in enumerate(current_sop["sections"]):
            with st.expander(f"Section: {section.get('heading', 'Untitled')}", expanded=True):
                section["heading"] = st.text_input("Heading Title", section.get("heading", ""), key=f"h_{s_idx}_{current_sop.get('id')}")
                if "content" in section:
                    section["content"] = st.text_area("Content", section.get("content", ""), key=f"c_{s_idx}_{current_sop.get('id')}")
                if "steps" in section:
                    for step_idx, step in enumerate(section["steps"]):
                        section["steps"][step_idx] = st.text_input(f"Step {step_idx+1}", step, key=f"st_{s_idx}_{step_idx}_{current_sop.get('id')}")
