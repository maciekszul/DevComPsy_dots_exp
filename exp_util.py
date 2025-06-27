import json
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path


class replacement_u3:
        def __init__(self):
            pass
        def getAIN(self, number):
            return np.random.random()


def check_equal(a):
    """
    returns boolean if every element in iterable is equal
    """
    try:
        a = iter(a)
        first = next(a)
        return all(first == rest for rest in a)
    except StopIteration:
        return True


def search_n(a, n):
    """
    search for n repeating numbers
    a = iterable
    n = number of repeating elements
    """
    check = []
    carrier = a[n-1:]
    for index, value in enumerate(carrier):
        check = check_equal(a[index: index+n])
        if check:
            break
    return check


def randomisation(c, N=3, n=1):
    """
    c - conditions dict
    n - number of repetitions
    N - number of consecutive elements
    """
    if isinstance(c, dict):
        c = np.tile(c.keys(), n)
    elif isinstance(c, np.ndarray):
        pass
    np.random.shuffle(c)
    while search_n(c, N):
        np.random.shuffle(c)
    return c


def is_valid(arr, N):
    """Check if the array has no N consecutive same elements."""
    for i in range(len(arr) - N + 1):
        if len(set(arr[i:i+N])) == 1:
            return False
    return True



def load_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
    return data


