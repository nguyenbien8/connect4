# 🎮 Connect Four AI Project Report

## 📋 Thành viên nhóm
- `23021477` Nguyễn Văn Biển
- `23021551` Nguyễn Quang Hiếu
- `23021543` Tô Ngọc Hải
- `23021721` Đỗ Phương Thảo

## 📝 Mục lục
1. [🌟 Giới thiệu](#giới-thiệu)
2. [🎯 Tổng quan về trò chơi Connect Four](#tổng-quan-về-trò-chơi-connect-four)
3. [🧠 Thuật toán](#thuật-toán)
   - [Minimax](#minimax)
   - [Cắt tỉa Alpha-Beta](#cắt-tỉa-alpha-beta)
4. [🚀 Cải tiến thuật toán](#cải-tiến-thuật-toán)
5. [🔮 Hướng phát triển](#hướng-phát-triển)
6. [📚 Tài liệu tham khảo](#tài-liệu-tham-khảo)

## 🌟 Giới thiệu

Báo cáo này nhóm em xin trình bày về việc phát triển trí tuệ nhân tạo (AI) cho trò chơi Connect Four. Nhóm đã triển khai thuật toán Minimax kết hợp với kỹ thuật cắt tỉa Alpha-Beta, cùng với một số cải tiến để tối ưu hóa hiệu suất và tăng cường khả năng chơi của AI.

## 🎯 Tổng quan về trò chơi Connect Four

Connect Four là một trò chơi chiến thuật dành cho hai người chơi. Mỗi người chơi sẽ lần lượt thả quân cờ của mình xuống bảng gồm 7 cột và 6 hàng. Quân cờ sẽ rơi xuống vị trí thấp nhất có thể trong cột được chọn. Người chơi đầu tiên tạo được một đường thẳng liên tiếp gồm 4 quân cờ theo chiều ngang, dọc hoặc chéo sẽ thắng cuộc.

## 🧠 Thuật toán

Nhóm em phát triển AI cho Game `Connect4` dựa trên thuật toán `Minimax` và kỹ thuật cắt tỉa `Alpha-Beta`. Dưới đây là tổng quan về thuật toán `Minimax` và kỹ thuật cắt tỉa `Alpha-Beta`

### Minimax

Minimax là thuật toán tìm kiếm đệ quy sử dụng trong lý thuyết trò chơi và trí tuệ nhân tạo để đưa ra quyết định tối ưu cho các trò chơi hai người chơi zero-sum (tổng bằng không), như cờ vua, cờ tướng hay Connect Four.

#### Nguyên lý cơ bản:
- Minimax xem trò chơi như một cây quyết định, trong đó mỗi nút đại diện cho một trạng thái của trò chơi, và mỗi nhánh đại diện cho một nước đi hợp lệ.
- Hai người chơi được gọi là `Max` (người chơi tối đa hóa điểm số) và `Min` (người chơi tối thiểu hóa điểm số).
- Thuật toán giả định rằng cả hai người chơi đều chơi tối ưu (`Min` luôn chọn nước đi gây bất lợi nhất cho `Max`).

#### Mã nguồn thuật toán Minimax:

```python
function minimax(node, depth, maximizingPlayer) is
    if depth = 0 or node is a terminal node then
        return the heuristic value of node
    if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, minimax(child, depth − 1, FALSE))
        return value
    else (* minimizing player *)
        value := +∞
        for each child of node do
            value := min(value, minimax(child, depth − 1, TRUE))
        return value
```

### Cắt tỉa alpha-beta

Cắt tỉa `Alpha-Beta` là một cải tiến của thuật toán `Minimax`, giúp giảm số lượng nút cần đánh giá trong cây tìm kiếm mà không ảnh hưởng đến kết quả cuối cùng.

#### Nguyên lý cơ bản:
- Alpha: Giá trị tốt nhất hiện tại đã tìm thấy cho người chơi MAX trên đường đi tới nút hiện tại.
- Beta: Giá trị tốt nhất hiện tại đã tìm thấy cho người chơi MIN trên đường đi tới nút hiện tại.
- Khi `alpha ≥ beta`, chúng ta có thể cắt tỉa (bỏ qua) các nhánh còn lại vì chúng không ảnh hưởng đến quyết định cuối cùng.

#### Mã nguồn thuật toán Alpha-Beta:

```python
function alphabeta(node, depth, α, β, maximizingPlayer) is
    if depth == 0 or node is terminal then
        return the heuristic value of node
    if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
            if value ≥ β then
                break (* β cutoff *)
            α := max(α, value)
        return value
    else
        value := +∞
        for each child of node do
            value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
            if value ≤ α then
                break (* α cutoff *)
            β := min(β, value)
        return value
```

## 🚀 Cải tiến thuật toán

Cùng với việc xây dựng dựa trên 2 thuật toán cơ bản là `Minimax` và cắt tỉa `Alpha-Beta`. Nhóm em đã thực hiện một số cải tiến quan trọng cho AI của Game giúp AI có khả năng đưa ra quyết định tối ưu trong thời gian hợp lý và xây dựng chiến lược tấn công hiệu quả.

**1. Sử dụng bảng chuyển vị (Transposition Table)**

```python
# Check transposition table
if state_key in transposition_table:
    return transposition_table[state_key]
```

- Bảng chuyển vị lưu trữ các trạng thái đã được tính toán trước đó để tránh việc tính toán lại, giúp cải thiện đáng kể hiệu suất khi gặp lại trạng thái đã xử lý.

**2. Sắp xếp nước đi hợp lệ (Move Ordering)**

```python
def sort_valid_moves_with_boards(valid_moves, board, piece):
    scored_moves = []
    for col in valid_moves:
        row = get_next_open_row(board, col)
        if row != -1:
            board_copy = drop_piece(board, row, col, piece)
            score = score_position(board_copy, piece)
            scored_moves.append((col, score, board_copy))
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    return scored_moves
```

- Nước đi được sắp xếp theo điểm số tiềm năng, giúp cắt tỉa `Alpha-Beta` hoạt động hiệu quả hơn bằng cách đánh giá các nước đi tốt nhất trước.

**3. Tối ưu hóa bộ nhớ với Tuple**

```python
# Convert board to hashable format
board_tuple = tuple(tuple(row) for row in board)
state_key = (board_tuple, depth, maximizing_player)
```

- Chuyển đổi bảng thành tuple để có thể sử dụng làm khóa trong bảng chuyển vị, giúp lưu trữ và tìm kiếm trạng thái hiệu quả hơn.

## 🔮 Hướng phát triển

Trong tương lai để phát triển hơn cho AI của Game hoạt động tốt hơn, nhóm em dự định cải tiến thêm cho AI bằng cách áp dụng mô hình học máy `Reinforcement Learning` để train AI tốt hơn. Từ đó tích hợp vào giao diện và thêm các cấp độ khó khác nhau của AI trong giao diện của người dùng.

## 📚 Tài liệu tham khảo

🐙 **GitHub**:
   - [GitHub - Connect Four AI Implementations](https://github.com/topics/connect-four)
   - [GitHub - Minimax Algorithm Examples](https://github.com/topics/minimax)

▶️ **YouTube**: [Keith Galli](https://www.youtube.com/@KeithGalli)

🤖 **ChatGPT**