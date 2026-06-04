import os
import io
import requests
import pandas as pd

from dotenv import load_dotenv

load_dotenv()


# ==================================
# EXPORT CSV
# ==================================

def dataframe_to_csv(df):

    return df.to_csv(
        index=False
    ).encode("utf-8")


# ==================================
# EXPORT EXCEL
# ==================================

def dataframe_to_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False
        )

    return output.getvalue()


# ==================================
# EXPORT PDF VIA PDFSHIFT
# ==================================

def generate_pdf_via_api(
    title,
    html_content,
    footer_text=""
):

    api_key = os.getenv(
        "PDFSHIFT_API_KEY"
    )

    if not api_key:

        raise Exception(
            "PDFSHIFT_API_KEY tidak ditemukan pada file .env"
        )

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #1e293b;
                background: white;
            }}

            .header {{
                background: linear-gradient(
                    135deg,
                    #0f172a,
                    #1e3a8a
                );
                color: white;
                padding: 50px;
                text-align: center;
            }}

            .header h1 {{
                margin: 0;
                font-size: 30px;
            }}

            .header h2 {{
                margin-top: 15px;
                color: #67e8f9;
            }}

            .container {{
                padding: 35px;
            }}

            .section {{
                margin-bottom: 30px;
                border-left: 5px solid #06b6d4;
                padding-left: 15px;
            }}

            .section h3 {{
                color: #0f172a;
            }}

            .card {{
                background: #f8fafc;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
                border: 1px solid #e2e8f0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}

            th {{
                background: #0f172a;
                color: white;
                padding: 10px;
            }}

            td {{
                padding: 10px;
                border: 1px solid #d1d5db;
            }}

            .footer {{
                margin-top: 50px;
                padding-top: 15px;
                border-top: 2px solid #e5e7eb;
                text-align: center;
                color: #64748b;
                font-size: 12px;
            }}

        </style>

    </head>

    <body>

        <div class="header">

            <h1>
            🦟 Sistem Prediksi Kasus DBD Indonesia
            </h1>

            <h2>
            {title}
            </h2>

        </div>

        <div class="container">

            {html_content}

            <div class="footer">

                {footer_text}

            </div>

        </div>

    </body>

    </html>
    """

    response = requests.post(
        "https://api.pdfshift.io/v3/convert/pdf",
        auth=("api", api_key),
        json={
            "source": html
        }
    )

    if response.status_code != 200:

        raise Exception(
            f"PDFShift Error: {response.text}"
        )

    return response.content