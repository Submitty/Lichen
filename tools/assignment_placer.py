import os
import argparse
import shutil
import secrets

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("semester", help="The semester_id where assignments will be placed (i.e. s20).")
    parser.add_argument("course", help="The course_id where assignments will be placed (i.e. sample).")
    parser.add_argument("gradeable", help="The gradeable_id where assignments will be placed (i.e. grades_released_homework_autohiddenEC).")
    args = parser.parse_args()
    return args

def generateHashPrefix(nbytes = 8):
    return secrets.token_hex(nbytes)

if __name__ == "__main__":
    args = getArgs()
    gradeable_path = f'/var/local/submitty/courses/{args.semester}/{args.course}/submissions/{args.gradeable}'
    assignments_path = f'{os.path.dirname(os.path.realpath(__file__))}/assignments'

    if not os.path.isdir(assignments_path) or not os.path.isdir(gradeable_path):
        raise SystemExit('The assignments directory or the gradeable does not exist. Please create those.')

    files_in_assign = os.listdir(assignments_path)
    users_for_placement = os.listdir(gradeable_path)
    num_to_place = min(len(users_for_placement), len(files_in_assign))
    a_ind = 0

    hash_prefix = generateHashPrefix()
    print(f'Assignment prefix is: {hash_prefix} (regex: {hash_prefix}_*)')
    for user_id in users_for_placement:
        current_path = f'{gradeable_path}/{user_id}'
        res = list(filter(lambda x: os.path.isdir(f'{current_path}/{x}'), os.listdir(current_path)))
        highest = len(res) + 1
        new_path = f'{current_path}/{highest}'
        os.mkdir(new_path)
        ext = os.path.splitext(files_in_assign[a_ind])[1]
        shutil.copy2(f'assignments/{files_in_assign[a_ind]}', f'{new_path}/{hash_prefix}_{a_ind}{ext}')
        a_ind += 1
        if a_ind == num_to_place:
            break
