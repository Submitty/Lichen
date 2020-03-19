import os, sys
import shutil

gradeable_path = '/var/local/submitty/courses/s20/sample/submissions/grades_released_homework_autohiddenEC'

if __name__ == "__main__":
    if not os.path.isdir('assignments') or not os.path.isdir(gradeable_path):
        print('The assignments directory or the gradeable does not exist. Please create these.')
        sys.exit(1)

    files_in_assign = os.listdir('assignments')
    num_to_place = min(len(os.listdir(gradeable_path)), len(files_in_assign))
    placed = 0
    ci = 0
    gradeable_path_count = gradeable_path.count('/')
    for root, dirs, files in os.walk(gradeable_path):
        for name in dirs:
            print(f'{root} {name}')
            if (root.count('/') == gradeable_path_count):
                res = list(filter(lambda x: not 'json' in x, os.listdir(f'{root}/{name}')))
                highest = int(max(res)) + 1
                new_path = f'{root}/{name}/{highest}'
                os.mkdir(new_path)
                shutil.copy2(f'assignments/{files_in_assign[ci]}', f'{new_path}/{files_in_assign[ci]}')
                ci+=1
                placed += 1
            if(placed == num_to_place):
                sys.exit()
