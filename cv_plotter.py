import matplotlib.pyplot as plt
from genescores_dumper import AllScoresGeneScoresDumper
from math import sqrt

class CrossValidationPlotter(object):

    def __init__(self, directory_path=None):
        super(CrossValidationPlotter, self).__init__()
        if directory_path:
            self.directory_path = directory_path + "/"
        else:
            self.directory_path = ""

    def plot_cross_validation(self, cross_validation, iteration_number=None):
        for entity_list in cross_validation.entity_lists:
            entities = entity_list.get_entities()
            x_values = range(len(entities))

            scores = [ent.score for ent in entities]

            #plt.scatter(x_values, scores, label="Scores", color="green",marker="*", s=30)

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
            plot_filepath = "{preceding}{list_name}-" \
                            "{iteration:03d}.png".format(
                                preceding=self.directory_path,
                                list_name=entity_list.name,
                                iteration=iteration_number
                            )
            plt.savefig(plot_filepath)
            plt.close()

        gsd = AllScoresGeneScoresDumper(cross_validation, self.directory_path, ".{iteration:03d}".format(iteration=iteration_number))
        gsd.dump()






