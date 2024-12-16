import streamlit as st
from PIL import Image
import io
import zipfile

from utils.image import Danpane

def main():
    st.title("ダンパネ分割")

    # 画像をアップロード
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    # パラメータを入力
    ncols = st.number_input("Number of Columns", value=5, min_value=1)
    nrows = st.number_input("Number of Rows", value=2, min_value=1)

    # 向きを入力
    direction = st.radio("Direction", ("vertical", "horizontal"), horizontal=True)

    if uploaded_image is not None:
        # アップロードされた画像を読み込む
        image = Image.open(uploaded_image)
        if direction == "horizontal":
            image = image.rotate(90, expand=True)
        danpane = Danpane(image, ncols, nrows)
        danpane.preprocess_image()
        outputs = danpane.divide_image()
        
        # 前処理後の複数画像を圧縮してダウンロード
        if st.button("Generate Zip File"):
            # zipファイルを作成
            zip_bytes = io.BytesIO()
            with zipfile.ZipFile(zip_bytes, "w") as zipf:
                for i, output in enumerate(outputs):
                    # 画像をバイト列に変換
                    img_byte_array = io.BytesIO()
                    output.save(img_byte_array, format="PNG")
                    img_bytes = img_byte_array.getvalue()
                    # zipファイルに画像を追加
                    zipf.writestr(f"processed_image_{str(i+1).zfill(2)}.png", img_bytes)
            
            # zipファイルをダウンロード
            zip_bytes.seek(0)
            st.download_button(label="Download Zip", data=zip_bytes, file_name="processed_images.zip", mime="application/zip")

        # 前処理後の画像を結合したPDFをダウンロード
        if st.button("Generate PDF"):
            img_byte_array = io.BytesIO()
            # PDFを作成
            outputs[0].save(img_byte_array, format="PDF", resolution=100.0, save_all=True, append_images=outputs[1:])
            img_bytes = img_byte_array.getvalue()
            st.download_button(label="Download PDF", data=img_bytes, file_name="processed_images.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()