import asyncio
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
        self.logo_width = 1208 / 5
        self.logo_height = 498 / 5

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
        # y = height - 1 * inch

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
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', current_file_path.parent / "pdf" / "DejaVuSans-Bold.ttf"))

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
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),  # Увеличенный нижний отступ
        ('TOPPADDING', (0, 1), (-1, -1), 5),  # Увеличенный верхний отступ
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),  # Увеличенный нижний отступ
        ('LEFTPADDING', (0, 1), (-1, -1), 5),  # Увеличенный левый отступ
        ('RIGHTPADDING', (0, 1), (-1, -1), 5),  # Увеличенный правый отступ
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Увеличенный размер шрифта заголовков
        ('FONTSIZE', (0, 1), (-1, -1), 12),  # Увеличенный размер шрифта для остальных
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
        fontSize=18,  # Размер шрифта для заголовка
        alignment=1,  # Выравнивание по центру
        spaceAfter=10 # Отступ после заголовка
    )

    # Стиль для ссылки
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=15,
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
        fontSize=14,
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
    elif len(dataset['Name']) == 9:
        page_height = 7.6 * inch
    elif len(dataset['Name']) == 10:
        page_height = 7.7 * inch
    else:
        page_height = 8 * inch

    pdf = MyPDF(str(pdf_file), pagesize=(page_width, page_height))
    pdf.build(elements)

    return pdf_file


