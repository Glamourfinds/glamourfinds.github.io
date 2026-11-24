"""Glamour overlays v2 (clean template, Nov 23 2026).
All text sits in one compact block at the top-left, inside the TikTok/Reels safe zone
(below the top tabs, above the caption area, left of the like/comment rail), so the outfit
and the bottom of the frame stay clear.

usage: python3 overlays_v2.py <outdir>
writes  {n,d}_hook.png            hook line (first ~2s only)
        {n,d}_track_{S,M,XL}.png  size tracker (active size lit) + small "AI model" tag
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
W, H = 1080, 1920
X0, Y_HOOK, Y_TRACK = 56, 300, 444
LH = 58  # hook line height


def mont(size, w='SemiBold'):
    return ImageFont.truetype(f'{F}/Montserrat-{w}.ttf', size)


def play(size, w='500'):
    return ImageFont.truetype(f'{F}/PlayfairItalic{w}.ttf', size)


def soft_shadow(im, draw_fn, radius=12, alpha=170):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(sh), (0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(radius)))
    draw_fn(ImageDraw.Draw(im), None)


THEMES = {
    'n': dict(hook=('one dress,', 'three bodies'), fg=(226, 196, 140, 255), dim=(255, 255, 255, 110),
              tag=(255, 255, 255, 190), chip=(14, 11, 13, 150), caps=True),
    'd': dict(hook=('same set,', 'three bodies'), fg=(88, 60, 48, 255), dim=(88, 60, 48, 95),
              tag=(88, 60, 48, 200), chip=(251, 240, 231, 215), caps=False),
}


def scrim(im, y0, y1, alpha):
    """Soft dark fade behind the left text block (Nightly only), invisible as a shape."""
    sc = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sc).rounded_rectangle((0, y0, 420, y1), radius=80, fill=(0, 0, 0, alpha))
    im.alpha_composite(sc.filter(ImageFilter.GaussianBlur(60)))


def hook(acc):
    """Two short lines in the left column, clear of the model's face."""
    t = THEMES[acc]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = play(50)
    lines = t['hook']
    if acc == 'n':
        scrim(im, Y_HOOK - 40, Y_HOOK + 2 * LH + 20, 110)

        def draw(d, sh):
            for i, ln in enumerate(lines):
                d.text((X0, Y_HOOK + i * LH), ln, font=f, fill=sh or t['fg'])
        soft_shadow(im, draw, radius=10, alpha=230)
    else:
        d = ImageDraw.Draw(im)
        tw = max(d.textlength(ln, font=f) for ln in lines)
        d.rounded_rectangle((X0 - 20, Y_HOOK - 10, X0 + tw + 22, Y_HOOK + LH * len(lines) + 8), radius=30, fill=t['chip'])
        for i, ln in enumerate(lines):
            d.text((X0, Y_HOOK + i * LH), ln, font=f, fill=t['fg'])
    return im


def track(acc, active):
    t = THEMES[acc]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sizes = ['S', 'M', 'XL'] if t['caps'] else ['s', 'm', 'xl']
    f_on, f_off = mont(30, 'Bold'), mont(30, 'Medium')
    gap = 28
    widths = [d.textlength(s, font=f_on) for s in sizes]
    total = sum(widths) + gap * (len(sizes) - 1)
    # chip behind tracker for legibility on any background
    d.rounded_rectangle((X0 - 22, Y_TRACK - 12, X0 + total + 22, Y_TRACK + 50), radius=31, fill=t['chip'])
    x = X0
    for s, w in zip(sizes, widths):
        on = s.upper() == active
        d.text((x, Y_TRACK), s, font=f_on if on else f_off, fill=t['fg'] if on else t['dim'])
        if on:
            d.rounded_rectangle((x, Y_TRACK + 40, x + w, Y_TRACK + 43), radius=2, fill=t['fg'])
        x += w + gap
    tag = 'AI MODEL' if t['caps'] else 'ai model'
    ft = mont(22, 'Medium')
    if acc == 'n':
        soft_shadow(im, lambda dd, sh: dd.text((X0, Y_TRACK + 72), tag, font=ft, fill=sh or t['tag']), radius=6, alpha=200)
    else:
        tw = d.textlength(tag, font=ft)
        d.rounded_rectangle((X0 - 14, Y_TRACK + 64, X0 + tw + 14, Y_TRACK + 100), radius=18, fill=t['chip'])
        d.text((X0, Y_TRACK + 70), tag, font=ft, fill=t['tag'])
    return im


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for a in ('n', 'd'):
        hook(a).save(f'{out}/{a}_hook.png')
        for s in ('S', 'M', 'XL'):
            track(a, s).save(f'{out}/{a}_track_{s}.png')
    print('v2 overlays written to', out)
