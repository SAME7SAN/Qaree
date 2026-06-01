import os
import json
import wave

def get_audio_duration(file_path):
    """حساب مدة الملف الصوتي بالثواني بدقة"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return round(duration, 3)  # تقريب لـ 3 أرقام عشرية
    except Exception:
        return None

def build_audio_index():
    # تحديد المسارات الثابتة بناءً على ترتيب جهازك المذكور
    base_dir = r"F:\Qaree"
    words_dir = os.path.join(base_dir, "words")
    phonemes_dir = os.path.join(base_dir, "maqatee")
    output_json = os.path.join(base_dir, "database_index.json")
    
    # هيكل قاعدة البيانات النصية
    database = {
        "words": {},
        "phonemes": {}
    }
    
    print("--- بدء عملية حصر وفهرسة الملفات الصوتية ---")
    
    # 1. فحص مجلد الكلمات الكاملة (words)
    if os.path.exists(words_dir):
        print(f"جاري حصر الكلمات من المجلد: {words_dir}")
        for filename in os.listdir(words_dir):
            if filename.lower().endswith('.wav'):
                word_name = os.path.splitext(filename)[0]
                file_path = os.path.join(words_dir, filename)
                duration = get_audio_duration(file_path)
                
                if duration is not None:
                    database["words"][word_name] = {
                        "file_path": file_path,
                        "duration": duration,
                        "source": "words"
                    }
    else:
        print(f"تنبيه: لم يتم العثور على مجلد الكلمات في المسار: {words_dir}")

    # 2. فحص مجلد المقاطع الصوتية (maqatee)
    if os.path.exists(phonemes_dir):
        print(f"جاري حصر المقاطع الصوتية من المجلد: {phonemes_dir}")
        for filename in os.listdir(phonemes_dir):
            if filename.lower().endswith('.wav'):
                phoneme_name = os.path.splitext(filename)[0]
                file_path = os.path.join(phonemes_dir, filename)
                duration = get_audio_duration(file_path)
                
                if duration is not None:
                    database["phonemes"][phoneme_name] = {
                        "file_path": file_path,
                        "duration": duration,
                        "source": "maqatee"
                    }
    else:
        print(f"تنبيه: لم يتم العثور على مجلد المقاطع في المسار: {phonemes_dir}")

    # حفظ النتيجة في ملف JSON داخل F:\Qaree يدعم اللغة العربية بشكل كامل
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
        
    print("\n==========================================")
    print("--- تم الانتهاء من الفهرسة بنجاح! ---")
    print(f"عدد الكلمات الكاملة المفهرسة: {len(database['words'])}")
    print(f"عدد المقاطع الصوتية المفهرسة: {len(database['phonemes'])}")
    print(f"تم حفظ ملف الفهرس في: {output_json}")
    print("==========================================")

if __name__ == "__main__":
    build_audio_index()