import os
import csv

if __name__ == '__main__':
    fieldnames = ['uid','gifUrl', 'title', 'alt']
    writer = csv.DictWriter(open(os.path.join('result', 'merge_gif_alt_info.csv'), 'w', encoding='utf-8'), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    for i in range(1, 3):
        reader = csv.DictReader(open(os.path.join('alt', 'q%d_gif_alt_info'%i + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
        while True:
            try:
                row  = next(reader)
                writer.writerow(row)
            except StopIteration:
                break
            except:
                print('error in ' + str(i))
        