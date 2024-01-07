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

3. **Tạo Môi Trường Ảo (Recommend):**

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
   source venv/Scripts/activate
   ```

5. **Cài đặt thư viện:**

   ```bash
   pip install -r requirements.txt
   ```

6. **Tải và cài đặt phần mềm wkhtmltopdf và thêm vào PATH của máy:**

   **Chú ý** Chỉ thực hiện bước này nếu có sử dụng chức năng **Xuất PDF**

   ```bash
   https://wkhtmltopdf.org/downloads.html
   ```

7. **Tạo CSDL MYSQL:**

   **Chú ý:** Có thể dùng MySQL Workbench

   ```bash
   CREATE DATABASE clinic CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```

8. **Tạo file .env và thêm vào các biến môi trường tương ứng với các biến trong file config.py**

9. **Tạo các bảng cho CSDL:**

   ```bash
   flask db migrate
   ```

   ```bash
   flask db upgrade
   ```

10. **Chạy ứng dụng:**

      ```bash
      python manage.py
      ```

  
