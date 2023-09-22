from c_files_parser.ast_parsing import AST_parsing
from auxiliary_functions import save_to_cvs
from itertools import permutations
DEPENDENCIES = list(permutations("ijk", 1)) + list(permutations("ijk", 2)) + list(permutations("ijk", 3))

def reconstruct_arrays(list_of_iterators):
    arrays_for_read = []
    arrays_for_write = []
    current_pattern = ''
    current_index = list_of_iterators[0][1]
    for idx, iterator in enumerate(list_of_iterators):
        array_name, dimensionality, side, it = iterator
        if current_index == 0:
            current_index += dimensionality
            if list_of_iterators[idx - 1][2] == 'l':
                arrays_for_write.append(current_pattern)
            else:
                arrays_for_read.append(current_pattern)
            current_pattern = it
            current_index -= 1
        else:
            current_pattern += it
            current_index -= 1
    if list_of_iterators[-1][2] == 'l':
        arrays_for_write.append(current_pattern)
    else:
        arrays_for_read.append(current_pattern)
    return arrays_for_read, arrays_for_write


def yuki_approach_ijk_loop(arrays_for_read, arrays_for_writes):
    features = [0] * 6
    locality = ['i', 'j', 'k', 'ij', 'ik', 'jk', 'ijk']
    for array in arrays_for_read:
        if 'k' not in array:
            features[0] += 1
        else:
            if array in locality:
                features[1] += 1
            else:
                features[2] += 1

    for array in arrays_for_writes:
        if 'k' not in array:
            features[3] += 1
        else:
            if array in locality:
                features[4] += 1
            else:
                features[5] += 1

    return features


def bruteforce_approach_ijk_loop(arrays_for_read, arrays_for_writes):
    combinations_read = {}
    combinations_write = {}
    for elem in DEPENDENCIES:
        combinations_read["".join(elem)] = 0
        combinations_write["".join(elem)] = 0
    # combinations_read = {'a': 0, 'b': 0, 'c': 0, 'aa': 0, 'ab': 0, 'ac': 0, 'ba': 0,
    #                      'bb':0,'bc':0,'ca':0,'cb':0,'cc':0, 'aaa':0,'aab':0,'aac':0,'aba':0,'abb':0,'abc':0,
    #                      'aca':0, 'acb':0, 'acc':0, 'baa':0,'bab':0,'bac':0,'bba':0,'bbb':0,'bbc':0,
    #                      'bca':0, 'bcb':0, 'bcc':0,'caa':0,'cab':0,'cac':0,'cba':0,'cbb':0,'cbc':0,
    #                      'cca':0, 'ccb':0, 'ccc':0,}
    # combinations_write = {'a': 0, 'b': 0, 'c': 0, 'aa': 0, 'ab': 0, 'ac': 0, 'ba': 0,
    #                      'bb':0,'bc':0,'ca':0,'cb':0,'cc':0, 'aaa':0,'aab':0,'aac':0,'aba':0,'abb':0,'abc':0,
    #                      'aca':0, 'acb':0, 'acc':0, 'baa':0,'bab':0,'bac':0,'bba':0,'bbb':0,'bbc':0,
    #                      'bca':0, 'bcb':0, 'bcc':0,'caa':0,'cab':0,'cac':0,'cba':0,'cbb':0,'cbc':0,
    #                      'cca':0, 'ccb':0, 'ccc':0,}

    for array in arrays_for_read:
        combinations_read[array] += 1
    for array in arrays_for_writes:
        combinations_write[array] += 1

    combined_array = list(combinations_read.values()) + list(combinations_write.values())
    return combined_array


def liu_approach_ijk_loop(arrays_for_read, arrays_for_writes, number_of_statements=1):
    number_of_statements = len(arrays_for_writes)
    combined_array = arrays_for_read + arrays_for_writes
    features = [0] * 4
    iterators = ['k', 'j', 'i']
    locality = ['i', 'j', 'k', 'ij', 'ik', 'jk', 'ijk']
    inner_most_iterator = 'k'
    for array in combined_array:
        if array[-1] == inner_most_iterator and array in locality:
            features[0] += 1
    for idx, iterator in enumerate(iterators):
        for array in combined_array:
            if (iterator not in array) or (array[-1] == iterator and array in locality):
                features[1 + idx] += 1
    features = [x / number_of_statements for x in features]

    return features


def extract_features_generated_code(path):
    ast_parsing = AST_parsing()
    ast_features = ast_parsing.get_features(path)
    extract_features_based_on_reconstructed_arrays(ast_features)
    return list(ast_features.values())


def extract_features_based_on_reconstructed_arrays(features):
    for k, v in features.items():
        arrays = v['iterators']
        # print(v)
        reconstructed_arrays = reconstruct_arrays(arrays)
        liu_features = liu_approach_ijk_loop(*reconstructed_arrays)
        bruteforce_features = bruteforce_approach_ijk_loop(*reconstructed_arrays)
        yuki_features = yuki_approach_ijk_loop(*reconstructed_arrays)
        features[k] = {'label': features[k]['label']}

        add_features(features[k], liu_features, 'liu')
        add_features(features[k], yuki_features, 'yuki')
        add_features(features[k], bruteforce_features, 'brute')



def add_features(features, encoding, name):
    feature_names = {'liu': ['vectorization_feature', 'k-loop_feature', 'j-loop_feature', 'i-loop_feature'],
                     'yuki': ['loop_invariant_read', 'spatial_locality_read', 'no_locality_read',
                              'loop_invariant_write', 'spatial_locality_write', 'no_locality_write'],
                     'brute': ['a_r', 'b_r', 'c_r', 'aa_r', 'ab_r', 'ac_r', 'ba_r', 'bb_r', 'bc_r', 'ca_r', 'cb_r',
                               'cc_r', 'aaa_r', 'aab_r', 'aac_r', 'aba_r', 'abb_r', 'abc_r', 'aca_r', 'acb_r', 'acc_r',
                               'baa_r', 'bab_r', 'bac_r', 'bba_r', 'bbb_r', 'bbc_r', 'bca_r', 'bcb_r', 'bcc_r', 'caa_r',
                               'cab_r', 'cac_r', 'cba_r', 'cbb_r', 'cbc_r', 'cca_r', 'ccb_r', 'ccc_r', 'a_w', 'b_w',
                               'c_w', 'aa_w', 'ab_w', 'ac_w', 'ba_w', 'bb_w', 'bc_w', 'ca_w', 'cb_w', 'cc_w', 'aaa_w',
                               'aab_w', 'aac_w', 'aba_w', 'abb_w', 'abc_w', 'aca_w', 'acb_w', 'acc_w', 'baa_w', 'bab_w',
                               'bac_w', 'bba_w', 'bbb_w', 'bbc_w', 'bca_w', 'bcb_w', 'bcc_w', 'caa_w', 'cab_w', 'cac_w',
                               'cba_w', 'cbb_w', 'cbc_w', 'cca_w', 'ccb_w', 'ccc_w']

                     }
    for idx, value in enumerate(encoding):
        features[feature_names[name][idx]] = value