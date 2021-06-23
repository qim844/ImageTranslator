import io
from enum import Enum

# Imports the Google Cloud client libraries
from google.cloud import translate
from google.cloud import vision

from PIL import Image, ImageFont, ImageDraw

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

# Returns a list of the text in the given an image
def get_document_text(image_file):

    client = vision.ImageAnnotatorClient()
    breaks = vision.TextAnnotation.DetectedBreak.BreakType
    paragraphs = []
    lines = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    for page in document.pages:
     for block in page.blocks:
       for paragraph in block.paragraphs:
         para = ""
         line = ""
         for word in paragraph.words:
           for symbol in word.symbols:
               line+=symbol.text
               try:
                   if(symbol.property.detected_break.type_ == breaks.SPACE):
                     line += ' '
                   if(symbol.property.detected_break.type_ == breaks.EOL_SURE_SPACE):
                     line += ' '
                     lines.append(line)
                     para += line
                     line = ''
                   if(symbol.property.detected_break.type_ == breaks.LINE_BREAK):
                     lines.append(line)
                     para += line
                     line = ''
               except AttributeError:
                   continue
         paragraphs.append(para)

    return paragraphs

# Returns a list of the text in the given an image uri
def get_document_text_uri(uri):
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    breaks = vision.TextAnnotation.DetectedBreak.BreakType
    paragraphs = []
    lines = []

    for page in document.pages:
     for block in page.blocks:
       for paragraph in block.paragraphs:
         para = ""
         line = ""
         for word in paragraph.words:
           for symbol in word.symbols:
               line+=symbol.text
               try:
                   if(symbol.property.detected_break.type_ == breaks.SPACE):
                     line += ' '
                   if(symbol.property.detected_break.type_ == breaks.EOL_SURE_SPACE):
                     line += ' '
                     lines.append(line)
                     para += line
                     line = ''
                   if(symbol.property.detected_break.type_ == breaks.LINE_BREAK):
                     lines.append(line)
                     para += line
                     line = ''
               except AttributeError:
                   continue
         paragraphs.append(para)

    return paragraphs

# Returns document bounds given an image
def get_document_bounds(image_file, feature):

    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
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


    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds

# Translate text function
def translate_text(text="YOUR_TEXT_TO_TRANSLATE", project_id="YOUR_PROJECT_ID"):

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": "en-US",
            "target_language_code": "zh", # Chinese, but it can be any lanuage you want
        }
    )

    # Display the translation for each input text provided
    for translation in response.translations:
        translated_text = format(translation.translated_text)

    return translated_text

def main():

    ####### Replace with your own #########
    infile = "test_image/test1_input.jpeg"
    # image_uri = "https://storage.cloud.google.com/sam_mini_competition/test1_input.jpeg"
    projectID = "mini-individual-competition"
    #######################################

    translated_text_list = []

    # photo -> detected text
    text_to_translate = get_document_text(infile)
    # text_to_translate = get_document_text_uri(image_uri)
    # print (text_to_translate)


    # detected text -> translated text
    for text in text_to_translate:
        translated_text = translate_text(text, projectID)
        translated_text_list.append(translated_text)

    # print (translated_text_list[0])

    bounds = get_document_bounds(infile, FeatureType.PARA)
    my_image = Image.open(infile)

    font = ImageFont.truetype("resources/arial-unicode-ms.ttf",20)
    image_editable = ImageDraw.Draw(my_image)

    # print (str(bounds[0].vertices[0].x) + "," + str(bounds[0].vertices[0].y))
    # print (str(bounds[1].vertices[0].x) + "," + str(bounds[1].vertices[0].y))

    for i in range(0, len(bounds)):
            image_editable.text((bounds[i].vertices[3].x,bounds[i].vertices[3].y), translated_text_list[i], "red", font = font)

    my_image.save("test_image/test1_output.jpeg")

main()
