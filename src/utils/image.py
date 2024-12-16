from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import streamlit as st

# A4サイズの比率
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
A4_ASPECT_RATIO = A4_WIDTH_MM / A4_HEIGHT_MM

class Danpane:
    def __init__(self, image:Image, ncols:int, nrows:int):
        self.image = image
        self.ncols = ncols
        self.nrows = nrows

    # 元画像のサイズ調整
    def adjust_image_size(self, canvas_height:int, canvas_width:int) -> None:
        '''
        image:元画像のImage
        canvas_height:キャンバスの高さ
        canvas_width:キャンバスの幅
        '''
        # 比率の計算
        image_aspect_ratio = self.image.width / self.image.height
        canvas_aspect_ratio = canvas_width / canvas_height
        
        if  image_aspect_ratio >= canvas_aspect_ratio: # 元画像がキャンバスよりも横長の場合
            # キャンバスの横にはみ出さないように元画像を拡大
            new_width = canvas_width
            new_height = int(self.image.height * (canvas_width / self.image.width))

        else: # 元画像がキャンバスよりも縦長の場合
            # キャンバスの縦にはみ出さないように元画像を拡大
            new_width = int(self.image.width * (canvas_height / self.image.height))
            new_height = canvas_height
        
        self.image = self.image.resize((new_width, new_height), Image.BICUBIC) # リサイズ

    # 画像をキャンバスの真ん中に貼り付ける
    def paste_center(self, canvas:Image):
        '''
        image:貼り付けるImage
        canvas:貼り付け先のImage
        '''
        # 貼り付ける位置を計算
        left = (canvas.width - self.image.width) // 2
        top = (canvas.height - self.image.height) // 2
        right = left + self.image.width
        bottom = top + self.image.height
        
        # 元の画像の中央に貼り付ける
        canvas.paste(self.image, (left, top, right, bottom))

        return canvas

    # 画像の前処理
    def preprocess_image(self) -> None:
        '''
        image:元画像のImage
        ncols:横何枚分か
        nrows:縦何枚分か
        '''
        canvas_width = 217 * self.ncols
        canvas_height = 297 * self.nrows
        canvas = Image.new(self.image.mode, (canvas_width, canvas_height), "white") # 出力画像の比率のキャンバスを生成
        self.adjust_image_size(canvas_height, canvas_width) # サイズ調整
        self.image = self.paste_center(canvas) # サイズ調整した元画像をキャンバスに貼り付け

    # 画像の分割
    def divide_image(self) -> list:
        '''
        image:分割するImage
        ncols:横何枚分か
        nrows:縦何枚分か
        preview:プレビューの有無
        '''
            
        outputs = []

        # 1ページあたりの画像サイズ (ピクセル)
        output_width = self.image.width // self.ncols
        output_height = self.image.height // self.nrows

        # プレビューの作成
        fig, axes = plt.subplots(self.nrows, self.ncols, figsize=(14, 14/(self.ncols/self.nrows)/A4_ASPECT_RATIO))

        # 画像をA4用紙の枚数で分割する
        for i in range(self.nrows):
            for j in range(self.ncols):
                # 分割した画像の領域を計算
                left = j * output_width
                top = i * output_height
                right = left + output_width
                bottom = top + output_height
                
                # 画像を切り取る
                cropped_image = self.image.crop((left, top, right, bottom))
                outputs.append(cropped_image)

                # 画像を表示
                ax = axes[j] if self.nrows == 1 else axes[i] if self.ncols == 1 else axes[i][j]
                ax.imshow(cropped_image)
                ax.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, 
                                bottom=False, left=False, right=False, top=False) #目盛りを消す
        
        plt.subplots_adjust(wspace=0.01, hspace=0.01) #間隔の調整
        st.pyplot(fig) # プレビューの表示

        return outputs