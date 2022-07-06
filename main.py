import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import os
import requests
import time

names = []

def pushoverPost():
    r = requests.post("https://api.pushover.net/1/messages.json", data = {
        "token": "APPLICATION TOKEN", # Make application here: https://pushover.net/apps/build
        "user": "USER TOKEN", #User token found here: https://pushover.net/ when logged in.
        "message": "Here is a screenshot of " + matching[0] 
        },
        files = {
        "attachment": ("image.png", open(os.path.dirname(os.path.realpath(__file__)) + "/test.png", "rb"), "image/png")
        })
    print(r.text)

def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        n = win32gui.GetWindowText(hwnd)  
        if n:
            names.append(n)

win32gui.EnumWindows(winEnumHandler, None)

windowName = input("Enter the name of the window (case sensitive):")
matching = [s for s in names if windowName in s]



def main():
    hwnd = win32gui.FindWindow(None, matching[0])

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    #left, top, right, bot = win32gui.GetClientRect(hwnd)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    #result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 2)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        #PrintWindow Succeeded
        dir_path = os.path.dirname(os.path.realpath(__file__))
        im.save(os.path.dirname(os.path.realpath(__file__)) + "/test.png")
        pushoverPost()




if __name__ == "__main__":
    timer = input("Monitoring time interval (seconds):")
    while True:
        try:
            main()
            time.sleep(int(timer))
        except Exception as e:
            print("Error caught: " + str(e))
            print("Be sure the title of the Window is correct. Some programs have dynamic titles. Long window titles can result in error.")
            print("Will continue attempting every 5 seconds. CTRL + C to stop.")
            time.sleep(5)
            continue