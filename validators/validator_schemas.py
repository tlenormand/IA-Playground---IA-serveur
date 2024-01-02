#!/usr/bin/env python3

schema = {
    'env/model/create': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'model_config': {
                    'type': 'object',
                    'properties': {
                        'game': {'type': 'string'},
                        'is_new_model': {'type': 'boolean'},
                        'can_load_model': {'type': 'boolean'},
                        'can_save_model': {'type': 'boolean'},
                        'model_path': {'type': 'string'},
                        'model_target_name': {'type': 'string'},
                        'model_target_path': {'type': 'string'},
                        'parameters_optimizer_type': {'type': 'string'},
                        'parameters_optimizer_learningRate': {'type': 'number'},
                        'parameters_optimizer_clipnorm': {'type': 'number'},
                        'parameters_input_shape': {'type': 'array', 'items': {'type': 'number'}},
                        'parameters_loss_function_type': {'type': 'string'},
                    },
                    'required': ['game', 'is_new_model', 'can_load_model', 'can_save_model', 'model_path',
                                 'model_target_name', 'model_target_path',
                                 'parameters_optimizer_type', 'parameters_optimizer_learningRate',
                                 'parameters_optimizer_clipnorm', 'parameters_input_shape',
                                 'parameters_loss_function_type']
                },
                'model_layers': {
                    'type': 'object',
                    'properties': {
                        'layers': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'layer_position': {'type': 'number'},
                                    'type': {'type': 'string'},
                                    'input_shape': {'type': 'array', 'items': {'type': 'number'}},
                                    'filters': {'type': 'number'},
                                    'strides': {'type': 'number'},
                                    'activation': {'type': 'string'},
                                    'units': {'type': 'number'}
                                },
                                'required': ['layer_position', 'type']
                            }
                        }
                    },
                    'required': ['layers']
                }
            },
            'required': ['user_id', 'model_name', 'model_config', 'model_layers']
        }
    },
    'env/model/delete': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
            },
            'required': ['user_id', 'model_name']
        }
    },
    'env/dockers/create': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'docker_config': {
                    'type': 'object',
                    'properties': {

                    },
                    'required': []
                }
            },
            'required': ['user_id', 'model_name']
        }
    },
    'env/dockers/get_model': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'docker_config': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                    },
                    'required': ['id']
                }
            },
            'required': ['user_id', 'model_name']
        }
    },
    'env/dockers/running': {
        'POST': {
            'type': 'object',
            'properties': {
                'docker_instance_ids': {'type': 'array', 'items': {'type': 'string'}},
            },
            'required': ['docker_instance_ids']
        }
    },
    'env/atari/train/start': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'atari_config': {
                    'type': 'object',
                    'properties': {
                        'game': {'type': 'string'},
                        'epsilon': {'type': 'number'},
                        'epsilon_min': {'type': 'number'},
                        'can_render': {'type': 'boolean'},
                        'can_train': {'type': 'boolean'},
                        'can_save_logs': {'type': 'boolean'},
                        'can_send_logs': {'type': 'boolean'},
                    },
                    'required': ['game', 'epsilon', 'epsilon_min', 'can_render', 
                                 'can_train', 'can_save_logs', 'can_send_logs']
                },
                'docker_config': {
                    'type': 'object',
                    'properties': {
                        'model_path': {'type': 'string'},
                        'can_load_model': {'type': 'boolean'},
                        'can_save_model': {'type': 'boolean'},
                        'can_containerize': {'type': 'boolean'},
                    },
                    'required': ['model_path', 'can_load_model', 'can_save_model', 'can_containerize']
                }
            },
            'required': ['user_id', 'model_name', 'atari_config', 'docker_config']
        }
    },
    'env/atari/train/stop': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'docker_instance_ids': {'type': 'array', 'items': {'type': 'string'}},
                'docker_config': {
                    'type': 'object',
                    'properties': {
                        'model_path': {'type': 'string'},
                        'can_load_model': {'type': 'boolean'},
                        'can_save_model': {'type': 'boolean'},
                        'can_containerize': {'type': 'boolean'},
                    },
                    'required': ['model_path', 'can_load_model', 'can_save_model', 'can_containerize']
                }
            },
            'required': ['user_id', 'model_name', 'docker_instance_ids', 'docker_config']
        }
    },
    'env/atari/create': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'model_name': {'type': 'string'},
                'game': {'type': 'string'},
                'players': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {'type': 'string'},
                            'name': {'type': 'string'},
                            'atari_config': {
                                'type': 'object',
                                'properties': {
                                    'game': {'type': 'string'},
                                    'epsilon': {'type': 'number'},
                                    'epsilon_min': {'type': 'number'},
                                    'can_train': {'type': 'boolean'},
                                    'can_render': {'type': 'boolean'},
                                },
                                'required': ['game', 'epsilon', 'epsilon_min', 'can_train', 'can_render']
                            },
                            'model_config': {
                                'type': 'object',
                                'properties': {
                                    'model_name': {'type': 'string'},
                                    'model_path': {'type': 'string'},
                                    'can_load_model': {'type': 'boolean'},
                                    'can_save_model': {'type': 'boolean'},
                                    'can_containerize': {'type': 'boolean'},
                                },
                                'required': ['model_name', 'model_path', 'can_load_model', 'can_save_model', 'can_containerize']
                            },
                            'docker_config': {
                                'type': 'object',
                                'properties': {
                                    'can_containerize': {'type': 'boolean'},
                                },
                                'required': ['can_containerize']
                            },
                            'logs_config': {
                                'type': 'object',
                                'properties': {
                                    'can_save_logs': {'type': 'boolean'},
                                    'can_send_logs': {'type': 'boolean'},
                                },
                                'required': ['can_save_logs', 'can_send_logs']
                            }
                        },
                        'required': ['type', 'name', 'atari_config', 'model_config', 'docker_config', 'logs_config']
                    }
                },
            },
            'required': ['user_id', 'model_name', 'game', 'players']
        }
    },
    'env/atari/reset': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'reset': {'type': 'boolean'},
                'players': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                        },
                        'required': ['name']
                    }
                },
            },
            'required': ['user_id', 'reset', 'players']
        }
    },
    'env/atari/step': {
        'POST': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'string'},
                'players': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'action': {'type': 'number'},
                        },
                        'required': ['name']
                    }
                },
            },
            'required': ['user_id', 'players']
        }
    }
}
