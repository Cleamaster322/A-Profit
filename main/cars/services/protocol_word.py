import os
from pathlib import Path


WD_STATISTIC_PAGES = 2


def count_word_pages(docx_path):
    if os.name != "nt":
        raise RuntimeError("Для точного подсчета страниц требуется Microsoft Word в Windows.")

    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    word = None
    document = None
    owns_word = False
    previous_alerts = None
    previous_link_setting = None

    try:
        try:
            word = win32com.client.GetActiveObject("Word.Application")
        except pythoncom.com_error:
            word = win32com.client.DispatchEx("Word.Application")
            owns_word = True

        previous_alerts = word.DisplayAlerts
        previous_link_setting = word.Options.UpdateLinksAtOpen
        word.DisplayAlerts = 0
        word.Options.UpdateLinksAtOpen = False

        document = word.Documents.Open(
            str(Path(docx_path).resolve()),
            False,
            True,
            False,
            "",
            "",
            False,
            "",
            "",
            0,
            "",
            False,
            False,
            0,
            True,
            "",
        )
        document.Repaginate()
        return int(document.ComputeStatistics(WD_STATISTIC_PAGES))
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            if not owns_word:
                word.DisplayAlerts = previous_alerts
                word.Options.UpdateLinksAtOpen = previous_link_setting
            else:
                word.Quit(False)
        pythoncom.CoUninitialize()