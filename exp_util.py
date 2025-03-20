import json
import numpy as np
import pandas as pd
import matplotlib.pylab as plt


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


def randomisation(c, n):
    """
    c - conditions dict
    n - number of repetitions
    """
    if isinstance(c, dict):
        c = np.tile(c.keys(), n)
    elif isinstance(c, np.ndarray):
        pass
    np.random.shuffle(c)
    while search_n(c, 4):
        np.random.shuffle(c)
    return c


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
