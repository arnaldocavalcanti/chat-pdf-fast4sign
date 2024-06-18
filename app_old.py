import streamlit as st
from utils import chatbot, text
from streamlit_chat import message
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from config import Config
from utils import token_required, generate_token
import os

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Adicione lógica de verificação de usuário aqui (autenticação básica)
    if username and password:
        token = generate_token(username)
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    return pdf_docs


def main():
    

    st.set_page_config(page_title='ChatPDF Dataway', page_icon=':books:')

    st.header('Converse com seus arquivos')
    user_question = st.text_input("Faça uma pergunta para mim!")

    if('conversation' not in st.session_state):
        st.session_state.conversation = None

    if(user_question):
        
        response = st.session_state.conversation(user_question)['chat_history']

        for i, text_message in enumerate(response):

            if(i % 2 == 0):
                message(text_message.content, is_user=True, key=str(i) + '_user')

            else:
                message(text_message.content, is_user=False, key=str(i) + '_bot')


    with st.sidebar:

        st.subheader('Seus arquivos')
        pdf_docs = st.file_uploader("Carregue os seus arquivos em formato PDF", accept_multiple_files=True)

        if st.button('Processar'):
            all_files_text = text.process_files(pdf_docs)

            chunks = text.create_text_chunks(all_files_text)

            vectorstore = chatbot.create_vectorstore(chunks)

            st.session_state.conversation = chatbot.create_conversation_chain(vectorstore)

            

if __name__ == '__main__':
    app.run(debug=True)
    main()