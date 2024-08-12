fdir=$1
echo $fdir
CUDA_VISIBLE_DEVICES=0 python finetune2.py --base_model=openai/whisper-large-v2 --output_dir=$fdir/finetune_output  --train_data=$fdir/train.json --test_data=download/aiphone5/train_multi_lang.json  --per_device_train_batch_size=1 --language=None

python merge_lora.py --lora_model=$fdir/finetune_output/whisper-large-v2/checkpoint-final/ --output_dir=$fdir/model_output
