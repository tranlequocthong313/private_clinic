import pdfkit
from flask import render_template


def make_pdf_from_html(filename, **kwargs):
    wkhtmltopdf_path = "/usr/local/bin/wkhtmltopdf"
    pdf = None
    try:
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        rendered = render_template(filename, **kwargs)
        pdf = pdfkit.from_string(
            rendered,
            False,
            configuration=config,
        )
    except Exception as e:
        print(e)

    return pdf
