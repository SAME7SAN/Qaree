import os
import json
import wave

def get_audio_duration(file_path):
    """حساب مدة الملف الصوتي بالثواني"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return round(duration, 3)  # تقريب إلى 3 أرقام عشرية
    except Exception as e:
        # في حال وجود ملف تالف أو صيغة غير مدعومة
        return None

def build_audio_index(words_dir, phonemes_dir, output_json="database_index.json"):
    """
    فهرسة ملفات الكلمات والمقاطع الصوتية وحفظها في ملف JSON
    """
    database = {
        "words": {},
        "phonemes": {}
    }
    
    # 1. فهرسة مجلد الكلمات الكاملة
    if os.path.exists(words_dir):
        print(f"جاري فحص مجلد الكلمات: {words_dir}")
        for filename in os.listdir(words_dir):
            if filename.lower().endswith('.wav'):
                word_name = os.path.splitext(filename)[0]  # استخراج اسم الكلمة بدون الامتداد
                file_path = os.path.abspath(os.path.join(words_dir, filename))
                duration = get_audio_duration(file_path)
                
                if duration is not None:
                    database["words"][word_name] = {
                        "file_path": file_path,
                        "duration": duration,
                        "source": os.path.basename(words_dir) # لمعرفة مصدرها (البقرة، الواقعة.. إلخ)
                    }
    else:
        print(f"تنبيه: مجلد الكلمات غير موجود في المسار المحدد: {words_dir}")

    # 2. فهرسة مجلد المقاطع الصوتية (الفونيمات)
    if os.path.exists(phonemes_dir):
        print(f"جاري فحص مجلد المقاطع الصوتية: {phonemes_dir}")
        for filename in os.listdir(phonemes_dir):
            if filename.lower().endswith('.wav'):
                phoneme_name = os.path.splitext(filename)[0]
                file_path = os.path.abspath(os.path.join(phonemes_dir, filename))
                duration = get_audio_duration(file_path)
                
                if duration is not None:
                    database["phonemes"][phoneme_name] = {
                        "file_path": file_path,
                        "duration": duration,
                        "source": os.path.basename(phonemes_dir)
                    }
    else:
        print(f"تنبيه: مجلد المقاطع غير موجود في المسار المحدد: {phonemes_dir}")

    # حفظ البيانات في ملف JSON منسق يدعم اللغة العربية
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
        
    print("\n--- تم الانتهاء من الفهرسة بنجاح! ---")
    print(f"إجمالي الكلمات المفهرسة: {len(database['words'])}")
    print(f"إجمالي المقاطع المفهرسة: {len(database['phonemes'])}")
    print(f"تم حفظ الفهرس في: {os.path.abspath(output_json)}")

# --- تشغيل البرنامج ---
if __name__ == "__main__":
    # ضع هنا المسارات الفعلية للمجلدات المتاحة لديك الآن
    # يمكنك استخدام مسارات نسبية أو مسارات كاملة مثل: r"F:\Qaree\pure_mizan_database"
    WORDS_DIRECTORY = "path_to_your_words_folder" 
    PHONEMES_DIRECTORY = "path_to_your_phonemes_folder"
    
    build_audio_index(WORDS_DIRECTORY, PHONEMES_DIRECTORY)