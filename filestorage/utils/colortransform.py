from math import ceil


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def val_to_hex(val):
    if val < 0 :
        val = 0
    elif val>1:
        val = 1
    return rgb_to_hex((0,(ceil(255*(1-(0.7*val/1)))),0))