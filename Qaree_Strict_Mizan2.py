import os
import re
import whisper
import scipy.io.wavfile as wav
import numpy as np

def auto_diacritize_and_balance(word_text):
    """
    محلل الميزان الذكي: يستقبل الكلمة من Whisper، ويقوم ببناء 
    الخريطة التشكيلية (1 و 0) بناءً على النطق العربي القياسي للكلمة.
    """
    # تنظيف الكلمة من أي زوائد
    word_clean = re.sub(r'[^\w]', '', word_text)
    if not word_clean:
        return None

    pulses = []
    text_map = []

    # معالجة أشهر كلمات الفاتحة والسور القياسية لضمان النقاء المطلق
    # وبناء ميزان الحركات (1) والسكنات (0) لها آلياً خارج النطاق الصوتي
    dictionary_mizan = {
        "أعوذ": ([1, 0, 1, 0], ["أ", "ع", "و", "ذ"]),               # أَعُوذُ (أعْ: 10، و:0، ذ:1)
        "الله": ([1, 0, 1, 0, 1], ["أ", "ل", "ل", "ا", "ه"]),       # اَللَّه (الـ: 10، لَا: 10، هـ: 1)
        "لله": ([1, 0, 1, 0, 1], ["ل", "ل", "ل", "ا", "ه"]),        # لِلَّه
        "بالله": ([1, 0, 1, 0, 1, 0, 1], ["ب", "أ", "ل", "ل", "ل", "ا", "ه"]),
        "الرحمن": ([1, 0, 1, 0, 1, 0, 1], ["أ", "ر", "ر", "ح", "م", "ا", "ن"]), # أَرْ-رَحْ-مَانْ
        "الرحيم": ([1, 0, 1, 0, 1, 0, 1], ["أ", "ر", "ر", "ح", "ي", "م"]),      # أَرْ-رَ-حِـيمْ
        "الحمد": ([1, 0, 1, 0, 1], ["أ", "ل", "ح", "م", "د"]),      # اَلْ-حَمْ-دُ (10، 10، 1)
        "رب": ([1, 0, 1], ["ر", "ب", "ب"]),                         # رَبْ-بِ (10، 1)
        "العالمين": ([1, 0, 1, 0, 1, 0, 1, 0, 1], ["أ", "ل", "ع", "ا", "ل", "م", "ي", "ن"]),
        "مالك": ([1, 0, 1, 1], ["م", "ا", "ل", "ك"]),               # مَا-لِ-كِ (10، 1، 1)
        "يوم": ([1, 0, 1], ["ي", "و", "م"]),                         # يَوْ-مِ (10، 1)
        "الدين": ([1, 0, 1, 0, 1, 0, 1], ["أ", "د", "د", "ي", "ن"]), # أَدْ-دِ ينْ
        "إياك": ([1, 0, 1, 0, 1], ["إ", "ي", "ي", "ا", "ك"]),       # إِيْ-يَا-كَ
        "نعبد": ([1, 0, 1, 1], ["ن", "ع", "ب", "د"]),               # نَعْ-بُ-دُ
        "وإياك": ([1, 1, 0, 1, 0, 1], ["و", "إ", "ي", "ي", "ا", "ك"]),
        "نستعين": ([1, 0, 1, 1, 0, 1], ["ن", "س", "ت", "ع", "ي", "ن"]),
        "اهدنا": ([1, 0, 1, 1, 0], ["ا", "ه", "د", "ن", "ا"]),      # اِهْ-دِ-نَا
        "الصراط": ([1, 0, 1, 0, 1, 0, 1], ["أ", "ص", "ص", "ر", "ا", "ط"]),
        "المستقيم": ([1, 0, 1, 0, 1, 1, 0, 1], ["أ", "ل", "م", "س", "ت", "ق", "ي", "م"]),
        "صراط": ([1, 1, 0, 1], ["ص", "ر", "ا", "ط"]),              # صِ-رَا-طَ
        "الذين": ([1, 0, 1, 0, 1, 0, 1], ["أ", "ل", "ل", "ذ", "ي", "ن"]),
        "أنعمت": ([1, 0, 1, 0, 1], ["أ", "ن", "ع", "م", "ت"]),      # أَنْ-عَمْ-تَ (10، 10، 1)
        "عليهم": ([1, 1, 0, 1, 0], ["ع", "ل", "ي", "ه", "م"]),      # عَ-لَيْ-هُمْ (1، 10، 10)
        "غير": ([1, 0, 1], ["غ", "ي", "ر"]),                         # غَيْ-رِ (10، 1)
        "المغضوب": ([1, 0, 1, 0, 1, 0, 1], ["أ", "ل", "م", "غ", "ض", "و", "ب"]),
    }

    # إذا كانت الكلمة في قاموسنا الموزون، نمرر خريطتها فوراً
    if word_clean in dictionary_mizan:
        return dictionary_mizan[word_clean]
        
    # افتراض ديناميكي ذكي للكلمات الأخرى غير المدرجة لتوليد الحركات والسكنات تقريبياً
    vowels = ['ا', 'و', 'ي', 'ى', 'آ']
    for char in word_clean:
        if char in vowels:
            pulses.append(0)
        else:
            pulses.append(1)
        text_map.append(char)
        
    return pulses, text_map

