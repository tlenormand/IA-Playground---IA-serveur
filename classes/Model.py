#!/usr/bin/env python3

from tensorflow import keras as K

from classes.MasterClass import MasterClass


class Model(MasterClass):
    def __init__(self, data):
        super().__init__(data)

        self.model = None
        self.model_target = None
        self.config = data.get('model_config', {})
        self.layers = data.get('model_layers', {})

        if self.config.get('can_load_model'):
            self.load_model()
        else:
            self.init_data(data)

    def init_data(self, data):
        self.optimizer = self.build_optimizer()
        self.loss_function = self.build_loss_function()

################################################################################
# Model layers
################################################################################

    def Conv2D(self, layer):
        return K.layers.Conv2D(
            filters=layer.get('filters', 32),
            kernel_size=layer.get('kernel_size', (3, 3)),
            strides=layer.get('strides', 1),
            padding=layer.get('padding', 'valid'),
            activation=layer.get('activation', 'relu')
        )

    def Flatten(self, layer):
        return K.layers.Flatten()

    def Dense(self, layer):
        return K.layers.Dense(
            units=layer.get('units', 128),
            activation=layer.get('activation', 'relu')
        )

    def Input(self, layer):
        return K.Input(
            shape=layer['input_shape']
        )

################################################################################
# Model optimizer
################################################################################

    def Adam(self):
        return K.optimizers.Adam(
            learning_rate=self.config.get('parameters_optimizer_learningRate', 0.001),
            clipnorm=self.config.get('parameters_optimizer_clipnorm', 1.0)
        )

################################################################################
# Model loss function
################################################################################
    
    def Huber(self):
        return K.losses.Huber()

################################################################################
# Model build
################################################################################

    def build_model(self):
        self.model = K.Sequential()

        for layer in self.layers.get('layers'):
            self.model.add(self.build_layer(layer))

        self.model.compile(
            optimizer=self.optimizer,
            loss=self.loss_function
        )

        self.model.build(input_shape=self.config.get('parameters_input_shape'))
        self.model = self.model
        self.model_target = K.models.clone_model(self.model)

        return self.model

    def build_optimizer(self):
        optimizer_type = self.config.get('parameters_optimizer_type')
        optimizer_function = getattr(self, optimizer_type, None)

        if optimizer_function is not None and callable(optimizer_function):
            return optimizer_function()
        else:
            raise ValueError(f"Error when build optimizer: optimizer {optimizer_type} not found")

    def build_layer(self, layer):
        layer_type = layer.get('type')
        layer_function = getattr(self, layer_type, None)

        if layer_function is not None and callable(layer_function):
            return layer_function(layer)
        else:
            raise ValueError(f"Error when build layer: layer {layer_type} not found")

    def build_loss_function(self):
        loss_function_type = self.config.get('parameters_loss_function_type')
        loss_function_function = getattr(self, loss_function_type, None)

        if loss_function_function is not None and callable(loss_function_function):
            return loss_function_function()
        else:
            raise ValueError(f"Error when build loss function: loss function {loss_function_type} not found")

################################################################################
# Model save/load
################################################################################

    def get_model_full_path(self):
        return f"{self.config.get('model_path')}{super().get_user_id()}__{super().get_model_name()}"

    def save_model(self):
        if self.model is None:
            raise ValueError("Error when save model: model is not built")

        self.model.save(self.get_model_full_path())
        return self.get_model_full_path()

    def load_model(self):
        print("self.get_model_full_path()::",self.get_model_full_path())
        self.model = K.models.load_model(self.get_model_full_path())
        self.model_target = K.models.clone_model(self.model)
        self.config['input_shape'] = self.model.layers[0].input_shape[1:]
        self.loss_function = self.model.loss
        self.optimizer = self.model.optimizer
        return True

################################################################################
# Others
################################################################################

    def update(self):
        self.model_target.set_weights(self.model.get_weights())
