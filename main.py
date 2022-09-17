from fastapi import FastAPI
from pydantic import BaseModel

import io
import os
from urllib.request import Request, urlopen
from PyPDF2 import PdfFileReader
# pdf mining
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
# imports
import spacy
from spacy.matcher import PhraseMatcher

# init params of skill extractor

# load default skills data base
from skillNer.general_params import SKILL_DB
# import skill extractor
from skillNer.skill_extractor_class import SkillExtractor

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

    return data

def get_skills(job_description):

    # init params of skill extractor
    # nlp = spacy.load("en_core_web_lg")
    # init skill extractor
    nlp = spacy.load("en_core_web_lg")

    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

    # extract skills from job_description
    # job_description = """
    # You are a Python developer with a solid experience in web development
    # and can manage projects. You quickly adapt to new environments
    # and speak fluently English and French
    # """

    annotations = skill_extractor.annotate(job_description)
    return annotations

app = FastAPI()

class Msg(BaseModel):
    msg: str

class Url(BaseModel):
    url: str

@app.get("/pdf/{url}")
async def root(url: str):
    txt = pdfparser(url)
    annotations = get_skills(txt)

    return annotations


@app.get("/path")
async def demo_get():
    return {"message": "Hello World. Welcome to FastAPI!"}


@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/path/{path_id}")
async def demo_get_path_id(path_id: int):
    return {"message": f"This is /path/{path_id} endpoint, use post request to retrieve result"}