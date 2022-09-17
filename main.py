from fastapi import FastAPI
from pydantic import BaseModel

import io
from urllib.request import Request, urlopen
from PyPDF2 import PdfFileReader
# pdf mining
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def pdfparser(target_url="https://pexam-storage.b-cdn.net/hinterland/skill-based-cv.pdf"):
    data = ''
    # fp = open(data, 'rb')
    # get_url= urllib.request.urlopen('https://pexam-storage.b-cdn.net/lecture_1.pdf')
    # fp = get_url.read()

    remote_file = urlopen(Request(target_url)).read()
    fp = io.BytesIO(remote_file)
    # fp = PdfFileReader(memory_file)

    # print("Response Status: "+ str(get_url.getcode()) )
    # fp = get_url.open()
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data = retstr.getvalue()

    print("TEXT")
    print(data)
    sentences = nltk.sent_tokenize(data) #tokenize sentences
    print(sentences)
    nouns = [] #empty to array to hold all nouns

    for sentence in sentences:
        for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                if len(word) > 1:
                    nouns.append(word)

    return nouns


app = FastAPI()

class Msg(BaseModel):
    msg: str


@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}


@app.get("/path")
async def demo_get():
    return pdfparser()


@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/path/{path_id}")
async def demo_get_path_id(path_id: int):
    return {"message": f"This is /path/{path_id} endpoint, use post request to retrieve result"}