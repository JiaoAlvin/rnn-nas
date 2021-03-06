from config.env_config import EnvironmentConfig
from example_datasets.ptb.ptb_trainer import PtbTrainer
from model.architecture import Architecture
from ops.block_state_builder import CircularReferenceException


class ObjectiveEvaluation:
    __instance = None

    def __init__(self):
        if ObjectiveEvaluation.__instance is not None:
            raise Exception('Instance already exist.')
        ObjectiveEvaluation.__instance = self

    @staticmethod
    def get_instance():
        if ObjectiveEvaluation.__instance is None:
            ObjectiveEvaluation()

        return ObjectiveEvaluation.__instance

    @staticmethod
    def evaluate_cheap_objectives(_architecture: Architecture, identifier):
        """
        Returns the cheap objectives for the provided architecture.

        Cheap objectives are those that are quick to evaluate (and does not require training the model, for example).

        This method currently constructs a model as it would be used for the Penn Treebank dataset and then determine
        architectural attributes such as the number of parameters the model has, how many blocks the architecture contains,
        and how much multiplication operations does the architecture perform.

        :param _architecture:
        :param identifier:
        :return:
        """

        with PtbTrainer(_architecture, identifier, 0, nlayers=EnvironmentConfig.get_config('ptb_model_nlayers')) as ptb_trainer:
            try:
                model = ptb_trainer.build_model()
            except CircularReferenceException:
                return float('inf'), float('inf'), float('inf'), identifier

        number_of_parameters = model.get_arch_params(print_params=False)
        number_of_blocks = len(_architecture.blocks.keys())

        number_of_add = 0
        number_of_sub = 0
        number_of_mul = 0
        for key in _architecture.blocks.keys():
            block = _architecture.blocks[key]
            if len(block.inputs) > 1 or block.combination is not None:
                if block.combination == 'sub':
                    number_of_sub += 1
                elif block.combination == 'elem_mul':
                    number_of_mul += 1
                else:
                    number_of_add += 1

        if 'number_of_parameters' not in EnvironmentConfig.get_instance().config['cheap_objectives']:
            number_of_parameters = 1

        if 'number_of_blocks' not in EnvironmentConfig.get_instance().config['cheap_objectives']:
            number_of_blocks = 1

        if 'number_of_mul' not in EnvironmentConfig.get_instance().config['cheap_objectives']:
            number_of_mul = 1

        return number_of_parameters, number_of_blocks, number_of_mul, identifier