def run_pure_mizan_fixed_extractor(audio_file_path, output_folder="pure_mizan_database"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[+] تم إنشاء مجلد قاموس الميزان الفعلي: {output_folder}")

    print("[...] جاري استدعاء الذاكرة اللغوية وتحليل الملف الصوتي...")
    model = whisper.load_model("small")
    
    try:
        result = model.transcribe(audio_file_path, language="ar", word_timestamps=True)
        audio_data = whisper.load_audio(audio_file_path)
    except Exception as e:
        print(f"[-] خطأ: {e}")
        return
        
    sample_rate = 16000
    saved_count = 0
    max_duplicates = 5 

    print("\n==============================================")
    print("[💎] بدء التقسيم ومحاكاة ميزان التشكيل الحرفي الصحيح:")
    print("==============================================")

    for segment in result["segments"]:
        for word_info in segment["words"]:
            word_text = word_info["word"].strip()
            
            analysis = auto_diacritize_and_balance(word_text)
            if not analysis:
                continue
                
            pulses, text_map = analysis
            w_start = word_info["start"]
            w_end = word_info["end"]
            pulse_duration = (w_end - w_start) / len(pulses)
            
            p_idx = 0
            while p_idx < len(pulses):
                # 1. اقتناص الوتد المجموع (110)
                if p_idx + 2 < len(pulses) and pulses[p_idx] == 1 and pulses[p_idx+1] == 1 and pulses[p_idx+2] == 0:
                    unit_text = "".join(text_map[p_idx:p_idx+3])
                    u_start = w_start + (p_idx * pulse_duration)
                    u_end = u_start + (3 * pulse_duration)
                    unit_type = "110"
                    step = 3
                # 2. اقتناص السبب الخفيف (10)
                elif p_idx + 1 < len(pulses) and pulses[p_idx] == 1 and pulses[p_idx+1] == 0:
                    unit_text = "".join(text_map[p_idx:p_idx+2])
                    u_start = w_start + (p_idx * pulse_duration)
                    u_end = u_start + (2 * pulse_duration)
                    unit_type = "10"
                    step = 2
                else:
                    p_idx += 1
                    continue

                s_idx = int(u_start * sample_rate)
                e_idx = int(u_end * sample_rate)
                chunk = audio_data[s_idx:e_idx]
                
                if len(chunk) > 400:
                    file_name = f"{unit_type}_{unit_text}_001.wav"
                    file_path = os.path.join(output_folder, file_name)
                    
                    counter = 1
                    while os.path.exists(file_path):
                        counter += 1
                        file_name = f"{unit_type}_{unit_text}_{str(counter).zfill(3)}.wav"
                        file_path = os.path.join(output_folder, file_name)
                    
                    if counter > max_duplicates:
                        p_idx += step
                        continue
                        
                    wav.write(file_path, sample_rate, (chunk * 32767).astype(np.int16))
                    saved_count += 1
                    print(f"   [✔ حفظ ميزان صريح]: {file_name}")
                
                p_idx += step

    print(f"\n==============================================")
    print(f"[✔] اكتمل بناء القاموس اللفظي بنجاح مذهل!")
    print(f"    - إجمالي الوحدات الصوتية المحفوظة والمفرزة: {saved_count}")
    print("==============================================")

# التشغيل الفوري
run_pure_mizan_fixed_extractor("test.mp3")