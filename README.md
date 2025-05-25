# Tugas ETS Pemrograman Jaringan
## Daftar Isi
- [Soal](https://github.com/itozt/tugasETSProgjar/tree/main#soal)
- [Kegunaan Masing-Masing File](https://github.com/itozt/tugasETSProgjar/tree/main#kegunaan-masing-masing-file)
- [Arsitektur / Alur Kerja](https://github.com/itozt/tugasETSProgjar/tree/main#-arsitektur-alur-kerja)
- [Diagram Arsitektur / Alur Kerja](https://github.com/itozt/tugasETSProgjar/tree/main#-diagram-arsitektur-alur-kerja)
- Penjelasan Tiap File
  - [file_server.py](https://github.com/itozt/tugasETSProgjar/blob/main/README.md#-file_serverpy)
  - [file_interface.py]()
  - [file_protocol.py]()
  - [file_client_cli_test]()
- [Cara Pengerjaan]()

# 🌲Soal
Dari hasil modifikasi program [https://github.com/rm77/progjar/tree/master/progjar4a](https://github.com/rm77/progjar/tree/master/progjar4a) pada TUGAS 3 <br>

Rubahlah model pemrosesan concurrency yang ada, dari multithreading menjadi: 
  - Multihreading menggunakan pool<br>
  - Multiprocessing menggunakan pool <br>

Modifikasilah program client untuk melakukan:
- Download file
- Upload file
- List file <br>

Lakukan stress test pada program server tersebut dengan cara membuat client agar melakukan proses pada nomor 3 secara concurrent dengan menggunakan multithreading pool dan multiprocessing pool <br>

Kombinasi stress test: <br>
- Operasi download, upload
- Volume file 10 MB, 50 MB, 100 MB
- Jumlah client worker pool 1, 5, 50
- Jumlah server worker pool 1, 5, 50 <br>

Untuk setiap kombinasi tersebut catatlah:
- Waktu total per client melakukan proses upload/download (dalam seconds)
- Throughput per client (dalam bytes per second, total bytes yang sukses diproses per second)
- Jumlah worker client yang sukses dan gagal (jika sukses semua, maka gagal = 0)
- Jumlah worker server yang sukses dan gagal (jika sukses semua, maka gagal = 0) <br>

Hasil stress test, harus direkap ke sebuah tabel yang barisnya adalah total kombinasi dari nomor 4. Total baris kombinasi = 2x3x3x3 = 54 baris, dengan kolom: <br>
- Nomor
- Operasi
- Volume
- Jumlah client worker pool
- Jumlah server worker pool
- Waktu total per client
- Throughput per client
- Jumlah worker client yang sukses dan gagal
- Jumlah worker server yang sukses dan gagal

# 🌲Kegunaan Masing-Masing File
Untuk menjalankan stress test, saya memerlukan beberapa file class. Berikut merupakan kegunaan dari masing-masing fiel class : 
- **file_server.py** :
  - Menjalankan server TCP yang mendengarkan pada HOST:PORT.
  - Menerima permintaan client melalui socket, mem-parse perintah (LIST, UPLOAD, GET), mengakses direktori penyimpanan (storage/), dan mengirimkan respons JSON.
  - Mendukung tiga mode concurrency :
    - single : satu thread, melayani satu koneksi per satu waktu
    - thread : pool thread (ThreadPoolExecutor) untuk melayani banyak koneksi secara paralel
    - process : sebenarnya fallback ke single-threaded (karena socket tak bisa di-serialize dengan baik)
  - Mencatat log aktivitas dan menghitung jumlah worker yang sukses/gagal
- **file_interface.py**
  - Abstraksi layer akses file di direktori lokal files/.
  - Menyediakan method :
    - list() → daftar nama file
    - get(filename) → baca file, encode ke Base64
    - upload(filename, data_base64) → decode & tulis file
    - delete(filename) → hapus file
- **file_protocol.py**
  - “Glue” antara raw string perintah dari client dan FileInterface.
  - Method proses_string(...) menerima teks perintah, mem-split menjadi command & parameter, melakukan validasi format, memanggil method yang sesuai di FileInterface, lalu mereturn hasil (dict) yang di-json.dumps
  - Memudahkan implementasi server: tinggal terima string dari socket, panggil FileProtocol.proses_string, kirim balik JSON yang dihasilkan
- **file_client_cli_test.py**
  - Client-side CLI untuk menguji server : <br>
    upload_remote(), download_remote(), list_remote() → bungkus perintah ke string, kirim via socket, terima & parse JSON
  - Fungsi stress_test(...) dan jalankan_semua_stress_test(...)
    - Men-spawn pool worker (thread atau process) untuk menjalankan ratusan client request secara concurrent
    - Mencatat metrik per test case :
      - Total waktu, rata-rata waktu per client
      - Throughput (bytes/sec)
      - Jumlah success/fail client worker
      - (Input manual) jumlah server worker
    - Menyimpan hasil ke CSV

# 🌲 Arsitektur Alur Kerja
Berikut alur kerja detail saat menjalankan stress test, beserta file yang berperan di setiap langkahnya dan fungsinya :
1. **Menjalankan Server** <br>
   File : `file_server.py` <br>
   Fungsi :
   1. Membaca argumen `--mode` (single/thread/process) dan `--workers`.
   2. Membuka TCP socket di `HOST:PORT` (default `0.0.0.0:5666`).
   3. Jika mode thread, membuat `ThreadPoolExecutor` dengan `max_workers=args.workers`; jika process, fallback ke loop sinkron.
   4. Menunggu koneksi masuk; untuk setiap koneksi, memanggil `handle_client(conn, addr)` (baik langsung maupun via pool).
2. **Membangun Perintah Stress Test (Client Launcher)** <br>
   File : `file_client_cli_test.py` <br>
   Fungsi:
   1. Argumen `--mode stress, --file <path>, --pool_mode {thread,process}, --pool_size C, --server_workers S, --nomor N, --output <csv>`.
   2. Memilih `executor_cls = ThreadPoolExecutor` atau `ProcessPoolExecutor` sesuai `--pool_mode`.
   3. Memanggil fungsi `stress_test(...)` sebanyak `C` concurrent worker.
3. **Setiap Worker Stress Test** <br>
   File : `file_client_cli_test.py` (di dalam fungsi `stress_test`) <br>
   Langkah Utama :
   1. spawn C futures yang menjalankan `tugas_worker(server_ip, server_port, operasi, filepath)`.
   2. tugas_worker mencatat waktu_mulai = time.time() lalu:
      - Jika `operasi == "upload"` → `pload_remote(...)`
      - Jika `operasi == "download"` → `download_remote(...)`
      - Jika `operasi == "list"` → `list_remote(...)`
   3. Setelah operasi selesai, hitung `durasi` dan `ukuran_byte` yang berhasil ditransfer.
   4. Kembalikan tuple `(sukses_bool, durasi, ukuran_byte)`.
4. **Fungsi Perintah TCP Client** <br>
   File : `file_client_cli_test.py` <br>
   Fungsi Utama :
   - `kirim_perintah(server_ip, server_port, perintah_str)` <br>
     1. Membuka socket ke server.
     2. `sock.sendall((perintah_str + "\r\n\r\n").encode())`.
     3. Menerima data sampai marker `\r\n\r\n`, lalu `json.loads(...)`.
   - Wrapper untuk operasi :
     - `upload_remote` → baca file, `base64.b64encode`, form `"UPLOAD filename data"`.
     - `download_remote` → kirim `"GET filename"`, terima base64 → decode & simpan `unduh_filename`.
     - `list_remote` → kirim `"LIST"`.
5. **Server Menerima dan Menangani Permintaan** <br>
   File : `file_server.py` → fungsi `handle_client(conn, addr)` <br>
   Proses:
   - Baca data sampai `\r\n\r\n`.
   - Split teks menjadi `parts = data_received.strip().split()`.
   - Tentukan `command = parts[0].upper()`.
   - Untuk setiap command (LIST, UPLOAD, GET):
     - LIST : `filelist = os.listdir(STORAGE_DIR)` → kirim JSON `{"status":"OK","data":filelist}`.
     - UPLOAD : `filename = parts[1], encoded_data = " ".join(parts[2:])`, decode base64, tulis ke `storage/filename`.
     - GET : `filename = parts[1]`, baca file, encode base64, kirim `{"status":"OK","data_namafile":..., "data_file":...}`.
   - Panggil `tambah_sukses()` atau `tambah_gagal()` sesuai hasil, lalu `conn.close()`.
6. **(Internal) Proses String ke Operasi File** <br>
   File : `file_protocol.py` <br>
   Fungsi : `FileProtocol.proses_string(string_datamasuk)`
   1. Validasi format input (jumlah part, perintah dikenal).
   2. Mapping ke method di `FileInterface (list, get, upload, delete)`.
   3. Mengembalikan `json.dumps(...)` dari hasil operasi. <br>
   Catatan: pada file_server.py, alur ini implicit—server membaca string, lalu menyalurkannya ke logika sendiri. Jika Anda ingin menggunakan `FileProtocol`, Anda bisa mengganti blok parsing di `file_server.py` dengan panggilan ke `FileProtocol.proses_string`.
7. **Operasi File Sistem** <br>
   File : `file_interface.py` <br>
   Method :
   - `list(self)` → glob('*.*') di folder files/
   - `get(self, [filename])` → buka & baca, encode base64
   - `upload(self, [filename, data_base64])` → decode & tulis
   - `delete(self, [filename])` → hapus file <br>
  Output: dict `{status, data...}`
8. **Agregasi Hasil & Pelaporan** <br>
   File : `file_client_cli_test.py` (lanjutan di stress_test) <br>
   - Yang Dicatat :
     - `waktu_total` (seluruh batch), waktu_rata per client
     - `throughput` = total_bytes / waktu_total
     - `jumlah_sukses, jumlah_gagal` di client
     - `worker_server` (diisi manual sebagai parameter) <br>
   - Output :
     - Print ringkasan di console
     - Append satu baris ke CSV (`laporan_stress_test.csv`) dengan header dan data metrik

# 🌲 Diagram Arsitektur Alur Kerja
![Arsitektur Alur Kerja](https://github.com/user-attachments/assets/b8f73562-07dd-4067-835d-3480f1be7f43)

# 🌲 Penjelasan Tiap File
## ✨ file_server.py
**Tujuan** : Menerima koneksi dari klien. Menerima perintah seperti LIST, UPLOAD, DOWNLOAD. Memproses perintah dan mengirim respons kembali ke klien
- **Inisialisasi dan Konstanta**
  - Menentukan alamat dan port server
  - Menetapkan folder penyimpanan file server
  ``` py
  SERVER_HOST = '0.0.0.0'
  SERVER_PORT = 9000
  SERVER_STORAGE = './server_storage'
  ```
- **Fungsi handle_client(client_socket, client_address)** <br>
  Menangani 1 klien. Menerima perintah, proses, dan kirim balasan.
  ``` py
  def handle_client(client_socket, client_address):
    while True:
        data = client_socket.recv(1024)
        ...
        if command == 'LIST':
            ...
        elif command == 'UPLOAD':
            ...
        elif command == 'DOWNLOAD':
            ...
  ```
- **Perintah LIST** <br>
  Kirim daftar file dalam folder server.
  ``` py
  if command == 'LIST':
    files = os.listdir(SERVER_STORAGE)
    response = '\n'.join(files) + '\r\n\r\n'
    client_socket.sendall(response.encode())
  ```
- **Perintah UPLOAD** <br>
  Menerima file dari klien dan simpan ke server.
  ``` py
  elif command == 'UPLOAD':
    filename = parts[1]
    filesize = int(parts[2])
    filepath = os.path.join(SERVER_STORAGE, filename)
    with open(filepath, 'wb') as f:
        ...
  ```
- **Perintah DOWNLOAD** <br>
  Kirim ukuran dan isi file ke klien.
  ``` py
  elif command == 'DOWNLOAD':
    filename = parts[1]
    filepath = os.path.join(SERVER_STORAGE, filename)
    filesize = os.path.getsize(filepath)
    client_socket.sendall(f"{filesize}\r\n".encode())
    ...
  ```
-  **Main Server Loop** <br>
   Membuka socket TCP dan menerima banyak klien secara paralel (threading).
   ``` py
   def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    ...
    while True:
        client_socket, client_address = server_socket.accept()
        ...
        threading.Thread(target=handle_client, ...).start()
   ````
## ✨ file_interface.py
file_interface.py adalah interface penghubung antara client dengan server. <br>
File ini digunakan oleh file_client.py untuk komunikasi dengan server. <br>
**Tujuan** : Menghubungkan ke server. Mengirim perintah LIST, UPLOAD, DOWNLOAD. Menerima respon dari server 
- **Fungsi `connect(server_ip, server_port)`** <br>
  Membuka koneksi TCP ke server, mengembalikan objek socket.
  ``` py
  def connect(server_ip, server_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    return s
  ```
- **Fungsi `list_files(sock)`** <br>
  Mengirim perintah LIST ke server untuk meminta daftar file.
  ``` py
  def list_files(sock):
    sock.sendall(b'LIST\r\n')
    ...
    return response.split('\n')
  ```
- **Fungsi `upload_file(sock, filepath)`** <br>
  Mengirim file ke server dengan : Nama file, ukuran file, isi file
  ``` py
  def upload_file(sock, filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    sock.sendall(f"UPLOAD {filename} {filesize}\r\n".encode())
    ...
  ```
- **Fungsi `download_file(sock, filename, dest_folder)`** <br>
  Meminta file dari server dan menyimpannya ke folder lokal.
  ``` py
  def download_file(sock, filename, dest_folder):
    sock.sendall(f"DOWNLOAD {filename}\r\n".encode())
    ...
    with open(filepath, 'wb') as f:
        ...
  ```
