import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import textwrap
import re
import random


def make_background_gradient(default_width: int, default_height: int) -> Image:
    # Список пастельных цветов
    colors = [
        (205, 174, 174),  # светло-розовый
        (225, 175, 154),  # светло-жёлтый
        (174, 225, 174),  # светло-зелёный
        (190, 164, 205),  # светло-голубой
        (205, 174, 205),  # светло-фиолетовый
        (50, 50, 50)
    ]

    for i in range(20):
        # генерируем три случайных значения между 150 и 255 для получения пастельных цветов
        r = random.randint(100, 225)
        g = random.randint(100, 225)
        b = random.randint(100, 225)
        colors.append((r, g, b))

    # Размер градиента
    width, height = int(default_width * 1.5), int(default_width * 1.5)

    # Создание изображения
    gradient = Image.new('RGB', (width, height), color=colors[0])

    # Создание контекста рисования
    draw = ImageDraw.Draw(gradient)

    # Случайный угол поворота
    angle = random.randint(0, 359)

    # Случайные начальный и конечный цвета
    start_color = random.choice(colors)
    end_color = random.choice(colors)

    def smoothstep(start_color, end_color, position):
        # Ensure that the position is between 0.0 and 1.0
        position = max(0.0, min(1.0, position))

        # Calculate the smoothstep function value
        t = position * position * (3 - 2 * position)

        # Interpolate the color components
        r = int(start_color[0] + t * (end_color[0] - start_color[0]))
        g = int(start_color[1] + t * (end_color[1] - start_color[1]))
        b = int(start_color[2] + t * (end_color[2] - start_color[2]))

        # Return the interpolated color as an RGB tuple
        return r, g, b

    # Рисование плавного градиента
    for y in range(height):
        t = y / height
        color = smoothstep(start_color, end_color, t)
        draw.line((0, y, width, y), fill=color)

    # Поворот изображения
    gradient = gradient.rotate(angle)

    step = int(width / 5)

    gradient = gradient.crop((step, step, width - step, height - step))
    gradient = gradient.resize((default_width, default_height))
    return gradient


def get_flags(text: str) -> tuple:
    text_without_flags = re.sub(r'\/\w+\s\d+', '', text)

    # Извлекаем значения флагов в словарь
    flags = {}
    matches = re.findall(r'\/(\w+)\s(\d+)', text)
    for match in matches:
        try:
            flags[match[0]] = int(match[1])
        except TypeError:
            flags[match[0]] = match[1]
    return flags, text_without_flags


def get_optimal_font_size(text, font_path, max_size, image_width):
    """Возвращает оптимальный размер шрифта, основанный на максимальном размере и ширине изображения"""
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    while font.getsize(text)[0] < image_width and font_size < max_size:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    font = ImageFont.truetype(font_path, font_size - 1)
    return font


def make_preview(title: str, description: str, user_id: int, background: bool = False):
    """Рисует превью."""

    try:
        os.remove('./source/service/%s-result.jpg' % user_id)
    except FileNotFoundError:
        ...

    flags, description = get_flags(description)

    width, height = 3000, 1500

    if flags.get('sq', False):
        height = 3000

    if background:
        img = Image.open('./source/service/%s-background.jpg' % user_id)
        if flags.get('nc', '0') == '0':
            # Crop image
            size_x, size_y = img.size
            crop_width = min(size_x, size_y * 2)
            crop_height = min(size_y, size_x / 2)
            crop_left = (size_x - crop_width) // 2
            crop_top = (size_y - crop_height) // 2
            img = img.crop((crop_left, crop_top, crop_left + crop_width, crop_top + crop_height))
            img = img.resize((width, height))
    else:
        # img = Image.new('RGB', (width, height), 'black')
        img = make_background_gradient(width, height)

    if flags.get('bl', 0) != 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=abs(flags.get('bl', 5))))

    if flags.get('nbg', '0') == '0':
        # Darkness image
        flag = flags.get('bg', False)
        if flag:
            flag = abs(flag / 10)
        else:
            flag = 0.5
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(flag)

    draw = ImageDraw.Draw(img)
    size_x, size_y = img.size

    def draw_text(raw_text: str, font_size: int, line_width: int, offset: int = 0, raw_font='bold'):
        raw_font = ImageFont.truetype('./source/fonts/%s.ttf' % raw_font, size=font_size)
        line_width = line_width - raw_text.count(' ')
        raw_text = '\n'.join(textwrap.wrap(raw_text, width=line_width))

        # Draw quote text
        draw.text(
            (int(size_x / 2), int(size_y / 2) + offset), str(raw_text),
            anchor="mm",
            font=raw_font,
            fill='white'
        )

        return raw_font, raw_text

    font, text = draw_text(raw_text=title,
                           font_size=abs(flags.get('ts', 180)),
                           line_width=abs(flags.get('tlw', 20)),
                           offset=flags.get('to', 0),
                           raw_font=str(flags.get('tf', 'bold')).replace('0', 'bold').replace('1', 'light'))

    text_width, text_height = draw.textsize(text, font=font)
    draw_text(raw_text=description,
              font_size=abs(flags.get('ds', 100)),
              line_width=abs(flags.get('dlw', 50)),
              offset=flags.get('do', text_height),
              raw_font=str(flags.get('df', 'light')).replace('0', 'bold').replace('1', 'light'))

    # img.save('./source/service/%s-result.jpg' % user_id)

    return flags, img
