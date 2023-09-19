import os
from itertools import permutations
from ast_parsing import AST_parsing
from feature_spaces_tiling import extract_features_based_on_reconstructed_arrays

DEPENDENCIES = list(permutations("ijk", 1)) + list(permutations("ijk", 2)) + list(permutations("ijk", 3))


def is_prime(k):
    if k <= 1:
        return False
    if k == 2 or k == 3:
        return False
    if k % 2 == 0 or k % 3 == 0:
        return False

    for i in range(5, 1 + int(k ** 0.5), 6):
        if k % i == 0 or k % (i + 2) == 0:
            return False

    return True


def get_nth_prime_number(n):
    i = 2
    while n > 0:
        if is_prime(i):
            n -= 1
        i += 1
    i -= 1
    return i


def get_prime_number_parameter(brute_features):
    output = 1
    list_of_parameters = [int(parameter) for parameter in brute_features]
    for index in range(len(list_of_parameters)):
        output *= get_nth_prime_number(index) ** list_of_parameters[index]
    return output


def get_matrix_features(brute_features):
    read_features = brute_features[:len(DEPENDENCIES)]
    write_features = brute_features[len(DEPENDENCIES):]
    read_matrix = [[0, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]]
    for index, feature in enumerate(read_features):
        if feature > 0:
            dependency = DEPENDENCIES[index]
            for iterator_index, iterator in enumerate(dependency):
                read_matrix[iterator_index][ord(iterator) - ord('i')] += feature

    write_matrix = [[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]]
    for index, feature in enumerate(write_features):
        if feature > 0:
            dependency = DEPENDENCIES[index]
            for iterator_index, iterator in enumerate(dependency):
                write_matrix[iterator_index][ord(iterator) - ord('i')] += feature

    return read_matrix, write_matrix


def get_features(file_to_optimize='../cubic_tiling/programs_to_predict/mm_parsing.c'):
    ast_parsing = AST_parsing()
    ast_features = ast_parsing.get_features(file_to_optimize)
    extract_features_based_on_reconstructed_arrays(ast_features)
    extracted_features = list(ast_features.values())

    # print(extracted_features)
    liu_features = list(extracted_features[0].values())[1:5]
    yuki_features = list(extracted_features[0].values())[5:11]
    brute_features = list(extracted_features[0].values())[11:]
    return liu_features, yuki_features, brute_features, get_prime_number_parameter(brute_features), get_matrix_features(
        brute_features)


def make_string_from_list(elem):
    if str(elem.__class__) != "<class 'list'>" and str(elem.__class__) != "<class 'tuple'>":
        return str(elem)
    return str(elem).replace("[", "").replace("]", "").replace(")", "").replace("(", "")


def write_features():
    files = [file for file in os.listdir('./loop_generator_2/src') if (file != 'libs' and "parsing" not in file)]
    features = get_features('loop_generator_2/src/' + files[0])
    print(features, "\n_____________________")
    features_len = [len(i) if not isinstance(i, int) else 1 for i in features]
    with open("./X_params.csv", "a") as file_to_write:
        file_to_write.write(make_string_from_list(features_len) + "\n")
        to_print = ",".join([make_string_from_list(elem) for elem in features])
        file_to_write.write(to_print + "\n")
    for file in files[1:]:
        # os.system('gcc -E ../loop_generator/src/'+file)
        features = get_features('loop_generator_2/src/' + file)
        print(features, "\n_____________________")
        with open("./X_params.csv", "a") as file_to_write:
            to_print = ",".join([make_string_from_list(elem) for elem in features])
            file_to_write.write(to_print + "\n")

if __name__ == "__main__":
    write_features()
