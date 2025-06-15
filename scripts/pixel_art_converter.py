import numpy as np
from PIL import Image, ImageFilter
import json
from sklearn.cluster import KMeans
from skimage.color import rgb2lab # Added for CIELAB
import io
import base64
import sys # Added for potential debug prints
import itertools # For combinations

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

def hex_to_lab(hex_color_string):
    """
    Converts a hex color string to its CIELAB representation.
    """
    hex_color = hex_color_string.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Normalize RGB and convert to the 1x1x3 numpy array format for rgb2lab
    rgb_normalized = np.array([[[r / 255.0, g / 255.0, b / 255.0]]], dtype=np.float32)
    lab_array = rgb2lab(rgb_normalized)
    return lab_array[0][0] # Return the 1D CIELAB array [L, a, b]

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

def create_pixel_art(image_data, size, color_palette, max_colors=0): # Added max_colors
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
    
    # Corrected reconstruction of used_colors_list:
    # `used_colors` keys are the 'name' from the palette.
    # `color_palette` is a dict like {name: hex_string}
    current_used_colors_list = []
    for name, count in used_colors.items():
        # Ensure the name exists in the palette to avoid KeyError
        # find_closest_color should always return a name that's a key in color_palette.
        hex_value_for_name = color_palette.get(name, "#000000") # Default to black if name somehow not in palette
        current_used_colors_list.append({
            'name': name,
            'color': hex_value_for_name,
            'count': count
        })

    # ---- START COLOR REDUCTION LOGIC ----
    # Convert used_colors_list to a dictionary for easier management during reduction
    # Key by hex color string for direct access (assuming hex string is unique identifier)
    # However, the current_used_colors_list has 'color' field which includes '#'.
    # And the placeholder removal below uses dict keys.
    # Let's key by 'name' as it's used above and likely more stable if hex strings can vary (e.g. #fff vs #FFFFFF)
    # Or better, use the hex string (unique color value) as the key.
    # The `closest_hex_color_str` in `find_closest_color` is without '#'. Let's use that form.
    # `find_closest_color` returns f"#{closest_hex_color_str}"
    
    # Re-think current_used_colors_dict structure.
    # `used_colors` is already a dict: { colorName: count }
    # `color_palette` is { colorName: hexString }
    # `current_used_colors_list` is [{name: colorName, color: hexString, count: count}, ...]

    # For reduction, we need to manage a list of unique colors currently in the image.
    # `current_used_colors_list` is that list.

    modifiable_pixel_art = [[p.copy() for p in row] for row in pixel_art] # Deep copy
    # Use a dictionary for current used colors, keyed by hex string (e.g., "#RRGGBB")
    # Each value will be the {'name': ..., 'color': ..., 'count': ...} dict
    current_used_colors_dict = {item['color']: item.copy() for item in current_used_colors_list}

    if max_colors > 0 and len(current_used_colors_dict) > max_colors:
        # Pre-calculate LAB values for all current colors for efficiency
        lab_cache = {hex_color: hex_to_lab(hex_color) for hex_color in current_used_colors_dict.keys()}

        while len(current_used_colors_dict) > max_colors:
            unique_hex_colors = list(current_used_colors_dict.keys())
            if len(unique_hex_colors) < 2:
                break # Not enough colors to merge

            min_distance = float('inf')
            closest_pair = None

            for hex1, hex2 in itertools.combinations(unique_hex_colors, 2):
                lab1 = lab_cache[hex1]
                lab2 = lab_cache[hex2]
                distance = np.linalg.norm(lab1 - lab2)

                if distance < min_distance:
                    min_distance = distance
                    closest_pair = (hex1, hex2)

            if closest_pair is None: # Should not happen if len(unique_hex_colors) >= 2
                break

            hex_color1, hex_color2 = closest_pair

            # Determine which color to keep and which to replace
            # Keep the one with higher count. If counts are equal, an arbitrary one (e.g. first) is fine.
            if current_used_colors_dict[hex_color2]['count'] > current_used_colors_dict[hex_color1]['count']:
                hex_to_keep = hex_color2
                hex_to_replace = hex_color1
            else:
                hex_to_keep = hex_color1
                hex_to_replace = hex_color2

            # print(f"Debug: Merging {hex_to_replace} into {hex_to_keep}", file=sys.stderr)

            # Update counts and color info in current_used_colors_dict
            color_to_replace_info = current_used_colors_dict[hex_to_replace]
            current_used_colors_dict[hex_to_keep]['count'] += color_to_replace_info['count']
            del current_used_colors_dict[hex_to_replace]

            # Update LAB cache: remove replaced color, no need to update kept one as its LAB value doesn't change
            if hex_to_replace in lab_cache:
                del lab_cache[hex_to_replace]

            # Update modifiable_pixel_art
            name_to_keep = current_used_colors_dict[hex_to_keep]['name']
            for r_idx, row in enumerate(modifiable_pixel_art):
                for c_idx, pixel_info in enumerate(row):
                    if pixel_info['color'] == hex_to_replace:
                        modifiable_pixel_art[r_idx][c_idx]['color'] = hex_to_keep
                        modifiable_pixel_art[r_idx][c_idx]['colorName'] = name_to_keep

        final_used_colors_list = list(current_used_colors_dict.values())
    else:
        final_used_colors_list = current_used_colors_list
    # ---- END COLOR REDUCTION LOGIC ----

    return {
        'pixelArt': modifiable_pixel_art,
        'usedColors': final_used_colors_list
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
        max_colors = input_data.get('max_colors', 0) # Extract max_colors, default to 0

        if not all([image_data, size, color_palette]): # max_colors can be 0, so not checked here
            raise ValueError("Missing required parameters: image_data, size, or color_palette")

        result = create_pixel_art(image_data, size, color_palette, max_colors) # Pass max_colors

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
