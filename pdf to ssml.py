# importing required modules
import re
import PyPDF2

# creating a pdf file object
pdfFileObj = open('Data/michael-white-workshop-notes.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(9)

# extracting text from page
pdftext = pageObj.extractText()

text = re.sub(r'{/.\n}', ".</p><p>", pdftext)

print(pdftext)

