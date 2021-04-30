import pdfkit
import fitz# for Getting Bookmarks list 
import os
import sys
import cgi
import io
import re
import logging
import requests
import shutil
import wget
import PyPDF2
import urllib.request
from bs4 import BeautifulSoup
import xhtml2pdf.pisa as pisa
import pandas as pd

article_titles = []


# ================================================================
# Scrapping Data from site  =============================================
# ================================================================
def remove_tags(html):
    #Creating soup object
    soup = BeautifulSoup(html,'html.parser')

    #Getting Title List
    articles_entries = soup.find_all('h2', class_='entry-title')
    
    soup.find('div', id = 'right-sidebar').decompose()
    soup.find('div', class_ = 'site-footer').decompose()
    rmv_footer = soup.findAll('footer', class_ = 'entry-meta')
    for rmv_ele in rmv_footer:
        rmv_ele.decompose()
    soup.find('nav', id ='mobile-header').decompose()
    soup.find('div', class_ = 'nav-links').decompose()
    soup.find('header', id ='masthead').decompose()
    for data in soup(['style']):
        data.decompose()
    soup.find('a', class_ = 'screen-reader-text skip-link').decompose()
    soup.find('nav', class_ = 'paging-navigation').decompose()
    rmv_time_updated = soup.findAll('time', class_ = 'updated')
    for rmv_ele in rmv_time_updated:
        rmv_ele.decompose()
    for article_tag in soup.findAll('article'):
        article_tag.insert_before(soup.new_tag("div", style="page-break-after:always;"))

    return soup.prettify()




# ================================================================
# Convert to PDF File  =================================================
# ================================================================
def make_content_PDF(html):

    options = {
        'page-size': 'A4',
        'margin-top': '0.50in',
        'margin-right': '0.50in',
        'margin-bottom': '0.50in',
        'margin-left': '0.50in',
        'encoding': "UTF-8",
        'footer-right': '[page] of [topage]',
        'footer-center': 'https://vivekkaul.com/',
        'footer-left': '[date]',
    }    

    
    try:
        pdfkit.from_string(html, "content_file.pdf", options=options)
    except Exception :
        pass
    


# =================================================================
# Make Index PDF from list_content ========================================
# =================================================================
def  make_index_PDF():

    #Getting Bokkmarks List =================
    file = 'content_file.pdf'
    bookmarks_list = []
    counter = 1
    

    try:
        doc = fitz.open(file) 
        toc = doc.getToC(simple = True)
        for del_ele in toc:
            del del_ele[0]

        for ins_ele in toc:
            ins_ele.insert(0, counter)
            counter = counter + 1 

        bookmarks_list = toc
        
    except Exception as e:
        print(e)

    # make an Index ========================
    style = """td, th { border:1px solid black;border-collapse:collapse;}"""
    template = """
    <!DOCTYPE html>
    <html>
      <style>{}</style>
       <head>
          <meta charset="UTF-8">
       </head>
      <body> 
        <table width="100%"  cellspacing ="0px">
        <div name="header">
            <h1  style="text-align:center"> INDEX </h1>
        </div>
        <hr>
        <div>
            <tr>
                <th style="text-align:center; font-size:19px;height = "20px";">No.</th>
                <th style="text-align:center; font-size:19px;height = "20px";">Blog List</th>
                <th style="text-align:center; font-size:19px,height = "20px";">Page No.</th>
            </tr>
            {}
        </div>
        </table>
      </body>
    </html>
    """.format(style, '\t'+'\n'.join('\t<tr>'+'\n'.join('\t\t<td style="font-size:15px;" height = "20px";>{}</td>'.format(c) for c in i)+'\n'+'\t</tr>' for i in bookmarks_list[0:]))

    pdfkit.from_string(template, "index_file.pdf")



# ============================================================
# Mearging PDFs Contents =========================================
# ============================================================
def make_output_PDF():
    # Open the files that have to be merged one by one
    pdf_index = open('index_file.pdf', 'rb')
    pdf_content = open('content_file.pdf', 'rb')

     # Read the files that you have opened
    pdf1Reader = PyPDF2.PdfFileReader(pdf_index)
    pdf2Reader = PyPDF2.PdfFileReader(pdf_content)

     # Create a new PdfFileWriter object which represents a blank PDF document
    pdfWriter = PyPDF2.PdfFileWriter()

     # Loop through all the pagenumbers for the first document
    for pageNum in range(pdf1Reader.numPages):
        pageObj = pdf1Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)

     # Loop through all the pagenumbers for the second document
    for pageNum in range(pdf2Reader.numPages):
        pageObj = pdf2Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)

        # Now that you have copied all the pages in both the documents, write them into the a new document
    pdfOutputFile = open('output_PDF.pdf', 'wb')
    pdfWriter.write(pdfOutputFile)

        # Close all the files - Created as well as opened
    pdfOutputFile.close()
    pdf_index.close()
    pdf_content.close()
    print("File is Created=================")


# =================================================================
# Delete Extra PDF ====================================================  
# ================================================================= 
def  remove_extra_PDF():
    if os.path.exists("content_file.pdf"):
      os.remove("content_file.pdf")
    else:
      print("content_file file does not exist")
    if os.path.exists("index_file.pdf"):
      os.remove("index_file.pdf")
    else:
      print("index_file file does not exist")

    
# =================================================================
# Get Source from Website ==============================================   
# =================================================================    
def get_source():

    html_content=""
    all_page_contents =""
    for i in range(13):
        #Getting Website Link
        reqWebsite = requests.get("https://vivekkaul.com/articles/page/{}".format(i+1))
        #Getting only HTML Content
        get_htmlContent =  reqWebsite.content
        html_content = html_content+ remove_tags(get_htmlContent)

    
    make_content_PDF(html_content)
    make_index_PDF()
    make_output_PDF()
    remove_extra_PDF()
    

# =================================================================    
# Main Method =======================================================
# =================================================================    
if __name__=="__main__":
    get_source()    
    
