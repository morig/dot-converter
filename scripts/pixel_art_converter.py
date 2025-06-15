import numpy as np
from PIL import Image, ImageFilter
import json
from sklearn.cluster import KMeans
import io
import base64

def remove_background(image_data):
    """
    簡単な背景削除処理（実際の実装では、より高度なアルゴリズムを使用）
    """
    # Base64データをPIL Imageに変換
    image_data = image_data.split(',')[1]  # data:image/jpeg;base64, を除去
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    
    # 簡単な背景削除（白い背景を透明に）
    data = np.array(image)
    white_areas = (data[:,:,0] > 240) & (data[:,:,1] > 240) & (data[:,:,2] > 240)
    data[white_areas] = [255, 255, 255, 0]  # 透明に設定
    
    return Image.fromarray(data)

def find_closest_color(rgb, color_palette):
    """
    RGB値に最も近いパレット色を見つける
    """
    min_distance = float('inf')
    closest_color = None
    closest_name = None
    
    for name, hex_color in color_palette.items():
        # HEX to RGB
        hex_color = hex_color.lstrip('#')
        palette_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # ユークリッド距離を計算
        distance = sum((a - b) ** 2 for a, b in zip(rgb, palette_rgb)) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_color = hex_color
            closest_name = name
    
    return f"#{closest_color}", closest_name

def create_pixel_art(image_data, size, color_palette):
    """
    画像をピクセルアートに変換
    """
    # 背景削除
    image = remove_background(image_data)
    
    # リサイズ
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    
    # RGBAからRGBに変換（透明部分は白に）
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    
    # ピクセルデータを取得
    pixels = np.array(image)
    pixel_art = []
    used_colors = {}
    
    for row in pixels:
        pixel_row = []
        for pixel in row:
            # 最も近いパレット色を見つける
            closest_color, color_name = find_closest_color(pixel[:3], color_palette)
            pixel_row.append({
                'color': closest_color,
                'colorName': color_name
            })
            
            # 使用色をカウント
            if color_name in used_colors:
                used_colors[color_name] += 1
            else:
                used_colors[color_name] = 1
        
        pixel_art.append(pixel_row)
    
    # 使用色リストを作成
    used_colors_list = [
        {
            'name': name,
            'color': color_palette[name],
            'count': count
        }
        for name, count in used_colors.items()
    ]
    
    return {
        'pixelArt': pixel_art,
        'usedColors': used_colors_list
    }

# テスト用のメイン関数
if __name__ == "__main__":
    # サンプルカラーパレット
    sample_palette = {
        "しろ": "#FFFFFF",
        "くろ": "#000000",
        "あか": "#FF0000",
        "あお": "#0000FF",
        "みどり": "#008000"
    }
    
    print("ピクセルアート変換スクリプトが正常に読み込まれました")
    print(f"サンプルパレット色数: {len(sample_palette)}")
