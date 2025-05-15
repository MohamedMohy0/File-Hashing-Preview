import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

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

    try:
        doc_ref_hashes = db.collection("Hashes").document(code)
        doc_ref_num = db.collection("num").document(code)

        doc_hashes = doc_ref_hashes.get()
        doc_num = doc_ref_num.get()

        if not doc_num.exists:
            return None, "Code not found in num collection"

        data_num = doc_num.to_dict()
        number = data_num.get("number", 0)
        st.write("Current number:", number)

        if number <= 0:
            return None, "The code is not valid now"

        # Update attempts
        new_number = number - 1
        doc_ref_num.update({"number": new_number})

        if not doc_hashes.exists:
            return None, "Code not found in Hashes collection"

        data = doc_hashes.to_dict()
        link = data.get("drivelink", None)
        st.write("Drive link from DB:", link)

        if not link:
            return None, "No drive link found"

        return link, f"Remaining tries: {new_number}"

    except Exception as e:
        return None, f"Error: {str(e)}"

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
