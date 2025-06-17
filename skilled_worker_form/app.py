import os
import base64
import requests
from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Get the absolute path to the image
    image_path = os.path.abspath(os.path.join(
        app.static_folder, 'HJC_Letterhead_Ireland_FINAL.png'))

    # Convert to data URL
    with open(image_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
        img_url = f"data:image/png;base64,{img_data}"

    # Extract form data
    data = {key: request.form[key] for key in request.form}

    # Load template
    with open("template.html", "r") as file:
        template_html = file.read()

    # Replace image path and placeholders
    template_html = template_html.replace(
        '/static/HJC_Letterhead_Ireland_FINAL.png', img_url)
    for key, value in data.items():
        template_html = template_html.replace(f"{{{{{key}}}}}", value)

    # PDF.co API call
    response = requests.post(
        "https://api.pdf.co/v1/pdf/convert/from/html",
        headers={"x-api-key": PDFCO_API_KEY},
        json={
            "html": template_html,
            "name": f"{data['full_name'].replace(' ', '_')}_coversheet.pdf",
            "margins": "0px 0px 0px 0px",
            "paperSize": "A4",
            "orientation": "portrait",
            "printBackground": True,
            "renderingOptions": {
                "preferCssPageSize": True,
                "printBackground": True,
                "omitBackground": False
            }
        }
    )

    result = response.json()

    # Download and return the PDF
    if result.get("url"):
        pdf_url = result["url"]
        pdf_data = requests.get(pdf_url).content
        filename = f"{data['full_name'].replace(' ', '_')}_coversheet.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_data)
        return send_file(filename, as_attachment=True)

    return f"PDF generation failed: {result}", 500


if __name__ == '__main__':
    app.run(debug=True)
