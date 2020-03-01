import os, sys

gradeable_path = '/var/local/submitty/courses/s20/sample/submissions/grades_released_homework_autohiddenEC'

if __name__ == "__main__":
    if not os.exists('assignments') or not os.exists(gradeable_path):
        print('The assignments directory or the gradeable does not exist. Please create these.')
        sys.exit(1)

    num_to_place = min(len(os.list(greadeable_path)), len(os.list('assignments')))

    for root, dirs, files in os.walk(gradeable_path):
        for name in dirs:
            print(f'{root}: {name}')
