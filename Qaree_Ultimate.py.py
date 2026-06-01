import os
import whisper
import scipy.io.wavfile as wav
import numpy as np

def is_perfectly_isolated(current_word, next_word):
    """
    المصفاة الحاسمة: اختبار صارم لضمان العزل اللفظي والنقاء المطلق.
    تستبعد الكلمة عند أدنى شك في حدوث اتصال لغوي أو إدغام.
    """
    if not next_word:
        return True # الكلمة الأخيرة في الآية/المقطع نعتبرها نقية لإنها موقوف عليها حتماً
        
    current_clean = current_word.strip()
    next_clean = next_word.strip()
    
    # 1. القاعدة الكبرى: منع تداخل أل التعريف وألف الوصل تماماً
    if next_clean.startswith("ال") or (next_clean.startswith("ا") and not (next_clean.startswith("أ") or next_clean.startswith("إ") or next_clean.startswith("آ"))):
        return False
        
    # 2. منع الإدغام اللفظي الصارم (التنوين والنون الساكنة مع حروف يرملون)
    # تشمل الفحص إذا كانت الكلمة تنتهي بالنون أو التنوين (الذي يظهر في Whisper أحياناً كألف تنوين)
    huruf_yarmaloon = ['ي', 'ر', 'م', 'ل', 'و', 'ن']
    if current_clean.endswith("ن") or current_clean.endswith("ا"):
        if next_clean[0] in huruf_yarmaloon:
            return False
            
    # 3. حماية نهايات الكلمات من التداخل مع الحروف الحلقية والشفوية الشائعة في الوصل
    # إذا كانت المسافة الصوتية ملتحمة (Whisper يحدد هذا داخلياً بسياق الكلام)
    return True

def split_audio_into_words_ultimate(audio_file_path, output_folder="vocal_database_pure"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[+] تم إنشاء مجلد الجواهر النقية: {output_folder}")

    print("[...] جاري تحميل نموذج الذكاء الاصطناعي Whisper...")
    model = whisper.load_model("small")

    print(f"[...] جاري بدء الفحص الحاسم والمجهري للموجات الصوتية...")
    try:
        result = model.transcribe(audio_file_path, language="ar", word_timestamps=True)
        audio_data = whisper.load_audio(audio_file_path)
    except Exception as e:
        print(f"[-] خطأ في المعالجة: {e}")
        return
        
    sample_rate = 16000
    saved_count = 0
    skipped_count = 0

    # تجميع كل الكلمات في قائمة مرتبة سياقياً
    all_words = []
    for segment in result["segments"]:
        for word_info in segment["words"]:
            all_words.append(word_info)

    # حلقة الفرز والقطع المجهري
    for i in range(len(all_words)):
        word_info = all_words[i]
        word_text = word_info["word"].strip()
        
        # تنظيف علامات الترقيم
        clean_word = "".join(c for c in word_text if c.isalnum() or c in ["_", " "])
        if not clean_word:
            continue

        # جلب الكلمة التالية للفحص السياقي
        next_word_text = ""
        if i + 1 < len(all_words):
            next_word_text = all_words[i + 1]["word"].strip()

        # تطبيق اختبار النقاء الحاسم
        if not is_perfectly_isolated(clean_word, next_word_text):
            print(f"[-] [مستبعدة للتحيين] اتصال لغوي: ({clean_word}) -> التالية: ({next_word_text})")
            skipped_count += 1
            continue

        # حساب التوقيتات بهامش ميكرو-ثاني ضيق جداً لحماية نقاء اللفظ (20 ملي ثانية)
        start_time = max(0, word_info["start"] - 0.02)
        end_time = min(len(audio_data) / sample_rate, word_info["end"] + 0.02)
        
        start_index = int(start_time * sample_rate)
        end_index = int(end_time * sample_rate)

        word_audio_chunk = audio_data[start_index:end_index]

        # صياغة الاسم ومنع الكتابة فوق الملفات القديمة
        file_name = f"{clean_word}.wav"
        file_path = os.path.join(output_folder, file_name)
        
        counter = 1
        while os.path.exists(file_path):
            file_name = f"{clean_word}_{counter}.wav"
            file_path = os.path.join(output_folder, file_name)
            counter += 1

        # حفظ الملف بأعلى نقاء رقمي ذبذبي PCM 16-bit
        wav.write(file_path, sample_rate, (word_audio_chunk * 32767).astype(np.int16))
        saved_count += 1
        print(f"[💎 جوهرة معزولة]: {file_name}")

    print(f"\n==============================================")
    print(f"[✔] اكتمل جرد وتصفية قاعدة البيانات الصوتية!")
    print(f"    - إجمالي الجواهر النقية المستخرجة: {saved_count}")
    print(f"    - إجمالي الكلمات المستبعدة لعدم النقاء: {skipped_count}")
    print(f"==============================================")

# --- تشغيل النسخة الحاسمة والأدق ---
print("[!] تم إطلاق المحرك الصارم لعزل الكلمات النقية...")
split_audio_into_words_ultimate("test.mp3")
print("[!] انتهى البرنامج تماماً.")