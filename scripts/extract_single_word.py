import sys
import win32com.client
import os
import pythoncom

def extract_text(filepath):
    pythoncom.CoInitialize()
    word = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        word.AutomationSecurity = 3
        
        abs_path = os.path.abspath(filepath)
        wdoc = word.Documents.Open(
            abs_path, 
            ReadOnly=True, 
            ConfirmConversions=False,
            AddToRecentFiles=False,
            PasswordDocument="dummy_pass_1234"
        )
        text = wdoc.Content.Text
        wdoc.Close(False)
        
        # Output directly to stdout using UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        print(text)
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)
    finally:
        if word:
            try:
                word.Quit()
            except:
                pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_text(sys.argv[1])
