import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from streamlit.components.v1 import html
import time

# تهيئة Firebase
if not firebase_admin._apps:
    cred_dict = st.secrets["gcp_service_account"]
    cred = credentials.Certificate(dict(cred_dict))
    firebase_app = initialize_app(cred)

db = firestore.client()

def get_drive_link(code):
    if not code:
        return None, "No code entered"

    doc_ref = db.collection("Hashes").document(code)
    doc = doc_ref.get()
    
    if not doc.exists:
        return None, "كود غير صحيح"

    data = doc.to_dict()
    remaining = data.get("remain", 0)

    if remaining <= 0:
        return None, "انتهت عدد المحاولات المتاحة"

    # تحديث عدد المحاولات
    doc_ref.update({"remain": remaining - 1})
    return data.get("drivelink"), f"المحاولات المتبقية: {remaining - 1}"

# إعدادات الصفحة
st.set_page_config(page_title="عرض الملف", layout="centered")
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# كود الحماية الأساسي
protection_js = """
<script>
// منع فتح أدوات المطور
function blockDevTools() {
    function killDevTools() {
        document.body.innerHTML = '<h1 style="color:red;text-align:center;">غير مسموح فتح أدوات المطور</h1>';
        window.location.href = "about:blank";
        return false;
    }
    
    // منع فتح الأدوات عبر الأزرار
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12' || 
            (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) || 
            (e.ctrlKey && e.key === 'U')) {
            e.preventDefault();
            killDevTools();
        }
    });
    
    // منع النقر الأيمن
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        killDevTools();
    });
    
    // مراقبة تغيير حجم النافذة
    let width = window.innerWidth;
    let height = window.innerHeight;
    
    setInterval(function() {
        if (window.innerWidth !== width || window.innerHeight !== height) {
            killDevTools();
        }
    }, 200);
    
    // منع مغادرة الصفحة
    window.onbeforeunload = function() {
        return "هل أنت متأكد من المغادرة؟";
    };
}

// تشغيل الحماية بعد تحميل الصفحة
window.onload = blockDevTools;
</script>
"""

# حقن كود الحماية
html(protection_js, height=0, width=0)

# واجهة المستخدم
st.markdown("<h1 style='text-align:center;'>عرض الملف</h1>", unsafe_allow_html=True)

code = st.text_input("أدخل الكود:")
if st.button("عرض الملف"):
    if not code:
        st.error("الرجاء إدخال الكود")
    else:
        with st.spinner("جاري التحضير..."):
            link, message = get_drive_link(code)
            
            if link:
                st.success(message)
                
                # تحويل رابط Google Drive إلى عرض مباشر
                if "view" in link:
                    preview_url = link.split("view")[0] + "preview"
                else:
                    preview_url = link
                
                # عرض الملف في iframe محمي
                iframe_html = f"""
                <div style="position:relative;overflow:hidden;padding-top:90%;">
                    <iframe src="{preview_url}" 
                            style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
                            sandbox="allow-same-origin allow-scripts allow-popups allow-forms">
                    </iframe>
                </div>
                """
                st.markdown(iframe_html, unsafe_allow_html=True)
            else:
                st.error(message)
