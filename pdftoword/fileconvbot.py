import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler 

import os
import io
import requests
import PyPDF2
import docx2pdf

bot_token = 'your token here'
bot = telegram.Bot(token=bot_token)

def start(update, context):
    update.message.reply_text('Welcome to the Document Converter bot! Send me a Word or PDF file and I will convert it to the other format.')

def convert_to_word(update, context):
    # Get the document file from the user's message
    file = context.bot.getFile(update.message.document.file_id)
    
    if file.file_name.endswith('.pdf'):
        # Download the PDF file and read its contents
        response = requests.get(file.file_path)
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        
        # Create a new Word document and write the PDF contents to it
        word_document = PyPDF2.PdfFileWriter()
        for page in pdf_reader.pages:
            text = page.extractText()
            word_document.addPage(PyPDF2.pdf.PageObject.createTextPage(text))
        
        # Save the Word document as a file and send it back to the user
        file_name = file.file_name.split('.')[0] + '.docx'
        word_file = io.BytesIO()
        word_document.write(word_file)
        word_file.seek(0)
        context.bot.send_document(chat_id=update.message.chat_id, document=word_file, filename=file_name)
    
    elif file.file_name.endswith('.docx'):
        # Download the Word file and convert it to PDF
        response = requests.get(file.file_path)
        word_file = io.BytesIO(response.content)
        pdf_file = io.BytesIO()
        docx2pdf.convert(word_file, pdf_file)
        
        # Save the PDF file as a file and send it back to the user
        file_name = file.file_name.split('.')[0] + '.pdf'
        pdf_file.seek(0)
        context.bot.send_document(chat_id=update.message.chat_id, document=pdf_file, filename=file_name)

def convert_to_pdf(update, context):
    # Get the Word file from the user's message
    file = context.bot.getFile(update.message.document.file_id)
    
    # Download the Word file and convert it to PDF
    response = requests.get(file.file_path)
    word_file = io.BytesIO(response.content)
    pdf_file = io.BytesIO()
    docx2pdf.convert(word_file, pdf_file)
    
    # Save the PDF file as a file and send it back to the user
    file_name = file.file_name.split('.')[0] + '.pdf'
    pdf_file.seek(0)
    context.bot.send_document(chat_id=update.message.chat_id, document=pdf_file, filename=file_name)

# Create the updater and add the command handlers

updater = Updater(token=bot_token, use_context = False)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.document.mime_type('application/pdf') | Filters.document.mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document'), convert_to_word))
updater.dispatcher.add_handler(MessageHandler(Filters.document.mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document'), convert_to_pdf))

# Start the bot
updater.start_polling()
updater.idle()
