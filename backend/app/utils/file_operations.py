#backend/app/utils/file_operations.py
import os
import urllib.parse
from fastapi import UploadFile, HTTPException
from supabase import StorageException
from ..config import supabase, BUCKET_NAME
import shutil
import tempfile
import os



async def upload_file(file: UploadFile, folder: str):
    try:
        # قراءة جزء صغير من الملف للتأكد من أنه يمكن قراءته
        chunk = await file.read(1024)
        await file.seek(0)  # إعادة المؤشر إلى بداية الملف

        original_extension = os.path.splitext(file.filename)[1]
        safe_name = urllib.parse.quote(os.path.splitext(file.filename)[0])
        new_filename = f"{safe_name}{original_extension}"

        storage_path = f"media/{folder}/{new_filename}"

        # إنشاء ملف مؤقت
        with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
            # نسخ محتوى الملف المرفوع إلى الملف المؤقت
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name


        # قراءة الملف المؤقت للتأكد من وجود محتوى
        with open(temp_file_path, "rb") as f:
            file_content = f.read()


        # التأكد من أن المحتوى ليس فارغًا
        if not file_content:
            raise ValueError("File content is empty")

        # رفع الملف إلى Supabase
        with open(temp_file_path, "rb") as f:
            response = supabase.storage.from_(BUCKET_NAME).upload(
                storage_path, f, file_options={"content-type": file.content_type}
            )

        # حذف الملف المؤقت
        os.unlink(temp_file_path)

        if not response:
            raise HTTPException(status_code=400, detail="Failed to upload file")


        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)

        return public_url, new_filename

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
        
    except Exception as e:
        if "Duplicate" in str(e):
            raise HTTPException(status_code=400, detail="Duplicate file")
        else:
            raise HTTPException(status_code=500, detail=str(e))

#va
def delete_file(folder: str, filename: str):
    try:
        storage_path = f"media/{folder}/{filename}"
        supabase.storage.from_(BUCKET_NAME).remove(storage_path)
    except Exception as e:
        print(f"Error deleting file from storage: {str(e)}")
