import cv2
import numpy as np

# 1. Đọc 2 bức ảnh (Chuyển về ảnh xám)
img1 = cv2.imread('70_50.jpg', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('80_50.jpg', cv2.IMREAD_GRAYSCALE)

if img1 is None or img2 is None:
    print("❌ Lỗi: Không tìm thấy ảnh rồi ông ơi! Kiểm tra lại tên/đường dẫn nha.")
    exit()

print("📸 Đang quét ảnh và tính toán, đợi tôi tí...")

# 2. Cấu hình SIFT lấy TỐI ĐA điểm đặc trưng (Hạ threshold để lấy nhiều điểm hơn)
sift = cv2.SIFT_create(
    nfeatures=0,            # 0 = Lấy tối đa không giới hạn
    contrastThreshold=0.02, # Hạ thấp xuống để nhận diện cả các điểm mờ/nhỏ
    edgeThreshold=15        # Tăng lên để giữ lại nhiều cạnh hơn
)

kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# 3. Khớp các điểm bằng FLANN Matcher
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)

# 4. Sàng lọc sơ bộ bằng Lowe's ratio test (Thả xích lên 0.75 để gom nhiều ứng viên)
good_matches = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good_matches.append(m)

# 5. DÙNG RANSAC ĐỂ LỌC ĐIỂM NHIỄU (Bí kíp chính xác đây nè!)
final_matches = []
if len(good_matches) > 4:
    # Lấy tọa độ các điểm khớp sơ bộ
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Tìm ma trận Homography kết hợp lọc RANSAC (Ngưỡng sai số 5 pixel)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()
    
    # Chỉ giữ lại các điểm khớp HOÀN TOÀN ĐÚNG về mặt hình học (Inliers)
    for i in range(len(good_matches)):
        if matchesMask[i] == 1:
            final_matches.append(good_matches[i])
else:
    print("⚠️ Ít điểm trùng khớp quá, không đủ điều kiện chạy RANSAC.")
    final_matches = good_matches

# 6. TÍNH TOÁN VÀ XUẤT DỮ LIỆU RA FILE TXT
output_file = 'x78Dich10_y50.txt'
all_displacements = []

with open(output_file, 'w', encoding='utf-8') as f:
    # Ghi tiêu đề cột cho đẹp và rõ ràng
    f.write("DANH SÁCH TOẠ ĐỘ VÀ ĐỘ DỊCH CHUYỂN PIXEL GIỮA 2 ẢNH\n")
    f.write("=" * 90 + "\n")
    f.write(f"{'STT':<6}{'X1 (Ảnh 1)':<15}{'Y1 (Ảnh 1)':<15}{'X2 (Ảnh 2)':<15}{'Y2 (Ảnh 2)':<15}{'Dịch chuyển (Pixel)':<20}\n")
    f.write("-" * 90 + "\n")
    
    for idx, match in enumerate(final_matches):
        pt1 = kp1[match.queryIdx].pt  # Tọa độ ảnh 1 (x1, y1)
        pt2 = kp2[match.trainIdx].pt  # Tọa độ ảnh 2 (x2, y2)
        
        # Tính khoảng cách dịch chuyển Euclidean chuẩn chỉnh
        displacement = np.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
        all_displacements.append(displacement)
        
        # Ghi dữ liệu từng dòng vào file text
        f.write(f"{idx+1:<6}{pt1[0]:<15.2f}{pt1[1]:<15.2f}{pt2[0]:<15.2f}{pt2[1]:<15.2f}{displacement:<20.2f}\n")
    
    # Tính toán thông số tổng kết
    total_points = len(final_matches)
    avg_displacement = np.mean(all_displacements) if total_points > 0 else 0
    
    f.write("=" * 90 + "\n")
    f.write("📊 TỔNG KẾT THÔNG SỐ THỰC TẾ:\n")
    f.write(f"- Tổng số điểm khớp chính xác thu được: {total_points} điểm.\n")
    f.write(f"- Độ dịch chuyển trung bình của vật thể: {avg_displacement:.2f} pixels.\n")

print(f"🎯 CHỐT ĐƠN! Đã lưu thành công {total_points} điểm chuẩn vào file '{output_file}'!")

# 7. VẼ HÌNH CHECK MẮT (Tùy chọn, không thích có thể tắt)
# Chỉ vẽ các đường nối cho các điểm xịn (Inliers) đã được RANSAC lọc
img_matches = cv2.drawMatches(
    img1, kp1, img2, kp2, final_matches, None,
    matchColor=(0, 255, 0), # Đường nối màu xanh lá cho uy tín
    singlePointColor=None,
    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
)

# Resize lại ảnh hiển thị nếu ảnh gốc quá to so với màn hình
screen_res = 1280, 720
scale_width = screen_res[0] / img_matches.shape[1]
scale_height = screen_res[1] / img_matches.shape[0]
scale = min(scale_width, scale_height)
window_width = int(img_matches.shape[1] * scale)
window_height = int(img_matches.shape[0] * scale)

cv2.namedWindow('Data Matching Visual', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Data Matching Visual', window_width, window_height)
cv2.imshow('Data Matching Visual', img_matches)
cv2.waitKey(0)
cv2.destroyAllWindows()