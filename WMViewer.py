from PIL import Image, ImageDraw

def create_wafer_map_image(txt_file, image_file):
    with open(txt_file, 'r') as f:
        data = []
        for line in f:
            stripped_line = line.strip()
            if stripped_line and stripped_line[0] == '.':
                #stripped_line = stripped_line.rstrip('.')
                data.append(list(stripped_line))

    width = len(data[0])
    height = len(data)

    img = Image.new('RGB', (width * 10, height * 10), 'white')
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(data):
        for x, value in enumerate(row):
            if value == '5':
                draw.rectangle((x * 10, y * 10, (x + 1) * 10, (y + 1) * 10), fill='red', outline='black')
            elif value == '1':
                draw.rectangle((x * 10, y * 10, (x + 1) * 10, (y + 1) * 10), fill='green', outline='black')
            elif value == '.':
                draw.rectangle((x * 10, y * 10, (x + 1) * 10, (y + 1) * 10), fill='white', outline='black')

    img.save(image_file)

# 示例用法
create_wafer_map_image('map_test.txt', 'wafer_map.png')
