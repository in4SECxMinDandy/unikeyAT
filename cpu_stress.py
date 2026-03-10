import time
import multiprocessing
import msvcrt
import sys
import urllib.request
import urllib.parse
import json
import socket
import os
from cryptography.fernet import Fernet

# ==========================================
# 1. QUẢN LÝ KHÓA (KEY MANAGEMENT)
# ==========================================
def generate_key(key_filename="secret.key"):
    """Tạo một khóa mã hóa mới và lưu vào tệp."""
    key = Fernet.generate_key()
    with open(key_filename, "wb") as key_file:
        key_file.write(key)
    print(f"[*] Đã tạo và lưu khóa tại: {key_filename}")

def load_key(key_filename="secret.key"):
    """Đọc khóa mã hóa từ tệp."""
    return open(key_filename, "rb").read()

# ==========================================
# 2. MÃ HÓA VÀ GIẢI MÃ (ENCRYPTION & DECRYPTION)
# ==========================================
def encrypt_file(filename, key):
    """Mã hóa nội dung của một tệp."""
    f = Fernet(key)
    
    # Đọc dữ liệu gốc
    with open(filename, "rb") as file:
        file_data = file.read()
        
    # Mã hóa dữ liệu
    encrypted_data = f.encrypt(file_data)
    
    # Ghi đè dữ liệu đã mã hóa vào tệp
    with open(filename, "wb") as file:
        file.write(encrypted_data)
    print(f"[*] Đã mã hóa tệp: {filename}")

def decrypt_file(filename, key):
    """Giải mã nội dung của một tệp."""
    f = Fernet(key)
    
    # Đọc dữ liệu đã mã hóa
    with open(filename, "rb") as file:
        encrypted_data = file.read()
        
    # Giải mã dữ liệu
    decrypted_data = f.decrypt(encrypted_data)
    
    # Ghi đè dữ liệu đã giải mã vào tệp
    with open(filename, "wb") as file:
        file.write(decrypted_data)
    print(f"[*] Đã giải mã tệp: {filename}")

def send_telegram_message(token, message):
    try:
        updates_url = f"https://api.telegram.org/bot{token}/getUpdates"
        req = urllib.request.Request(updates_url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("ok") and len(data.get("result", [])) > 0:
                chat_id = data["result"][-1]["message"]["chat"]["id"]
                
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = urllib.parse.urlencode({
                    "chat_id": chat_id,
                    "text": message
                }).encode('utf-8')
                
                send_req = urllib.request.Request(send_url, data=payload)
                urllib.request.urlopen(send_req)
            else:
                print("\n[-] Không tìm thấy chat_id. Hãy gửi 1 tin nhắn bất kỳ cho bot trên Telegram rồi thử lại.")
    except Exception as e:
        pass # Bỏ qua lỗi kết nối để không làm gián đoạn chương trình chính

def cpu_stress_task(stop_event):
    """
    Tiến trình con mô phỏng tải tính toán.
    Sẽ liên tục kiểm tra cờ stop_event thay vì chạy vô hạn.
    """
    # Vòng lặp chỉ tiếp tục khi event chưa được kích hoạt (cờ đang hạ)
    while not stop_event.is_set():
        _ = 9999999 ** 2

if __name__ == '__main__':
    print("=== CHƯƠNG TRÌNH MÔ PHỎNG TẢI CPU ===")
    
    # ------------------ CẤU HÌNH ------------------
    duration = 10 # Giới hạn thời gian tối đa để chạy stress (tính bằng giây)
    stop_keyword = "PTIT1@" # Từ khóa bí mật dùng để ngắt chương trình
    telegram_bot_token = "5142290467:AAH8aHrW7GIyoZ5IGUCUZ3So5actekfmh0Q"
    # ----------------------------------------------
    
    print(f"=> KILL SWITCH: Nhập chuỗi '{stop_keyword}' vào console bất kỳ lúc nào để DỪNG KHẨN CẤP <=\n")
    print(f"=> TỰ ĐỘNG DỪNG: Sau {duration} giây <=\n")

    # Tạo một Event để đồng bộ hóa giữa các luồng. 
    # Khi cờ này được set(), tất cả các tiến trình con sẽ đọc được và tự động thoát vòng lặp.
    stop_event = multiprocessing.Event()
    
    num_cores = multiprocessing.cpu_count()
    print(f"Hệ thống cấp phát {num_cores} luồng CPU. Đang đẩy mức sử dụng lên cao...")
    
    pc_name = socket.gethostname()
    send_telegram_message(telegram_bot_token, f"🚀 [{pc_name}] Bắt đầu CPU stress với {num_cores} luồng (Tối đa {duration}s).")
    
    processes = []
    
    # Khởi tạo các tiến trình con và truyền stop_event vào bộ nhớ của chúng
    for _ in range(num_cores):
        p = multiprocessing.Process(target=cpu_stress_task, args=(stop_event,))
        processes.append(p)
        p.start()

    start_time = time.time()
    input_buffer = ""

    # Tiến trình chính đóng vai trò "người giám sát"
    try:
        while True:
            # 1. Kiểm tra giới hạn thời gian chạy
            elapsed = time.time() - start_time
            if elapsed >= duration:
                print(f"\n[+] Đạt giới hạn thời gian ({duration} giây). Đang gửi tín hiệu dừng...")
                stop_event.set()
                break

            # 2. Kiểm tra chuỗi phím nhập từ terminal
            if msvcrt.kbhit():
                # Đọc byte phím được nhấn
                char_bytes = msvcrt.getch()
                # Decode byte đó (bỏ qua những phím chức năng không decode được thành utf-8)
                try:
                    char = char_bytes.decode('utf-8')
                    # Ghi nhận phím vào buffer (lưu lại các ký tự cuối cùng vừa đủ độ dài của stop_keyword)
                    input_buffer += char
                    
                    # Nếu user gõ sai kí tự so với chuỗi mẫu, thì loại bỏ dần các kí tự thừa ở đầu
                    # để input_buffer luôn chỉ lưu tối đa số kí tự bằng chiều dài stop_keyword
                    if len(input_buffer) > len(stop_keyword):
                        input_buffer = input_buffer[-len(stop_keyword):]
                    
                    # Hiển thị dấu * trên console để biết là có gõ phím nhưng giấu nội dung (tùy chọn)
                    sys.stdout.write('*')
                    sys.stdout.flush()

                    # Nếu buffer khớp hoàn toàn với keyword thì dừng
                    if input_buffer == stop_keyword:
                        print(f"\n[!] Nhận dạng chuỗi khóa bí mật '{stop_keyword}'. Đang ngắt tiến trình con...")
                        stop_event.set()
                        break
                except UnicodeDecodeError:
                    pass
            
            # Tạm nghỉ nhẹ để tiến trình chính không tranh giành CPU với tiến trình con
            time.sleep(0.05)
                
    except KeyboardInterrupt:
        # Dự phòng cơ chế chuẩn của hệ điều hành: Người dùng nhấn Ctrl+C
        print("\n[!] Đã nhận tín hiệu ngắt (SIGINT/Ctrl+C). Đang dừng khẩn cấp...")
        stop_event.set()

    # Chờ hệ điều hành dọn dẹp và thu hồi lại vùng nhớ của từng tiến trình con
    for p in processes:
        p.join()

    print("\nHoàn tất dọn dẹp. Hệ thống đã an toàn và tài nguyên được giải phóng hoàn toàn.")
    send_telegram_message(telegram_bot_token, f"✅ [{pc_name}] Đã dừng CPU stress. Giải phóng an toàn tài nguyên.")