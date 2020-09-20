def detect_text(path):
    from google.cloud import vision
    import os
    import io

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/ocrTamil/secrets/gkey.json"
    # callOptions = CallOptions()
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(
        # retry = 2,
        timeout=10000,
        image=image,
        image_context={"language_hints": ["ta"]},  # Tamil
    )
    texts = response.text_annotations

    # for text in texts:
    #     for vertice in text.bounding_poly.vertices:
    #         print(vertice.y, vertice.x)
    #     print([text.bounding_poly.vertices[0].y, text.bounding_poly.vertices[0].x, text.description])

    return texts
# [END vision_text_detection]