def save_dict_as_json(file_path, dictionary):
    """Saves a dictionary as a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(dictionary, json_file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving dictionary: {e}")


def update_json_file(file_path, update_dict):
    """Updates an existing JSON file with a dictionary. Replaces values of existing keys."""
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        data.update(update_dict)
        
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error updating dictionary: {e}")


def plot_staircase_results(output_df, file_path):
    plt.ioff()
    f, ax = plt.subplots(2, 1, figsize=[12, 9])
    for ix, trial_type in enumerate(output_df.opposite_label.unique()):
        data_ = output_df.loc[output_df.opposite_label == trial_type].reset_index(drop=True)
        cf_value = np.min(data_.opposite_strenght.unique())
        ax[ix].set_title(f"Counterfactual evidence: {trial_type}")
        ax[ix].plot([0, data_.index.max()], [cf_value, cf_value], lw=1, c="#55505C")
        ax[ix].scatter(data_.index, np.repeat(cf_value, data_.index.shape[0]), c="#55505C", label="Counterfactual Evidence", s=3)
        ax[ix].fill_between(data_.index, cf_value, 0, color="#55505C", alpha=0.1, lw=0)

        ax[ix].plot(data_.index, data_.signal_prop + cf_value, c="#7FC6A4")
        ax[ix].scatter(data_.index, data_.signal_prop + cf_value, c="#7FC6A4", label="Evidence")
        error_bool = ~data_.response_correct.to_numpy()
        ax[ix].scatter(data_.index.to_numpy()[error_bool], data_.signal_prop[error_bool] + cf_value, c="red", label="Errors", zorder=999)

        ax[ix].fill_between(data_.index, data_.signal_prop + cf_value, 1, color="#FAF33E", alpha=0.1, lw=0, label="Noise")
        ax[ix].fill_between(data_.index, data_.signal_prop + cf_value, cf_value, color="#7FC6A4", alpha=0.2, lw=0)
        ax[ix].set_xlabel("trial")
        ax[ix].set_ylabel("signal dot proportion")
        ax[ix].set_ylim(0.0, 1.0)

        ax2 = ax[ix].twinx()
        ax2.plot(data_.index, data_.scale_response, c="dodgerblue")
        ax2.scatter(data_.index, data_.scale_response, c="dodgerblue")
        ax2.set_ylim(-5, 105)
        ax2.set_ylabel("Confidence rating", color="dodgerblue")

    ax[0].legend(fontsize="x-small", loc=3)
    plt.savefig(file_path, transparent=False)
    plt.close("all")

    return file_path


def check_many(multiple, target, func=None):
    """
    Check for the presence of strings in a target string.

    Parameters
    ----------
    multiple : list
        List of strings to be found in the target string.
    target : str
        The target string in which to search for the specified strings.
    func : str
        Specifies the search mode: "all" to check if all strings are present, or "any" to check if
        any string is present.

    Notes
    -----
    - This function works well with `if` statements in list comprehensions.
    """

    func_dict = {
        "all": all, "any": any
    }
    if func in func_dict:
        use_func = func_dict[func]
    else:
        raise ValueError("pick function 'all' or 'any'")
    check_ = []
    for i in multiple:
        check_.append(i in target)
    return use_func(check_)


def get_files(target_path, suffix, strings=(""), prefix=None, check="all", depth="all"):
    """
    Return a list of files with a specific extension, prefix, and name containing specific strings.

    Searches either all files in the target directory or within a specified directory.

    Parameters
    ----------
    target_path : str or pathlib.Path or os.Path
        The most shallow searched directory.
    suffix : str
        File extension in "\*.ext" format.
    strings : list of str
        List of strings to search for in the file name.
    prefix : str
        Limits the output list to file names starting with this prefix.
    check : str
        Specifies the search mode: "all" to check if all strings are present, or "any" to check if
        any string is present.
    depth : str
        Specifies the depth of the search: "all" for recursive search, "one" for shallow search.

    Returns
    -------
    subdirs : list
        List of pathlib.Path objects representing the found files.
    """

    path = Path(target_path)
    files = []
    if depth == "all":
        files = [file for file in path.rglob(suffix)
                 if file.is_file() and file.suffix == suffix[1:] and
                 check_many(strings, file.name, check)]
    elif depth == "one":
        files = [file for file in path.iterdir()
                 if file.is_file() and file.suffix == suffix[1:] and
                 check_many(strings, file.name, check)]

    if isinstance(prefix, str):
        files = [file for file in files if file.name.startswith(prefix)]
    files.sort(key=lambda x: x.name)
    return files


def get_directories(target_path, strings=(""), check="all", depth="all"):
    """
    Return a list of directories in the path (or all subdirectories) containing specified strings.

    Parameters
    ----------
    target_path : str or pathlib.Path or os.Path
        The most shallow searched directory.
    depth : str
        Specifies the depth of the search: "all" for recursive search, "one" for shallow search.

    Returns
    -------
    subdirs : list
        List of pathlib.Path objects representing the found directories.
    """

    path = Path(target_path)
    subdirs = []
    if depth == "all":
        subdirs = [subdir for subdir in path.glob("**/")
                   if subdir.is_dir() and check_many(strings, str(subdir), check)]
    elif depth == "one":
        subdirs = [subdir for subdir in path.iterdir()
                   if subdir.is_dir() and check_many(strings, str(subdir), check)]
    # pylint: disable=unnecessary-lambda
    subdirs.sort(key=lambda x: str(x))
    return subdirs


def make_directory(root_path, extended_dir):
    """
    Create a directory along with intermediate directories.

    Parameters
    ----------
    root_path : str or pathlib.Path or os.Path
        The root directory.
    extended_dir : str or list
        Directory or directories to create within `root_path`.

    Returns
    -------
    root_path : str or pathlib.Path or os.Path
        The updated root directory.
    """

    root_path = Path(root_path)
    if isinstance(extended_dir, list):
        root_path = root_path.joinpath(*extended_dir)
    else:
        root_path = root_path.joinpath(extended_dir)

    root_path.mkdir(parents=True, exist_ok=True)
    return root_path

def get_max(max_data, max_bool, no_block=999):
    blocks = np.unique(max_bool)
    blocks = blocks[blocks != no_block]
    block_maps = [max_bool == i for i in blocks]
    block_data = [max_data[i] for i in block_maps]
    max_0_100 = np.mean(np.sort([np.max(i) for i in block_data])[-3:])
    return max_0_100


def get_median(max_data, max_bool, no_block=999):
    blocks = np.unique(max_bool)
    blocks = blocks[blocks != no_block]
    block_maps = [max_bool == i for i in blocks]
    block_data = [max_data[i] for i in block_maps]
    max_0_100 = np.mean(np.sort([np.median(i) for i in block_data])[-3:])
    return max_0_100


def get_last_file(subject_path, ext="*.csv", string="block", ret_path=False):
    last_file = get_files(subject_path, ext, strings=[string])[-1]
    if ret_path:
        return last_file
    else:
        try:
            last_block = int(last_file.stem.split("_")[-2].split("-")[-1])
            return last_block
        except:
            return 0