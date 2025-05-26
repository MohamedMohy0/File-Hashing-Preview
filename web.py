import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import streamlit.components.v1 as components
components.html("""
    <script>
        // Disable right-click
        document.addEventListener('contextmenu', event => event.preventDefault());

        // Disable F12, Ctrl+Shift+I/J/C/U
        document.onkeydown = function(e) {
            if (
                e.keyCode == 123 || // F12
                (e.ctrlKey && e.shiftKey && ['I','J','C'].includes(e.key.toUpperCase())) ||
                (e.ctrlKey && e.key.toLowerCase() === 'u')
            ) {
                return false;
            }
        };

        // Disable all <a> tag default behavior (prevent opening in new tab)
        document.addEventListener("DOMContentLoaded", function() {
            const links = document.querySelectorAll("a");
            links.forEach(link => {
                link.addEventListener("click", function(e) {
                    e.preventDefault();
                });
            });
        });
    </script>
""", height=0)

# تحقق من أن Firebase تم تهيئته مسبقًا
if not firebase_admin._apps:
    cred_dict = st.secrets["gcp_service_account"]
    cred = credentials.Certificate(dict(cred_dict))  # تحويل من TOML إلى dict
    firebase_app = initialize_app(cred)

db = firestore.client()

# دالة جلب الرابط وعدد المحاولات وتحديث الرقم
def get_drive_link(code):
    if not code:
        return None, "No code entered"

    # جلب مستند من مجموعة Hashes
    doc_ref_hashes = db.collection("Hashes").document(code)
    doc_hashes = doc_ref_hashes.get()
    
    if not doc_hashes.exists:
        return None, "Document not found in Hashes"

    data_num = doc_hashes.to_dict()
    number = data_num.get("remain", 0)

    if number <= 0:
        return None, "The code is not valid now"

    # إذا كان الرقم أكبر من صفر، ننقصه ونحدث المستند
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

st.markdown(
    """
    <h1 style="text-align: center;">File preview</h1>
    """,
    unsafe_allow_html=True
)

# إدخال الكود من المستخدم
code = st.text_input("Enter The Code :")
link, message = get_drive_link(code)

# عرض رسالة عدد المحاولات أو الخطأ

# معالجة الرابط وتحويله إلى preview
if link and "view" in link:
    lim = link.find("view")
    Url = link[:lim] + "preview"
else:
    Url = None

# JavaScript لإخفاء واجهة Google Drive
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
                        elements.forEach(el => el.style.display = 'none');
                    }
                }
            }
        }
        setInterval(hideDriveUI, 1000);
    </script>
"""

# عرض الـ PDF داخل Iframe
pdf_display = f"""
    <iframe src="{Url}" width="700" height="900"
     style="border: none;" sandbox="allow-scripts allow-same-origin"></iframe>
    {hide_js}
"""

# زر عرض الملف
button = st.button("Preview")
if button:
    with st.spinner("In Progress..."):
        if Url:
            st.info(message)
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Invalid link or document not found.")
