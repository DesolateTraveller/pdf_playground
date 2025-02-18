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
import pikepdf
from docx import Document
from pdf2docx import Converter
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import PDFInfoNotInstalledError,PDFPageCountError,PDFSyntaxError
from pdfminer.high_level import extract_text
#---------------------------------------------------------------------------------------------------------------------------------
### Title and description for your Streamlit app
#---------------------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="PDF Playground | v0.2",
                    layout="wide",
                    page_icon="📘",            
                    initial_sidebar_state="collapsed")
#----------------------------------------
st.markdown(
    """
    <style>
    .title-large {
        text-align: center;
        font-size: 35px;
        font-weight: bold;
        background: linear-gradient(to left, red, orange, blue, indigo, violet);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .title-small {
        text-align: center;
        font-size: 20px;
        background: linear-gradient(to left, red, orange, blue, indigo, violet);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    <div class="title-large">PDF Playground</div>
    <div class="title-small">Play with PDF</div>
    """,
    unsafe_allow_html=True
)
#----------------------------------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #F0F2F6;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #333;
        z-index: 100;
    }
    .footer p {
        margin: 0;
    }
    .footer .highlight {
        font-weight: bold;
        color: blue;
    }
    </style>

    <div class="footer">
        <p>© 2025 | Created by : <span class="highlight">Avijit Chakraborty</span> | Prepared by: <a href="mailto:avijit.mba18@gmail.com">Avijit Chakraborty</a></p> <span class="highlight">Thank you for visiting the app | Unauthorized uses or copying is strictly prohibited | For best view of the app, please zoom out the browser to 75%.</span>
    </div>
    """,
    unsafe_allow_html=True)
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

def merge_pdfs(pdf_files):
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(pdf_file)
    merged_pdf = io.BytesIO()
    merger.write(merged_pdf)
    merger.close()
    merged_pdf.seek(0)
    return merged_pdf

@st.cache_data(ttl="2h")
def compress_pdf(input_pdf, compression_factor=0.5):
    """Compress a PDF file and return it as bytes."""
    
    doc = fitz.open(stream=input_pdf.read(), filetype="pdf")
    output_stream = io.BytesIO()
    new_doc = fitz.open()  # Create a new PDF

    for page in doc:
        # Convert PDF page to Pixmap
        pix = page.get_pixmap()  
        
        # Convert Pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Compress the image and store in a BytesIO stream
        img_stream = io.BytesIO()
        img.save(img_stream, format="JPEG", quality=int(compression_factor * 100))
        img_stream.seek(0)

        # Proper way to create a new Pixmap from a compressed JPEG
        compressed_pix = fitz.Pixmap(fitz.csRGB, fitz.open("jpeg", img_stream).extract_image(0)["image"])

        # Create new page and insert compressed image
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, pixmap=compressed_pix)

    # Save the new compressed PDF
    new_doc.save(output_stream)
    new_doc.close()

    output_stream.seek(0)
    return output_stream.getvalue()  # Return compressed PDF as bytes

def pdf_to_images_bytes(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    return images

def extract_metadata(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    metadata = pdf_reader.metadata
    return metadata

def extract_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def convert_pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes)

#---------------------------------------------------------------------------------------------------------------------------------
### Main app
#---------------------------------------------------------------------------------------------------------------------------------

#stats_expander = st.expander("**:blue[App Capabilities]**", expanded=False)
#with stats_expander:
with st.popover("**:red[App Capabilities]**", disabled=False, use_container_width=True): 
    st.info("""
                
            - **View** -           It allows you to preview PDF files directly within the application.
            - **Extract** -        It is designed to extract text and metadata from PDF files.
            - **Merge** -          It lets you combine multiple PDF files into a single document.
            - **Compress** -       It is used to reduce the file size of PDF documents.
            - **Protect** -        It enables you to add password protection to your PDF files.
            - **Unlock** -         It allows you to remove password protection from PDF files.
            - **Rotate** -         It lets you change the orientation of pages within a PDF file.
            - **Resize** -         It tab allows you to adjust the dimensions of a PDF file.    
            - **Convert** -        It offers conversion options between PDF and other formats, such as word or images. 
         
            """)
#---------------------------------------------------------------------------------------------------------------------------------
### Content
#---------------------------------------------------------------------------------------------------------------------------------

st.divider()

if "current_page" not in st.session_state:
    st.session_state.current_page = "view"

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
with col1:
    if st.button("**:red[View]**",use_container_width=True):
        st.session_state.current_page = "view"
with col2:
    if st.button("**:red[Extract]**",use_container_width=True):
        st.session_state.current_page = "extract"
with col3:
    if st.button("**:red[Merge]**",use_container_width=True):
        st.session_state.current_page = "merge"
with col4:
    if st.button("**:red[Compress]**",use_container_width=True):
        st.session_state.current_page = "compress"
with col5:
    if st.button("**:red[Protect]**",use_container_width=True):
        st.session_state.current_page = "protect"
with col6:
    if st.button("**:red[Unlock]**",use_container_width=True):
        st.session_state.current_page = "unlock"
with col7:
    if st.button("**:red[Rotate]**",use_container_width=True):
        st.session_state.current_page = "rotate"
with col8:
    if st.button("**:red[Resize]**",use_container_width=True):
        st.session_state.current_page = "resize"       

page = st.session_state.current_page 

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9  = st.tabs(["**View**","**Extract**","**Merge**","**Compress**","**Protect**","**Unlock**","**Rotate**","**Resize**","**Convert**"])
     
#---------------------------------------------------------------------------------------------------------------------------------
### View
#---------------------------------------------------------------------------------------------------------------------------------

#with tab1:
if page == "view":

            #st.session_state.pdf_tab = "View"
            st.info("""The **View** tab allows you to preview PDF files directly within the application. You can upload a PDF and view its content without any external software.""")

            col1, col2, col3 = st.columns((0.2,0.6,0.2))
            with col1:           
                with st.container(border=True):
                    uploaded_file = st.file_uploader("**Choose PDF file**",type="pdf",key="file_uploader_preview")
                    if uploaded_file is not None:
                        st.success("PDFs loaded successfully!")

                        try:
                            with col2:
                                with st.container(border=True):
                                    
                                    images = pdf_to_images(uploaded_file)
                                    if images and isinstance(images, list):
                                        for i, image in enumerate(images):
                                            st.image(image, caption=f'Page {i + 1}', use_column_width=True)
                                    else:
                                        st.warning("No images were generated from the PDF.")

                            with col3:
                                with st.container(border=True):

                                    metadata = extract_metadata(uploaded_file)
                                    if metadata:
                                        metadata_df = pd.DataFrame(list(metadata.items()), columns=["Key", "Value"])
                                        st.table(metadata_df)
                                    else:
                                        st.write("No metadata found in the PDF file.")
                        except Exception as e:
                            st.error(f"An error occurred while processing the PDF: {e}")
                    else:
                        st.warning("Please upload a PDF file to view.")

#---------------------------------------------------------------------------------------------------------------------------------
### Extract
#---------------------------------------------------------------------------------------------------------------------------------

#with tab2:
if page == "extract":

            #st.session_state.pdf_tab = "Extract"        
            st.info("""The **Extract** tab is designed to extract text and metadata from PDF files. You can upload a PDF, and the tool will pull out the text content for further analysis or editing.""")

            col1, col2 = st.columns((0.2,0.8))
            with col1:           
                with st.container(border=True):            
                    uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf", key="file_uploader_extract")
                    if uploaded_file is not None:
                        st.success("Text extracted successfully!")
                        #st.write(f"You have selected **{uploaded_file.name}** for text extraction.")

                        try:
                            with col2:
                                with st.container(height=650,border=True):
             
                                    with st.spinner("Extracting text..."):
                                        text = extract_text(uploaded_file)
                                        st.text_area("", value=text, height=7000)
                                        
                                st.download_button(label="**📥 Download Extracted Text**",data=text,file_name="extracted.txt",mime="application/txt") 
                                                    
                        except Exception as e:
                            st.error(f"An error occurred while processing the PDF: {e}")
                    else:
                        st.warning("Please upload a PDF file to extract.")

#---------------------------------------------------------------------------------------------------------------------------------
### Merge
#---------------------------------------------------------------------------------------------------------------------------------

#with tab3:
if page == "merge":
    
            #st.session_state.pdf_tab = "Merge"   
            st.info("""The **Merge** tab lets you combine multiple PDF files into a single document. Simply upload the PDFs you wish to merge, arrange them in the desired order, and merge them into one.""")

            col1, col2 = st.columns((0.2,0.8))
            with col1:           
                with st.container(border=True):              
            
                    uploaded_files = st.file_uploader("**Choose PDF files**", type="pdf", accept_multiple_files=True)
                    if uploaded_files:
                    
                        st.write(f"You have selected **{len(uploaded_files)} PDF file(s)** for merging.")
                        if st.button("**Merge PDFs**"):
                            with st.spinner("Merging PDFs..."):
                                merged_pdf = merge_pdfs(uploaded_files)
                            st.success("PDFs merged successfully!")

                            st.download_button(label="**📥 Download Merged PDF**",data=merged_pdf,file_name="merged_pdf.pdf",mime="application/pdf")

                            with col2:

                                #st.subheader("**View : Merged PDF**",divider='blue')    
                                with st.container(height=650,border=True):

                                    merged_pdf.seek(0)
                                    images = pdf_to_images(merged_pdf)
                                    for page_num, img in enumerate(images):
                                        st.image(img, caption=f"Page {page_num + 1}", use_column_width=True)

                    else:
                        st.warning("Please upload PDF files to Merge.")

#---------------------------------------------------------------------------------------------------------------------------------
### Compress
#---------------------------------------------------------------------------------------------------------------------------------

#with tab4:
if page == "compress":
    
            #st.session_state.pdf_tab = "Compress"   
            st.info("""The **Compress** tab is used to reduce the file size of PDF documents. This is useful when you need to share files with size restrictions or save storage space.""") 

            col1, col2 = st.columns((0.2,0.8))
            with col1:           
                with st.container(border=True):              
                
                    uploaded_files = st.file_uploader("**Choose PDF file**", type="pdf", accept_multiple_files=True)
                    if uploaded_files:

                        st.write(f"You have selected **{len(uploaded_files)} PDF file** for compress.")
                        st.divider()
                        compression_factor = st.slider("**Select compression factor**", 0.1, 1.0, 0.5, 0.1)
                
                        if st.button("**Compress PDF**"):

                            compressed_pdfs = []
                            for uploaded_file in uploaded_files:
                                with st.spinner("Compressing PDFs..."):
                                    compressed_pdf_bytes = compress_pdf(uploaded_file, compression_factor)
                                    compressed_pdfs.append(compressed_pdf_bytes)

                            st.success("PDFs compressed successfully!")

                            for i, uploaded_file in enumerate(uploaded_files):
                                original_size = len(uploaded_file.getvalue())
                                compressed_size = len(compressed_pdfs[i])
                                compression_ratio = (1 - compressed_size / original_size) * 100

                                st.write(f"**Original PDF size**: {original_size / 1024:.2f} KB")
                                st.write(f"**Compressed PDF size**: {compressed_size / 1024:.2f} KB")
                                st.write(f"**Compression achieved**: {compression_ratio:.2f}%")

                            st.download_button(label="**📥 Download Compressed PDF**",data=compressed_pdfs[i],file_name="compressed_pdf.pdf",mime="application/pdf")

                            with col2:

                                #st.subheader("**View : Compressed PDF**",divider='blue')    
                                with st.container(height=700,border=True):

                                    compressed_pdf.seek(0)
                                    images = pdf_to_images_bytes(compressed_pdf)
                                    for page_num, img in enumerate(images):
                                        st.image(img, caption=f"Page {page_num + 1}", use_column_width=True)

                                    if 'compressed_pdf' in locals():  # Ensure compressed_pdf exists before processing
                                        compressed_pdf_bytes = compressed_pdf  # Assuming compressed_pdf is already in bytes
                                        images = pdf_to_images_bytes(compressed_pdf)
                                        for page_num, img in enumerate(images):
                                            st.image(img, caption=f"Page {page_num + 1}", use_column_width=True)

                                    os.remove(temp_input_path)
                                    os.remove(temp_output_path)  

                    else:
                        st.warning("Please upload a PDF file to compress.")

#---------------------------------------------------------------------------------------------------------------------------------
### Protect
#---------------------------------------------------------------------------------------------------------------------------------

#with tab5:
if page == "protect":

        #st.session_state.pdf_tab = "Protect" 
        st.info("""The **Protect** tab enables you to add password protection to your PDF files. You can set a password to prevent unauthorized access or editing of your documents.""")
        
        col1, col2 = st.columns((0.2,0.8))
        with col1:           
            with st.container(border=True):
                
                uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf",key="file_uploader_protect")
                if uploaded_file is not None:

                    st.write(f"You have selected **{uploaded_file.name}** to protect. Please enter the password below and press **Protect** to protect the PDF.")
                    st.divider()
                    password = st.text_input("**Enter a password to protect your PDF**", type="password")

                    if st.button("**Protect**"):
                        if password:
                            
                            with col2:
                                with st.container(height=650,border=True):
                                    
                                    pdf_reader = PdfReader(uploaded_file)
                                    pdf_writer = PdfWriter()
                                    for page in pdf_reader.pages:
                                        pdf_writer.add_page(page)
                                    with st.spinner("Protecting PDFs..."):
                                        pdf_writer.encrypt(user_pwd=password, owner_pwd=None, use_128bit=True)

                                    output_pdf_io = io.BytesIO()
                                    pdf_writer.write(output_pdf_io)
                                    output_pdf_io.seek(0)  # Move to the start of the file
                                    
                                    st.success(f"Your PDF has been password protected and is ready for download.")
                                    st.download_button(label="**📥 Download Password Protected PDF**",data=output_pdf_io,file_name="protected.pdf",mime="application/pdf")

                        else:
                            st.warning("Please enter a password to protect your PDF.")
                else:
                    st.warning("Please upload a PDF file to protect.")

#---------------------------------------------------------------------------------------------------------------------------------
### Unlock
#---------------------------------------------------------------------------------------------------------------------------------

#with tab6:
if page == "unlock":    

        #st.session_state.pdf_tab = "Unlock" 
        st.info("""The **Unlock** tab allows you to remove password protection from PDF files. If you have a secured PDF and you know the password, you can unlock it for easier access.""")

        col1, col2 = st.columns((0.2,0.8))
        with col1:           
            with st.container(border=True):     
        
                uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf",key="file_uploader_unlock")
                if uploaded_file is not None:

                    st.write(f"You have selected **{uploaded_file.name}** for unlock. Please enter the password below and press **Unlock** to remove the password.")
                    st.divider()
                    password = st.text_input("**Enter the password to unlock the PDF**", type="password")

                    if st.button("**Unlock**"):
                        if uploaded_file and password:                           
                        
                            with col2:
                                with st.container(height=650,border=True):
                                
                                    try:
                                        with pikepdf.open(uploaded_file, password=password) as pdf:
                                            with st.spinner("Unlocking PDFs..."):
                                                output_pdf = f"unlocked_{uploaded_file.name}"
                                                pdf.save(output_pdf)

                                        with open(output_pdf, "rb") as f:
                                            st.success(f"Password has been removed from the PDF and is ready for download.")
                                        st.download_button(label="**📥 Download Unlocked PDF**",data=f,file_name="unlocked.pdf",mime="application/pdf")

                                    except pikepdf._qpdf.PasswordError:
                                        st.error("Incorrect password. Please try again.")
                                    except Exception as e:
                                        st.error(f"An error occurred: {str(e)}")
                        else:
                            st.warning("Please enter a password to unlock your PDF.")
                else:
                    st.warning("Please upload a PDF file to unlock")

#---------------------------------------------------------------------------------------------------------------------------------
### Rotate
#---------------------------------------------------------------------------------------------------------------------------------

with tab7:

        st.write("""
        The **Rotate** tab lets you change the orientation of pages within a PDF file. 
        You can rotate individual pages or the entire document to correct their orientation.
        """)

        uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf",key="file_uploader_rotate")
        st.divider()

        if uploaded_file is not None:
                
                st.write(f"You have selected **{uploaded_file.name}** for rotate. Please choose the rotation angle and press **Rotate** to make rotation.")
                rotation_angle = st.slider("**select rotation angle**", 0, 360, 90, 90)

                if st.button("**Rotate**"):        

                    reader = PdfReader(uploaded_file)
                    writer = PdfWriter()
                    for page in reader.pages:
                        page.rotate(rotation_angle)
                        writer.add_page(page)
                    rotated_pdf = io.BytesIO()
                    writer.write(rotated_pdf)
                    rotated_pdf.seek(0)
        
                    st.success("PDF rotated successfully!")
                    st.download_button(label="**📥 Download Rotated PDF**", data=rotated_pdf, file_name="rotated_pdf.pdf", mime="application/pdf")

        else:
            st.warning("Please upload a PDF file to rotate.")

#---------------------------------------------------------------------------------------------------------------------------------
### Resize
#---------------------------------------------------------------------------------------------------------------------------------

with tab8:

    st.write("""
    The **Resize** tab allows you to adjust the dimensions of a PDF file. 
    You can scale the content to a desired size, either enlarging or shrinking it as needed.
    """)
    #st.info('**Disclaimer : This portion is under Development**', icon="ℹ️")

    uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf",key="file_uploader_resize")
    st.divider()

    if uploaded_file is not None:
                
        st.write(f"You have selected **{uploaded_file.name}** for resize. Please choose the scale factor and press **Resize/Rescale**.")
        scale_factor = st.slider("**select scale factor**", 0.1, 2.0, 0.8, 0.1)

        if st.button("**Resize/Rescale**"):    
            try:
                images = pdf_to_images(uploaded_file)
                resized_images = [img.resize((int(img.width * scale_factor), int(img.height * scale_factor))) for img in images]
                resized_pdf = io.BytesIO()
                resized_images[0].save(resized_pdf, save_all=True, append_images=resized_images[1:], format="PDF")
                resized_pdf.seek(0)

                st.success("PDF resized or rescaled successfully!")
                st.download_button(label="**📥 Download Resized PDF**", data=resized_pdf, file_name="resized_pdf.pdf", mime="application/pdf")
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")

    else:
            st.warning("Please upload a PDF file to resize or rescale.")

#---------------------------------------------------------------------------------------------------------------------------------
### Convert
#---------------------------------------------------------------------------------------------------------------------------------

with tab9:

    st.write("""
    The **Convert** tab offers conversion options between PDF and other formats, such as Word or images. 
    You can upload a PDF and convert it to a different format or vice versa.
    """)
    #st.info('**Disclaimer : This portion is under Development**', icon="ℹ️")

    uploaded_file = st.file_uploader("**Choose PDF file**", type="pdf", key="file_uploader_convert")
    st.divider()

    if uploaded_file is not None:

        #st.write(f"You have selected **{uploaded_file.name}** for conversion.")
        conversion_type = st.selectbox("**Choose the output format**", ("Word Document (.docx)", "Plain Text (.txt)"))
        if st.button("**Convert**"):

            pdf_file_path = f"temp_{uploaded_file.name}"
            output_file_name = os.path.splitext(uploaded_file.name)[0]
            with open(pdf_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            if conversion_type == "Word Document (.docx)":
                word_file_path = f"{output_file_name}.docx"
                with st.spinner("Converting to Word..."):
                    converter = Converter(pdf_file_path)
                    converter.convert(word_file_path, start=0, end=None)
                    converter.close()

                with open(word_file_path, "rb") as f:
                    st.success("PDF converted to Word successfully!")
                    st.download_button(label="**📥 Download Word File**", data=f, file_name=word_file_path, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
                os.remove(word_file_path)
        
            elif conversion_type == "Plain Text (.txt)":
                text_file_path = f"{output_file_name}.txt"
                with st.spinner("Converting to Text..."):
                    text = extract_text(pdf_file_path)
                    with open(text_file_path, "w") as f:
                        f.write(text)

                with open(text_file_path, "rb") as f:
                    st.success("PDF converted to Text successfully!")
                    st.download_button(label="**📥 Download Text File**", data=f, file_name=text_file_path, mime="text/plain")

                os.remove(text_file_path)

            os.remove(pdf_file_path)

    else:
        st.warning("Please upload a PDF file to convert.")
