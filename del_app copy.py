import streamlit as st
from main import search
import base64

# Настройка страницы
st.set_page_config(
    page_title="Медицинский помощник Минздрава России",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили для профессионального вида
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://minzdrav.gov.ru/system/files/2021-07/background.jpg");
             background-size: cover;
             opacity: 0.9;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Применяем стили
remote_css('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap')
local_css("style.css")

# Заголовок с логотипами
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("https://minzdrav.gov.ru/system/files/2021-07/logo.png", width=150)
with col2:
    st.markdown("<h1 style='text-align: center; color: #0057B7;'>Медицинский помощник</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #0057B7;'>Минздрав России | Госуслуги</h3>", unsafe_allow_html=True)
with col3:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Gosuslugi_logo.svg/1200px-Gosuslugi_logo.svg.png", width=150)

# Разделительная линия
st.markdown("<hr style='border: 1px solid #0057B7;'>", unsafe_allow_html=True)

# Основной контент
st.markdown("""
<div class="container">
    <div class="service-description">
        <h3>🏥 Медицинский помощник помогает ответить на вопросы:</h3>
        <ul>
            <li>Записи на прием к врачу</li>
            <li>Отмене записи на прием</li>
            <li>Необходимых документах для медицинских услуг</li>
            <li>Записи к узким специалистам</li>
            <li>Получении справок и результатов анализов</li>
            <li>Оформлении больничных листов</li>
            <li>Подготовке к медицинским процедурам</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Поле ввода с улучшенным дизайном
user_input = st.text_input(
    "🔍 Введите ваш медицинский вопрос:",
    placeholder="Например: Как оформить больничный лист?",
    label_visibility="collapsed"
)

if user_input:
    with st.spinner("🔍 Идет поиск информации в медицинской базе данных..."):
        answer, _ = search(user_input)

    # Отображение ответа с профессиональным оформлением
    st.markdown("""
    <div class="answer-container">
        <div class="answer-header">
            <h3>⚕️ Ответ медицинского специалиста:</h3>
            <p class="disclaimer">Информация предоставлена на основе данных Минздрава России и является справочной. Для точной диагностики и лечения обратитесь к врачу.</p>
        </div>
        <div class="answer-content">
    """, unsafe_allow_html=True)

    st.markdown(f"<p class='answer-text'>{answer}</p>", unsafe_allow_html=True)

    st.markdown("""
        </div>
        <div class="answer-footer">
            <p>💡 Полезно знать: Для получения официальной медицинской помощи обратитесь в поликлинику по месту жительства или через портал <a href="https://www.gosuslugi.ru/" target="_blank">Госуслуги</a>.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Футер с полезными ссылками
st.markdown("<hr style='border: 1px solid #0057B7;'>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <div class="footer-links">
        <h4>Полезные ресурсы:</h4>
        <ul>
            <li><a href="https://minzdrav.gov.ru/" target="_blank">Официальный сайт Минздрава России</a></li>
            <li><a href="https://www.gosuslugi.ru/" target="_blank">Портал Госуслуг - Запись к врачу</a></li>
            <li><a href="https://emias.info/" target="_blank">ЕМИАС - Единая медицинская информационно-аналитическая система</a></li>
        </ul>
    </div>
    <div class="footer-info">
        <p>⚠️ Важно: Данный сервис предоставляет справочную информацию и не заменяет консультацию врача.</p>
        <p>Для экстренной медицинской помощи звоните по телефону: <strong>103</strong> или <strong>112</strong></p>
    </div>
</div>
""", unsafe_allow_html=True)
