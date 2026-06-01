import os
import wave
import re

def parse_srt_time(time_str):
    """تحويل وقت الـ SRT (HH:MM:SS,mmm) إلى ثواني بدقة الملي ثانية"""
    match = re.match(r"(\d+):(\d+):(\d+),(\d+)", time_str)
    if match:
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return 0.0

def slice_audio_by_srt(audio_filename, srt_filename, output_folder_name):
    """
    تقطيع الملف الصوتي الكبير إلى ملفات صغيرة بناءً على فواصل وأسماء ملف الـ SRT
    """
    base_dir = r"F:\Qaree"
    audio_path = os.path.join(base_dir, audio_filename)
    srt_path = os.path.join(base_dir, srt_filename)
    output_dir = os.path.join(base_dir, output_folder_name)
    
    if not os.path.exists(audio_path) or not os.path.exists(srt_path):
        print("خطأ: تأكد من وجود ملف الصوت وملف الـ SRT في مجلد F:\\Qaree")
        return

    # إنشاء مجلد الحفظ إذا لم يكن موجوداً
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"جاري قراءة ملف الترجمة: {srt_filename} ...")
    
    # قراءة وتحليل ملف SRT
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # نمط البحث عن كتل الترجمة (الرقم، التوقيت، الاسم)
    pattern = r"(\d+)\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\n(.+?)(?=\n\n|\n*$)"
    matches = re.findall(pattern, srt_content, re.DOTALL)
    
    if not matches:
        print("خطأ: لم يتم العثور على مقاطع صالحة داخل ملف الـ SRT أو التنسيق غير صحيح.")
        return

    print(f"جاري فتح ملف الصوت الرئيسي للبدء في القطع الكيميائي النقي...")
    with wave.open(audio_path, 'rb') as wav:
        params = wav.getparams()
        sample_rate = wav.getframerate()
        sampwidth = wav.getsampwidth()
        channels = wav.getnchannels()
        
        for idx, start_str, end_str, text in matches:
            text = text.strip()
            # تنظيف الاسم ليكون صالحاً كاسم ملف في ويندوز (إزالة الرموز غير الصالحة)
            clean_filename = re.sub(r'[\\/*?:"<>|]', "", text)
            if not clean_filename:
                clean_filename = f"segment_{idx}"
                
            start_sec = parse_srt_time(start_str)
            end_sec = parse_srt_time(end_str)
            
            # حساب مكان الإطارات (Frames) في الملف الصوتي
            start_frame = int(start_sec * sample_rate)
            end_frame = int(end_sec * sample_rate)
            num_frames_to_read = end_frame - start_frame
            
            # الانتقال لمكان بداية المقطع وقراءته
            wav.setpos(start_frame)
            audio_frames = wav.readframes(num_frames_to_read)
            
            # حفظ الملف الصغير الجديد
            output_file_path = os.path.join(output_dir, f"{clean_filename}.wav")
            with wave.open(output_file_path, 'wb') as sub_wav:
                sub_wav.setparams(params)
                sub_wav.writeframes(audio_frames)
                
            print(f"تم استخراج: {clean_filename}.wav [{start_str} -> {end_str}]")

    print(f"\n--- تم الانتهاء بنجاح عبقري! ---")
    print(f"تم حفظ جميع الملفات المقطعة داخل المجلد: {output_dir}")

# --- تشغيل البرنامج ---
if __name__ == "__main__":
    # اسم الملف الصوتي الكبير لديك
    LARGE_AUDIO = "test_record.wav" 
    # اسم ملف SRT (الذي استخرجناه من الصمت وقمنا بتعديل أسماء المقاطع داخله)
    SRT_FILE = "output_subtitles.srt" 
    # اسم المجلد الجديد الذي ستوضع فيه الملفات المقطعة تلقائياً
    OUTPUT_FOLDER = "sliced_segments"
    
    slice_audio_by_srt(LARGE_AUDIO, SRT_FILE, OUTPUT_FOLDER)