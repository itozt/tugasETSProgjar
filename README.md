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
