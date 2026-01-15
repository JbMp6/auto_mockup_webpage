from playwright.sync_api import sync_playwright
import time
import os
from PIL import Image
import numpy as np
import re

def accept_cookies(page, timeout: int = 2000) -> bool:
    """Try to detect and click common cookie-accept buttons.

    Returns True if an accept button was clicked, False otherwise.
    """
    selectors = [
        "button:has-text(\"Accept all\")",
        "button:has-text(\"Accept\")",
        "button:has-text(\"I accept\")",
        "button:has-text(\"I Agree\")",
        "button:has-text(\"Tout accepter\")",
        "button:has-text(\"Accepter\")",
        "button:has-text(\"J'accepte\")",
        "text=Accept all",
        "text=Accept",
        "text=Accepter",
        "text=Agree",
    ]

    for sel in selectors:
        try:
            locator = page.locator(sel)
            # is_visible will raise if locator not found within timeout
            if locator.first.is_visible(timeout=timeout):
                locator.first.click()
                print(f"Clicked cookie accept button: {sel}")
                return True
        except Exception:
            continue

    # Try inside frames (some cookie banners live in iframes)
    try:
        for frame in page.frames:
            for sel in selectors:
                try:
                    locator = frame.locator(sel)
                    if locator.first.is_visible(timeout=timeout):
                        locator.first.click()
                        print(f"Clicked cookie accept button in frame: {sel}")
                        return True
                except Exception:
                    continue
    except Exception:
        pass

    print("No cookie accept button found.")
    return False

def screenWebPage(url : str, width: int = 1920, height: int = 1080, waiting: int = 10) -> str :
    """
    Docstring for screenWebPage function.
    
    :param url: Description
    :param width: Description
    :param height: Description
    """

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})

        page.goto(url, wait_until="networkidle")

        # Wait for additional seconds to ensure all elements are loaded
        for i in range(waiting, 0, -1):
            print(f"Waiting for {i} seconds to ensure complete loading...")
            time.sleep(1)
        # Try to accept cookie banners automatically (if any)
        try:
            accepted = accept_cookies(page)
            if accepted:
                # give page a brief moment to react after acceptance
                time.sleep(2)
        except Exception:
            # Non-blocking: if accept_cookies fails, continue anyway
            pass
        
        folder_path = "screen/"
        screen_name = f"{url.replace('http://', '').replace('https://', '').replace('/', '_')}_{width}x{height}.png"
        os.makedirs(folder_path, exist_ok=True)

        page.screenshot(
            path=f"{folder_path}{screen_name}",
            full_page=True
        )

        print(f"Screenshot saved for {url} at {width}x{height} resolution.")

        browser.close()

    return f"{folder_path}{screen_name}"

def createFrameFromImage(image_path: str, frame_number: int, viewport_height: int) -> None :
    """
    Docstring for createFrameFromImage function.
    
    :param image_path: Description
    """

    folder_path = "frames/"
    img_name = os.path.basename(image_path).replace('.png', '')

    os.makedirs(folder_path, exist_ok=True)

    img = Image.open(image_path).convert('RGBA')
    image_width, image_height = img.size

    for i in range(frame_number + 1):
        start_height = int(i * (image_height - viewport_height) / frame_number)
        end_height = int(start_height + viewport_height)

        box = (0, start_height, image_width, end_height)
        frame = img.crop(box)

        frame.save(f"{folder_path}{img_name}_frame_{i:03d}.png")
        print(f"Frame {i}/{frame_number} saved.")

def createGifFromFrames(frame_folder: str, duration: float = 2.0) -> None :
    """
    Docstring for createGifFromFrames function.
    
    :param frame_folder: Description
    :param duration: Description (total seconds for the whole GIF)
    """

    frames = []
    frame_files = sorted([f for f in os.listdir(frame_folder)])

    for frame_file in frame_files:
        frame_path = os.path.join(frame_folder, frame_file)
        img = Image.open(frame_path).convert('RGBA')
        frames.append(img)

    if not frame_files:
        raise ValueError("No frame files found in folder.")

    # Use the first frame filename, remove extension and trailing "_frame_<num>" if present
    first_frame = frame_files[0]
    name_no_ext = os.path.splitext(first_frame)[0]
    name_base = re.sub(r'_frame_\d+$', '', name_no_ext)
    output_name = f"{name_base}.gif"

    # Treat `duration` as total duration (seconds) for the whole GIF.
    # Compute per-frame duration in milliseconds for Pillow.
    per_frame_ms = max(1, int((duration / max(1, len(frames))) * 1000))

    frames[0].save(
        output_name,
        save_all=True,
        append_images=frames[1:],
        duration=per_frame_ms,
        loop=0,
    )

    print(f"GIF saved at {output_name} (loop=0, {per_frame_ms} ms/frame).")

    return output_name

def cleanUpTempFolders() -> None :
    """
    Docstring for cleanUpTempFolders function.
    """

    folders = ["screen/", "frames/"]

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                os.remove(file_path)
            os.rmdir(folder)
            print(f"Cleaned up folder: {folder}")

def addOverlayToGif(gif_path: str, overlay_path: str, gif_size: list) -> None :
    """
    Docstring for addOverlayToGif function.
    
    :param gif_path: Description
    :param overlay_path: Description
    :param gif_size: Description
    """

    def find_coeffs(pa, pb):
        """Find perspective transform coefficients.

        pa: list of destination points [(x,y), ...]
        pb: list of source points [(x,y), ...]
        Returns an 8-tuple suitable for PIL.Image.transform(..., Image.PERSPECTIVE, coeffs)
        """
        matrix = []
        for p1, p2 in zip(pa, pb):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[1]*p1[0]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[0]*p1[1], -p2[1]*p1[1]])

        A = np.array(matrix, dtype=float)
        B = np.array([coord for p in pb for coord in p], dtype=float)
        res = np.linalg.solve(A, B)
        return res

    overlay = Image.open(overlay_path).convert("RGBA")
    overlay_w, overlay_h = overlay.size

    gif = Image.open(gif_path)
    frames_out = []

    try:
        while True:
            frame = gif.convert("RGBA")
            fw, fh = frame.size

            # Expecting gif_size as 4 destination points in order: TL, TR, BL, BR
            dst = [(int(x), int(y)) for (x, y) in gif_size]

            # Source points corresponding to the GIF frame
            src = [(0, 0), (fw, 0), (0, fh), (fw, fh)]

            coeffs = find_coeffs(dst, src)

            warped = frame.transform((overlay_w, overlay_h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

            base = Image.new("RGBA", (overlay_w, overlay_h))
            base.paste(warped, (0, 0), warped)
            base.paste(overlay, (0, 0), overlay)

            frames_out.append(base)

            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    if not frames_out:
        print("No frames extracted from GIF.")
        return

    duration = gif.info.get('duration', 100)

    frames_out[0].save(
        f"{gif_path[:-4]}_with_overlay.gif",
        save_all=True,
        append_images=frames_out[1:],
        duration=duration,
        loop=0,
    )

    print(f"GIF with overlay saved at {gif_path[:-4]}with_overlay.gif.")

def createMacMockup() -> None :
    """
    Docstring for createMacMockup function.
    """

    macbook_screen_size = [(110, 120), (744, 120), (110, 527), (744, 527)]

    cleanUpTempFolders()

    url = input("Enter the URL of the webpage to screenshot: ")
    width, height = 1920, 1080
    nbre_frames = int(input("Enter the number of frames to create: "))
    tmps = int(input("Enter the total duration of the GIF in seconds: "))
    
    web_screen = screenWebPage(url, width=width, height=height)                                        # Default desktop dimensions
    createFrameFromImage(web_screen, nbre_frames, height)                                              # Example viewport size
    gif = createGifFromFrames("frames/", duration=tmps)                                                      # Total GIF duration in seconds
    addOverlayToGif(gif, "./overlay/mac.png", macbook_screen_size)                            # Add overlay to the GIF
    print("Mac mockup GIF created successfully: output_with_overlay.gif")
    
def createIphoneMockup() -> None :
    """
    Docstring for createIphoneMockup function.
    """

    iphone_screen_size = [(365, 30), (714, 30), (365, 738), (714, 738)]

    cleanUpTempFolders()

    url = input("Enter the URL of the webpage to screenshot: ")
    width, height = 828, 1792
    nbre_frames = int(input("Enter the number of frames to create: "))
    tmps = int(input("Enter the total duration of the GIF in seconds: "))
    
    web_screen = screenWebPage(url, width=width, height=height)                                        # Default desktop dimensions
    createFrameFromImage(web_screen, nbre_frames, height)                                              # Example viewport size
    gif = createGifFromFrames("frames/", duration=tmps)                                                      # Total GIF duration in seconds
    addOverlayToGif(gif, "./overlay/iphone.png", iphone_screen_size)                            # Add overlay to the GIF
    print("iPhone mockup GIF created successfully: output_with_overlay.gif")
    
if __name__ == "__main__":

    createMacMockup()
    #createIphoneMockup()