# if __name__ == '__main__':
#     asyncio.run(pdf_generator(data={'coins': {
#         'Bitcoin': {'id': 1, 'tag': 'BTC', 'algorithm': 'SHA-256', 'block_time': '492.0', 'block_reward': 3.18012175,
#                     'block_reward24': 3.2018413522222224, 'last_block': 853457, 'difficulty': 82047728459932.7,
#                     'difficulty24': 82047728459932.75, 'nethash': 716244533427844308943, 'exchange_rate': 67624.0,
#                     'exchange_rate24': 67587.01605337078, 'exchange_rate_vol': 20953.12363, 'exchange_rate_curr': 'BTC',
#                     'market_cap': '$1,334,187,031,760', 'estimated_rewards': '0.00008',
#                     'estimated_rewards24': '0.00008', 'btc_revenue': '0.00007797', 'btc_revenue24': '0.0000785',
#                     'profitability': 100, 'profitability24': 100, 'lagging': False, 'timestamp': 1721687553},
#         'BitcoinCash': {'id': 193, 'tag': 'BCH', 'algorithm': 'SHA-256', 'block_time': '604.0', 'block_reward': 3.125,
#                         'block_reward24': 3.125, 'last_block': 855687, 'difficulty': 473931166313.47,
#                         'difficulty24': 468717082880.5683, 'nethash': 3370064337535579470, 'exchange_rate': 0.00574,
#                         'exchange_rate24': 0.005817454289732783, 'exchange_rate_vol': 1687.0599835677697,
#                         'exchange_rate_curr': 'BTC', 'market_cap': '$7,660,953,363', 'estimated_rewards': '0.01326',
#                         'estimated_rewards24': '0.01341', 'btc_revenue': '0.00007614', 'btc_revenue24': '0.00007698',
#                         'profitability': 98, 'profitability24': 98, 'lagging': False, 'timestamp': 1721688024},
#         'eCash': {'id': 370, 'tag': 'XEC', 'algorithm': 'SHA-256', 'block_time': '668.0',
#                   'block_reward': 1812499.9999999998, 'block_reward24': 1812499.9999999998, 'last_block': 854459,
#                   'difficulty': 24865905144.79423, 'difficulty24': 24739846582.787956, 'nethash': 159877618835822305,
#                   'exchange_rate': 5.217082692535194e-10, 'exchange_rate24': 5.28127313207065e-10,
#                   'exchange_rate_vol': 15.773013965145953, 'exchange_rate_curr': 'BTC', 'market_cap': '$696,162,764',
#                   'estimated_rewards': '146539.95942', 'estimated_rewards24': '147286.16497',
#                   'btc_revenue': '0.00007645', 'btc_revenue24': '0.00007684', 'profitability': 98,
#                   'profitability24': 98, 'lagging': False, 'timestamp': 1721686456},
#         'Nicehash-SHA-AB': {'id': 51, 'tag': 'NICEHASH', 'algorithm': 'SHA-256', 'block_time': 1, 'block_reward': 1,
#                             'block_reward24': 1, 'last_block': 0, 'difficulty': 1, 'difficulty24': 1,
#                             'nethash': 6774153408653852672, 'exchange_rate': 0.0007651634111824258,
#                             'exchange_rate24': 0.0007758971247452716, 'exchange_rate_vol': 5.264005841045715,
#                             'exchange_rate_curr': 'BTC', 'market_cap': '$0', 'estimated_rewards': '0.00007',
#                             'estimated_rewards24': '0.00008', 'btc_revenue': '0.00007499',
#                             'btc_revenue24': '0.00007604', 'profitability': 96, 'profitability24': 97, 'lagging': False,
#                             'timestamp': 1721688307},
#         'Peercoin': {'id': 52, 'tag': 'PPC', 'algorithm': 'SHA-256', 'block_time': '2700.0',
#                      'block_reward': 34.704701910874554, 'block_reward24': 35.229232474584634, 'last_block': 758978,
#                      'difficulty': 6890853226.5126, 'difficulty24': 6500133723.20755, 'nethash': 10961477499780625,
#                      'exchange_rate': 6.636697030640009e-06, 'exchange_rate24': 6.601874887774235e-06,
#                      'exchange_rate_vol': 0.002055577534603099, 'exchange_rate_curr': 'BTC',
#                      'market_cap': '$13,024,317', 'estimated_rewards': '10.0398', 'estimated_rewards24': '10.79829',
#                      'btc_revenue': '0.00006663', 'btc_revenue24': '0.00007166', 'profitability': 85,
#                      'profitability24': 91, 'lagging': False, 'timestamp': 1721687414},
#         'Nicehash-SHA-AB1': {'id': 51, 'tag': 'NICEHASH', 'algorithm': 'SHA-256', 'block_time': 1, 'block_reward': 1,
#                             'block_reward24': 1, 'last_block': 0, 'difficulty': 1, 'difficulty24': 1,
#                             'nethash': 6774153408653852672, 'exchange_rate': 0.0007651634111824258,
#                             'exchange_rate24': 0.0007758971247452716, 'exchange_rate_vol': 5.264005841045715,
#                             'exchange_rate_curr': 'BTC', 'market_cap': '$0', 'estimated_rewards': '0.00007',
#                             'estimated_rewards24': '0.00008', 'btc_revenue': '0.00007499',
#                             'btc_revenue24': '0.00007604', 'profitability': 96, 'profitability24': 97, 'lagging': False,
#                             'timestamp': 1721688307},
#         'Peercoin1': {'id': 52, 'tag': 'PPC', 'algorithm': 'SHA-256', 'block_time': '2700.0',
#                      'block_reward': 34.704701910874554, 'block_reward24': 35.229232474584634, 'last_block': 758978,
#                      'difficulty': 6890853226.5126, 'difficulty24': 6500133723.20755, 'nethash': 10961477499780625,
#                      'exchange_rate': 6.636697030640009e-06, 'exchange_rate24': 6.601874887774235e-06,
#                      'exchange_rate_vol': 0.002055577534603099, 'exchange_rate_curr': 'BTC',
#                      'market_cap': '$13,024,317', 'estimated_rewards': '10.0398', 'estimated_rewards24': '10.79829',
#                      'btc_revenue': '0.00006663', 'btc_revenue24': '0.00007166', 'profitability': 85,
#                      'profitability24': 91, 'lagging': False, 'timestamp': 1721687414},
#         'Nicehash-SHA-AB21': {'id': 51, 'tag': 'NICEHASH', 'algorithm': 'SHA-256', 'block_time': 1, 'block_reward': 1,
#                              'block_reward24': 1, 'last_block': 0, 'difficulty': 1, 'difficulty24': 1,
#                              'nethash': 6774153408653852672, 'exchange_rate': 0.0007651634111824258,
#                              'exchange_rate24': 0.0007758971247452716, 'exchange_rate_vol': 5.264005841045715,
#                              'exchange_rate_curr': 'BTC', 'market_cap': '$0', 'estimated_rewards': '0.00007',
#                              'estimated_rewards24': '0.00008', 'btc_revenue': '0.00007499',
#                              'btc_revenue24': '0.00007604', 'profitability': 96, 'profitability24': 97,
#                              'lagging': False,
#                              'timestamp': 1721688307},
#         'Peercoin12': {'id': 52, 'tag': 'PPC', 'algorithm': 'SHA-256', 'block_time': '2700.0',
#                       'block_reward': 34.704701910874554, 'block_reward24': 35.229232474584634, 'last_block': 758978,
#                       'difficulty': 6890853226.5126, 'difficulty24': 6500133723.20755, 'nethash': 10961477499780625,
#                       'exchange_rate': 6.636697030640009e-06, 'exchange_rate24': 6.601874887774235e-06,
#                       'exchange_rate_vol': 0.002055577534603099, 'exchange_rate_curr': 'BTC',
#                       'market_cap': '$13,024,317', 'estimated_rewards': '10.0398', 'estimated_rewards24': '10.79829',
#                       'btc_revenue': '0.00006663', 'btc_revenue24': '0.00007166', 'profitability': 85,
#                       'profitability24': 91, 'lagging': False, 'timestamp': 1721687414},
#         'DGB-SHA': {'id': 113, 'tag': 'DGB', 'algorithm': 'SHA-256', 'block_time': '75.0',
#                     'block_reward': 335.6810668878335, 'block_reward24': 335.6810668878443, 'last_block': 19674456,
#                     'difficulty': 1112549928.628753, 'difficulty24': 1140230180.7925751, 'nethash': 63711540781701706,
#                     'exchange_rate': 1.2e-07, 'exchange_rate24': 1.2000000000000105e-07,
#                     'exchange_rate_vol': 0.31425999, 'exchange_rate_curr': 'BTC', 'market_cap': '$139,129,637',
#                     'estimated_rewards': '606.01042', 'estimated_rewards24': '591.3214', 'btc_revenue': '0.00007272',
#                     'btc_revenue24': '0.00007096', 'profitability': 93, 'profitability24': 90, 'lagging': False,
#                     'timestamp': 1721688307}}},
#                               btc_exchange_rate=67624.0,
#                               user_id=2049012121,
#                               algo_name='SHA-256',
#                               hashrate='100',
#                               hash_type='Th/s'
#                               ))
