# Tugas ETS Pemrograman Jaringan
## Daftar Isi
- [Soal]()
- [Kegunaan Masing-Masing File]()
- [Arsitektur / Alur Kerja]()
- [Diagram Arsitektur / Alur Kerja]()
- Penjelasan Tiap File
  - [file_server.py]()
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
