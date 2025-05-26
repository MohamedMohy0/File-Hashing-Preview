import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# تحقق من أن Firebase تم تهيئته مسبقًا
if not firebase_admin._apps:
    cred_dict = st.secrets["gcp_service_account"]
    cred = credentials.Certificate(dict(cred_dict))
    firebase_app = initialize_app(cred)

db = firestore.client()

def get_drive_link(code):
    if not code:
        return None, "No code entered"

    doc_ref_hashes = db.collection("Hashes").document(code)
    doc_hashes = doc_ref_hashes.get()
    
    if not doc_hashes.exists:
        return None, "Document not found in Hashes"

    data_num = doc_hashes.to_dict()
    number = data_num.get("remain", 0)

    if number <= 0:
        return None, "The code is not valid now"

    new_number = number - 1
    doc_ref_hashes.update({"remain": new_number})

    data = doc_hashes.to_dict()
    link = data.get("drivelink", "No drive link found")

    return link, f"Remaining tries: {new_number}"

# إعدادات الصفحة
st.set_page_config(page_title="File Hashing")
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# كود الحماية الأساسي
protection_js = """
<script>
// منع فتح أدوات المطور
document.addEventListener('keydown', function(e) {
    if (e.key === 'F12' || 
        (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) || 
        (e.ctrlKey && e.key === 'U') || 
        (e.metaKey && e.altKey && e.key === 'I')) {
        e.preventDefault();
        window.close();
        document.body.innerHTML = 'غير مسموح بالوصول إلى أدوات المطور';
    }
});

// منع النقر الأيمن
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    window.close();
    document.body.innerHTML = 'غير مسموح باستخدام النقر الأيمن';
});

// مراقبة تغيير الصفحة
let currentUrl = window.location.href;
setInterval(function() {
    if (window.location.href !== currentUrl) {
        window.close();
        document.body.innerHTML = 'غير مسموح بتغيير الصفحة';
    }
}, 200);
</script>
"""

st.markdown(protection_js, unsafe_allow_html=True)

st.markdown(
    """
    <h1 style="text-align: center;">File preview</h1>
    """,
    unsafe_allow_html=True
)

code = st.text_input("Enter The Code :")
link, message = get_drive_link(code)

if link and "view" in link:
    lim = link.find("view")
    Url = link[:lim] + "preview"
else:
    Url = None

hide_js = """
<script>
function hideDriveUI() {
    const iframe = document.querySelector("iframe");
    if (iframe) {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            const elements = iframeDoc.querySelectorAll('a, button, .ndfHFb-c4YZDc');
            elements.forEach(el => el.style.display = 'none');
        } catch (e) {
            console.log("Cannot access iframe due to CORS");
        }
    }
}
setInterval(hideDriveUI, 1000);
</script>
"""

pdf_display = f"""
<div id="pdf-container">
    <iframe src="{Url}" width="700" height="900" style="border: none;" sandbox="allow-scripts allow-same-origin"></iframe>
</div>
{hide_js}
"""

button = st.button("Preview")
if button:
    with st.spinner("In Progress..."):
        if Url:
            st.info(message)
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Invalid link or document not found.")
