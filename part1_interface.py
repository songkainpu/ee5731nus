import numpy
import typing

def convolution_2D(src: numpy.ndarray, kernel: numpy.ndarray) -> numpy.ndarray:
    image_height, image_width = src.shape
    kernel_height, kernel_width = kernel.shape
    output = numpy.zeros(( image_height - kernel_height + 1, image_width - kernel_width + 1))
    for i in range(image_height - kernel_height + 1):
        for j in range(image_width - kernel_width + 1):
            output[i, j] = numpy.sum(numpy.multiply(src[i:i+kernel_height, j:j+kernel_width], kernel))
    return output

def gaussian_2d_convolution(size:int, sigma: float=1.0)-> numpy.ndarray:
    if size & 1 == 0:
        size += 1
    if size < 3:
        size = 3
    # gussian_1d = cv2.getGaussianKernel(ksize=size, sigma=sigma)
    # logger.info(f"size:{size}, gussian_1d:{gussian_1d}")
    center = size // 2

    kernel = numpy.zeros((size, size), dtype=numpy.float64)

    constant = 1 / (2 * numpy.pi * sigma ** 2)

    for i in range(size):
        for j in range(size):
            distance = (i - center) ** 2 + (j - center) ** 2
            kernel[i, j] = constant * numpy.exp(-distance / (2 * sigma ** 2))
    kernel /= numpy.sum(kernel)
    return kernel