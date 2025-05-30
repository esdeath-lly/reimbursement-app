from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import csv, os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制最大10MB

ALLOWED_EXTENSIONS = {'pdf'}
DATA_FILE = 'data/expenses.csv'

# 创建所需目录
os.makedirs('data', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 如果数据文件不存在，则写入表头
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            '发票日期', '发票号码', '发票内容', '发票金额',
            '具体使用人', '是否自费', '对方公司', '银行号',
            '银行账户', '附件PDF'
        ])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    file = request.files.get('pdf')
    filename = ''

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            data['date'], data['number'], data['content'], data['amount'],
            data['user'], data['selfPay'], data['company'],
            data['bankNumber'], data['bankAccount'], filename
        ])
    return jsonify({'message': '提交成功'})

@app.route('/data', methods=['GET'])
def get_data():
    records = []
    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return jsonify(records)

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_excel', methods=['GET'])
def download_excel():
    df = pd.read_csv(DATA_FILE)
    path = 'data/报销信息.xlsx'
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/download', methods=['GET'])
def download_csv():
    return send_file(DATA_FILE, as_attachment=True)

# ✅ 正确监听平台分配端口（如 Railway）
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
