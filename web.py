import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# تهيئة Firebase إذا لم يكن مهيأ بعد
if not firebase_admin._apps:
    cred_dict = st.secrets["gcp_service_account"]
    cred = credentials.Certificate(dict(cred_dict))
    firebase_app = initialize_app(cred)

db = firestore.client()

def get_drive_link(code):
    if not code:
        return None, "No code entered"

    # جلب المستندات من Hashes و num
    doc_ref_hashes = db.collection("Hashes").document(code)
    doc_ref_num = db.collection("num").document(code)

    doc_hashes = doc_ref_hashes.get()
    doc_num = doc_ref_num.get()

    if not doc_num.exists:
        return None, "Code is not valid (not found in num collection)"

    number = doc_num.to_dict().get("number", 0)

    if number <= 0:
        return None, "The code is not valid now"

    # تحديث عدد المحاولات
    new_number = number - 1
    doc_ref_num.update({"number": new_number})

    if not doc_hashes.exists:
        return None, "Document not found in Hashes collection"

    link = doc_hashes.to_dict().get("drivelink", None)

    if not link:
        return None, "No drive link found"

    return link, f"Remaining tries: {new_number}"

# إعداد واجهة Streamlit
st.set_page_config(page_title="File Hashing")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>File Preview</h1>", unsafe_allow_html=True)

# إدخال الكود
code = st.text_input("Enter The Code:")
link, message = get_drive_link(code)

# عرض الرسالة للمستخدم


# تعديل الرابط ليكون بصيغة preview
Url = None
if link:
    if "preview" in link:
        Url = link
    elif "view" in link:
        lim = link.find("view")
        Url = link[:lim] + "preview"
    elif "/d/" in link:
        # تحويل رابط مباشر إلى preview
        file_id = link.split("/d/")[1].split("/")[0]
        Url = f"https://drive.google.com/file/d/{file_id}/preview"

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

# إعداد عرض الملف
pdf_display = f"""
    <iframe src="{Url}" width="700" height="900"
     style="border: none;" sandbox="allow-scripts allow-same-origin"></iframe>
    {hide_js}
"""

# زر المعاينة
if st.button("Preview"):
    with st.spinner("In Progress..."):
        if Url:
            st.info(message)
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Invalid link or no preview available.")
