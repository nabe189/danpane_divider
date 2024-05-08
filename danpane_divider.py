import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import io
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# A4サイズの比率
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
A4_ASPECT_RATIO = A4_WIDTH_MM / A4_HEIGHT_MM

# 元画像のサイズ調整
def adjust_image_size(image: Image, canvas_height:int, canvas_width:int) -> Image:
    '''
    image:元画像のImage
    canvas_height:キャンバスの高さ
    canvas_width:キャンバスの幅
    '''
    # 比率の計算
    image_aspect_ratio = image.width / image.height
    canvas_aspect_ratio = canvas_width / canvas_height
    
    if  image_aspect_ratio >= canvas_aspect_ratio: # 元画像がキャンバスよりも横長の場合
        # キャンバスの横にはみ出さないように元画像を拡大
        new_width = canvas_width
        new_height = int(image.height * (canvas_width / image.width))

    else: # 元画像がキャンバスよりも縦長の場合
        # キャンバスの縦にはみ出さないように元画像を拡大
        new_width = int(image.width * (canvas_height / image.height))
        new_height = canvas_height
    
    return image.resize((new_width, new_height), Image.BICUBIC) # リサイズ

# 画像をキャンバスの真ん中に貼り付ける
def paste_center(image, canvas):
    '''
    image:貼り付けるImage
    canvas:貼り付け先のImage
    '''
    # 貼り付ける位置を計算
    left = (canvas.width - image.width) // 2
    top = (canvas.height - image.height) // 2
    right = left + image.width
    bottom = top + image.height
    
    # 元の画像の中央に貼り付ける
    canvas.paste(image, (left, top, right, bottom))

    return canvas

# 画像の前処理
def preprocess_image(image:Image, ncols:int, nrows:int) -> Image:
    '''
    image:元画像のImage
    ncols:横何枚分か
    nrows:縦何枚分か
    '''
    canvas_width = 217 * ncols
    canvas_height = 297 * nrows
    canvas = Image.new(image.mode, (canvas_width, canvas_height), "white") # 出力画像の比率のキャンバスを生成
    canvas = paste_center(adjust_image_size(image, canvas_height, canvas_width), canvas) # サイズ調整した元画像をキャンバスに貼り付け
    
    return canvas

# 画像の分割
def divide_image(image:Image, ncols:int, nrows:int, preview=False) -> list:
    '''
    image:分割するImage
    ncols:横何枚分か
    nrows:縦何枚分か
    preview:プレビューの有無
    '''
        
    outputs = []

    # 1ページあたりの画像サイズ (ピクセル)
    output_width = image.width // ncols
    output_height = image.height // nrows

    # プレビューの作成
    if preview:
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 14/(ncols/nrows)/A4_ASPECT_RATIO))

    # 画像をA4用紙の枚数で分割する
    for i in range(nrows):
        for j in range(ncols):
            # 分割した画像の領域を計算
            left = j * output_width
            top = i * output_height
            right = left + output_width
            bottom = top + output_height
            
            # 画像を切り取る
            cropped_image = image.crop((left, top, right, bottom))
            outputs.append(cropped_image)

            if preview:
                # 画像を表示
                ax = axes[i][j] if nrows > 1 else axes[j]
                ax.imshow(cropped_image)
                ax.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, 
                                bottom=False, left=False, right=False, top=False) #目盛りを消す
    
    if preview:
        plt.subplots_adjust(wspace=0.01, hspace=0.01) #間隔の調整
        st.pyplot(fig) # プレビューの表示

    return outputs

def main():
    st.title("ダンパネ分割")

    # 画像をアップロード
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    # パラメータを入力
    ncols = st.number_input("Number of Columns", value=5, min_value=1)
    nrows = st.number_input("Number of Rows", value=2, min_value=1)


    if uploaded_image is not None:
        # アップロードされた画像を読み込む
        image = Image.open(uploaded_image)
        processed_image = preprocess_image(image, ncols, nrows)
        outputs = divide_image(processed_image, ncols, nrows, preview=True)
        
        # 前処理後の画像をダウンロード
        # if st.button("Download Processed Images"):
        #     # zipファイルを作成
        #     zip_bytes = io.BytesIO()
        #     with zipfile.ZipFile(zip_bytes, "w") as zipf:
        #         for i, output in enumerate(outputs):
        #             # 画像をバイト列に変換
        #             img_byte_array = io.BytesIO()
        #             output.save(img_byte_array, format="PNG")
        #             img_bytes = img_byte_array.getvalue()
        #             # zipファイルに画像を追加
        #             zipf.writestr(f"processed_image_{str(i+1).zfill(2)}.png", img_bytes)
            
        #     # zipファイルをダウンロード
        #     zip_bytes.seek(0)
        #     st.download_button(label="Download Zip", data=zip_bytes, file_name="processed_images.zip", mime="application/zip")

        # 前処理後の画像を結合したPDFをダウンロード
        if st.button("Generate PDF"):
            img_byte_array = io.BytesIO()
            # PDFを作成
            outputs[0].save(img_byte_array, format="PDF" ,resolution=100.0, save_all=True, append_images=outputs[1:])
            img_bytes = img_byte_array.getvalue()
            st.download_button(label="Download PDF", data=img_bytes, file_name="processed_images.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()