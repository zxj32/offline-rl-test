#@title Import modules.
#python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import time
from absl import app, flags, logging
from tqdm import tqdm

from acme.agents.tf import actors

from acme import EnvironmentLoop
from acme.utils import counting
import wandb

import networks
import trfl
import tensorflow as tf
import sonnet as snt
from utils import load_tf_dataset, _build_environment, _build_custom_loggers, \
    preprocess_dataset, compute_empirical_policy, load_wb_model
from visualization import evaluate_q, visualize_policy

from acme.tf import utils as tf2_utils
from cql.learning import CQLLearner

# general run config
flags.DEFINE_string('environment_name', 'MiniGrid-Empty-6x6-v0', 'MiniGrid env name.')
flags.DEFINE_string('logs_tag', 'tag', 'Tag a specific run for logging in TB.')
flags.DEFINE_boolean('wandb', True, 'Whether to log results to wandb.')
flags.DEFINE_string('wandb_id', '', 'Specific wandb id if you wish to continue in a checkpoint "fd47827575b50ffd19890ea8ef00e8b6fb86587e".')
flags.DEFINE_string('dataset_dir', 'datasets', 'Directory containing an offline dataset.')
flags.DEFINE_integer('evaluate_every', 100, 'Evaluation period.')
flags.DEFINE_integer('evaluation_episodes', 10, 'Evaluation episodes.')
flags.DEFINE_integer('max_eval_episode_len', 100, 'Evaluation episodes.')
flags.DEFINE_integer('epochs', 100, 'Number of epochs to run (samples only 1 transition per episode in each epoch).')
flags.DEFINE_integer('seed', 1234, 'Random seed for replicable results. Set to 0 for no seed.')

# general learner config
flags.DEFINE_integer('batch_size', 64, 'Batch size.')
flags.DEFINE_float('epsilon', 0.05, 'Epsilon for the epsilon greedy in the env.')
flags.DEFINE_float('learning_rate', 1e-4, 'Learning rate.')
flags.DEFINE_float('discount', 0.99, 'Discount factor.')
flags.DEFINE_integer('n_step_returns', 1, 'Bootstrap after n steps.')

# specific config
flags.DEFINE_float('cql_alpha', 1.0, 'Scaling parameter for the offline loss regularizer.')
flags.DEFINE_string('policy_improvement_mode', 'binary', 'Defines how the advantage is processed.')
flags.DEFINE_float('translate_lse', 1., 'Coefficient by which LogSumExp is scaled to make estimate more accurate.')
flags.DEFINE_string('model_name', 'dqn-online-FourRooms', 'load model.')
flags.DEFINE_string('model_tag', 'v5', 'load model.')


FLAGS = flags.FLAGS

WANDB_PROJECT_PATH = 'zxj32/test/{}:{}'


def init_or_resume():
    wb_run = wandb.init(project="test",
                        group=FLAGS.logs_tag,
                        id=FLAGS.wandb_id or str(int(time.time())),
                        config=FLAGS.flag_values_dict(),
                        resume=FLAGS.wandb_id is not None,
                        reinit=True) if FLAGS.wandb else None
    if FLAGS.wandb_id:
        checkpoint_dir = wandb.run.summary['checkpoint_dir']
        group = wandb.run.summary['group']

        logging.info("Downloading model artifact from: " + WANDB_PROJECT_PATH.format(group))
        artifact = wb_run.use_artifact(WANDB_PROJECT_PATH.format(group), type='model')
        download_dir = artifact.download(root=checkpoint_dir)
        FLAGS.acme_id = checkpoint_dir.split('/')[-2]
        logging.info("Model checkpoint downloaded to: {}".format(download_dir))
    return wb_run


def main(_):
    wb_run = init_or_resume()

    if FLAGS.seed:
        tf.random.set_seed(FLAGS.seed)
    # Create an environment and grab the spec.
    environment, env_spec = _build_environment(FLAGS.environment_name,
                                               max_steps=FLAGS.max_eval_episode_len)

    # Load demonstration dataset.
    raw_dataset = load_tf_dataset(directory=FLAGS.dataset_dir)
    empirical_policy = compute_empirical_policy(raw_dataset)

    dataset = preprocess_dataset(raw_dataset,
                                 FLAGS.batch_size,
                                 FLAGS.n_step_returns,
                                 FLAGS.discount)

    # Create the main critic network
    model_name = FLAGS.model_name  # @param {type:"string"}
    model_tag = FLAGS.model_tag # @param {type:"string"}
    critic_network = load_wb_model(model_name, model_tag)

    policy_network = snt.Sequential([
        critic_network,
        networks.GreedyHead2(),
    ])

    tf2_utils.create_variables(critic_network, [env_spec.observations])

    # Create the actor which defines how we take actions.
    evaluation_actor = actors.FeedForwardActor(policy_network)

    counter = counting.Counter()

    disp, disp_loop = _build_custom_loggers(wb_run)

    eval_loop = EnvironmentLoop(
        environment=environment,
        actor=evaluation_actor,
        counter=counter,
        logger=disp_loop)

    learner = CQLLearner(
        network=critic_network,
        dataset=dataset,
        discount=FLAGS.discount,
        importance_sampling_exponent=0.2,
        learning_rate=FLAGS.learning_rate,
        cql_alpha=FLAGS.cql_alpha,
        translate_lse=FLAGS.translate_lse,
        target_update_period=100,
        empirical_policy=empirical_policy,
        logger=disp,
        counter=counter)

    # Run the environment loop.
    for e in tqdm(range(FLAGS.epochs)):
        for _ in range(FLAGS.evaluate_every):
            learner.step()
        eval_loop.run(FLAGS.evaluation_episodes)
        # Visualization of the policy
        Q = evaluate_q(learner._network, environment)
        plot = visualize_policy(Q, environment)
        wb_run.log({'chart': plot, 'epoch_counter': e})

    learner.save(tag=FLAGS.logs_tag)


if __name__ == '__main__':
    app.run(main)

