import numpy as np
from PIL import Image, ImageFilter
import json
from sklearn.cluster import KMeans
from skimage.color import rgb2lab # Added for CIELAB
import io
import base64
import sys # Added for potential debug prints

def remove_background(image_data):
    """
    簡単な背景削除処理（実際の実装では、より高度なアルゴリズムを使用）
    """
    # Base64データをPIL Imageに変換
    image_data_parts = image_data.split(',')
    if len(image_data_parts) > 1:
        b64_data = image_data_parts[1]
    else:
        b64_data = image_data_parts[0] # Assume it's already pure base64

    image_bytes = base64.b64decode(b64_data)
    image = Image.open(io.BytesIO(image_bytes))
    # print(f"Debug: remove_background - Initial loaded image mode: {image.mode}, size: {image.size}, sample pixel (0,0): {image.getpixel((0,0)) if image.width > 0 and image.height > 0 else 'Image is empty'}", file=sys.stderr)
    image = image.convert('RGB') # Convert to RGB first to correctly interpret colors
    # print(f"Debug: remove_background - After convert to RGB, mode: {image.mode}, size: {image.size}, sample pixel (0,0): {image.getpixel((0,0)) if image.width > 0 and image.height > 0 else 'Image is empty'}", file=sys.stderr)
    image = image.convert('RGBA') # Then convert to RGBA for alpha manipulation
    # print(f"Debug: After initial convert to RGBA: mode={image.mode}, size={image.size}, P(0,0)={image.getpixel((0,0)) if image.width > 0 and image.height > 0 else 'N/A'}, P(1,0)={image.getpixel((1,0)) if image.width > 1 and image.height > 0 else 'N/A'}", file=sys.stderr)
    
    data = np.array(image)
    # Make the condition stricter for identifying white areas
    white_areas = (data[:,:,0] > 250) & (data[:,:,1] > 250) & (data[:,:,2] > 250) & (data[:,:,3] > 0) # Check alpha too
    data[white_areas] = [255, 255, 255, 0]  # 透明に設定
    return Image.fromarray(data)

