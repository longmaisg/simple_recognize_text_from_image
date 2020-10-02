import sys
import numpy as np
import time
import cv2
from PIL import Image
from PIL import ImageTk
import threading
import tkinter as tk
from tkinter import filedialog
import pytesseract


# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# where to save text recognized
text_file = "P:/WORK/Download/recognized.txt"


def button1_clicked(videoloop_stop):
    threading.Thread(target=videoLoop, args=(videoloop_stop,)).start()


def button2_clicked(videoloop_stop):
    videoloop_stop[0] = True


# def onOpen():
#     filename = filedialog.askopenfilename()
#     photo = tk.PhotoImage(file=filename)
#     # button.configure(image=photo)
#     return photo


def image_preprocessing(image):

    # get grayscale image
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(image):
        return cv2.medianBlur(image, 5)

    # thresholding
    def thresholding(image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation
    def dilate(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    # erosion
    def erode(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation
    def opening(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    def canny(image):
        return cv2.Canny(image, 100, 200)

    def deskew(image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    # template matching
    def match_template(image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    image = get_grayscale(image)
    # image = remove_noise(image)
    image = thresholding(image)
    # image = dilate(image)
    # image = erode(image)
    # image = opening(image)
    # image = canny(image)
    # image = deskew(image)
    return image


def videoLoop(mirror=False):

    # A text file is created and flushed
    file = open(text_file, "w+")
    file.write("")
    file.close()

    filename = filedialog.askopenfile(parent=root, mode='rb', title='Choose a file')

    if filename:

        # canvas for text recognized
        text_canvas = tk.Text(canvas, width=120, height=40)
        canvas.create_window((0, 0), window=text_canvas, anchor='nw')
        # text_canvas.insert('end', 'START\n')

        # image = cv2.imread("P:/WORK/Download/Eiffel.jpg", 0)
        image = cv2.imread(filename.name)
        image = image_preprocessing(image)

        # show image
        im1 = Image.fromarray(image)
        im1 = ImageTk.PhotoImage(im1)
        # img_canvas.create_image(500, 200, image=im1)
        img_canvas.create_image(0, 0, image=im1, anchor="nw")

        # Apply OCR on the cropped image
        # Adding custom options
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        # show text recognized on canvas
        text_canvas.insert('end', text + '\n')

        # Open the file in append mode
        file = open(text_file, "a")

        # Appending the text into file
        file.write(text)
        file.write("\n")

        # show text recognized on canvas
        text_canvas.insert('end', text + '\n')

        # Close the file
        file.close

        while True:
            time.sleep(1)
            if videoloop_stop[0]:
                # if switcher tells to stop then we switch it again and stop videoloop
                videoloop_stop[0] = False
                canvas.delete("all")
                img_canvas.delete("all")
                # panel.destroy()
                return

        # im1 = Image.fromarray(image)
        # im1 = ImageTk.PhotoImage(im1)
        # panel = tk.Label(image=im1)
        # panel.image = im1
        # panel.place(x=50, y=50)

        # # Finding contours
        # contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # # Looping through the identified contours
        # # Then rectangular part is cropped and passed on
        # # to pytesseract for extracting text from it
        # # Extracted text is then written into the text file
        # for cnt in contours:
        #     x, y, w, h = cv2.boundingRect(cnt)
        #
        #     # Drawing a rectangle on copied image
        #     im2 = image.copy()
        #     rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #
        #     # Cropping the text block for giving input to OCR
        #     cropped = im2[y:y + h, x:x + w]
        #
        #     # Open the file in append mode
        #     file = open("P:/WORK/Download/recognized.txt", "a")
        #
        #     # Apply OCR on the cropped image
        #     # text = pytesseract.image_to_string(cropped)
        #     # text = 'abc'
        #     # Adding custom options
        #     custom_config = r'--oem 3 --psm 6'
        #     text = pytesseract.image_to_string(cropped, config=custom_config)
        #
        #     # Appending the text into file
        #     file.write(text)
        #     file.write("\n")
        #
        #     # show text recognized on canvas
        #     text_canvas.insert('end', text + '\n')
        #
        #     # Close the file
        #     file.close
        #
        #     # check switcher value
        #     if videoloop_stop[0]:
        #         # if switcher tells to stop then we switch it again and stop videoloop
        #         videoloop_stop[0] = False
        #         canvas.delete("all")
        #         img_canvas.delete("all")
        #         # panel.destroy()
        #         return

        canvas.delete("all")
        img_canvas.delete("all")


# videoloop_stop is a simple switcher between ON and OFF modes
videoloop_stop = [False]

root = tk.Tk()
root.geometry("1920x1080+0+0")
w = tk.Label(root, text='Read text from image', font="200")
w.pack()

# canvas for text recognized
canvas = tk.Canvas(root, width=200, height=600)
canvas.pack(side="left", fill="both")

# canvas to show image
img_canvas = tk.Canvas(root, width=500, height=1000)
img_canvas.pack(side="top", fill="both")
img_canvas.pack()

# start button
button1 = tk.Button(
    root, text="start", bg="#fff", font=("", 50),
    command=lambda: button1_clicked(videoloop_stop))
button1.place(x=1500, y=100, width=400, height=250)

# stop button
button2 = tk.Button(
    root, text="stop", bg="#fff", font=("", 50),
    command=lambda: button2_clicked(videoloop_stop))
button2.place(x=1500, y=360, width=400, height=250)

root.mainloop()
