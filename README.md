# Private Clinic

Ngày nay, với sự phát triển không ngừng của công nghệ thông tin, con người dễ dàng tiếp cận được những sản phẩm từ công nghệ mang lại trong cuộc sống. Việc tạo ra một sản phẩm phần mềm mang lại hiệu quả cao cho người sử dụng thì những kỹ năng phân tích thiết kế hệ thống thông tin và quy trình xử lý của phần mềm là hết sức cần thiết. Đứng trước nhu cầu áp dụng công nghệ thông tin vào việc quản lý và vận hành hệ thống ngày càng cao của các doanh nghiệp, việc xây dựng hoàn thiện một hệ thống phần mềm quản lý là việc không thể thiếu, là bước nền của mọi doanh nghiệp trong việc tồn tại và phát triển. Trong đó lĩnh vực Y tế về các phòng mạch tư ngày càng mở rộng về số lượng lẫn quy mô. Chính vì thế, việc công tác quản lý các thông tin liên quan đến bệnh nhân cũng như việc khám chữa bệnh của bác sĩ là rất cần thiết. Đó cũng là lý do nhóm chúng em làm đề tài “Quản Lý Phòng Mạch Tư” để xây dựng phần mềm hệ thống hỗ trợ cho người dùng có thể quản lý phòng mạch một cách hiệu quả và đạt độ chính xác nhất.

## Hướng dẫn Chạy Dự Án Flask

1. **Clone Repository:**

   ```bash
   git clone https://github.com/tranlequocthong313/private_clinic.git
   ```

2. **Di chuyển vào thư mục Dự án:**

   ```bash
   cd private_clinic
   ```

3. **Tạo Môi Trường Ảo (Optional, nhưng được khuyến khích):**

   ```bash
   python -m venv venv
   ```

4. **Truy Cập vào Môi Trường Ảo:**

   - **Windows:**

     ```bash
     .\venv\Scripts\activate
     ```

   - **Bash:**
     ```bash
     source venv/bin/activate
     ```

5. **Cài đặt thư viện:**

   ```bash
   pip install -r requirements.txt
   ```

6. **Tạo CSDL MYSQL:**

   **_NOTE:_** Có thể dùng MySQL Workbench

   ```bash
   CREATE DATABASE db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```

7. **Tạo file .env và thêm vào các biến môi trường:**

   ```
   SECRET_KEY=secrect_key_to_encrypt_data_in_session
   DATABASE_HOST=db_host
   DATABASE_NAME=db_name
   DATABASE_PORT=db_port
   DATABASE_USERNAME=db_username
   DATABASE_PASSWORD=db_password
   ```

8. **Tạo các bảng cho CSDL:**

   ```bash
   flask db init && flask db migrate && flask db upgrade
   ```

9. **Chạy ứng dụng:**

   - **Windows:**

   ```bash
   set FLASK_APP=app && flask run --debug
   ```

   - **Bash:**

   ```bash
   export FLASK_APP='app' && flask run --debug
   ```
