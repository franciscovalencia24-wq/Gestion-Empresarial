import os
import time
from playwright.sync_api import sync_playwright

def test_wa_attachment():
    print("Starting Playwright...")
    with sync_playwright() as p:
        print("Launching browser...")
        browser_context = p.chromium.launch_persistent_context(
            user_data_dir="data/whatsapp_session",
            headless=False,
            viewport={'width': 1280, 'height': 800},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = browser_context.new_page()
        page.goto("https://web.whatsapp.com/send?phone=56966779662")
        print("Waiting for chat box...")
        
        try:
            page.wait_for_selector('footer div[contenteditable="true"]', timeout=30000)
            print("Chat box found!")
        except Exception as e:
            print("Timeout waiting for chat box")
            page.screenshot(path="data/wa_debug_1.png")
            browser_context.close()
            return
            
        time.sleep(2)
        
        # Click attach button
        attach_selectors = [
            'div[title="Adjuntar"]', 'div[title="Añadir"]', 'button[aria-label="Adjuntar"]',
            'button[aria-label="Añadir"]', 'div[aria-label="Adjuntar"]', 'div[aria-label="Añadir"]',
            'span[data-icon="plus"]', 'span[data-icon="clip"]', 'footer button', 'footer div[role="button"]'
        ]
        
        clicked_plus = False
        for _ in range(10):
            for sel in attach_selectors:
                btns = page.locator(sel)
                try:
                    for i in range(btns.count()):
                        b = btns.nth(i)
                        if b.is_visible():
                            b.click()
                            print(f"Clicked plus using selector: {sel}")
                            clicked_plus = True
                            break
                except Exception:
                    pass
                if clicked_plus: break
            if clicked_plus: break
            time.sleep(1)
            
        time.sleep(2)
        
        # Click document button
        doc_selectors = [
            'span[data-icon="document"]',
            'ul li div[role="button"]:has-text("Documento")',
            'ul li:has-text("Documento")',
            'span:has-text("Documento")',
            'div:text-is("Documento")',
            'span:has-text("Document")',
            'span[data-icon="attach-document"]',
            'ul li button'
        ]
        
        # Setup file chooser
        with page.expect_file_chooser(timeout=10000) as fc_info:
            clicked_doc = False
            for _ in range(8):
                for d_sel in doc_selectors:
                    btns = page.locator(d_sel)
                    try:
                        for i in range(btns.count()):
                            b = btns.nth(i)
                            if b.is_visible():
                                print(f"Clicking doc button using selector: {d_sel}")
                                b.click()
                                clicked_doc = True
                                break
                    except Exception:
                        pass
                    if clicked_doc: break
                if clicked_doc: break
                time.sleep(1)
                
        file_chooser = fc_info.value
        # Pick any file
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.close()
        file_chooser.set_files(os.path.abspath(tmp.name))
        
        print("File uploaded to browser.")
        time.sleep(5)
        
        print("Dumping HTML...")
        with open("data/wa_debug_dom.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        page.screenshot(path="data/wa_debug_final.png")
        print("Done capturing menu.")
        browser_context.close()

if __name__ == "__main__":
    test_wa_attachment()
