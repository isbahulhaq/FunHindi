import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import nest_asyncio
import random
import argparse
import getindianname as name

nest_asyncio.apply()

# Flag to indicate whether the script is running
running = True

async def start(name, user, wait_time, meetingcode, passcode):
    print(f"{name} started!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
        context = await browser.new_context(permissions=['microphone'])
        page = await context.new_page()
        await page.goto(f'https://zoom.us/wc/join/{meetingcode}', timeout=200000)

        try:
            await page.click('//button[@id="onetrust-accept-btn-handler"]', timeout=5000)
        except Exception as e:
            pass

        try:
            await page.click('//button[@id="wc_agree1"]', timeout=5000)
        except Exception as e:
            pass

        try:
            await page.wait_for_selector('input[type="text"]', timeout=200000)
            await page.fill('input[type="text"]', user)
            await page.fill('input[type="password"]', passcode)
            join_button = await page.wait_for_selector('button.preview-join-button', timeout=200000)
            await join_button.click()
        except Exception as e:
            pass

        try:
            query = '//button[text()="Join Audio by Computer"]'
            await asyncio.sleep(13)
            mic_button_locator = await page.wait_for_selector(query, timeout=350000)
            await asyncio.sleep(10)
            await mic_button_locator.evaluate_handle('node => node.click()')
            print(f"{name} mic aayenge.")
        except Exception as e:
            print(f"{name} mic nahe aayenge. ", e)

        print(f"{name} sleep for {wait_time} seconds ...")
        while running and wait_time > 0:
            await asyncio.sleep(1)
            wait_time -= 1
        print(f"{name} ended!")

        await browser.close()
        
def main():
    global running
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, help="Number of Users")
    parser.add_argument("--meetingcode", type=str, help="Meeting Code (No Space)")
    parser.add_argument("--passcode", type=str, help="Password (No Space)")

    args = parser.parse_args()

    if args.users is None or args.meetingcode is None or args.passcode is None:
        print("Missing required arguments. Please provide --users, --meetingcode, and --passcode.")
        return

    sec = 90
    wait_time = sec * 60

    with ThreadPoolExecutor(max_workers=args.users) as executor:
        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(args.users):
            try:
                # Generate a random Indian name using getindianname
                user = name.randname()
            except IndexError:
                break
            task = loop.create_task(start(f'[Thread{i}]', user, wait_time, args.meetingcode, args.passcode))
            tasks.append(task)
        try:
            loop.run_until_complete(asyncio.gather(*tasks))
        except KeyboardInterrupt:
            running = False
            # Wait for tasks to complete
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass


