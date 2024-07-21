from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import pytz
import pandas as pd
from reportlab.pdfgen import canvas

current_file_path = Path(__file__).resolve()

class MyPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo_path = current_file_path.parent / "pdf" / "logo.png"
        self.logo_width = 1108 / 10
        self.logo_height = 1191.5 / 10

    def build(self, content):
        # Создаем PDF с использованием Canvas
        c = canvas.Canvas(self.filename, pagesize=self.pagesize)
        width, height = self.pagesize

        # Добавляем логотип
        center_x = width / 2
        center_y = height - self.logo_height - 0.5 * inch

        image_x = center_x - (self.logo_width / 2)
        image_y = center_y
        c.drawImage(self.logo_path, image_x, image_y, width=self.logo_width,
                    height=self.logo_height, preserveAspectRatio=True)

        # Позиция для добавления элементов ниже логотипа
        y = height - self.logo_height - 1 * inch

        # Используем стандартное добавление элементов
        for elem in content:
            if isinstance(elem, Paragraph):
                elem_width, elem_height = elem.wrap(width, height)
                # Центрирование текста на странице
                elem_x = (width - elem_width) / 2
                elem_y = y - elem_height
                elem.drawOn(c, elem_x, elem_y)
                y -= elem_height + 0.25 * inch  # Отступ после элемента
            else:
                elem_width, elem_height = elem.wrap(width, y)
                elem.drawOn(c, 0.5 * inch, y - elem_height)
                y -= elem_height + 0.5 * inch
            # elem.wrapOn(c, width, y)
            # elem.drawOn(c, 0.5 * inch, y - elem.wrapOn(c, width, y)[1])
            # y -= elem.wrapOn(c, width, y)[1] + 0.5 * inch

        # Завершение страницы
        c.showPage()
        c.save()

# add async
async def pdf_generator(data: dict, btc_exchange_rate: float,
                        user_id: int, algo_name: str, hashrate: float, hash_type: str):
    pdfmetrics.registerFont(TTFont('DejaVuSans', current_file_path.parent / "pdf" / "DejaVuSans.ttf"))

    dataset = {
        'Name': [],
        'Est. Rewards 24h': [],
        'Rev. BTC': [],
        'Profit Day': [],
        'Profit Week': [],
        'Profit Month': []
    }

    for k, v in data['coins'].items():
        if v['tag'] != "NICEHASH":
            dataset['Name'].append(f"{k}({v['tag']})")
        else:
            dataset['Name'].append(k)
        dataset['Est. Rewards 24h'].append(v['estimated_rewards'])
        btc_revenue = float(v['btc_revenue'])
        dataset['Rev. BTC'].append(f"{btc_revenue:.6f}")
        btc_revenue24 = float(v['btc_revenue24'])
        profit_day = btc_revenue24 * btc_exchange_rate
        dataset['Profit Day'].append("$" + str(round(profit_day, 2)))
        dataset['Profit Week'].append("$" + str(round(profit_day * 7, 2)))
        dataset['Profit Month'].append("$" + str(round(profit_day * 30, 2)))


    df = pd.DataFrame(dataset)

    # Преобразование данных в список для таблицы
    table_data = [df.columns.tolist()] + df.values.tolist()

    # Создание таблицы
    table = Table(table_data)

    # Стилизация таблицы
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ])
    table.setStyle(style)

    # Получение текущей даты и времени в Московском времени
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    formatted_datetime = now.strftime('%Y-%m-%d %H:%M:%S')

    # Создание стилей
    styles = getSampleStyleSheet()

    # Стиль для заголовка
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=16,  # Размер шрифта для заголовка
        alignment=1,  # Выравнивание по центру
        spaceAfter=6  # Отступ после заголовка
    )

    # Стиль для ссылки
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=14,
        textColor=colors.blue,
        underline=True,
        alignment=1,  # Выравнивание по центру
        spaceBefore=6
    )

    # Стиль для даты/времени
    date_time_style = ParagraphStyle(
        'DateTimeStyle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        alignment=1,  # Выравнивание по центру
    )

    # Создание заголовка, ссылки и текста
    header = Paragraph(f'{algo_name}: {hashrate} {hash_type}', header_style)
    link = Paragraph(
        '<a href="https://crypto-king.pro">Продажа и размещение майнинг - оборудования crypto-king.pro</a>',
        link_style)
    date_time = Paragraph(f'Отчет сгенерирован {formatted_datetime}', date_time_style)

    # Создание и сборка документа
    elements = [header, table, date_time, link]
    pdf_file = current_file_path.parent / f"{algo_name}-{user_id}.pdf"
    # Замените размеры страницы на желаемые
    page_width = 8.5 * inch
    if len(dataset['Name']) == 4:
        page_height = 6 * inch
    elif len(dataset['Name']) == 6:
        page_height = 6.5 * inch
    elif len(dataset['Name']) == 10:
        page_height = 7.5 * inch

    pdf = MyPDF(str(pdf_file), pagesize=(page_width, page_height))
    pdf.build(elements)

    return pdf_file

