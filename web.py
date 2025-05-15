import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore,initialize_app

# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred_dict = st.secrets["gcp_service_account"]
    cred = credentials.Certificate(dict(cred_dict))  # Convert TOML to dict
    firebase_app = initialize_app(cred)

db = firestore.client()
def get_drive_link(code):
    if not code:
        return None, "No code entered"

    # جلب مستند من مجموعة Hashes
    doc_ref_hashes = db.collection("Hashes").document(code)
    doc_hashes = doc_ref_hashes.get()

    # جلب مستند من مجموعة num
    doc_ref_num = db.collection("num").document(code)
    doc_num = doc_ref_num.get()

    if not doc_num.exists:
        return None, "Code is not valid (no num document found)."

    data_num = doc_num.to_dict()
    number = data_num.get("number", 0)

    if number <= 0:
        return None, "The code is not valid now"

    # إذا كان الرقم أكبر من صفر، ننقصه ونحدث المستند
    new_number = number - 1
    doc_ref_num.update({"number": new_number})

    if not doc_hashes.exists:
        return None, "Document not found in Hashes"

    data = doc_hashes.to_dict()
    link = data.get("drivelink", "No drive link found")

    return link, f"Remaining tries: {new_number}"


st.set_page_config(page_title="File Hashing")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown(
    """
    <h1 style="text-align: center; ">File preview</h1>
    """, 
    unsafe_allow_html=True
)



code=st.text_input("Enter The Code :")
link, message = get_drive_link(code)

# عرض رسالة عدد المحاولات أو الخطأ


if "view" in link:
    lim = link.find("view")
    Url = link[:lim] + "preview"
else:
    Url = None

hide_js = """
    <script>
        function hideDriveUI() {
            let iframe = document.querySelector("iframe");
            if (iframe) {
                let iframeWindow = iframe.contentWindow;
                if (iframeWindow) {
                    let iframeDoc = iframeWindow.document;
                    if (iframeDoc) {
                        let elements = iframeDoc.querySelectorAll('a, button, .ndfHFb-c4YZDc');
                        elements.forEach(el => el.style.display = 'none');  // Hide all links, buttons, UI elements
                    }
                }
            }
        }
        
        setInterval(hideDriveUI, 1000);
    </script>
"""

pdf_display = f"""
    <iframe src="{Url}" width="700" height="900" 
    style="border: none;" sandbox="allow-scripts allow-same-origin"></iframe>
    {hide_js}
"""

button = st.button("Preview")
if button:
    with st.spinner("In Progress..."):
        if Url:
            if message:
                st.info(message)
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Invalid link or document not found.")
