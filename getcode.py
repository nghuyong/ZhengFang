import pytesseract
from PIL import Image
from PIL import ImageFilter

def getcode(image):
	threshold = 69
	table = []
	for i in range(256):  
	    if i < threshold:  
	        table.append(0)  
	    else:  
	        table.append(1)
	image = Image.open(image).convert('L')
	image = image.resize((216,81))
	image = image.filter(ImageFilter.RankFilter(5,13))
	image = image.point(table, '1')
	image.show()

	code = pytesseract.image_to_string(image, config='--psm letters')
	return code
