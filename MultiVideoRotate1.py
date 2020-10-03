import imageio
import numpy as np
from skimage.transform import resize, rotate
from skimage import img_as_ubyte


image_path = input('Input image path: ')
size = 256
raw_image = resize(imageio.imread(image_path), (size, size))

image = rotate(raw_image, -90)
print('image info: ', image.shape, type(image))


def overlap_image(image, base, coordinate, center=True, ignore_empty_pixel=True):
    height, width = image.shape[:2]
    max_y, max_x = base.shape[:2]
    y, x = coordinate
    if center:
        x -= width // 2
        y -= height // 2
    res = np.copy(base)
    for pixel_y in range(height):
        for pixel_x in range(width):
            new_x, new_y = x + pixel_x, y + pixel_y
            pixel = np.copy(image[pixel_y][pixel_x])[:base.shape[-1]]
            if ignore_empty_pixel and all(color == 0 for color in pixel):
                continue
            if 0 <= new_x < max_x and 0 <= new_y < max_y:
                res[new_y][new_x] = pixel
    return res


def rotate_coord(coord, c, o_coord=None):
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


def make_squirming_video(newsize, T=1, fps=30, w=8, bg=None):
    if bg is None:
        bg = (0,) * image.shape[-1]
    bg = tuple(i / 256 for i in bg)
    result = []

    # a = 0
    for height in np.sin(2 * np.pi * np.arange(0, 1, 1 / (T * fps))) / 2 + 1:
        frame = np.zeros((newsize, newsize, image.shape[-1])) + bg
        for angle in np.arange(0, 360, 360 / w):
            tempimage = resize(
                img_as_ubyte(rotate(image, -angle)),
                (height * size // 2, size // 2)
            )
            # imageio.imsave(f'a/{angle}-{a}.png', img_as_ubyte(tempimage))

            angle_rad = angle * np.pi / 180
            image_center = rotate_coord((height * size / 1.5, 0), angle_rad)
            # print(height, image_center)
            image_center = [newsize // 2 + int(round(i)) for i in image_center]
            frame = overlap_image(tempimage, frame, reversed(image_center), center=True, ignore_empty_pixel=True)
        result.append(frame)
        print(end='.', flush=True)
        # a += 1
    print()
    return result


def rotate_video(video):
    return [rotate(i[1], 360 * i[0] / len(video)) for i in enumerate(video)]


newsize = int(size * 2.5)
fps = 30

squirm_video = make_squirming_video(newsize, T=1, fps=fps, w=8, bg=(255,) * image.shape[-1])
print('Video Generated: squirm_video')

rotating_video = rotate_video(np.concatenate((squirm_video,) * 3))
print('Video Generated: rotating_video')


result = []
for i in enumerate(rotating_video):
    frame = i[1]
    angle = 360 * i[0] / len(rotating_video)
    result.append(overlap_image(rotate(raw_image, -angle), frame, (newsize // 2, newsize // 2), center=True))
    if i[0] % 3 == 0:
        print(end='.', flush=True)
print()

path = 'generated.mp4'
imageio.mimsave(path, [img_as_ubyte(frame) for frame in result], fps=fps)
print(f'Video Saved at {path}')

input('Press ENTER to exit...')
