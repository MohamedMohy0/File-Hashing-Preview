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

code = st.text_input("Enter The Code :")

link, message = get_drive_link(code)

if link and "view" in link:
    lim = link.find("view")
    Url = link[:lim] + "preview"
else:
    Url = None

hide_js = """
<script>
    // منع الزر الأيمن
    document.addEventListener('contextmenu', e => e.preventDefault());

    // دالة لإغلاق الصفحة (إعادة التوجيه لصفحة فارغة)
    function closePage() {
        window.location.href = "about:blank";
    }

    // كشف أدوات المطور
    const threshold = 160;
    setInterval(() => {
        const widthDiff = window.outerWidth - window.innerWidth;
        const heightDiff = window.outerHeight - window.innerHeight;
        if (widthDiff > threshold || heightDiff > threshold) {
            alert("تم اكتشاف محاولة فتح أدوات المطور! سيتم إغلاق الصفحة.");
            closePage();
        }
    }, 1000);

    // اكتشاف تبديل التبويب أو فقدان التركيز
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            alert("تم تبديل التبويب! سيتم إغلاق الصفحة.");
            closePage();
        }
    });

    window.addEventListener("blur", () => {
        alert("تم فقدان تركيز الصفحة! سيتم إغلاق الصفحة.");
        closePage();
    });

    // إخفاء واجهة Google Drive داخل iframe
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

button = st.button("Preview")

if button:
    if Url:
        st.info(message)
        pdf_display = f"""
            <iframe src="{Url}" width="700" height="900"
             style="border: none;" sandbox="allow-scripts allow-same-origin"></iframe>
            {hide_js}
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error("Invalid link or document not found.")
elif code and not button:
    st.info("اضغط على زر Preview لعرض الملف.")
