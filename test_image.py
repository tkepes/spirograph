from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1000, 1000
IM = Image.new('RGB', (WIDTH, HEIGHT))
DRAW = ImageDraw.Draw(IM)
BACKGROUND = (127, 127, 127)
DRAW.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=BACKGROUND, outline=BACKGROUND, width=2)
DRAW.line((0, 0, WIDTH, HEIGHT),fill=(0,0,0), width=2)
IM.save('mypic.png')
