from pdf2image import convert_from_path
import pytesseract


def ocr_pdf_with_tesseract(
    pdf_path="/Users/darren.rooney/Downloads/Rooney Attendee List.pdf",
):
    images = convert_from_path(pdf_path, poppler_path="/opt/homebrew/bin")
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text


if __name__ == "__main__":
    t = ocr_pdf_with_tesseract()
    print(t)
