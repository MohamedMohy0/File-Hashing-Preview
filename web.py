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
    // ========== منع الزر الأيمن ==========
    document.addEventListener('contextmenu', event => event.preventDefault());

    // ========== اكتشاف فتح DevTools ==========
    let devtoolsOpen = false;
    const threshold = 160;
    setInterval(() => {
        const widthThreshold = window.outerWidth - window.innerWidth > threshold;
        const heightThreshold = window.outerHeight - window.innerHeight > threshold;
        if (widthThreshold || heightThreshold) {
            if (!devtoolsOpen) {
                devtoolsOpen = true;
                document.body.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%;'>🚫 تم كشف أدوات المطور وتم إيقاف الصفحة</h1>";
            }
        }
    }, 1000);

    // ========== اكتشاف فقدان التركيز (فتح تبويب آخر) ==========
    document.addEventListener("visibilitychange", function() {
        if (document.hidden) {
            document.body.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%;'>🚫 لا يُسمح بفتح التبويبات أو التبديل بينها</h1>";
        }
    });
</script>
"""


# عرض داخل IFrame
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
