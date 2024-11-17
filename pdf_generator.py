from fpdf import FPDF, HTMLMixin
import os
from jinja2 import Environment, FileSystemLoader

class PDFGenerator(FPDF, HTMLMixin):
    pass

# テンプレートフォルダへのパスを設定
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Jinja2 の環境設定
env = Environment(loader=FileSystemLoader(template_dir))

def render_template(template_name, context=None):
    template = env.get_template(template_name)
    if context:
        return template.render(context)
    else:
        return template.render()

def generate_pdf(row):
    pdf = PDFGenerator()
    pdf.add_page()

    # 日本語フォントの設定
    font_path = os.path.join(os.path.dirname(__file__), 'ipaexg.ttf')

    # フォントの登録
    pdf.add_font('IPAexGothic', '', font_path, uni=True)
    pdf.add_font('IPAexGothic', 'B', font_path, uni=True)
    pdf.set_font('IPAexGothic', '', 12)

    # 固定情報の設定
    employer_info_data = {
        'employer': "株式会社REIGETSU",
        'employer_address': "東京都豊島区西池袋2-39-11　英興ビル2階"
    }

    labor_conditions_data = {
        'contract_renewal': "無し",
        'trial_period': "無し",
        'contract_duration': "就労日当日に限る",
        'overtime': "有り",
        'pay_day': "月末締め翌月末払い。但し、前払い申請があった場合は都度支給日より前に支払う",
        'payment_method': "労働者指定の銀行口座への振込にて全額支払う",
        'raise_bonus_retirement': "無し",
        'holidays': "無し",
        'social_insurance': "労災保険の適用あり。雇用保険、健康保険及び厚生年金の適用無し"
    }

    # PDFタイトル
    pdf.cell(0, 10, txt="労働条件通知書", ln=True, align='C')
    pdf.ln(10)

    # 使用者情報のテーブル
    employer_html = render_template('employer_info.html', employer_info_data)
    pdf.write_html(employer_html)
    pdf.ln(5)

    # 労働者情報のテーブル
    worker_data = row.to_dict()
    worker_html = render_template('worker_info.html', worker_data)
    pdf.write_html(worker_html)
    pdf.ln(5)

    # 労働条件のテーブル
    labor_html = render_template('labor_conditions.html', labor_conditions_data)
    pdf.write_html(labor_html)
    pdf.ln(5)

    # 解雇の事由のテーブル
    dismissal_html = render_template('dismissal_reasons.html')
    pdf.write_html(dismissal_html)

    return pdf.output(dest='S')
