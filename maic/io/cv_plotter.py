import matplotlib.pyplot as plt
from os import makedirs, path

class CrossValidationPlotter(object):

    def __init__(self, directory_path=None):
        super(CrossValidationPlotter, self).__init__()
        if directory_path:
            makedirs(directory_path, exist_ok=True)
            self.directory_path = directory_path
        else:
            self.directory_path = ""

    def plot_cross_validation(self, cross_validation, iteration_number=None):
        for entity_list in cross_validation.entity_lists:
            x_values = range(len(entity_list))

            truncated_list_weights = entity_list.get_truncated_weights_list()
            plt.plot(x_values, truncated_list_weights,
                     label="Truncated list weight", color="blue")
            fitted_weights = entity_list.weights_list
            if len(fitted_weights) == len(x_values):
                plt.plot(x_values, fitted_weights, label="Fitted",
                         color="pink")
                plt.plot(x_values, [entity_list.weight for x in x_values], ':', label="weight",
                         color="grey")
            # x-axis label
            plt.xlabel('Slot')
            # frequency label
            plt.ylabel('Score')
            # plot title
            if iteration_number:
                title = "{list_name} - iteration {iteration}".format(
                    list_name=entity_list.name, iteration=iteration_number)
            else:
                title = entity_list.name
            plt.title(title)
            # showing legend
            plt.legend()
            # function to save the plot
            plot_filepath = path.join(self.directory_path, f"{entity_list.name}-{iteration_number:03d}.png")
            plt.savefig(plot_filepath)
            plt.close()
