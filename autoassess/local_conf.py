__author__ = 'moonkey'

import platform
import socket

# ##################################
##########  SERVER  ###############
###################################
model_root = '/mnt/ebs1/models/'



# easy hack to differ from local and server
local_name = platform.node()
if not local_name:
    local_name = socket.gethostname()
if 'mac' in local_name.lower():
    ###################################
    ##########    MAC   ###############
    ###################################
    model_root = '/opt/'

stanford_parser_dir = model_root + 'stanford-parser/'
stanford_postagger_dir = model_root + 'stanford-postagger/'
stanford_ner_dir = model_root + 'stanford-ner/'
word2vec_model_dir = model_root + 'word2vec/'
skip_thought_models_dir = model_root + 'skip-thought/'