import imageio
import numpy as np
import matplotlib.pyplot as plt


def rotate_coord(coord, c, o_coord=None):
    '''
        (x, y)의 점을 원점을 기준으로 각 c만큼 회전했을 때 좌표
    '''
    x, y = coord
    if o_coord is None:
        o_coord = (0, 0)
    ox, oy = o_coord
    sx, sy = x - ox, y - oy
    r = np.sqrt(sx ** 2 + sy ** 2)  # 반지름
    angle = np.arctan2(sy, sx)  # 각도
    return (
        r * np.cos(angle + c) + ox,
        r * np.sin(angle + c) + oy
    )


def rotate_image(im, c, dtype='uint8', o_coord=None, bg=None):
    '''
        이미지 회전
    '''
    if o_coord is None:
        o_coord = [i / 2 for i in im.shape[:2]]
    if bg is None:
        bg = (0,) * im.shape[-1]
    height, width = im.shape[:2]
    # print(o_coord, im.shape)
    newimage = np.zeros(im.shape, dtype=dtype) + bg
    y = 0
    for row in im:
        x = 0
        # print(f'Y: {y}')
        for pixel in row:
            newx, newy = map(round, rotate_coord((x, y), c, o_coord))
            # print(x, y, newx, newy, pixel)
            x += 1
            if 0 <= newx < width and 0 <= newy < height:
                newimage[int(newy)][int(newx)] = pixel
        y += 1
    return newimage


def make_rotating_video(writer, im, fps, w):
    '''
        이미지 회전 비디오 제작
    '''
    T = 2 * np.pi / w
    for i in range(round(T * fps)):
        writer.append_data(rotate_image(im, i * w / fps, bg=(255,) * 4))
        print(end='.')


fps = 30
image = imageio.imread('test.png')
writer = imageio.get_writer('generated.mp4', fps=fps)
make_rotating_video(writer, image, fps, 2 * np.pi)
writer.close()
print('\nGenerated')
