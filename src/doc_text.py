from enum import Enum
import io, os

from PIL import ImageFont
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

from src.constants import ANNOTATED_FILE_PREFIX, PNG_FILE_EXTENSION


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)
    # make a blank image for the text, initialized to transparent text color
    txt = Image.new("RGBA", image.size, (255, 255, 255, 0))

    counter = 0
    for bound in bounds:
        counter += 1
        # get a font
        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 30)
        # get a drawing context
        # draw text, half opacity

        min_x = min([bound.vertices[0].x, bound.vertices[1].x, bound.vertices[2].x, bound.vertices[3].x])
        min_y = min([bound.vertices[0].y, bound.vertices[1].y, bound.vertices[2].y, bound.vertices[3].y])
        draw.text((min_x, min_y), "{}".format(counter), font=fnt, fill='blue')

        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)

        new_image = Image.alpha_composite(image, txt)

    return new_image


def get_document_properties(image_file):
    """Returns full_text_annotation bounds given an image."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/ocrTamil/secrets/gkey.json"
    client = vision.ImageAnnotatorClient()

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    full_text_annotation = response.full_text_annotation
    ocr_text = response.text_annotations

    # The list `bounds` contains the coordinates of the bounding boxes.
    return ocr_text, full_text_annotation


def get_bounds(full_text_annotation, feature):
    bounds = []
    # Collect specified feature bounds by enumerating all full_text_annotation features
    for page in full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)
    return bounds


def get_document_paragraphs(full_text_annotation):
    """Returns document bounds given an image."""
    breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType
    paragraphs = []
    lines = []
    for page in full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                para = ""
                line = ""
                for word in paragraph.words:
                    for symbol in word.symbols:
                        line += symbol.text
                        if symbol.property.detected_break.type == breaks.SPACE:
                            line += ' '
                        if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                            line += ' '
                            lines.append(line)
                            para += line
                            line = ''
                        if symbol.property.detected_break.type == breaks.LINE_BREAK:
                            lines.append(line)
                            para += line
                            line = ''
                paragraphs.append(para)
    return paragraphs, lines


def render_doc_text(filein):
    image = Image.open(filein).convert("RGBA")
    texts, full_text_annotation  = get_document_properties(filein)
    return texts, full_text_annotation, image


def write_annotated_image(image, full_text_annotation, feature, ref_dir, file_name_without_extension):
    feature_type = FeatureType(feature).name.lower()
    fileout = "{}/{}{}{}{}".format(ref_dir, feature_type, ANNOTATED_FILE_PREFIX, file_name_without_extension,
                                             PNG_FILE_EXTENSION)
    word_bounds = get_bounds(full_text_annotation, feature)
    new_image = draw_boxes(image, word_bounds, 'yellow')
    print("Ref File Name: ", fileout)
    new_image.save(fileout, optimize=True, quality=90)