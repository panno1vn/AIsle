# MÔ HÌNH HỌC MÁY DỰ ĐOÁN KHẢ NĂNG THÀNH CÔNG CỦA TRÒ CHƠI ĐIỆN TỬ

## 1. MỤC TIÊU BAN ĐẦU CỦA DỰ ÁN

Trong ngành công nghiệp trò chơi điện tử, việc phát triển và phát hành một tựa game đòi hỏi nguồn vốn đầu tư khổng lồ cũng như nguồn lực nhân sự rất lớn. Mục tiêu cốt lõi của dự án này là xây dựng một hệ thống mô hình Học máy (Machine Learning) có khả năng phân tích các thông tin ban đầu của một trò chơi trước khi ra mắt bao gồm Hệ máy, Thể loại, Nhà xuất bản và Năm phát hành, từ đó dự đoán chính xác tựa game đó có khả năng trở thành một sản phẩm Bom Tấn đạt mốc doanh số toàn cầu từ 1.0 triệu bản trở lên hay không. 

Thông qua dự án này, hệ thống sẽ cung cấp căn cứ định lượng giúp các nhà đầu tư, nhà phát hành game và các studio tối ưu hóa quá trình lựa chọn dự án, giảm thiểu rủi ro tài chính và phân bổ ngân sách marketing một cách hiệu quả nhất.

---

## 2. GIAI ĐOẠN 1: THỰC HIỆN MÔ HÌNH BASELINE (MÔ HÌNH NỀN TẢNG)

Để tạo ra một mốc đo lường chuẩn mực ban đầu, dự án tiến hành xây dựng mô hình Logistic Regression cơ bản thông qua các bước xử lý code cụ thể như sau.

### Các bước xử lý trong mô hình Baseline:

Bước đầu tiên là Tải dữ liệu và Loại bỏ rò rỉ thông tin. Dữ liệu từ file vgsales_cleaned.csv gồm 16,598 dòng được nạp vào hệ thống. Nhằm đảm bảo mô hình có thể dự đoán cho một tựa game chưa phát hành, dự án tiến hành loại bỏ toàn bộ các cột thông tin quá trình bao gồm cột xếp hạng Rank và các cột doanh số chi tiết theo từng khu vực như NA_Sales, EU_Sales, JP_Sales và Other_Sales. Việc giữ lại các cột này sẽ gây ra hiện tượng rò rỉ dữ liệu làm mô hình bị ảo tưởng sức mạnh.

Bước thứ hai là Tiền xử lý thuộc tính và Gom nhóm dữ liệu. Tập dữ liệu chứa hơn 500 Nhà xuất bản khác nhau, trong đó có rất nhiều nhà xuất bản nhỏ chỉ phát hành từ 1 đến 2 game. Dự án tiến hành lọc và giữ nguyên tên đối với các Nhà xuất bản lớn có từ 20 tựa game trở lên, toàn bộ các nhà xuất bản nhỏ còn lại được gom chung thành một nhóm có tên là Other. Điều này giúp giảm bớt số lượng chiều dữ liệu và tránh tình trạng quá nhiễu.

Bước thứ ba là Tạo biến mục tiêu và Mã hóa One-Hot. Dự án tạo biến mục tiêu nhị phân Is_Hit nhận giá trị 1 nếu doanh số toàn cầu Global_Sales đạt từ 1.0 triệu bản trở lên và nhận giá trị 0 nếu dưới 1.0 triệu bản. Các thuộc tính định tính bao gồm Platform, Genre và Publisher_Clean được mã hóa sang dạng số nhị phân bằng phương thức pd.get_dummies với tham số drop_first=True để tránh hiện tượng đa cộng tuyến.

Bước thứ tư là Phân chia tập dữ liệu. Tập dữ liệu sau khi mã hóa được phân chia thành tập Huấn luyện chiếm 80% và tập Kiểm thử chiếm 20% thông qua hàm train_test_split. Tham số stratify=y được thiết lập nhằm đảm bảo tỷ lệ phân bố giữa game Hit và game không Hit trên hai tập là hoàn toàn đồng đều.

Bước thứ năm là Huấn luyện mô hình Logistic Regression cơ bản. Dự án khởi tạo mô hình LogisticRegression với số vòng lặp tối đa max_iter=1000 và sử dụng các tham số mặc định, trong đó trọng số phạt các lớp class_weight được giữ nguyên là None. Mô hình sau đó được fit trên tập Train và tiến hành dự đoán trên tập Test.

