# Private Clinic Management - Quản lý phòng mạch tư (Flask)

**Private Clinic Management** là một ứng dụng web được phát triển bằng Flask, giúp quản lý thông tin bệnh nhân, lịch hẹn, và các hoạt động hàng ngày của phòng mạch tư. Ứng dụng này cung cấp các tính năng cần thiết để quản lý hiệu quả hoạt động của phòng khám, bao gồm quản lý bệnh nhân, lịch hẹn, và hồ sơ y tế.

## Tính năng chính

- **Quản lý bệnh nhân**: Thêm, sửa, xóa, và xem thông tin bệnh nhân.
- **Quản lý lịch hẹn**: Tạo, cập nhật, và xóa lịch hẹn khám bệnh.
- **Quản lý hồ sơ y tế**: Lưu trữ và quản lý hồ sơ y tế của bệnh nhân.
- **Quản lý nhân viên**: Thêm, sửa, xóa, và xem thông tin nhân viên phòng khám.
- **Báo cáo và thống kê**: Xem báo cáo thống kê về hoạt động của phòng khám.
- **Xác thực và phân quyền**: Xác thực người dùng và phân quyền (admin, bác sĩ, nhân viên).

## Công nghệ sử dụng

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite (hoặc PostgreSQL/MySQL tùy cấu hình)
- **Authentication**: Flask-Login (hoặc JWT nếu sử dụng API)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap (hoặc bất kỳ framework frontend nào bạn sử dụng)
- **API**: RESTful API (nếu có)
- **Deployment**: Docker, Nginx, Gunicorn (tùy chọn)

## Cài đặt và chạy dự án

### Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)

### Các bước cài đặt

1. **Clone dự án**:
   ```bash
   git clone https://github.com/tranlequocthong313/private_clinic.git
   cd private_clinic
   ```

2. **Tạo và kích hoạt môi trường ảo (virtual environment)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```

3. **Cài đặt các dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình cơ sở dữ liệu**:
   - Cấu hình kết nối cơ sở dữ liệu trong file `config.py`:
     ```python
     SQLALCHEMY_DATABASE_URI = 'sqlite:///clinic.db'  # Sử dụng SQLite
     # Hoặc sử dụng PostgreSQL/MySQL
     # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/clinic'
     ```

5. **Chạy migrations**:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Chạy server**:
   ```bash
   flask run
   ```

7. **Truy cập ứng dụng**:
   - Mở trình duyệt và truy cập vào địa chỉ: `http://localhost:5000`

### Cấu hình môi trường

Tạo file `.env` trong thư mục gốc của dự án và thêm các biến môi trường cần thiết:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///clinic.db
```

## Cấu trúc thư mục

```
private_clinic/
├── app/
│   ├── __init__.py          # File khởi tạo ứng dụng Flask
│   ├── models.py            # Các model (SQLAlchemy)
│   ├── routes.py            # Các route (API endpoints)
│   ├── templates/           # Các file template HTML
│   ├── static/              # CSS, JS, hình ảnh
│   ├── forms.py             # Các form (Flask-WTF)
│   ├── auth.py              # Xác thực người dùng (Flask-Login)
│   └── utils.py             # Các tiện ích (helper functions)
├── migrations/              # Thư mục chứa các file migration
├── config.py                # Cấu hình ứng dụng
├── requirements.txt         # Danh sách các dependencies
├── .env                     # File cấu hình môi trường
└── README.md                # Tài liệu hướng dẫn
```

## Các trang chính

- **Trang chủ**: Hiển thị thông tin tổng quan về phòng khám.
- **Quản lý bệnh nhân**: Thêm, sửa, xóa, và xem thông tin bệnh nhân.
- **Quản lý lịch hẹn**: Tạo, cập nhật, và xóa lịch hẹn khám bệnh.
- **Quản lý hồ sơ y tế**: Lưu trữ và quản lý hồ sơ y tế của bệnh nhân.
- **Quản lý nhân viên**: Thêm, sửa, xóa, và xem thông tin nhân viên phòng khám.
- **Báo cáo và thống kê**: Xem báo cáo thống kê về hoạt động của phòng khám.

## API Endpoints (nếu có)

Dưới đây là một số API endpoints chính (nếu sử dụng RESTful API):

- **Bệnh nhân (Patients)**:
  - `GET /api/patients` - Lấy danh sách bệnh nhân.
  - `POST /api/patients` - Thêm bệnh nhân mới.
  - `GET /api/patients/{id}` - Lấy thông tin chi tiết của một bệnh nhân.
  - `PUT /api/patients/{id}` - Cập nhật thông tin bệnh nhân.
  - `DELETE /api/patients/{id}` - Xóa bệnh nhân.

- **Lịch hẹn (Appointments)**:
  - `GET /api/appointments` - Lấy danh sách lịch hẹn.
  - `POST /api/appointments` - Tạo lịch hẹn mới.
  - `GET /api/appointments/{id}` - Lấy thông tin chi tiết của một lịch hẹn.
  - `PUT /api/appointments/{id}` - Cập nhật lịch hẹn.
  - `DELETE /api/appointments/{id}` - Xóa lịch hẹn.

- **Hồ sơ y tế (Medical Records)**:
  - `GET /api/records` - Lấy danh sách hồ sơ y tế.
  - `POST /api/records` - Thêm hồ sơ y tế mới.
  - `GET /api/records/{id}` - Lấy thông tin chi tiết của một hồ sơ y tế.
  - `PUT /api/records/{id}` - Cập nhật hồ sơ y tế.
  - `DELETE /api/records/{id}` - Xóa hồ sơ y tế.

## Đóng góp

Nếu bạn muốn đóng góp vào dự án, vui lòng làm theo các bước sau:

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/YourFeatureName`)
3. Commit các thay đổi (`git commit -m 'Add some feature'`)
4. Push lên branch (`git push origin feature/YourFeatureName`)
5. Mở một Pull Request

## Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ:

- **Tên**: Trần Lê Quốc Thông
- **Email**: tranlequocthong313@gmail.com
- **GitHub**: [tranlequocthong313](https://github.com/tranlequocthong313)
