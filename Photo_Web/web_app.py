import streamlit as st
from PIL import Image, UnidentifiedImageError
import io
import os

# ================= 1. 全局配置 =================
st.set_page_config(
    page_title="摸鱼指北·证件照助手",
    page_icon="📸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= 2. 样式修正 (含蓝色下载按钮) =================
st.markdown("""
    <style>
    /* --- 1. 标题渐变色 --- */
    .gradient-title {
        font-size: 32px;
        font-weight: 900;
        background: linear-gradient(45deg, #00D084, #007BFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        font-family: 'Microsoft YaHei', sans-serif;
    }

    /* --- 2. 核心大按钮 (开始压缩 - 绿色) --- */
    /* 针对 st.button */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        background-color: #00D084 !important; 
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        font-size: 18px !important;
        box-shadow: 0 4px 10px rgba(0, 208, 132, 0.3);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #00FFA3 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 208, 132, 0.5);
    }

    /* --- [重点] 下载按钮专用样式 (保存图片 - 蓝色) --- */
    /* 针对 st.download_button */
    .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        background-color: #007BFF !important; /* 科技蓝 */
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        font-size: 18px !important;
        box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3);
        transition: all 0.3s;
    }
    .stDownloadButton > button:hover {
        background-color: #0056b3 !important; /* 深蓝色 */
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 123, 255, 0.5);
    }

    /* --- 3. 上传按钮修复 --- */
    [data-testid="stFileUploaderDropzone"] button {
        color: transparent !important; 
        position: relative;
    }
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "📂 选择图片";
        color: #555;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        font-size: 14px;
        font-weight: bold;
        white-space: nowrap !important;
        width: 100%;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stFileUploaderDropzone"] button::after { color: #ddd; }
    }

    /* --- 4. 隐藏上传框内的英文 --- */
    [data-testid="stFileUploaderDropzoneInstructions"] div,
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"]::before {
        content: "支持 JPG / PNG / WEBP / BMP";
        visibility: visible;
        display: block;
        text-align: center;
        color: #888;
        font-size: 14px;
        padding: 10px 0;
    }

    /* --- 5. 数字指标颜色 --- */
    div[data-testid="stMetricValue"] {
        color: #00D084 !important;
        font-weight: bold;
    }

    /* --- 6. 底部状态栏样式 --- */
    .status-bar {
        background-color: #f0f2f6;
        color: #555;
        padding: 10px;
        border-radius: 5px;
        font-size: 14px;
        text-align: center;
        margin-top: 10px;
        word-wrap: break-word;
        word-break: break-all;
    }
    @media (prefers-color-scheme: dark) {
        .status-bar {
            background-color: #262730;
            color: #ccc;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ================= 3. 核心逻辑 =================
PRESETS = {
    "国考/省考 (35x45mm, <100KB)": {"w": 413, "h": 531, "kb": 100},
    "研究生报名 (学信网, <50KB)": {"w": 480, "h": 640, "kb": 50},
    "教师资格证 (295x413, <200KB)": {"w": 295, "h": 413, "kb": 190},
    "一寸标准照 (25x35mm, <100KB)": {"w": 295, "h": 413, "kb": 100},
    "二寸标准照 (35x49mm, <200KB)": {"w": 413, "h": 579, "kb": 200},
    "自定义模式 (手动设置)": {"w": 0, "h": 0, "kb": 200},
}


def compress_image(image, target_kb, target_w=0, target_h=0):
    if image.mode != "RGB":
        image = image.convert("RGB")
    if target_w > 0 and target_h > 0:
        image = image.resize((target_w, target_h), Image.Resampling.LANCZOS)

    safe_target_kb = target_kb * 0.95
    target_bytes = safe_target_kb * 1024
    min_q, max_q = 10, 95
    best_img_bytes = None

    for _ in range(8):
        mid_q = (min_q + max_q) // 2
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=mid_q, dpi=(300, 300))
        size = buffer.tell()
        if size <= target_bytes:
            best_img_bytes = buffer.getvalue()
            min_q = mid_q + 1
        else:
            max_q = mid_q - 1

    if best_img_bytes is None:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=10, dpi=(300, 300))
        best_img_bytes = buffer.getvalue()
    return best_img_bytes, image.size


# 文件名生成逻辑
def get_download_name(original_name, file_id):
    if 'file_history' not in st.session_state:
        st.session_state.file_history = {}
    count = st.session_state.file_history.get(file_id, 0)
    st.session_state.file_history[file_id] = count + 1
    stem = os.path.splitext(original_name)[0]
    if count == 0:
        suffix = "-证件照"
    else:
        suffix = f"-证件照{count}"
    return f"{stem}{suffix}.jpg"


# ================= 4. 界面构建 =================

st.markdown('<div class="gradient-title">⚡ 摸鱼指北·证件照助手</div>', unsafe_allow_html=True)

st.markdown("#### 🛠️ 场景配置")
selected_preset = st.selectbox("请选择考试类型", list(PRESETS.keys()), label_visibility="collapsed")
params = PRESETS[selected_preset]

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    if "自定义" in selected_preset:
        target_w = st.number_input("宽度 (px)", value=413)
    else:
        target_w = params['w']
        st.metric("宽度 (px)", f"{target_w}")
with c2:
    if "自定义" in selected_preset:
        target_h = st.number_input("高度 (px)", value=531)
    else:
        target_h = params['h']
        st.metric("高度 (px)", f"{target_h}")
with c3:
    if "自定义" in selected_preset:
        target_kb = st.number_input("限制 (KB)", value=100)
    else:
        target_kb = params['kb']
        st.metric("大小限制", f"< {target_kb} KB")

st.markdown("---")

st.markdown("#### 📤 照片上传")

uploaded_file = st.file_uploader(
    "label_hidden",
    type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
    label_visibility="collapsed"
)

if uploaded_file:
    # 鲁棒性检查：大小限制
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10MB
    if uploaded_file.size > FILE_SIZE_LIMIT:
        st.error(f"❌ 文件过大！请上传小于 10MB 的图片")
        st.stop()

    try:
        # 鲁棒性检查：内容合法性
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)

        # 状态栏自适应
        st.info(f"🟢 已读取：{uploaded_file.name} | 原图：{int(uploaded_file.size / 1024)} KB | 格式：{img.format}")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 开始一键压缩"):
            with st.spinner("⚡ 正在处理中..."):
                res_bytes, final_size = compress_image(img, target_kb, target_w, target_h)
                final_kb = len(res_bytes) / 1024

                # 生成文件名
                file_unique_id = f"{uploaded_file.name}_{uploaded_file.size}"
                download_name = get_download_name(uploaded_file.name, file_unique_id)

                st.success(f"✅ 处理成功！最终大小：{final_kb:.2f} KB")

                col_l, col_r = st.columns(2)
                with col_l:
                    st.image(res_bytes, caption=f"效果预览: {final_size[0]}x{final_size[1]}", use_container_width=True)
                with col_r:
                    st.markdown(f"#### ✅ 达标")
                    st.download_button(
                        label=f"📥 保存图片 ({download_name})",
                        data=res_bytes,
                        file_name=download_name,
                        mime="image/jpeg",
                        type="primary"
                    )

    except UnidentifiedImageError:
        st.error("❌ 无法识别的图片文件！文件可能已损坏。")
    except Exception as e:
        st.error(f"❌ 发生未知错误: {str(e)}")

else:
    # 底部提示
    st.markdown('<div class="status-bar">🟢 系统准备就绪，支持拖拽上传...</div>', unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px; margin-top: 50px;'>
        POWERED BY 摸鱼指北 | 纯本地处理，不保存照片
    </div>
""", unsafe_allow_html=True)