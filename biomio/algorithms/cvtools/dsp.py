"""
OpenCV Tools
DSP Module
Implementation of functions for image data signal processing based on OpenCV.
"""
import numpy as np
import cv2


def dsp_spectrum(image):
    """
    OpenCV Tools/DSP Module
        OpenCV provides the functions cv2.dft() and cv2.idft().
    It returns the same result as numpy, but with two channels.
    First channel will have the real part of the result and
    second channel will have the imaginary part of the result.
    The input image should be converted to np.float32 first.

    :param image: numpy.ndarray image object
    :return: numpy array of spectrum magnitude
    """

    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    a = dft_shift[:,:,0]
    b = dft_shift[:,:,1]
    magnitude = 20 * np.log(cv2.magnitude(a, b))
    magnitude = magnitude.astype(np.uint8)
    return magnitude


def dsp_lpf_mask(image, size):
    """
    OpenCV Tools/DSP Module
        Create mask for frequency low-pass filter.

    :param image: numpy.ndarray image object
    :param size: mask window size (w, h)
    :return: numpy.ndarray mask object
    """
    rows = image.shape[0]
    cols = image.shape[1]
    crow, ccol = rows / 2, cols / 2
    mask = np.zeros((rows, cols, 2), np.uint8)
    mask[crow-size:crow+size, ccol-size:ccol+size] = 1
    return mask


def dsp_hpf_mask(image, size):
    """
    OpenCV Tools/DSP Module
        Create mask for frequency high-pass filter.

    :param image: numpy.ndarray image object
    :param size: mask window size (w, h)
    :return: numpy.ndarray mask object
    """
    rows = image.shape[0]
    cols = image.shape[1]
    crow, ccol = rows / 2, cols / 2
    mask = np.ones((rows, cols, 2), np.uint8)
    mask[crow-size:crow+size, ccol-size:ccol+size] = 0
    return mask


def dsp_filter(image, kernel):
    """
    OpenCV Tools/DSP Module
        Applies frequency filter with kernel to the image.

    :param image: numpy.ndarray image object
    :param kernel: numpy.ndarray mask object
    :return: numpy.ndarray mask object
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    fshift = dft_shift*kernel
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
    img_back = img_back.astype(np.uint8)
    return img_back
