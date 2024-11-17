from flask import Flask, request, render_template, send_file, after_this_request
import pandas as pd
from io import BytesIO
from pdf_generator import generate_pdf
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ファイルがアップロードされているか確認
        if 'file' not in request.files:
            return 'ファイルがアップロードされていません。'

        file = request.files['file']

        if file.filename == '':
            return 'ファイルが選択されていません。'

        # CSVファイルを読み込む
        try:
            df = pd.read_csv(file, encoding='utf-8') 
            df.columns = df.columns.str.strip() 
            #print("データフレームの列名:", df.columns)
        except Exception as e:
            return f'CSVファイルの読み込みに失敗しました：{e}'

        # 各行のデータからPDFを生成
        pdf_files = []
        for index, row in df.iterrows():
            pdf_bytes = generate_pdf(row) 
            file_name = f"{row['名前']}_労働条件通知書.pdf"
            pdf_files.append((file_name, pdf_bytes))

        # 単一のPDFを返す場合
        if len(pdf_files) == 1:
            pdf_file = pdf_files[0]
            return send_file(
                BytesIO(pdf_file[1]),
                as_attachment=True,
                download_name=pdf_file[0],
                mimetype='application/pdf'
            )
        else:
            # 複数のPDFをZIPにまとめて返す場合
            import zipfile

            # 一時的なバイトストリームを作成
            zip_stream = BytesIO()
            with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_name, pdf_data in pdf_files:
                    zipf.writestr(file_name, pdf_data)

            zip_stream.seek(0)

            return send_file(
                zip_stream,
                as_attachment=True,
                download_name='労働条件通知書.zip',
                mimetype='application/zip'
            )

    # GETリクエスト時のフォーム表示
    return '''
    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>労働条件通知書生成</title>
            <style>
                body {
                    font-family: "ヒラギノ角ゴ ProN", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    width: 40%;
                    margin: 100px auto;
                    background-color: #ffffff;
                    padding: 40px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }
                h1 {
                    text-align: center;
                    color: #333333;
                    margin-bottom: 40px;
                }
                p {
                    font-size: 16px;
                    color: #555555;
                }
                input[type="file"] {
                    display: block;
                    margin: 20px 0;
                    font-size: 16px;
                }
                input[type="submit"] {
                    background-color: #007BFF;
                    color: #ffffff;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s ease;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                .message {
                    margin-top: 20px;
                    font-size: 16px;
                    color: #28a745;
                }
                @media screen and (max-width: 768px) {
                    .container {
                        width: 80%;
                        margin: 50px auto;
                    }
                }
            </style>
            <script>
                function showDownloadMessage() {
                    // メッセージを表示
                    document.getElementById('download-message').style.display = 'block';
                    // フォームの送信を許可
                    return true;
                }
            </script>
        </head>
        <body>
            <div class="container">
                <h1>労働条件通知書生成</h1>
                <form method="post" enctype="multipart/form-data" onsubmit="return showDownloadMessage();">
                    <p>CSVファイルをアップロードしてください。</p>
                    <input type="file" name="file" accept=".csv" required>
                    <input type="submit" value="アップロード">
                    <p id="download-message" class="message" style="display: none;">ダウンロードしています。</p>
                </form>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