def find_closest_color(rgb, color_palette):
    """
    RGB値に最も近いパレット色を見つける (using CIELAB color space)
    """
    # Convert target pixel to CIELAB
    # rgb is expected to be a list/tuple or numpy array slice like [R, G, B] with values 0-255
    pixel_rgb_normalized = np.array([[(c / 255.0) for c in rgb]], dtype=np.float32) # Corrected: removed extra ']'
    pixel_lab = rgb2lab(pixel_rgb_normalized)[0][0]

    min_distance = float('inf')
    closest_hex_color_str = None # Store the hex string part
    closest_name = None
    
    for name, hex_color_palette_entry in color_palette.items():
        # HEX to RGB (0-255)
        hex_color_str_palette = hex_color_palette_entry.lstrip('#')
        palette_rgb_tuple = tuple(int(hex_color_str_palette[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert palette RGB to CIELAB
        palette_rgb_normalized = np.array([[(c / 255.0) for c in palette_rgb_tuple]], dtype=np.float32) # Corrected: removed extra ']'
        palette_lab = rgb2lab(palette_rgb_normalized)[0][0]

        # Calculate Euclidean distance in CIELAB space
        distance = np.linalg.norm(pixel_lab - palette_lab)
        
        if distance < min_distance:
            min_distance = distance
            closest_hex_color_str = hex_color_str_palette # store the hex numbers only
            closest_name = name

    if closest_hex_color_str is None: # Should not happen if palette is not empty
        # Fallback or error, though practically, with a non-empty palette, a closest will always be found.
        # For safety, could return a default or raise an error.
        # Here, we'll assume it always finds one if palette is valid.
        # Defaulting to black if nothing found (should be handled better if palette can be empty)
        return "#000000", "black"

    return f"#{closest_hex_color_str}", closest_name

def create_pixel_art(image_data, size, color_palette):
    """
    画像をピクセルアートに変換
    """
    # print(f"Debug: create_pixel_art - Initial image_data type: {type(image_data)}", file=sys.stderr)
    image = remove_background(image_data)
    # print(f"Debug: create_pixel_art - After remove_background, image mode: {image.mode}, image size: {image.size}, P(0,0)={image.getpixel((0,0)) if image.width > 0 and image.height > 0 else 'N/A'}, P(1,0)={image.getpixel((1,0)) if image.width > 1 and image.height > 0 else 'N/A'}", file=sys.stderr)

    image = image.resize((size, size), Image.Resampling.NEAREST)
    # print(f"Debug: Resized image: mode={image.mode}, size={image.size}", file=sys.stderr)
    # if image.width > 0 and image.height > 0 and image.width > size//2 and image.width > (size-1) : # ensure width is enough for sampling points
    #     print(f"Debug: Resized P(0,0)={image.getpixel((0,0))}", file=sys.stderr)
    #     print(f"Debug: Resized P({size//2 -1},0)={image.getpixel((size//2 -1,0))}", file=sys.stderr)
    #     print(f"Debug: Resized P({size//2},0)={image.getpixel((size//2,0))}", file=sys.stderr)
    #     print(f"Debug: Resized P({size-1},0)={image.getpixel((size-1,0))}", file=sys.stderr)
    
    if image.mode == 'RGBA':
        if len(image.split()) == 4:
            alpha_mask = image.split()[-1]
        else:
            alpha_mask = None
            # print(f"Debug: Image mode is RGBA but channels are not 4: {len(image.split())}", file=sys.stderr)
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=alpha_mask)
        image = background
    # print(f"Debug: create_pixel_art - After RGBA->RGB, image mode: {image.mode}, image size: {image.size}, sample pixel (0,0): {image.getpixel((0,0)) if image.width > 0 and image.height > 0 else 'Image is empty'}", file=sys.stderr)
    
    pixels = np.array(image)
    # print(f"Debug: Numpy array 'pixels' shape: {pixels.shape}", file=sys.stderr)
    # if pixels.shape[0] > 0 and pixels.shape[1] > 0 and pixels.shape[1] > size//2 and pixels.shape[1] > (size-1): # ensure width is enough
    #     print(f"Debug: Numpy P(0,0)={pixels[0,0]}", file=sys.stderr)
    #     print(f"Debug: Numpy P(0,{size//2 -1})={pixels[0,size//2 -1]}", file=sys.stderr)
    #     print(f"Debug: Numpy P(0,{size//2})={pixels[0,size//2]}", file=sys.stderr)
    #     print(f"Debug: Numpy P(0,{size-1})={pixels[0,size-1]}", file=sys.stderr)

    pixel_art = []
    used_colors = {}
    
    for row_idx, row_data in enumerate(pixels):
        pixel_row = []
        for col_idx, pixel_value in enumerate(row_data):
            # if row_idx == 0:
            #     if col_idx == 0:
            #         print(f"Debug: Loop P(0,0) raw: {pixel_value[:3]}", file=sys.stderr)
            #     if col_idx == size // 2 -1:
            #         print(f"Debug: Loop P(0,{size//2-1}) raw: {pixel_value[:3]}", file=sys.stderr)
            #     if col_idx == size // 2:
            #         print(f"Debug: Loop P(0,{size//2}) raw: {pixel_value[:3]}", file=sys.stderr)
            #     if col_idx == size - 1:
            #         print(f"Debug: Loop P(0,{size-1}) raw: {pixel_value[:3]}", file=sys.stderr)
            closest_color, color_name = find_closest_color(pixel_value[:3], color_palette)
            pixel_row.append({
                'color': closest_color,
                'colorName': color_name
            })
            
            if color_name in used_colors:
                used_colors[color_name] += 1
            else:
                used_colors[color_name] = 1
        
        pixel_art.append(pixel_row)
    
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

if __name__ == "__main__":
    try:
        # 1. Read input from sys.stdin more robustly
        input_str = sys.stdin.buffer.read().decode('utf-8')

        # 2. Parse JSON input
        input_data = json.loads(input_str)

        image_data = input_data.get("image_data")
        size = input_data.get("size")
        color_palette = input_data.get("color_palette")
        position = input_data.get("position")
        scale = input_data.get("scale")

        if not all([image_data, size, color_palette]):
            raise ValueError("Missing required parameters: image_data, size, or color_palette")

        result = create_pixel_art(image_data, size, color_palette)

        sys.stdout.write(json.dumps(result))

    except json.JSONDecodeError as e:
        error_message = {"error": f"JSONDecodeError: {str(e)}", "input_received": input_str[:500]}
        sys.stderr.write(json.dumps(error_message) + "\n")
        sys.exit(1)
    except ValueError as e:
        error_message = {"error": f"ValueError: {str(e)}"}
        sys.stderr.write(json.dumps(error_message) + "\n")
        sys.exit(1)
    except Exception as e:
        error_message = {"error": f"An unexpected error occurred: {str(e)}"}
        sys.stderr.write(json.dumps(error_message) + "\n")
        sys.exit(1)