### Kết luận thu được từ mô hình Baseline:

Kết quả thực thi của mô hình Baseline trên tập kiểm thử cho ra chỉ số Độ chính xác tổng thể (Accuracy) đạt 72.59%. Tuy nhiên, khi đi sâu vào các chỉ số phân loại chi tiết, chỉ số Độ gợi nhớ (Recall) đối với các tựa game Hit chỉ đạt mức 10.34%, chỉ số Độ xác thực (Precision) đạt 27.34%. Trong tổng số 416 game bom tấn thực tế có trong tập kiểm thử, mô hình Baseline chỉ phát hiện được vỏn vẹn 43 game và bỏ sót tới 373 game.

### Nhìn ra Vấn đề 1 từ mô hình Baseline:

Từ kết luận trên, vấn đề nghiêm trọng đầu tiên được phát hiện là Hiện tượng mất cân bằng lớp dữ liệu (Class Imbalance). Số lượng game Hit chỉ chiếm khoảng 12.5% tổng số dữ liệu. Do mô hình Baseline được huấn luyện với trọng số bằng nhau cho mọi mẫu, thuật toán đã lười biếng ưu tiên học theo số đông và dự đoán hầu hết các game là không Hit để đạt được Accuracy cao. Điều này khiến mô hình Baseline hoàn toàn thất bại về mặt ứng dụng thực tế, vì nhiệm vụ quan trọng nhất là tìm ra game bom tấn thì mô hình lại bỏ sót đến gần 90%.

---

## 3. GIAI ĐOẠN 2: NÂNG CẤP VỚI CƠ CHẾ BALANCED (CLASS_WEIGHT='BALANCED')

Để khắc phục triệt để Vấn đề 1 mà mô hình Baseline gặp phải, dự án tiến hành bước nâng cấp thứ hai bằng cách can thiệp vào cơ chế phạt của thuật toán.

### Thực hiện nâng cấp cơ chế Balanced:

Dự án tái khởi tạo mô hình Logistic Regression nhưng bổ sung thêm tham số class_weight='balanced'. Cơ chế này tự động tính toán trọng số phạt nghịch đảo với tần suất xuất hiện của các lớp trong tập huấn luyện. Vì lớp game Hit xuất hiện rất ít, mô hình sẽ gán cho các lỗi đoán sai game Hit một mức phạt cao gấp nhiều lần so me với lỗi đoán sai game thường. Điều này ép thuật toán phải tập trung học kỹ các đặc trưng của những tựa game thành công.

### Kết luận thu được từ mô hình Balanced:

Sau khi áp dụng cơ chế Balanced, chỉ số Độ chính xác tổng thể (Accuracy) vẫn duy trì ở mức 72.59%, nhưng chỉ số Độ gợi nhớ (Recall) cho lớp game Hit đã có sự bứt phá kinh ngạc khi nhảy vọt từ 10.34% lên mức 71.63%. Mô hình lúc này đã bắt trúng 298 game bom tấn trong tổng số 416 game, tăng gấp 7 lần khả năng tìm kiếm so với mô hình Baseline ban đầu.

### Nhìn ra Vấn đề 2 từ mô hình Balanced:

Mặc dù chỉ số Recall 71.63% ở bước này đã là một cải tiến rất lớn, nhưng khi phân tích dưới góc độ chiến lược kinh doanh thực tế, một vấn đề thứ hai lại phát sinh. Mô hình Balanced mặc định sử dụng ngưỡng phân loại cố định là 0.5. 

Đối với các Nhà phát hành game đang trong giai đoạn săn tìm ý tưởng (Scouting), việc mô hình vẫn còn bỏ sót 118 game bom tấn (tương đương 28.37%) vẫn là một sự lãng phí cơ hội rất lớn. 

Ngược lại, đối với các Studio game lớn chuẩn bị rót 100 triệu USD vào một dự án duy nhất, chỉ số Precision 27.34% ở ngưỡng 0.5 khiến mô hình đưa ra tới 792 báo động nhầm (False Positives), tạo ra rủi ro tài chính cực kỳ cao nếu đầu tư nhầm vào dự án thất bại. Ngưỡng cố định 0.5 rõ ràng chưa thể đáp ứng linh hoạt cho từng nhu cầu kinh doanh khác nhau.

---

## 4. GIAI ĐOẠN 3: TỐI ƯU HÓA BẰNG KỸ THUẬT THRESHOLD TUNING (TINH CHỈNH NGƯỠNG)

