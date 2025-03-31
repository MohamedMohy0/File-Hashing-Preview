import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")  # Ensure the correct path
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_drive_link(code):
    if not code:
        return "No code entered"

    doc_ref = db.collection("Hashes").document(code)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        return data.get("drivelink", "No drive link found")
    else:
        return "Document not found"

st.set_page_config(page_title="File Hashing")
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown(
    """
    <h1 style="text-align: center; ">File preview</h1>
    """, 
    unsafe_allow_html=True
)



code=st.text_input("Enter The Code :")
link = get_drive_link(code)

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
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Invalid link or document not found.")