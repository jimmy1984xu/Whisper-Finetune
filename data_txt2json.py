import json
import wave
import sys
import os

# 获取wav音频时长
def get_wav_dur(path):
    with wave.open(path, 'rb') as wav_file:
        frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()
        return frames / float(frame_rate)

def make_data_json_by_txt(data_path):
    # data_path必须是一个绝对路径， 里面包含文件text.txt和wav，输出文件固定为text.json
    data_txt_file = data_path + "/text.txt"
    wav_path = data_path + "/wav/"
    data_json_file = data_path + "/text.json"
    # 先判断data_txt_file文件是否存在
    if not os.path.exists(data_txt_file) or not os.path.exists(wav_path):
        raise FileNotFoundError(f"{data_txt_file} or {wav_path} 不存在")
    if os.path.exists(data_json_file):
        os.remove(data_json_file)

    with open(data_txt_file, encoding='utf-8') as f, open(data_json_file, 'w', encoding='utf-8') as f_json:
        for line in f:
            l = line.strip().split(' ', 2)
            js = {}
            js["audio"] = {"path": wav_path + l[0] + ".wav"}
            js["sentence"] = l[2]
            js["language"] = l[1]
            dur = get_wav_dur(wav_path + l[0] + ".wav")
            js["duration"] = dur
            sent = {"start": 0, "end": dur, "text": l[2]}
            sents = []
            sents.append(sent)
            js["sentences"] = sents
            print(json.dumps(js, ensure_ascii=False))
            f_json.write(json.dumps(js, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python data_txt2json.py data_path")
        sys.exit(1)
    data_path = sys.argv[1]
    make_data_json_by_txt(data_path)
