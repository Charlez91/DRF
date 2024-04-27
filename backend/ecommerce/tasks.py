from PIL import Image
from celery import shared_task


@shared_task(name="process item image")
def process_item_image(imagepath, thumbnailpath=None)->None:
    """
    to process thumbnail and images
    """
    #open image and makes a copy
    img = Image.open(imagepath)
    img_thumbnail = Image.Image.copy(img)
    #logic to resize image and save to image path
    if img.height > 300 or img.width > 300:
        output_size = (300,300)
        img = img.resize(output_size)
        img.save(imagepath)
    #logic to resize as thumbnail and save to thumbnail path
    if img_thumbnail.height > 125 or img_thumbnail.width > 125:
        img_thumbnail.thumbnail((125,125))
        img_thumbnail.save(thumbnailpath)