import json
import logging

from file_interface import FileInterface


class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"String diproses: {string_datamasuk[:100]}...")
        try:
            if not string_datamasuk.strip():
                return json.dumps(dict(status='ERROR', data='Perintah kosong'))
            
            parts = string_datamasuk.strip().split(" ", 2)
            c_request = parts[0].lower().strip()
            logging.warning(f"Memproses request: {c_request}")
            
            # Validasi perintah dan parameter
            if c_request == 'upload':
                if len(parts) != 3:
                    return json.dumps(dict(status='ERROR', data='Format perintah upload: UPLOAD <nama_file> <data_base64>'))
                params = [parts[1], parts[2]]
                
            elif c_request in ['get', 'delete']:
                if len(parts) != 2:
                    return json.dumps(dict(status='ERROR', data=f'Format perintah {c_request}: {c_request.upper()} <nama_file>'))
                params = [parts[1]]
                
            elif c_request == 'list':
                params = []
                
            else:
                return json.dumps(dict(status='ERROR', data=f'Perintah tidak dikenal: {c_request}. Perintah yang tersedia: LIST, GET, UPLOAD, DELETE'))

            # Panggil method yang sesuai
            if hasattr(self.file, c_request):
                cl = getattr(self.file, c_request)(params)
                return json.dumps(cl)
            else:
                return json.dumps(dict(status='ERROR', data=f'Method {c_request} tidak tersedia'))
                
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            return json.dumps(dict(status='ERROR', data=f'Gagal memproses perintah: {str(e)}'))


if __name__ == '__main__':
    print("=== Test FileProtocol ===")
    fp = FileProtocol()
    
    # Test upload
    print("1. Test UPLOAD:")
    hasil_upload = fp.proses_string("UPLOAD test_protocol.txt dGVzdCBjb250ZW50Cg==")
    print(hasil_upload)
    
    # Test list
    print("\n2. Test LIST:")
    hasil_list = fp.proses_string("LIST")
    print(hasil_list)
    
    # Test get
    print("\n3. Test GET:")
    hasil_get = fp.proses_string("GET test_protocol.txt")
    print(hasil_get[:100] + "..." if len(hasil_get) > 100 else hasil_get)
    
    # Test delete
    print("\n4. Test DELETE:")
    hasil_delete = fp.proses_string("DELETE test_protocol.txt")
    print(hasil_delete)
    
    # Test list setelah delete
    print("\n5. Test LIST setelah delete:")
    hasil_list_akhir = fp.proses_string("LIST")
    print(hasil_list_akhir)
    
    # Test perintah tidak valid
    print("\n6. Test perintah tidak valid:")
    hasil_invalid = fp.proses_string("INVALID command")
    print(hasil_invalid)
    
    # Test perintah kosong
    print("\n7. Test perintah kosong:")
    hasil_kosong = fp.proses_string("")
    print(hasil_kosong)
