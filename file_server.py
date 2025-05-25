import socket
import os
import argparse
import logging
import base64
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


HOST = '0.0.0.0'
PORT = 5666
STORAGE_DIR = 'storage'
LOG_FILE = 'server5666.log'

os.makedirs(STORAGE_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# Counter untuk tracking sukses/gagal worker
sukses_counter = 0
gagal_counter = 0
counter_lock = threading.Lock()

def tambah_sukses():
    global sukses_counter
    with counter_lock:
        sukses_counter += 1

def tambah_gagal():
    global gagal_counter
    with counter_lock:
        gagal_counter += 1

def ambil_counter():
    with counter_lock:
        return sukses_counter, gagal_counter

def reset_counter():
    global sukses_counter, gagal_counter
    with counter_lock:
        sukses_counter = 0
        gagal_counter = 0

def handle_client(conn, addr):
    thread_name = threading.current_thread().name
    try:
        logging.info(f"Koneksi dari {addr}")

        # Terima data sampai \r\n\r\n
        data_received = ""
        while True:
            data = conn.recv(524288).decode()
            if not data:
                break
            data_received += data
            if "\r\n\r\n" in data_received:
                break
        logging.debug(f"Data diterima (dipotong): {data_received[:100]}")

        parts = data_received.strip().split()
        if len(parts) < 1:
            resp = json.dumps({"status": "ERROR", "data": "Format perintah tidak valid"}) + "\r\n\r\n"
            conn.sendall(resp.encode())
            tambah_gagal()
            return

        command = parts[0].upper()

        if command == "LIST":
            # Handle LIST command
            try:
                filelist = os.listdir(STORAGE_DIR)
                filelist = [f for f in filelist if os.path.isfile(os.path.join(STORAGE_DIR, f))]
                resp = json.dumps({"status": "OK", "data": filelist}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                logging.info(f"Mengirim daftar file ke {addr}")
                tambah_sukses()
            except Exception as e:
                logging.error(f"Error mendapatkan daftar file: {e}")
                resp = json.dumps({"status": "ERROR", "data": f"Gagal mendapatkan daftar file: {str(e)}"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()

        elif command == "UPLOAD":
            if len(parts) < 3:
                resp = json.dumps({"status": "ERROR", "data": "Tidak ada data untuk diunggah"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()
                return
            
            filename = parts[1]
            encoded_data = " ".join(parts[2:])
            filepath = os.path.join(STORAGE_DIR, filename)
            
            try:
                file_data = base64.b64decode(encoded_data)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                logging.info(f"File {filename} disimpan dari {addr}")
                resp = json.dumps({"status": "OK", "data": f"File {filename} berhasil diunggah"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_sukses()
            except Exception as e:
                logging.error(f"Error decode/simpan file {filename}: {e}")
                resp = json.dumps({"status": "ERROR", "data": f"Gagal mengunggah file: {str(e)}"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()

        elif command == "GET":
            if len(parts) < 2:
                resp = json.dumps({"status": "ERROR", "data": "Nama file tidak disediakan"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()
                return
                
            filename = parts[1]
            filepath = os.path.join(STORAGE_DIR, filename)
            
            if not os.path.exists(filepath):
                resp = json.dumps({"status": "ERROR", "data": "File tidak ditemukan"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()
                return
            
            try:
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                encoded_data = base64.b64encode(file_data).decode()
                resp = json.dumps({
                    "status": "OK",
                    "data_namafile": filename,
                    "data_file": encoded_data
                }) + "\r\n\r\n"
                conn.sendall(resp.encode())
                logging.info(f"File {filename} dikirim ke {addr}")
                tambah_sukses()
            except Exception as e:
                logging.error(f"Error membaca file {filename}: {e}")
                resp = json.dumps({"status": "ERROR", "data": f"Gagal membaca file: {str(e)}"}) + "\r\n\r\n"
                conn.sendall(resp.encode())
                tambah_gagal()

        else:
            resp = json.dumps({"status": "ERROR", "data": "Perintah tidak valid"}) + "\r\n\r\n"
            conn.sendall(resp.encode())
            tambah_gagal()

    except Exception as e:
        logging.error(f"Exception menangani klien {addr}: {e}")
        resp = json.dumps({"status": "ERROR", "data": f"Error server: {str(e)}"}) + "\r\n\r\n"
        try:
            conn.sendall(resp.encode())
            tambah_gagal()
        except:
            pass
    finally:
        conn.close()
        logging.info(f"Koneksi dari {addr} ditutup")

def start_server_single():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(100)
        logging.info(f"Server single-threaded dimulai di {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            logging.info(f"Koneksi diterima dari {addr}")
            handle_client(conn, addr)

def start_server_threaded(workers):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(100)
        logging.info(f"Server thread-pool dimulai di {HOST}:{PORT} dengan {workers} worker")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            try:
                while True:
                    conn, addr = server_socket.accept()
                    logging.info(f"Koneksi diterima dari {addr}")
                    executor.submit(handle_client, conn, addr)
            except KeyboardInterrupt:
                logging.info("Server dihentikan dengan KeyboardInterrupt")

def start_server_process(workers):
    # Note: Process pool tidak ideal untuk socket handling karena socket tidak bisa di-serialize
    # Menggunakan pendekatan single-threaded untuk process mode
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(100)
        logging.info(f"Server process-pool dimulai di {HOST}:{PORT} dengan {workers} worker (mode sinkron)")

        while True:
            try:
                conn, addr = server_socket.accept()
                logging.info(f"Koneksi diterima dari {addr}")
                handle_client(conn, addr)
            except KeyboardInterrupt:
                logging.info("Server dihentikan dengan KeyboardInterrupt")
                break

def main():
    parser = argparse.ArgumentParser(description="File server dengan berbagai mode concurrency.")
    parser.add_argument('--mode', choices=['single', 'thread', 'process'], default='single', help="Mode untuk menjalankan server")
    parser.add_argument('--workers', type=int, default=1, help="Jumlah worker thread atau process")
    args = parser.parse_args()

    reset_counter()
    
    try:
        if args.mode == 'single':
            start_server_single()
        elif args.mode == 'thread':
            start_server_threaded(args.workers)
        elif args.mode == 'process':
            start_server_process(args.workers)
        else:
            logging.error("Mode tidak valid dipilih.")
    except KeyboardInterrupt:
        sukses, gagal = ambil_counter()
        logging.info(f"Server dihentikan. Worker sukses: {sukses}, Worker gagal: {gagal}")

if __name__ == '__main__':
    main()
