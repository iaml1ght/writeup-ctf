import numpy as np


poem = [
    "Đêm khuya phòng máy sáng đèn",
    "Ngón tay gõ phím như quen tiếng lòng",
    "Màn hình chữ chạy như dòng",
    "Mắt cay vẫn dõi từng vòng lặp sâu",
    "Cờ kia giấu tận nơi đâu",
    "Ai nghe đúng nhịp mới hầu hiểu nhau",
    "Đường xa còn lắm nhịp cầu",
    "Lần từng dấu nhỏ tìm câu trả lời",
    "Khoá kia như hạt sương rơi",
    "Mỗi lần thử lỗi lại vơi niềm tin",
    "Anh em vẫn giữ lòng tin",
    "Thêm dòng lệnh nữa để nhìn lối ra",
    "Gió đêm thổi lạnh hiên nhà",
    "Mảnh trăng nghiêng xuống như là mỉm cười",
    "Màn hình bỗng hiện tên người",
    "Chiếc cờ nhỏ bé đỏ tươi trong màn",
    "Tiếng reo vui khắp nhân gian",
    "Đêm dài bỗng hoá muôn vàn sao xa",
    "Nhắn ai mai mốt đi qua",
    "Nhớ rằng mật mã chỉ là bước đầu",
]


def is_trac(word):
 
  trac_vowels = "áắấéếíóốớúứýảẳẩẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ"
  return 1 if any(c in trac_vowels for c in word.lower()) else 0


# Lấy các chữ tự do (vị trí 1, 3, 5 trong câu lục; 1, 3, 5, 7 trong câu bát - chỉ số 0-indexed: 0, 2, 4, [6])
free_bits = []
for line in poem:
  words = line.split()
  free_indices = [0, 2, 4] if len(words) == 6 else [0, 2, 4, 6]
  for idx in free_indices:
    free_bits.append(is_trac(words[idx]))
    if len(free_bits) == 64:
      break
  if len(free_bits) == 64:
    break


TAPS = int("".join(str(b) for b in free_bits), 2)
OUT_MASK = 0x9E3779B97F4A7C15
out_hex = open("out.txt").read().strip()
ciphertext = bytes.fromhex(out_hex)


A = np.zeros((64, 64), dtype=int)
for i in range(1, 64):
  A[i - 1, i] = 1
for i in range(64):
  if (TAPS >> i) & 1:
    A[63, i] ^= 1

out_vec = np.array([(OUT_MASK >> i) & 1 for i in range(64)], dtype=int)
