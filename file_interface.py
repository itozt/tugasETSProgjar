import os
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.makedirs('files', exist_ok=True)
        os.chdir('files/')

    def list(self, params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=f'Gagal mendapatkan daftar file: {str(e)}')

    def get(self, params=[]):
        try:
            filename = params[0] if params else ''
            if filename == '':
                return dict(status='ERROR', data='Nama file tidak disediakan')
            
            if not os.path.exists(filename):
                return dict(status='ERROR', data='File tidak ditemukan')
            
            with open(filename, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=f'Gagal membaca file: {str(e)}')

    def upload(self, params=[]):
        try:
            if len(params) < 2:
                return dict(status='ERROR', data='Parameter tidak lengkap untuk upload')
            
            filename = params[0]
            filedata_base64 = params[1]
            
            if not filename:
                return dict(status='ERROR', data='Nama file tidak valid')
            
            try:
                filedata = base64.b64decode(filedata_base64)
            except Exception as e:
                return dict(status='ERROR', data='Data file tidak valid (base64 decode gagal)')
            
            with open(filename, 'wb') as f:
                f.write(filedata)
            return dict(status='OK', data=f"File {filename} berhasil diunggah")
        except Exception as e:
            return dict(status='ERROR', data=f'Gagal mengunggah file: {str(e)}')

    def delete(self, params=[]):
        try:
            filename = params[0] if params else ''
            if filename == '':
                return dict(status='ERROR', data='Nama file tidak disediakan')
            
            if not os.path.exists(filename):
                return dict(status='ERROR', data='File tidak ditemukan')
                
            os.remove(filename)
            return dict(status='OK', data=f"File {filename} berhasil dihapus")
        except Exception as e:
            return dict(status='ERROR', data=f'Gagal menghapus file: {str(e)}')


if __name__ == '__main__':
    f = FileInterface()
    print("=== Test FileInterface ===")
    
    # Test upload
    print("1. Test Upload:")
    hasil_upload = f.upload(['test_upload.txt', base64.b64encode(b'konten file test\n').decode()])
    print(hasil_upload)
    
    # Test list
    print("\n2. Test List:")
    hasil_list = f.list()
    print(hasil_list)
    
    # Test get
    print("\n3. Test Get:")
    hasil_get = f.get(['test_upload.txt'])
    print({k: v[:50] + '...' if k == 'data_file' and len(str(v)) > 50 else v for k, v in hasil_get.items()})
    
    # Test delete
    print("\n4. Test Delete:")
    hasil_delete = f.delete(['test_upload.txt'])
    print(hasil_delete)
    
    # Test list lagi
    print("\n5. Test List setelah delete:")
    hasil_list_akhir = f.list()
    print(hasil_list_akhir)
