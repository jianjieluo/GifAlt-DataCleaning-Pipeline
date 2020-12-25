start /wait python 1_precook_data_multi_process.py --src merge_gif_alt_info_all --num_worker 5  --remove_punc --dst gif_alt_info_clean_wo_punc

start /wait python 2_pos_tags_multi_process.py --num_worker 5 --src gif_alt_info_clean_wo_punc --backend spacy

start /wait python 3_main_cleaner.py --stage 1
start /wait python 3_main_cleaner.py --stage 2
start /wait python 3_main_cleaner.py --stage 3

start /wait python 4_domain_cleaner.py --stage 4
start /wait python 4_domain_cleaner.py --stage 5

@REM modify sentences
start /wait python 4_domain_cleaner.py --stage 6
start /wait python 7_boiler_plate_cleaner.py
start /wait python 8_hyper_transform_multi_process.py --num_worker 5 --src gif_alt_info_clean_5 --dst gif_alt_info_clean_5_hyper
start /wait python 8_hyper_transform_multi_process.py --num_worker 5 --src gif_alt_info_clean_6 --dst gif_alt_info_clean_6_hyper
start /wait python 8_hyper_transform_multi_process.py --num_worker 5 --src gif_alt_info_clean_7 --dst gif_alt_info_clean_7_hyper