Để giải quyết triệt để Vấn đề 2 về sự gò bó của ngưỡng cố định, dự án tiến hành bước tối ưu hóa thứ ba bằng cách can thiệp vào xác suất đầu ra của mô hình.

### Thực hiện kỹ thuật Threshold Tuning:

Thay vì dùng hàm predict mặc định với ngưỡng 0.5, dự án trích xuất xác suất dự báo dự án thành công thông qua hàm predict_proba và cho chạy thử nghiệm quét qua các dải ngưỡng từ 0.1 đến 0.95. Việc thay đổi ngưỡng này giúp thay đổi linh hoạt ranh giới quyết định mà không cần phải huấn luyện lại mô hình từ đầu.

Kịch bản 1 dành cho Mục tiêu Săn tìm dự án (Hạ ngưỡng xuống 0.3): 
Khi hạ ngưỡng xuống 0.3, mô hình trở nên rộng lượng hơn trong việc dán nhãn game Hit. Kết quả thu được là chỉ số Recall tăng vọt lên mức 85.10%, giúp bắt trúng 354 game bom tấn và giảm số game bị bỏ sót xuống chỉ còn 62 game. Đây là cấu hình hoàn hảo cho các nhà phát hành muốn bao phủ tối đa thị trường.

Kịch bản 2 dành cho Mục tiêu Đầu tư an toàn vốn lớn (Tăng ngưỡng lên 0.7 đến 0.95):
Khi nâng ngưỡng lên 0.7, chỉ số Precision tăng lên 38.05%. Nếu tiếp tục nâng ngưỡng lên mức 0.95, chỉ số Precision nhảy vọt lên 76.47%, đồng thời số ca báo động nhầm giảm từ 792 game xuống vỏn vẹn 8 game. Lúc này, mô hình trở nên cực kỳ khắt khe, chỉ những dự án nào có xác suất thành công trên 95% mới được bật đèn xanh, giúp bảo vệ an toàn tối đa cho nguồn vốn đầu tư khủng.

---

## 5. KẾT LUẬN CUỐI CÙNG VÀ ĐÁNH GIÁ TỔNG THỂ

Hành trình phát triển mô hình dự đoán thành công cho trò chơi điện tử qua 3 giai đoạn đã chứng minh một lộ trình cải tiến kỹ thuật hoàn chỉnh và chặt chẽ.

Bảng tổng hợp so sánh tiến trình hiệu năng qua các giai đoạn:

Giai đoạn Baseline (Mặc định class_weight=None, Ngưỡng 0.5): 
Accuracy đạt 72.59%, Recall đạt 10.34%, Precision đạt 27.34%, Bắt đúng 43 game Hit, Bỏ sót 373 game. Kết luận: Thất bại do mất cân bằng lớp dữ liệu.

Giai đoạn Balanced (Thêm class_weight='balanced', Ngưỡng 0.5): 
Accuracy đạt 72.59%, Recall đạt 71.63%, Precision đạt 27.34%, Bắt đúng 298 game Hit, Bỏ sót 118 game. Kết luận: Giải quyết thành công bài toán imbalanced data, nâng hiệu quả tìm kiếm lên gấp 7 lần.

Giai đoạn Threshold Tuned (Hạ ngưỡng xuống 0.3): 
Accuracy đạt 64.90%, Recall đạt 85.10%, Precision đạt 24.70%, Bắt đúng 354 game Hit, Bỏ sót 62 game. Kết luận: Tối ưu hóa tối đa cho mục tiêu tìm kiếm cơ hội đầu tư, bắt trọn 85.1% game bom tấn.

Giai đoạn Threshold Tuned (Tăng ngưỡng lên 0.95): 
Accuracy đạt 88.01%, Recall đạt 6.25%, Precision đạt 76.47%, Báo động nhầm giảm về 8 game. Kết luận: Tối ưu hóa tối đa cho mục tiêu an toàn nguồn vốn khủng, đảm bảo độ chuẩn xác lên tới 76.47%.

Dự án đã khẳng định rằng không có một mô hình nào duy nhất đúng cho mọi trường hợp. Việc kết hợp giữa cơ chế Balanced để xử lý dữ liệu lệch lớp và kỹ thuật Threshold Tuning để linh hoạt điều chỉnh theo bài toán kinh doanh chính là chìa khóa mang lại giá trị thực tế cao nhất cho việc dự đoán thành công của các tựa game điện tử.
