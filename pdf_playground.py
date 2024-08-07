#---------------------------------------------------------------------------------------------------------------------------------
### Authenticator
#---------------------------------------------------------------------------------------------------------------------------------
import streamlit as st
#---------------------------------------------------------------------------------------------------------------------------------
### Import Libraries
#---------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#----------------------------------------
import os
import sys
import io
import traceback
from PIL import Image
#----------------------------------------
from io import BytesIO
#----------------------------------------
import fitz
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_bytes

#---------------------------------------------------------------------------------------------------------------------------------
### Title and description for your Streamlit app
#---------------------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title="PDF Playground | v0.1",
                    layout="wide",
                    page_icon="📘",            
                    initial_sidebar_state="collapsed")
#----------------------------------------
st.title(f""":rainbow[PDF Playground]""")
st.markdown(
    '''
    Created by | <a href="mailto:avijit.mba18@gmail.com">Avijit Chakraborty</a> |
    for best view of the app, please **zoom-out** the browser to **75%**.
    ''',
    unsafe_allow_html=True)
st.info('**An easy-to-use, open-source PDF application to preview and extract content and metadata from PDFs, add or remove passwords, modify, merge, convert and compress PDFs**', icon="ℹ️")
#----------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------
### Functions & Definitions
#---------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl="2h")
def pdf_to_images(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

#------------------------------------------------------------------------------------

@st.cache_data(ttl="2h")
def merge_pdfs(pdf_files):
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(pdf_file)
    merged_pdf = io.BytesIO()
    merger.write(merged_pdf)
    merger.close()
    merged_pdf.seek(0)
    return merged_pdf

#------------------------------------------------------------------------------------

@st.cache_data(ttl="2h")
def compress_pdf(input_pdf, output_pdf, compression_factor):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    with open(output_pdf, 'wb') as f_out:
        writer.write(f_out)

@st.cache_data(ttl="2h")
def pdf_to_images_bytes(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    return images
#---------------------------------------------------------------------------------------------------------------------------------
### Main app
#---------------------------------------------------------------------------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6  = st.tabs(["**Preview**","**Extract**","**Merge**","**Compress**","**Protect**","**Unlock**"])

#---------------------------------------------------------------------------------------------------------------------------------
### Content
#---------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------
### Preview
#---------------------------------------------------------------------------------------------------------------------------------

with tab1:

    col1, col2 = st.columns((0.2,0.8))
    with col1:

        st.subheader("Input", divider='blue') 
        uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf")

        if uploaded_file is not None:
            st.success("PDFs loaded successfully!")
            with col2:

                st.subheader("View", divider='blue') 
                with st.container(height=900,border=True):

                    images = pdf_to_images(uploaded_file)
                    for i, image in enumerate(images):
                        st.image(image, caption=f'Page {i + 1}', use_column_width=True)

#---------------------------------------------------------------------------------------------------------------------------------
### Extract
#---------------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------------------------------
### Merge
#---------------------------------------------------------------------------------------------------------------------------------

with tab3:

        st.markdown("This app allows you to merge more than two pdf files", unsafe_allow_html=True)  
        uploaded_files = st.file_uploader("**Choose PDF files**", type="pdf", accept_multiple_files=True)
        st.divider()

        if uploaded_files:

            col1, col2 = st.columns((0.2,0.8))
            with col1:
                
                st.write(f"You have selected **{len(uploaded_files)} PDF file(s)** for merging.")
                if st.button("**Merge PDFs**"):
                    with st.spinner("Merging PDFs..."):
                        merged_pdf = merge_pdfs(uploaded_files)
                    st.success("PDFs merged successfully!")

                    st.download_button(label="**📥 Download Merged PDF**",data=merged_pdf,file_name="merged_pdf.pdf",mime="application/pdf")

                    with col2:

                        st.subheader("**View : Merged PDF**",divider='blue')    
                        with st.container(height=600,border=True):

                            merged_pdf.seek(0)
                            images = pdf_to_images(merged_pdf)
                            for page_num, img in enumerate(images):
                                st.image(img, caption=f"Page {page_num + 1}", use_column_width=True)

#---------------------------------------------------------------------------------------------------------------------------------
### Compress
#---------------------------------------------------------------------------------------------------------------------------------

with tab4:

        st.markdown("This app allows you to reduce/compresss sizes of the PDF", unsafe_allow_html=True)  
        uploaded_files = st.file_uploader("**Choose PDF file**", type="pdf", accept_multiple_files=True)
        compression_factor = st.slider("**Select compression factor**", 0.1, 1.0, 0.5, 0.1)
        st.divider()

        if uploaded_files:

            col1, col2 = st.columns((0.2,0.8))
            with col1:

                st.write(f"You have selected **{len(uploaded_files)} PDF file** for compress.")
                if st.button("**Compress PDF**"):

                        for uploaded_file in uploaded_files:
                            temp_input_path = f"/tmp/{uploaded_file.name}"
                            temp_output_path = f"compressed_{uploaded_file.name}"

                            with open(temp_input_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            with st.spinner("Compressing PDFs..."):
                                compress_pdf(temp_input_path, temp_output_path, compression_factor)

                            with open(temp_output_path, "rb") as f:
                                compressed_pdf = f.read()
                            
                            st.success("PDFs compressed successfully!")

                            original_size = os.path.getsize(temp_input_path)
                            compressed_size = os.path.getsize(temp_output_path)
                            compression_ratio = (1 - compressed_size / original_size) * 100

                            st.write(f"**Original PDF size of** : {original_size / 1024:.2f} KB")
                            st.write(f"**Compressed PDF size of**: {compressed_size / 1024:.2f} KB")
                            st.write(f"**Compression achieved**: {compression_ratio:.2f}%")

                            st.download_button(label="**📥 Download Compressed PDF**",data=compressed_pdf,file_name="compressed_pdf.pdf",mime="application/pdf")

                            with col2:

                                st.subheader("**View : Compressed PDF**",divider='blue')    
                                with st.container(height=600,border=True):

                                    #compressed_pdf.seek(0)
                                    images = pdf_to_images_bytes(compressed_pdf)
                                    for page_num, img in enumerate(images):
                                        st.image(img, caption=f"Page {page_num + 1}", use_column_width=True)

                                    os.remove(temp_input_path)
                                    os.remove(temp_output_path)  





#---------------------------------------------------------------------------------------------------------------------------------
