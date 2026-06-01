import os
import json
import wave

def load_database(json_path):
    """تحميل فهرس البيانات النصي"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def concatenate_audio_files(file_paths, output_path):
    """دمج ملفات الصوت المتتالية في ملف واحد مع الحفاظ على الخصائص"""
    if not file_paths:
        print("خطأ: لا توجد ملفات صوتية صالحة للدمج.")
        return False

    try:
        data = []
        # قراءة خصائص أول ملف للاعتماد عليها (التردد، القنوات، وعمق الصوت)
        with wave.open(file_paths[0], 'rb') as w:
            params = w.getparams()
            
        # تجميع قنوات الصوت من كل الملفات
        for path in file_paths:
            with wave.open(path, 'rb') as w:
                # نتأكد أن الملفات لها نفس الخصائص تقريباً لتفادي التشوه
                data.append(w.readframes(w.getnframes()))

        # كتابة الملف الصوتي المدمج النهائي
        with wave.open(output_path, 'wb') as w_out:
            w_out.setparams(params)
            for frame in data:
                w_out.writeframes(frame)
                
        return True
    except Exception as e:
        print(f"حدث خطأ أثناء دمج الصوت: {e}")
        return False

def generate_speech():
    base_dir = r"F:\Qaree"
    json_path = os.path.join(base_dir, "database_index.json")
    output_audio = os.path.join(base_dir, "output_speech.wav")
    
    if not os.path.exists(json_path):
        print(f"خطأ: لم يتم العثور على ملف الفهرس في: {json_path}. يرجى تشغيل برنامج الحصر أولاً.")
        return

    # 1. تحميل البيانات
    db = load_database(json_path)
    words_pool = db.get("words", {})
    
    print("\n--- محرك توليد الكلام التجريبي جاهز ---")
    print("اكتب الجملة التي تريد توليدها (مستخدماً كلمات متوفرة في المجلد لديك حالياً):")
    user_text = input("أدخل النص هنا: ")
    
    # 2. تحليل النص إلى كلمات
    input_words = user_text.strip().split()
    audio_files_to_merge = []
    missing_words = []
    
    # 3. البحث عن الملفات الصوتية للكلمات
    for word in input_words:
        # إزالة علامات التشكيل البسيطة إن وجدت لتسهيل البحث (خطوة أولية)
        clean_word = word.replace("َ","").replace("ُ","").replace("ِ","").replace("ْ","")
        clean_word = clean_word.replace("ّ","") # الشدة
        
        # البحث في قاعدة البيانات عن الكلمة (باسمها كما هو مخزن)
        # ملاحظة: يفضل إدخال الكلمات بالاسم المطابق تماماً لملف الصوت
        if word in words_pool:
            audio_files_to_merge.append(words_pool[word]["file_path"])
        elif clean_word in words_pool:
            audio_files_to_merge.append(words_pool[clean_word]["file_path"])
        else:
            missing_words.append(word)

    # تنبيه المستخدم بالكلمات غير المتاحة
    if missing_words:
        print(f"\nتنبيه: الكلمات التالية غير متوفرة في مجلد الكلمات الكاملة حالياً: {missing_words}")
        print("في المراحل القادمة، سنقوم بتركيب هذه الكلمات من مجلد المقاطع (maqatee).")
    
    # 4. تنفيذ الدمج للمتاح
    if audio_files_to_merge:
        print(f"\nجاري دمج {len(audio_files_to_merge)} ملفات صوتية...")
        success = concatenate_audio_files(audio_files_to_merge, output_audio)
        if success:
            print("\n==========================================")
            print("--- تم توليد الصوت بنجاح! ---")
            print(f"تم حفظ الملف الصوتي النهائي في: {output_audio}")
            print("يمكنك الذهاب للمجلد وتشغيله لتسمع النتيجة بنفسك.")
            print("==========================================")
    else:
        print("\nخطأ: لم نجد أي كلمة مطابقة في المجلد لتوليد الصوت.")

if __name__ == "__main__":
    generate_speech()