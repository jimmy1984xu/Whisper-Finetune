import argparse
import functools
import os

import evaluate
import re
from typing import List

from zhconv import convert

from utils.utils import print_arguments, add_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg("ref_file",   type=str,     default="",     help="标注文件路径")
add_arg("hyp_file",   type=str,     default="",     help="预测文件路径")
add_arg("out_file",   type=str,     default="",     help="输出文件路径")
add_arg("remove_pun", type=bool,    default=False,  help="是否移除标点符号")
add_arg("to_simple",  type=bool,    default=True,   help="是否转为简体中文")
add_arg("to_small",   type=bool,    default=True,   help="是否转为小写英文")
add_arg("to_digit",   type=bool,    default=True,   help="是否转为数字")
add_arg("metric",     type=str,     default="cer",  choices=['cer', 'wer'],              help="评估方式")
args = parser.parse_args()
print_arguments(args)

def remove_punctuation(text: str or List[str]):
    punctuation = '!,.;:?、！，。；：？'
    if isinstance(text, str):
        text = re.sub(r'[{}]+'.format(punctuation), '', text).strip()
        return text
    elif isinstance(text, list):
        result_text = []
        for t in text:
            t = re.sub(r'[{}]+'.format(punctuation), '', t).strip()
            result_text.append(t)
        return result_text
    else:
        raise Exception(f'不支持该类型{type(text)}')


# 将繁体中文总成简体中文
def to_simple(text: str or List[str]):
    if isinstance(text, str):
        text = convert(text, 'zh-cn')
        return text
    elif isinstance(text, list):
        result_text = []
        for t in text:
            t = convert(t, 'zh-cn')
            result_text.append(t)
        return result_text
    else:
        raise Exception(f'不支持该类型{type(text)}')

def to_digit(text: str):
    number_word_to_digit = {
        # 英语
        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',
        # 瑞典语
        'noll': '0',
        'ett': '1',
        'två': '2',
        'tre': '3',
        'fyra': '4',
        'fem': '5',
        'sex': '6',
        'sju': '7',
        'åtta': '8',
        'nio': '9',
        # 法语
        'zéro': '0',
        'un': '1',
        'deux': '2',
        'trois': '3',
       'quatre': '4',
        'cinq': '5',
        'six': '6',
        'sept': '7',
        'huit': '8',
        'neuf': '9',
        # 西班牙语
        'cero': '0',
        'uno': '1',
        'dos': '2',
        'tres': '3',
        'cuatro': '4',
        'cinco': '5',
        'seis': '6',
        'siete': '7',
        'ocho': '8',
        'nueve': '9',
    }
    pattern = r'\b(' + '|'.join(number_word_to_digit.keys()) + r')\b'
    text = re.sub(pattern, lambda match: number_word_to_digit[match.group()], text)
    return text

def calculate_total_cer(args):
    metric = evaluate.load(f'metrics/{args.metric}.py')
    ref_file = args.ref_file
    hyp_file = args.hyp_file
    assert os.path.exists(ref_file), "标注文件不存在"
    assert os.path.exists(hyp_file), "预测文件不存在"

    # 打开文件
    ref_lines = open(ref_file, 'r', encoding='utf-8').readlines()
    hyp_lines = open(hyp_file, 'r', encoding='utf-8').readlines()

    assert len(ref_lines) == len(hyp_lines), "标注文件和预测文件行数不一致"
    results = []
    for i in range(len(ref_lines)):
        ref_line = ref_lines[i].strip()
        hyp_line = hyp_lines[i].strip()
        ref_id, ref_lang, ref_text = ref_line.strip().split(' ', 2)
        if len(hyp_line.strip().split(' ')) < 3:
            hyp_id, hyp_lang = hyp_line.strip().split(' ', 2)
            hyp_text = "null"
        else:
            hyp_id, hyp_lang, hyp_text = hyp_line.strip().split(' ', 2)
        assert ref_id == hyp_id, "标注文件和预测文件id不一致"

        if args.remove_pun:
            ref_text = remove_punctuation(ref_text)
            hyp_text = remove_punctuation(hyp_text)
        if args.to_small:
            ref_text = ref_text.lower()
            hyp_text = hyp_text.lower()
        if args.to_digit:
            ref_text = to_digit(ref_text)
            hyp_text = to_digit(hyp_text)
        if args.to_simple:
            ref_text = to_simple(ref_text)
            hyp_text = to_simple(hyp_text)

        metric.add(predictions=hyp_text, references=ref_text)

    # 输出文件
    # 对results 按照cer从大到小排序
    result = metric.compute()
    # result只保留3位小数
    result = round(result, 3)
    print(f"result: {result}")
    return result
def calculate_cer(args):
    metric = evaluate.load(f'metrics/{args.metric}.py')
    ref_file = args.ref_file
    hyp_file = args.hyp_file
    out_file = args.out_file
    assert os.path.exists(ref_file), "标注文件不存在"
    assert os.path.exists(hyp_file), "预测文件不存在"

    # 打开文件
    ref_lines = open(ref_file, 'r', encoding='utf-8').readlines()
    hyp_lines = open(hyp_file, 'r', encoding='utf-8').readlines()

    assert len(ref_lines) == len(hyp_lines), "标注文件和预测文件行数不一致"
    results = []
    for i in range(len(ref_lines)):
        ref_line = ref_lines[i].strip()
        hyp_line = hyp_lines[i].strip()
        ref_id, ref_lang, ref_text = ref_line.strip().split(' ', 2)
        if len(hyp_line.strip().split(' ')) < 3:
            hyp_id, hyp_lang = hyp_line.strip().split(' ', 2)
            hyp_text = "null"
        else:
            hyp_id, hyp_lang, hyp_text = hyp_line.strip().split(' ', 2)
        assert ref_id == hyp_id, "标注文件和预测文件id不一致"

        if args.remove_pun:
            ref_text = remove_punctuation(ref_text)
            hyp_text = remove_punctuation(hyp_text)
        if args.to_small:
            ref_text = ref_text.lower()
            hyp_text = hyp_text.lower()
        if args.to_digit:
            ref_text = to_digit(ref_text)
            hyp_text = to_digit(hyp_text)
        if args.to_simple:
            ref_text = to_simple(ref_text)
            hyp_text = to_simple(hyp_text)

        metric.add(predictions=hyp_text, references=ref_text)
        result = metric.compute()
        # result只保留3位小数
        result = round(result, 3)
        results.append((ref_id, result, ref_text, hyp_text))
    # 输出文件
    # 对results 按照cer从大到小排序
    results = sorted(results, key=lambda x: x[1], reverse=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        total_cer = calculate_total_cer(args)
        f.write(f"total_cer: {total_cer}\n")
        # 遍历results，判断cer为0.0的数量
        cer_0_count = 0
        for result in results:
            if result[1] == 0.0:
                cer_0_count += 1
        f.write(f"cer zero count: {cer_0_count}\n")
        for result in results:
            f.write(f"{result[0]} {result[1]} {result[2]} <-> {result[3]}\n")

if __name__ == '__main__':
    calculate_cer(args)
