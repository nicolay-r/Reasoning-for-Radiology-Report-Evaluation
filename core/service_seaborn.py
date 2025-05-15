import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


class SeabornService(object):
    """ Handy visualizations based on seaborn API.
    """

    @staticmethod
    def __show_no_data(ax):
        ax.text(0.5, 0.5, 'NO DATA', horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=20, color='red')

    @staticmethod
    def confusion_heatmap_2d(true_list, predict_list, save_png_path, classes_list=None,
                             classes_list_visual=None, do_normalize=False,
                             title=None, x_caption=None, y_caption=None, figsize=(12, 6),
                             handle_visual_func=None):
        assert (isinstance(true_list, list))
        assert (isinstance(predict_list, list))
        assert (isinstance(classes_list, list) or classes_list is None)
        assert (isinstance(classes_list_visual, list) or classes_list_visual is None)
        assert (callable(handle_visual_func) or handle_visual_func is None)
        assert (len(true_list) == len(predict_list))

        fig, ax = plt.subplots(figsize=figsize)

        if len(true_list) == 0:
            SeabornService.__show_no_data(ax)
            plt.close()
            return

        if classes_list is None:
            # Extract the complete set of classes automatically.
            classes_list = list(set(true_list).union(predict_list))

        def __map_2_classes(answers):
            # Limitation O(N^2)
            return [classes_list.index(a) for a in answers]

        cf_matrix = confusion_matrix(y_true=__map_2_classes(true_list), y_pred=__map_2_classes(predict_list))

        # Optional normalization.
        hm_kwargs = {}
        if do_normalize:
            cf_matrix = (cf_matrix - np.min(cf_matrix)) / (np.max(cf_matrix) - np.min(cf_matrix))
            cf_matrix = cf_matrix.round(2)
            # Setup min and max default values.
            hm_kwargs["vmin"] = 0
            hm_kwargs["vmax"] = 1

        classes_list_visual = classes_list if classes_list_visual is None else classes_list_visual
        if classes_list_visual != classes_list:
            visual_classes = __map_2_classes(classes_list_visual)
            cf_matrix = cf_matrix[np.ix_(visual_classes, visual_classes)]

        # Optionally handle visual labels.
        classes_ticks = classes_list_visual
        if handle_visual_func is not None:
            classes_ticks = [handle_visual_func(c) for c in classes_list_visual]

        sns.heatmap(cf_matrix, linewidths=1, annot=True, fmt='g', cmap="Blues",
                    xticklabels=classes_ticks, yticklabels=classes_ticks, **hm_kwargs)

        if title is not None:
            plt.title(title)
        plt.xlabel(x_caption, fontsize=10)
        plt.ylabel(y_caption, fontsize=10)

        plt.tight_layout()
        plt.savefig(save_png_path)

        plt.clf()
        plt.close()
