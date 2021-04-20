import os
import wandb
import tensorflow as tf
from absl import logging


WANDB_PROJECT_PATH = 'zxj32/test/{}:{}'



def load_wb_model(model_name: str, model_tag: str, dir:str='network'):
  wb_run = wandb.init(project='test', entity='zxj32')
  wb_path = WANDB_PROJECT_PATH.format(model_name, model_tag)
  logging.info("Downloading model artifact from: " + wb_path)
  artifact = wb_run.use_artifact(wb_path, type='model')
  download_dir = artifact.download()
  logging.info("Model checkpoint downloaded to: {}".format(download_dir))
  model = os.path.join(download_dir, f'snapshots/{dir}')
  loaded_network = tf.saved_model.load(model)
  return loaded_network


if __name__ == '__main__':
    model_name = "dqn-online-Empty-Random-6x6"  # @param {type:"string"}
    model_tag = "v0"  # @param {type:"string"}
    loaded_network = load_wb_model(model_name, model_tag)

    print(1111222)

