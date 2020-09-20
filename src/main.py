import os
import traceback
from src.detect_text import detect_text

from docx import Document
from docx.shared import Inches


# texts = detect_text("/home/ubuntu/ocrTamil/images/First.jpg")

# print(texts[0].description)
from src.doc_text import render_doc_text


def main(image_dir, doc_dir, ref_dir):
    file_list = os.listdir(image_dir)
    counter = 0
    total_files = len(file_list)
    for file_name in file_list:
        try:
            counter += 1
            input_file_with_path="{}/{}".format(image_dir, file_name)
            print("Processing file no: {} of {} with filename: {}".format(counter, total_files, input_file_with_path))
            file_name_without_extension = os.path.splitext(file_name)[0]
            doc_file_name = "{}/{}{}".format(doc_dir, file_name_without_extension, ".docx")
            annotated_file_name = "{}/{}{}".format(ref_dir, file_name_without_extension, ".png")

            if is_file_dir_present(doc_file_name):
                print("Skipping processing file: {} as the file {} is present.".format(file_name, doc_file_name))
                continue

            # texts = detect_text(input_file_with_path)
            # print(texts)
            # ocr_text = texts[0].description
            # ocr_text = "Ravin is great!!!"

            texts = render_doc_text(input_file_with_path, annotated_file_name)
            ocr_text = texts[0].description

            document = Document()
            document.add_heading(file_name_without_extension, 0)
            doc_page = document.add_paragraph()
            doc_page.add_run(ocr_text)
            document.add_page_break()
            document.save(doc_file_name)
        except Exception as e:
            print("Error in processing for filename: {}".format(file_name))
            traceback.print_exc()
            print(e)
            pass


def is_file_dir_present(path):
    return os.path.exists(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='OCR for tamil novels - Provide dir')
    parser.add_argument('--input_imagedir', metavar='path', required=True,
                        help='the path to input image dirs for OCR')
    parser.add_argument('--output_docdir', metavar='path', required=True,
                        help='the path to output doc dir after OCR')
    parser.add_argument('--reference_imgdir', metavar='path', required=True,
                        help='the path to output reference image dir after OCR')

    args = parser.parse_args()

    image_dir = args.input_imagedir
    doc_dir = args.output_docdir
    reference_imgdir = args.reference_imgdir

    image_dir_present = is_file_dir_present(image_dir)
    doc_dir_present = is_file_dir_present(doc_dir)
    reference_imgdir_present = is_file_dir_present(reference_imgdir)

    if doc_dir_present and image_dir_present and reference_imgdir_present:
        main(image_dir=image_dir, doc_dir=doc_dir, ref_dir=reference_imgdir)
    else:
        print("Program exits without doing anything as requisite dirs are not present. The program expects "
              "the dirs to be present")

